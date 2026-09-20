#!/usr/bin/env python3
"""Mine agent session transcripts for recurring, task-shaped failure points.

Usage: mine.py [--sessions N] [--out failures.json] [--projects DIR]
               [--sources claude,opencode,codex]

Sessions come from sources.py (Claude Code, opencode, Codex CLI).

Two signal sources:
  1. `session-recall --report --all N` aggregate error taxonomy
  2. Direct transcript scan of the N most recent sessions for
     user corrections ("never ...", "don't ...", "stop ...", "wrong") and
     tool error signatures.

Output: ranked clusters. Only clusters with recurrence across >=2 sessions
are emitted - one-off environment breakage is not a skill gap.
"""
import argparse
import json
import os
import re
import sqlite3
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sources  # noqa: E402

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


def recent_sessions(projects_dir, n, kinds=("claude",)):
    return sources.list_sessions(kinds, n, roots={"claude": projects_dir})


def error_signature(text):
    """Signature for one tool error text, or None when it has no content."""
    lines = [l.strip() for l in str(text or "").strip().splitlines() if l.strip()]
    if not lines:
        return None
    # "Exit code N" alone is content-free; pair it with the first
    # substantive line so different command failures cluster apart.
    first = lines[0]
    if re.match(r"^(Exit code|Error:?)\s*\d*\s*$", first) and len(lines) > 1:
        first = f"{lines[0]} | {lines[1]}"
    # Normalise volatile bits (paths, numbers) so signatures cluster.
    return re.sub(r"(/[\w./-]+|\d+)", "<x>", first)[:120]


def norm_prompt(text):
    return re.sub(r"\s+", " ", text.strip().lower())[:160]


def scan(sessions):
    corrections = {}  # signature -> {count, sessions, evidence}
    errors = {}
    anger = []
    first_prompts = {}  # normalized prefix -> {count, sessions, sample}
    session_stats = []  # {session, cwd, kind, user_msgs, out_tokens, errors}
    events_by_kind = {}  # kind -> {event type: count}
    for sess in sessions:
        sid = sess.id
        cwd = sess.cwd
        first_user_seen = False
        user_msgs = 0
        out_tokens = 0
        sess_errors = 0
        ev_counts = events_by_kind.setdefault(sess.kind, {})
        try:
            events = sources.iter_events(sess)
            for ev in events:
                et = ev["type"]
                ev_counts[et] = ev_counts.get(et, 0) + 1
                if et == "usage":
                    out_tokens += ev.get("output_tokens", 0) or 0
                elif et == "user_text":
                    text = ev["text"]
                    if not text:
                        continue
                    banner = bool(SYSTEM_BANNER_RE.search(text))
                    if not banner and not first_user_seen:
                        first_user_seen = True
                        if len(text) > 60 and not text.lstrip().startswith("<local-command-caveat>"):
                            key = norm_prompt(text)
                            slot = first_prompts.setdefault(key, {"count": 0, "sessions": set(),
                                                                  "sample": " ".join(text.split())[:MAX_SNIPPET]})
                            slot["count"] += 1
                            slot["sessions"].add(sid)
                        continue  # opening message is a prompt, not a correction
                    user_msgs += 1
                    if len(text) <= 500 and ANGER_RE.search(text) and not NOISE_RE.search(text):
                        anger.append({"session": sid, "cwd": cwd,
                                      "text": " ".join(text.split())[:MAX_SNIPPET]})
                    if (25 < len(text) <= 300 and CORRECTION_RE.search(text)
                            and not NOISE_RE.search(text) and not banner):
                        key = " ".join(text.lower().split())[:100]
                        key = re.sub(r"[^\w ]", "", key)[:80]
                        slot = corrections.setdefault(key, {"count": 0, "sessions": set(), "evidence": []})
                        slot["count"] += 1
                        slot["sessions"].add(sid)
                        if len(slot["evidence"]) < 3:
                            slot["evidence"].append(" ".join(text.split())[:MAX_SNIPPET])
                elif et == "tool_error":
                    sig = error_signature(ev["text"])
                    if sig is None:
                        continue
                    sess_errors += 1
                    slot = errors.setdefault(sig, {"count": 0, "sessions": set(), "evidence": []})
                    slot["count"] += 1
                    slot["sessions"].add(sid)
                    if not slot["evidence"]:
                        slot["evidence"].append(sig)
        except (OSError, sqlite3.Error) as exc:
            print(f"warning: could not read {sess.kind} session {sid}: {exc}", file=sys.stderr)
        session_stats.append({"session": sid, "cwd": cwd, "kind": sess.kind, "user_msgs": user_msgs,
                              "out_tokens": out_tokens, "errors": sess_errors})
    return corrections, errors, anger, first_prompts, session_stats, events_by_kind


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
    ap.add_argument("--sources", default=None,
                    help="comma list of claude,opencode,codex (default: all whose root exists)")
    args = ap.parse_args()

    roots = {"claude": args.projects}
    if args.sources:
        kinds = [k.strip() for k in args.sources.split(",") if k.strip()]
        bad = [k for k in kinds if k not in sources.KINDS]
        if bad:
            sys.exit(f"unknown source(s): {', '.join(bad)}")
    else:
        kinds = sources.available_kinds(roots)

    paths = recent_sessions(args.projects, args.sessions, kinds)
    if not paths:
        sys.exit("no session transcripts found")
    corrections, errors, anger, first_prompts, session_stats, events_by_kind = scan(paths)
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
        "sources": {k: sum(1 for p in paths if p.kind == k) for k in sources.KINDS},
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
    for k, counts in sorted(events_by_kind.items()):
        print(f"events[{k}]: " + "  ".join(f"{t}={n}" for t, n in sorted(counts.items())))
    if top_spend:
        t = top_spend[0]
        print(f"top spend session: {t['cwd']} ({t['out_tokens']:,} out tokens, {t['errors']} errors)")


if __name__ == "__main__":
    main()
