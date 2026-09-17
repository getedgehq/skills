#!/usr/bin/env python3
"""Adoption gate + ledger for skill-forge.

Usage: gate.py <brief.json> <candidate-skill-dir> [--adopt-dir ~/.agents/skills]

Decision rule (deliberately conservative):
  ADOPT only if winner_arm == "with" AND the with-arm's verify passed (exit 0)
  AND it made no more tool errors than baseline.
  PROBATION (--probation): for context-rot failure classes that one-shot evals
  cannot discriminate (long sessions, buried rules, mid-flow shortcuts). Requires
  the eval to be a tie-or-better with the with-arm's verify passing. Adopted with
  a probation flag + baseline failure rate; recheck.py re-mines later sessions
  and revokes the skill if the failure rate did not drop.
  Everything else is REJECT. Ties without --probation are rejections - a skill
  that does not demonstrably improve the task is context debt, not an asset.

On ADOPT: copies the skill into --adopt-dir and appends to ledger.jsonl.
On REJECT: appends to ledger.jsonl so we never re-eval the same pairing.
"""
import argparse
import json
import os
import shutil
import sys
import time


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("brief")
    ap.add_argument("skill_dir")
    ap.add_argument("--adopt-dir", default=os.path.expanduser("~/.agents/skills"))
    ap.add_argument("--probation", action="store_true",
                    help="adopt as probationary when eval can't discriminate but the production failure is real")
    ap.add_argument("--failure-rate", type=float, default=None,
                    help="baseline failure rate (sessions with failure / total) for later recheck")
    args = ap.parse_args()

    brief = json.load(open(args.brief))
    root = os.environ.get("FORGE_ROOT", os.path.expanduser("~/skill-forge"))
    verdict_path = os.path.join(root, "runs", brief["id"], "verdict.json")
    if not os.path.exists(verdict_path):
        sys.exit(f"no verdict at {verdict_path} - run judge.py first")
    v = json.load(open(verdict_path))

    skill_name = os.path.basename(os.path.normpath(args.skill_dir))
    errors = v.get("tool_errors", {})
    if v.get("invalid"):
        adopt = False
    else:
        adopt = (v["winner_arm"] == "with" and v["verify"].get("with") == 0
                 and errors.get("with", 0) <= errors.get("without", 0))
    probation = False
    if not adopt and args.probation:
        # Probation bar: eval didn't discriminate (tie) but the skill is harmless
        # in eval (verify passed) and the production failure is documented.
        probation = (not v.get("invalid") and v["winner_arm"] in ("tie", "with")
                     and v["verify"].get("with") == 0)

    decision = "adopt" if adopt else ("probation" if probation else "reject")
    entry = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "brief": brief["id"],
        "skill": skill_name,
        "skill_src": os.path.abspath(args.skill_dir),
        "decision": decision,
        "invalid": bool(v.get("invalid")),
        "invalid_reason": v.get("invalid_reason"),
        "winner_arm": v["winner_arm"],
        "verify": v["verify"],
        "tool_errors": v.get("tool_errors"),
        "reasons": v["verdict"].get("reasons", []),
        "failure": brief.get("source_failure"),
    }
    if probation:
        entry["baseline_failure_rate"] = args.failure_rate
        entry["recheck_due"] = time.strftime(
            "%Y-%m-%d", time.gmtime(time.time() + 7 * 86400))
    ledger = os.path.join(root, "ledger.jsonl")
    with open(ledger, "a") as fh:
        fh.write(json.dumps(entry) + "\n")

    if adopt or probation:
        dest = os.path.join(args.adopt_dir, skill_name)
        if os.path.exists(dest):
            print(f"note: {dest} already exists, refreshing")
            shutil.rmtree(dest)
        shutil.copytree(args.skill_dir, dest)
        tag = "ADOPTED" if adopt else "PROBATION (recheck due %s)" % entry["recheck_due"]
        print(f"{tag} {skill_name} -> {dest}")
    else:
        print(f"REJECTED {skill_name} (winner={v['winner_arm']}, verify={v['verify']})")
    print(f"ledger: {ledger}")


if __name__ == "__main__":
    main()
