#!/usr/bin/env python3
"""Mine Claude session transcripts for recurring, task-shaped failure points.

Usage: mine.py [--sessions N] [--out failures.json] [--projects DIR]

Two signal sources:
  1. `session-recall --report --all N` aggregate error taxonomy
  2. Direct transcript scan of the N most recent JSONL session files for
     user corrections ("never ...", "don't ...", "stop ...", "wrong") and
     tool_result error signatures.

Output: ranked clusters. Only clusters with recurrence across >=2 sessions
are emitted - one-off environment breakage is not a skill gap.
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys
import time

CORRECTION_RE = re.compile(
    r"\b(never|don'?t|stop (doing|saying|using)|that'?s wrong|why did you|i told you|again[.!])\b",
    re.IGNORECASE,
)
# Stronger frustration signal: anger, exasperation, disbelief (EN+DE).
ANGER_RE = re.compile(
    r"(what (the|are) (fuck|hell)|wTF|jesus christ|for fuck'?s sake|verdammt|scheiße|"
    r"nicht schon wieder|warum (ist|das)|you (keep|broke|ruined)|this is (broken|wrong|a mess)|"
    r"i'?m (done|so tired)|unbelievable|ridiculous|what are you doing|why (is|does|did) (this|it|you)|!!!)",
    re.IGNORECASE,
)
NOISE_RE = re.compile(r"^\s*(\[|```|<|ok|okay|yes|no|thanks|continue|go)\b", re.IGNORECASE)
# System-injected text that arrives as user-role messages, not real corrections.
SYSTEM_BANNER_RE = re.compile(
    r"(this session is being continued from a previous conversation|^\s*<system-reminder"
    r"|^\s*base directory for this skill)",
    re.IGNORECASE,
)
MAX_SNIPPET = 220


# Eval-arm working dirs produce machine sessions, not real user work.
HARNESS_RE = re.compile(r"(skill-evals.*runs|skill-forge.runs)|-(with|without)$")


def recent_sessions(projects_dir, n):
    files = glob.glob(os.path.join(projects_dir, "*", "*.jsonl"))
    files = [f for f in files if os.path.getsize(f) > 2000
             and not HARNESS_RE.search(os.path.basename(os.path.dirname(f)))]
    files.sort(key=os.path.getmtime, reverse=True)
    return files[:n]


def user_text(entry):
    msg = entry.get("message")
    if not isinstance(msg, dict) or msg.get("role") != "user":
        return None
    content = msg.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [c.get("text", "") for c in content
                 if isinstance(c, dict) and c.get("type") == "text"]
        return "\n".join(p for p in parts if p)
    return None


def tool_errors(entry):
    """Yield an error signature for each tool_result error in an entry."""
    msg = entry.get("message")
    if not isinstance(msg, dict):
        return
    content = msg.get("content")
    if not isinstance(content, list):
        return
    for c in content:
        if isinstance(c, dict) and c.get("type") == "tool_result" and c.get("is_error"):
            text = c.get("content")
            if isinstance(text, list):
                text = " ".join(x.get("text", "") for x in text if isinstance(x, dict))
            text = str(text or "")
            lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
            if not lines:
                continue
            # "Exit code N" alone is content-free; pair it with the first
            # substantive line so different command failures cluster apart.
            first = lines[0]
            if re.match(r"^(Exit code|Error:?)\s*\d*\s*$", first) and len(lines) > 1:
                first = f"{lines[0]} | {lines[1]}"
            # Normalise volatile bits (paths, numbers) so signatures cluster.
            sig = re.sub(r"(/[\w./-]+|\d+)", "<x>", first)[:120]
            yield sig


def norm_prompt(text):
    return re.sub(r"\s+", " ", text.strip().lower())[:160]


def scan(paths):
    corrections = {}  # signature -> {count, sessions, evidence}
    errors = {}
    anger = []
    first_prompts = {}  # normalized prefix -> {count, sessions, sample}
    session_stats = []  # {session, cwd, user_msgs, out_tokens, errors}
    for path in paths:
        sid = os.path.basename(path)
        cwd = os.path.basename(os.path.dirname(path))
        try:
            fh = open(path, errors="replace")
        except OSError:
            continue
        first_user_seen = False
        user_msgs = 0
        out_tokens = 0
        sess_errors = 0
        for line in fh:
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            msg = entry.get("message")
            if isinstance(msg, dict):
                usage = msg.get("usage") or {}
                out_tokens += usage.get("output_tokens", 0) or 0
            text = user_text(entry)
            if text and not SYSTEM_BANNER_RE.search(text):
                if not first_user_seen:
                    first_user_seen = True
                    if len(text) > 60 and not text.lstrip().startswith("<local-command-caveat>"):
                        key = norm_prompt(text)
                        slot = first_prompts.setdefault(key, {"count": 0, "sessions": set(),
                                                              "sample": " ".join(text.split())[:MAX_SNIPPET]})
                        slot["count"] += 1
                        slot["sessions"].add(sid)
                    text = None  # opening message is a prompt, not a correction
            if text:
                user_msgs += 1
                if len(text) <= 500 and ANGER_RE.search(text) and not NOISE_RE.search(text):
                    anger.append({"session": sid, "cwd": cwd,
                                  "text": " ".join(text.split())[:MAX_SNIPPET]})
            if (text and 25 < len(text) <= 300 and CORRECTION_RE.search(text)
                    and not NOISE_RE.search(text) and not SYSTEM_BANNER_RE.search(text)):
                key = " ".join(text.lower().split())[:100]
                key = re.sub(r"[^\w ]", "", key)[:80]
                slot = corrections.setdefault(key, {"count": 0, "sessions": set(), "evidence": []})
                slot["count"] += 1
                slot["sessions"].add(sid)
                if len(slot["evidence"]) < 3:
                    slot["evidence"].append(" ".join(text.split())[:MAX_SNIPPET])
            for sig in tool_errors(entry):
                sess_errors += 1
                slot = errors.setdefault(sig, {"count": 0, "sessions": set(), "evidence": []})
                slot["count"] += 1
                slot["sessions"].add(sid)
                if not slot["evidence"]:
                    slot["evidence"].append(sig)
        session_stats.append({"session": sid, "cwd": cwd, "user_msgs": user_msgs,
                              "out_tokens": out_tokens, "errors": sess_errors})
    return corrections, errors, anger, first_prompts, session_stats


INFRA_RE = re.compile(
    r"(hook error|Permission to use|don'?t ask mode|timed out|Permission denied|"
    r"hook blocked|rate limit|usage limit)",
    re.IGNORECASE,
)


def emit_clusters(corrections, errors, min_sessions=2):
    clusters = []
    for sig, d in corrections.items():
        if len(d["sessions"]) >= min_sessions:
            clusters.append({
                "kind": "correction",
                "class": "infra" if INFRA_RE.search(sig) else "task",
                "signature": sig,
                "count": d["count"],
                "session_count": len(d["sessions"]),
                "evidence": d["evidence"],
            })
    for sig, d in errors.items():
        if len(d["sessions"]) >= min_sessions and d["count"] >= 3:
            clusters.append({
                "kind": "tool_error",
                "class": "infra" if INFRA_RE.search(sig) else "task",
                "signature": sig,
                "count": d["count"],
                "session_count": len(d["sessions"]),
                "evidence": d["evidence"],
            })
    # Recurrence across sessions dominates raw count.
    clusters.sort(key=lambda c: (c["session_count"], c["count"]), reverse=True)
    for i, c in enumerate(clusters):
        c["id"] = f"F-{int(time.time())}-{i:02d}"
    return clusters


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sessions", type=int, default=40)
    ap.add_argument("--out", default="failures.json")
    ap.add_argument("--projects", default=os.path.expanduser("~/.claude/projects"))
    ap.add_argument("--min-sessions", type=int, default=2)
    args = ap.parse_args()

    paths = recent_sessions(args.projects, args.sessions)
    if not paths:
        sys.exit("no session transcripts found")
    corrections, errors, anger, first_prompts, session_stats = scan(paths)
    clusters = emit_clusters(corrections, errors, args.min_sessions)

    # Repeated opening prompts = manual workflows begging to become skills.
    workflows = [{"kind": "repeated_workflow", "class": "task",
                  "signature": d["sample"][:80], "count": d["count"],
                  "session_count": len(d["sessions"]), "evidence": [d["sample"]]}
                 for k, d in first_prompts.items() if len(d["sessions"]) >= args.min_sessions]
    workflows.sort(key=lambda w: w["session_count"], reverse=True)
    clusters.extend(workflows)

    top_spend = sorted(session_stats, key=lambda s: s["out_tokens"], reverse=True)[:10]
    report = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "sessions_scanned": len(paths),
        "cluster_count": len(clusters),
        "clusters": clusters,
        "anger": anger[:30],
        "top_spend_sessions": top_spend,
        "session_stats": session_stats,
    }
    json.dump(report, open(args.out, "w"), indent=1)
    print(f"{len(clusters)} clusters from {len(paths)} sessions -> {args.out}")
    for c in clusters[:10]:
        print(f"  [{c['kind']}] x{c['count']} in {c['session_count']} sessions: {c['signature'][:90]}")
    print(f"anger hits: {len(anger)}  repeated workflows: {len(workflows)}")
    if top_spend:
        t = top_spend[0]
        print(f"top spend session: {t['cwd']} ({t['out_tokens']:,} out tokens, {t['errors']} errors)")


if __name__ == "__main__":
    main()
