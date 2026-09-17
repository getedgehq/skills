#!/usr/bin/env python3
"""Replay every Bash command a PreToolUse hook blocked in past sessions through the CURRENT hooks.

Usage: replay-hook-blocks.py [--projects ~/.claude/projects] [--settings ~/.claude/settings.json]
                             [--dump DIR] [--must-block FILE]

A guard hook that blocks legitimate work is an infra failure: the agent burns a turn, retries a
workaround, and learns nothing. This finds each blocked call in the transcripts (tool_result
"PreToolUse:Bash hook error: [<hook>]: ..."), pairs it with the command, and re-runs that command
through the hook it hit. Read the output as a triage list:
  still blocked -> inspect: true positive, or a pattern that is still too broad
  now passes    -> the hook was already fixed (or the fix works)

--must-block FILE: one command per line that MUST still exit 2 (verify guards negatively:
a loosened pattern that stops blocking `rm -rf ~` is worse than a false positive).
--dump DIR writes each blocked input as JSON for a regression suite.
"""
import argparse
import collections
import glob
import json
import os
import re
import subprocess
import sys

ERR = re.compile(r"PreToolUse:Bash hook error: \[([^\]]+)\]: ?(.*)", re.S)


def bash_hooks(settings):
    out = []
    for entry in json.load(open(settings)).get("hooks", {}).get("PreToolUse", []):
        if re.search(r"\bBash\b", entry.get("matcher", "")):
            out += [h["command"] for h in entry.get("hooks", []) if h.get("type") == "command"]
    return out


def blocked_calls(projects):
    for f in glob.glob(os.path.join(projects, "*", "*.jsonl")):
        calls = {}
        for line in open(f, errors="replace"):
            if '"tool_use"' not in line and "hook error" not in line:
                continue
            try:
                d = json.loads(line)
            except ValueError:
                continue
            content = (d.get("message") or {}).get("content")
            if not isinstance(content, list):
                continue
            for x in content:
                if x.get("type") == "tool_use":
                    calls[x["id"]] = (x.get("input") or {}).get("command")
                elif x.get("type") == "tool_result":
                    c = x.get("content")
                    text = c if isinstance(c, str) else " ".join(
                        p.get("text", "") for p in c or [] if isinstance(p, dict))
                    m = ERR.match(text.lstrip().removeprefix("Error: ").removeprefix("<error>"))
                    cmd = calls.get(x.get("tool_use_id"))
                    if m and cmd:
                        yield {"hook": m.group(1), "reason": m.group(2).strip()[:120], "command": cmd,
                               "session": os.path.basename(f)[:8], "ts": d.get("timestamp", "")[:16]}


def run_hook(hook, cmd):
    r = subprocess.run([hook], input=json.dumps({"tool_name": "Bash", "tool_input": {"command": cmd}}),
                       capture_output=True, text=True, timeout=30)
    return r.returncode, (r.stderr.strip().splitlines() or [""])[-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--projects", default=os.path.expanduser("~/.claude/projects"))
    ap.add_argument("--settings", default=os.path.expanduser("~/.claude/settings.json"))
    ap.add_argument("--dump", default=None)
    ap.add_argument("--must-block", default=None)
    args = ap.parse_args()

    live = set(bash_hooks(args.settings))
    rows = list(blocked_calls(args.projects))
    sessions = {r["session"] for r in rows}
    print(f"{len(rows)} blocked Bash calls in {len(sessions)} sessions")
    by_hook = collections.defaultdict(lambda: collections.Counter())
    still = []
    for i, r in enumerate(rows):
        if args.dump:
            os.makedirs(args.dump, exist_ok=True)
            json.dump(r, open(os.path.join(args.dump, f"{i:04d}.json"), "w"))
        if r["hook"] not in live or not os.access(r["hook"], os.X_OK):
            by_hook[r["hook"]]["hook no longer configured"] += 1
            continue
        code, err = run_hook(r["hook"], r["command"])
        if code == 0:
            by_hook[r["hook"]]["now passes"] += 1
        else:
            by_hook[r["hook"]]["still blocked"] += 1
            still.append((r, err))
    for hook, c in by_hook.items():
        print(f"  {os.path.basename(hook)}: " + ", ".join(f"{k} {v}" for k, v in c.items()))
    reasons = collections.Counter(err for _, err in still)
    if still:
        print("still blocked, by reason (inspect each: true positive or too broad?):")
        for reason, n in reasons.most_common():
            print(f"  {n:3d}  {reason[:100]}")
            for r, err in [s for s in still if s[1] == reason][:3]:
                first = next((l for l in r["command"].splitlines() if l.strip()), "")
                print(f"         {r['ts']} {first[:110]}")

    failed = 0
    if args.must_block:
        for cmd in (l.rstrip("\n") for l in open(args.must_block)):
            if not cmd.strip() or cmd.startswith("#"):
                continue
            codes = [run_hook(h, cmd)[0] for h in live if os.access(h, os.X_OK)]
            if 2 not in codes:
                failed += 1
                print(f"GUARD MISSED: {cmd}")
        print(f"must-block cases missed: {failed}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
