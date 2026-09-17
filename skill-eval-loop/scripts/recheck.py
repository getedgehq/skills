#!/usr/bin/env python3
"""Recheck probationary skills: did the failure rate drop after adoption?

Usage: recheck.py [--projects DIR] [--sessions N] [--sources claude,opencode,codex]

For each ledger entry with decision="probation" and recheck_due <= today,
re-mines recent sessions and compares the failure's session-rate against the
baseline recorded at adoption. Rate dropped -> KEEP (decision: adopt-confirmed).
No drop -> REVOKE: removes the installed skill and records decision: revoked.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import time


def main():
    root = os.environ.get("FORGE_ROOT", os.path.expanduser("~/skill-forge"))
    projects = os.path.expanduser("~/.claude/projects")
    sessions = 40
    args = sys.argv[1:]
    if "--projects" in args:
        projects = args[args.index("--projects") + 1]
    if "--sessions" in args:
        sessions = int(args[args.index("--sessions") + 1])
    src = ["--sources", args[args.index("--sources") + 1]] if "--sources" in args else []

    ledger = os.path.join(root, "ledger.jsonl")
    rows = [json.loads(l) for l in open(ledger)]
    today = time.strftime("%Y-%m-%d")
    due = [r for r in rows if r.get("decision") == "probation"
           and r.get("recheck_due", "9999") <= today]
    already = {r.get("skill") for r in rows if r.get("decision") in ("adopt-confirmed", "revoked")}
    due = [r for r in due if r["skill"] not in already]
    if not due:
        print("no probation rechecks due")
        return

    tmp = os.path.join(root, "mined", "recheck-failures.json")
    here = os.path.dirname(os.path.abspath(__file__))
    # mine.py lives in the sibling skill-miner skill
    miner = os.environ.get("MINER_SCRIPTS") or os.path.join(here, "..", "..", "skill-miner", "scripts")
    if not os.path.isfile(os.path.join(miner, "mine.py")):
        miner = here
    subprocess.run([sys.executable, os.path.join(miner, "mine.py"), "--sessions", str(sessions),
                    "--projects", projects, "--out", tmp] + src, check=True)
    fresh = json.load(open(tmp))

    for entry in due:
        sig = (entry.get("failure") or {}).get("signature") or ""
        baseline = entry.get("baseline_failure_rate")
        sig_tokens = set(re.findall(r"[a-z0-9]+", sig.lower()))
        rate_now = 0.0
        total = fresh.get("sessions_scanned", 0) or 1
        for c in fresh.get("clusters", []):
            ct = set(re.findall(r"[a-z0-9]+", c["signature"].lower()))
            if len(sig_tokens & ct) >= max(2, len(sig_tokens) // 2):
                rate_now = c["session_count"] / total
                break
        if baseline is None:
            print(f"SKIP {entry['skill']}: no baseline rate recorded")
            continue
        improved = rate_now < baseline * 0.7
        verdict = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "skill": entry["skill"],
            "decision": "adopt-confirmed" if improved else "revoked",
            "baseline_failure_rate": baseline,
            "current_failure_rate": round(rate_now, 4),
            "sessions_scanned": total,
        }
        with open(ledger, "a") as fh:
            fh.write(json.dumps(verdict) + "\n")
        if improved:
            print(f"KEEP {entry['skill']}: {baseline:.2%} -> {rate_now:.2%}")
        else:
            for d in (os.path.expanduser("~/.agents/skills"), os.path.expanduser("~/.claude/skills")):
                p = os.path.join(d, entry["skill"])
                if os.path.isdir(p):
                    shutil.rmtree(p)
                    print(f"REVOKED {entry['skill']}: removed {p} ({baseline:.2%} -> {rate_now:.2%})")


if __name__ == "__main__":
    main()
