#!/usr/bin/env python3
"""Pull the rules a person wrote for their agents out of their own local files. Local only, no network.

usage: extract_rules.py [PATH ...] [--no-defaults] [--out DIR] [--show] [--min-words N]

Reads the given files or folders plus, unless --no-defaults, the usual agent-instruction places:
  ~/.claude/CLAUDE.md, ./CLAUDE.md, ./AGENTS.md, ./.cursorrules, ./.cursor/rules/,
  ~/.claude/projects/*/memory/*.md, ~/.codex/AGENTS.md
Keeps imperative rule lines (never, always, don't, must, prefer, avoid, "use X not Y", feedback
"How to apply:" lines), redacts private details, drops rules that are mostly redaction, dedupes,
and sorts each rule into decide / judge / report / bans / format / persona.

Writes DIR/rules.json (default ./clone-work). Prints counts only; rule text is printed only with --show.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

TEXT_EXT = {".md", ".mdc", ".txt", ".markdown", ""}
MAX_BYTES = 1_000_000

# Redaction. Order matters: URLs before paths, emails before handles.
REDACT = [
    ("url", re.compile(r"\b(?:https?://|www\.)\S+", re.I)),
    ("email", re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b")),
    ("url", re.compile(r"\b[\w-]+(?:\.[\w-]+)*\.(?:com|io|cc|dev|ai|org|net|app|co|de|so|sh|me|xyz|uk|eu|us|gg|tv|ly|to)\b(?:/\S*)?", re.I)),
    ("handle", re.compile(r"(?<![\w@])@[A-Za-z0-9_][\w.]{1,30}")),
    ("ip", re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}(?::\d+)?\b")),
    ("phone", re.compile(r"(?<!\w)\+?\d[\d ()./-]{7,}\d(?!\w)")),
    ("amount", re.compile(r"(?:[$\u20ac\u00a3]\s?\d[\d,.]*\s?(?:[kKmMbB]\b|bn\b|million\b|billion\b)?|\b\d[\d,.]*\s?(?:[kKmM]\b|USD\b|EUR\b|euros?\b|dollars?\b|bucks\b)|\b\d[\d,.]*\s?[$\u20ac\u00a3])")),
    ("number", re.compile(r"\b\d{5,}\b")),
    ("path", re.compile(r"(?:~|\.{1,2})/[\w.@+-]*(?:/[\w.@+-]+)*/?|(?<![\w/])/(?:[\w.@+-]+/)+[\w.@+-]*|\b[\w-]+/[\w./-]+\.(?:md|json|py|ts|js|sh|yml|yaml|txt|toml)\b")),
    ("name", re.compile(r"\b[A-Z][a-z]+(?:[ -](?:[A-Z][a-z]+|[A-Z]{2,}))+\b")),
]
# Capitalised pairs that are ordinary words in rules, not people or companies.
NAME_OK = {
    "Claude Code", "Use When", "How To", "Google Docs", "Google Sheets", "Pull Request", "Pull Requests",
    "Read Before", "Do Not", "Never Use", "Always Use", "Title Case",
}
TOKEN = re.compile(r"\[(?:url|email|handle|ip|phone|amount|number|path|name|word)\]")

STARTERS = re.compile(
    r"^(never|always|don'?t|do not|must|mustn'?t|should|shouldn'?t|prefer|avoid|use|keep|lead|ship|check|"
    r"stop|no|only|ask|make|write|put|run|verify|decide|cut|default|treat|give|report|reply|start|"
    r"before|after|when|if)\b", re.I)
CONTAINS = re.compile(r"\b(never|always|must|don'?t|do not|instead of|rather than|banned|not allowed|hate|annoys?|can'?t stand|love it when)\b|\b\w+,? not \w+", re.I)
HOW_TO = re.compile(r"^\**\s*how to apply\s*:?\**\s*:?\s*", re.I)
WHY = re.compile(r"^\**\s*why\s*:?\**\s*:?", re.I)

BUCKETS = {
    "bans": ["never", "don't", "dont", "do not", "avoid", "banned", "ban", "no ", "stop", "not allowed", "forbidden"],
    "decide": ["decide", "decision", "choose", "pick", "recommend", "option", "approve", "approval", "ask",
               "wait", "ship", "launch", "plan", "priorit", "default", "escalate", "before acting"],
    "judge": ["verify", "check", "evidence", "test", "review", "quality", "proof", "source", "measure",
              "confirm", "audit", "fact", "number", "claim", "correct", "broken"],
    "report": ["report", "reply", "answer", "summary", "summar", "message", "update", "lead with",
               "outcome", "link", "status", "tell", "ping", "notify"],
    "format": ["format", "dash", "capital", "font", "layout", "markdown", "bullet", "emoji", "words",
               "line break", "length", "short", "table", "heading", "lowercase", "caption"],
    "persona": ["tone", "voice", "sound", "annoy", "hate", "love", "i like", "i want", "frustrat",
                "my style", "personality", "cheeky", "confident", "insecure", "casual", "formal"],
}
PRIORITY = ["persona", "format", "report", "judge", "decide", "bans"]


def default_paths(home: Path, cwd: Path) -> list[Path]:
    out = [home / ".claude/CLAUDE.md", cwd / "CLAUDE.md", cwd / "AGENTS.md", cwd / ".cursorrules",
           cwd / ".cursor/rules", home / ".codex/AGENTS.md"]
    out += [Path(p) for p in sorted(glob.glob(str(home / ".claude/projects/*/memory/*.md")))]
    return out


def iter_files(paths: list[Path]):
    seen = set()
    for p in paths:
        if p.is_dir():
            cands = sorted(q for q in p.rglob("*") if q.is_file())
        elif p.is_file():
            cands = [p]
        else:
            continue
        for q in cands:
            if q.suffix.lower() not in TEXT_EXT or q.stat().st_size > MAX_BYTES:
                continue
            r = q.resolve()
            if r not in seen:
                seen.add(r)
                yield q


COMMON = {"the", "a", "an", "if", "when", "use", "never", "always", "do", "don't", "only", "keep", "ask", "make",
          "write", "run", "check", "read", "send", "give", "put", "stop", "avoid", "prefer", "every", "each",
          "no", "not", "for", "in", "on", "with", "and", "or", "but", "then", "before", "after", "via", "from",
          "as", "how", "what", "who", "why", "where", "which", "you", "i", "my", "we", "your", "be", "is", "are", "it", "this", "that", "to", "at", "by"}


def _name(m: re.Match) -> str | None:
    words = re.split(r"[ -]", m.group(0))
    while words and words[0].lower() in COMMON:
        words = words[1:]
    if len(words) < 2 or " ".join(words) in NAME_OK or m.group(0) in NAME_OK:
        return None
    return " ".join(words)


# Well-known tools, platforms and languages that --aggressive keeps. Everything else capitalised mid-sentence goes.
KNOWN = {
    "Claude", "Codex", "Cursor", "ChatGPT", "GPT", "Gemini", "Opus", "Sonnet", "Haiku", "OpenAI", "Anthropic",
    "Google", "Gmail", "Chrome", "Safari", "Firefox", "Mac", "macOS", "Linux", "Windows", "iOS", "Android",
    "GitHub", "Git", "Slack", "Notion", "Figma", "Docker", "Python", "JavaScript", "TypeScript", "Node", "React",
    "SQL", "Postgres", "LinkedIn", "WhatsApp", "Instagram", "TikTok", "YouTube", "Twitter", "X", "Markdown",
    "English", "German", "French", "Spanish", "Italian", "Portuguese", "I", "OK", "AI", "API", "UI", "PR", "CI",
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
}
OPTIONS = {"aggressive": False, "words": set()}


def _word_pass(text: str, counts: dict | None) -> str:
    words = OPTIONS["words"]

    def sub(m):
        w = m.group(0)
        if w.lower() in words or (OPTIONS["aggressive"] and w not in KNOWN):
            if counts is not None:
                counts["word"] = counts.get("word", 0) + 1
            return "[word]"
        return w

    if words:
        text = re.sub(r"(?<![A-Za-z0-9])[A-Za-z0-9]+(?![A-Za-z0-9])", lambda m: sub(m) if m.group(0).lower() in words else m.group(0), text)
    if OPTIONS["aggressive"]:
        text = re.sub(r"(?<=[\w,;:)] )[A-Z][\w-]+", sub, text)
    return text


def redact(text: str, counts: dict | None = None) -> str:
    """Replace private details with [kind] tokens; counts[kind] is incremented per hit."""
    text = _word_pass(text, counts)
    for kind, pat in REDACT:
        def sub(m, kind=kind):
            if kind == "name":
                hit = _name(m)
                if hit is None:
                    return m.group(0)
                if counts is not None:
                    counts[kind] = counts.get(kind, 0) + 1
                return m.group(0)[: m.group(0).index(hit.split(" ")[0])] + "[name]"
            if counts is not None:
                counts[kind] = counts.get(kind, 0) + 1
            return f"[{kind}]"
        text = pat.sub(sub, text)
    return text


def clean_line(raw: str) -> str:
    s = raw.strip()
    s = re.sub(r"^(?:[-*+>]|\d+[.)])\s+", "", s)          # bullets, numbering, quotes
    s = re.sub(r"\*\*|__|`", "", s)                         # bold, code ticks
    s = re.sub(r"\[\[([^\]]+)\]\]", r"\1", s)               # wiki links
    s = re.sub(r"\s+", " ", s).strip()
    return s


def candidates(text: str):
    in_front = False
    lines = text.splitlines()
    for i, raw in enumerate(lines):
        if i == 0 and raw.strip() == "---":
            in_front = True
            continue
        if in_front:
            if raw.strip() == "---":
                in_front = False
            continue
        if raw.lstrip().startswith(("#", "|", "```")):
            continue
        s = clean_line(raw)
        if not s or WHY.match(s):
            continue
        how = HOW_TO.match(s)
        if how:
            s = s[how.end():].strip()
            for part in re.split(r"(?<=[.!?])\s+", s):
                yield part.strip()
            continue
        for part in re.split(r"(?<=[.!?])\s+(?=[A-Z])", s):
            part = part.strip()
            if STARTERS.match(part) or CONTAINS.search(part):
                yield part


def bucket_of(rule: str) -> str:
    low = " " + rule.lower() + " "
    scores = {b: sum(low.count(k) for k in kws) for b, kws in BUCKETS.items()}
    for b in ("persona", "format"):
        if scores[b]:
            return b
    neg = re.match(r"^(never|don'?t|do not|avoid|no|stop)\b", rule, re.I)
    best = max(PRIORITY, key=lambda b: (scores[b], -PRIORITY.index(b)))
    if neg and scores["bans"] >= max(scores[b] for b in ("decide", "judge", "report")):
        return "bans"
    return best if scores[best] else ("bans" if neg else "decide")


def norm(s: str) -> frozenset:
    return frozenset(w for w in re.findall(r"[a-z]+", s.lower()) if len(w) > 2)


def extract(paths: list[Path], min_words: int = 4, max_words: int = 45):
    redactions: dict = {}
    rules: list[dict] = []
    files = list(iter_files(paths))
    for f in files:
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for c in candidates(text):
            n = len(c.split())
            if not min_words <= n <= max_words:
                continue
            local: dict = {}
            r = redact(c, local)
            toks = len(TOKEN.findall(r))
            if toks and toks / max(1, len(r.split())) >= 0.25:
                for k, v in local.items():
                    redactions[k] = redactions.get(k, 0) + v
                redactions["dropped_rules"] = redactions.get("dropped_rules", 0) + 1
                continue
            for k, v in local.items():
                redactions[k] = redactions.get(k, 0) + v
            key = norm(r)
            if len(key) < 3:
                continue
            for existing in rules:
                k2 = existing["_key"]
                if key == k2 or len(key & k2) / len(key | k2) >= 0.8:
                    existing["count"] += 1
                    if f.name not in existing["sources"]:
                        existing["sources"].append(f.name)
                    break
            else:
                rules.append({"text": r, "count": 1, "sources": [f.name], "_key": key})
    for i, r in enumerate(sorted(rules, key=lambda r: -r["count"]), 1):
        r["id"] = f"r{i:03d}"
    rules.sort(key=lambda r: -r["count"])
    out = []
    for r in rules:
        out.append({"id": r["id"], "bucket": bucket_of(r["text"]), "text": r["text"], "count": r["count"],
                    "sources": r["sources"], "confirmed": False})
    return files, out, redactions


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Extract agent rules from your own local files (local only).")
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--no-defaults", action="store_true", help="only read the paths given")
    ap.add_argument("--out", default="clone-work", help="output folder for rules.json")
    ap.add_argument("--show", action="store_true", help="also print the rule text")
    ap.add_argument("--min-words", type=int, default=4)
    ap.add_argument("--redact-words", default="", help="comma-separated names to always redact (people, clients, companies)")
    ap.add_argument("--aggressive", action="store_true",
                    help="also redact every capitalised word mid-sentence except well-known tools and languages")
    a = ap.parse_args(argv)
    OPTIONS["aggressive"] = a.aggressive
    OPTIONS["words"] = {w.strip().lower() for w in a.redact_words.split(",") if w.strip()}
    paths = [Path(os.path.expanduser(p)) for p in a.paths]
    if not a.no_defaults:
        paths += default_paths(Path.home(), Path.cwd())
    files, rules, red = extract(paths, a.min_words)
    counts = {b: sum(1 for r in rules if r["bucket"] == b) for b in BUCKETS}
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    data = {"generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "files_read": len(files), "counts": counts, "redactions": red, "rules": rules}
    (out / "rules.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"files read: {len(files)}")
    print(f"rules kept: {len(rules)}")
    for b in BUCKETS:
        print(f"  {b:8s} {counts[b]}")
    print("redactions: " + ", ".join(f"{k} {v}" for k, v in sorted(red.items())) if red else "redactions: none")
    print(f"wrote {out / 'rules.json'} (local only; review it, set confirmed: true on the rules to keep)")
    if a.show:
        for r in rules:
            print(f"[{r['bucket']}] x{r['count']} {r['text']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
