#!/usr/bin/env python3
"""Lint copy against Fede's bans. Standard library only, no network.

usage: check_copy.py [--mode any|dm|post|linkedin|page] [--json] [--strict] [FILE ...]
       (reads stdin when no FILE is given)

Exit 0 clean, 1 on any error (or any warning with --strict), 2 on bad usage.
Errors are hard rules (dashes, banned phrases, disclaimers, the LinkedIn hook gate).
Warnings are judgment calls (length, greetings in DMs, repo links in posts).
"""
from __future__ import annotations

import argparse
import json
import re
import sys

EM, EN = "\u2014", "\u2013"
DASH_ENTITIES = ("&mdash;", "&ndash;", "&#8212;", "&#8211;", "&#x2014;", "&#x2013;")

BANNED = [
    "excited to announce", "thrilled to announce", "proud to announce", "happy to announce",
    "game changer", "game-changer", "game changing", "game-changing", "revolutionary",
    "unlock the power", "unlock your", "unleash", "supercharge", "in today's fast-paced",
    "in today’s fast-paced", "delve", "i hope this helps", "hope this helps", "truly insane",
    "let that sink in", "the future is here", "without further ado", "elevate your",
]
DISCLAIMERS = [
    r"\b(images?|visuals?|photos?|video|graphics?)\s+(are|is|were|was)\s+(ai[- ]generated|generated (by|with) ai)",
    r"\bthis (post|text) was (written|generated) (with|by) ai\b",
    r"\bai[- ]generated (images?|visuals?|content)\b",
    r"\bnot (sponsored|financial advice)\b",
]
GREETING = re.compile(r"^(hi|hey|hello|dear|good (morning|afternoon|evening))\b", re.I)
SIGNOFF = re.compile(r"^(best|cheers|regards|kind regards|best regards|thanks|thank you)\s*[,!.]?\s*$", re.I)
QUESTION_START = re.compile(r"^(what|why|how|who|when|where|which|do|does|did|are|is|have|has|can|could|would|should|ever|ready)\b", re.I)
UNCENSORED = re.compile(r"\bfuck(ing|ed|er)?\b", re.I)
RAISED_HANDS = "\U0001F64C"
MODES = ("any", "dm", "post", "linkedin", "page")


def _words(line: str) -> list[str]:
    return re.findall(r"[\w'’$%.,/+-]+", line)


def check(text: str, mode: str = "any") -> list[dict]:
    """Return findings: dicts with severity, rule, line, message."""
    out: list[dict] = []

    def add(sev, rule, line, msg):
        out.append({"severity": sev, "rule": rule, "line": line, "message": msg})

    lines = text.splitlines()
    for i, raw in enumerate(lines, 1):
        low = raw.lower()
        if EM in raw or EN in raw:
            add("error", "dash", i, "em or en dash; use a period, comma or colon")
        for ent in DASH_ENTITIES:
            if ent in low:
                add("error", "dash", i, f"dash entity {ent}; use a period, comma or colon")
        for phrase in BANNED:
            if phrase in low:
                add("error", "banned-phrase", i, f'banned phrase "{phrase}"')
        for pat in DISCLAIMERS:
            if re.search(pat, low):
                add("error", "disclaimer", i, "disclaimer line; lead with value, cut the disclaimer")
        if UNCENSORED.search(raw):
            add("error", "swearing", i, 'write "f*ck", not the full word')
        if RAISED_HANDS in raw:
            add("error", "emoji", i, "banned emoji")
        if mode in ("post", "linkedin") and "github.com" in low:
            add("warning", "repo-link", i, "posts link the website, not a repository")

    body = [l for l in lines if l.strip()]
    if mode == "linkedin" and body:
        hook = body[0].strip()
        n = len(_words(hook))
        if not 8 <= n <= 10:
            add("error", "hook-length", 1, f"hook is {n} words; the gate is 8 to 10")
        if not re.search(r"\d", hook):
            add("error", "hook-digit", 1, "hook has no digit")
        if hook.endswith("?") or QUESTION_START.match(hook):
            add("error", "hook-question", 1, "hook is a question; make it a statement")
    if mode in ("post", "linkedin"):
        wc = len(_words(text))
        if wc > 220:
            add("warning", "length", 0, f"{wc} words; aim for about 150 to 170")
        if body and body[-1].strip().endswith("?"):
            add("warning", "closing-question", len(lines), "ends on an engagement question; stop on the last fact")
    if mode == "dm" and body:
        if GREETING.match(body[0].strip()):
            add("warning", "dm-greeting", 1, "DMs skip the greeting")
        if SIGNOFF.match(body[-1].strip()):
            add("warning", "dm-signoff", len(lines), "DMs skip the signoff")
        if len(body) > 5:
            add("warning", "dm-length", 0, f"{len(body)} lines; two or three short lines")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("files", nargs="*")
    ap.add_argument("--mode", choices=MODES, default="any")
    ap.add_argument("--json", action="store_true", help="print findings as JSON")
    ap.add_argument("--strict", action="store_true", help="warnings also fail")
    a = ap.parse_args(argv)
    sources = []
    for f in a.files:
        with open(f, encoding="utf-8") as fh:
            sources.append((f, fh.read()))
    sources = sources or [("<stdin>", sys.stdin.read())]
    report, failed = [], False
    for name, text in sources:
        for f in check(text, a.mode):
            f["file"] = name
            report.append(f)
            if f["severity"] == "error" or a.strict:
                failed = True
    if a.json:
        print(json.dumps({"ok": not failed, "findings": report}, ensure_ascii=False, indent=2))
    else:
        for f in report:
            print(f'{f["file"]}:{f["line"]}: {f["severity"]} [{f["rule"]}] {f["message"]}')
        print("ok" if not failed else f"{sum(1 for f in report if f['severity'] == 'error')} error(s)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
