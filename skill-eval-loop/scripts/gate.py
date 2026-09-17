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
  Neither decision is available on fewer than MIN_VALID valid samples, whatever
  the winner says: the majority rule counts valid samples, so a run whose others
  were thrown out is one run, and one run is an anecdote.

Every row records what the win was against. A baseline arm with no skill
installed makes the verdict "better than nothing", and a skill is adopted into a
fleet that is not nothing: a candidate loads 18 times in 21 with-arms, where it
is the only skill on the machine, and once in 189 real sessions, where it is one
of 314 and several of the others answer the same trigger. --rival names the skill
the baseline arm was given, so a later reader can tell the two verdicts apart
instead of reading every past row as a head-to-head it never was.

On ADOPT: copies the skill into --adopt-dir and appends to ledger.jsonl. Both adopt
and probation rows carry a baseline failure rate and a recheck date (14 days for an
adoption, 7 for probation), so recheck.py can demote either one later.
On REJECT: appends to ledger.jsonl so we never re-eval the same pairing.
"""
import argparse
import json
import os
import shutil
import sys
import time

# Samples that actually decided something. Three samples exist so that one lucky run
# cannot adopt a skill, and dropping the invalid ones can quietly undo that: a 2-1
# adoption on record survived losing both samples where the with-arm never loaded the
# skill, leaving one run holding an adoption the majority rule was written to prevent.
# The majority is over valid samples, so the floor has to be too.
MIN_VALID = 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("brief")
    ap.add_argument("skill_dir")
    ap.add_argument("--adopt-dir", default=os.path.expanduser("~/.agents/skills"))
    ap.add_argument("--rival", default=None,
                    help="skill the baseline arm was given; absent means it had none, "
                         "and the verdict is 'better than nothing' rather than a head-to-head")
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
    # What the baseline actually had, read off the run rather than off the flag. The
    # flag says what was asked for and the verdict says what was installed, and the
    # whole point of the row is that a reader can tell a head-to-head from a walkover;
    # a --rival that never reached the arm would put the wrong one on the ledger.
    baseline = sorted(v.get("skills_installed", {}).get("without", []) or [])
    if args.rival and not baseline:
        sys.exit(f"--rival {args.rival} was passed but the baseline arm ran with no "
                 f"skill installed. Rerun the brief or drop the flag; recording a "
                 f"head-to-head that did not happen is worse than recording nothing.")
    # An older verdict has no valid_samples; treat its own sample count as the answer
    # rather than refusing every pre-fix verdict on a field it could not have written.
    n_valid = v.get("valid_samples", v.get("samples", MIN_VALID))
    thin = n_valid < MIN_VALID
    if v.get("invalid") or thin:
        adopt = False
    else:
        adopt = (v["winner_arm"] == "with" and v["verify"].get("with") == 0
                 and errors.get("with", 0) <= errors.get("without", 0))
    probation = False
    if not adopt and args.probation and not thin:
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
        "valid_samples": n_valid,
        # How often the model reached for this skill in its own eval, where it was
        # installed and the task was the one it is for. recheck.py asks the same
        # question of real sessions weeks later and keeps finding zero; this is the
        # earliest the loop can see it coming, on the row the recheck already reads.
        "eval_skill_loads": v.get("skill_loads"),
        # What the candidate beat. An empty list is the honest reading of every row
        # written before this field existed: the baseline arm was an empty machine,
        # so the verdict is "better than nothing" and says nothing about whether the
        # model would pick this skill over the one already installed for the trigger.
        "baseline_skills": baseline,
        "verify": v["verify"],
        "tool_errors": v.get("tool_errors"),
        "reasons": v["verdict"].get("reasons", []),
        "failure": brief.get("source_failure"),
    }
    if adopt or probation:
        # An adopted skill gets a production recheck too, just a later one: winning a
        # rebuilt eval task is not the same as reducing failures in real sessions.
        entry["baseline_failure_rate"] = args.failure_rate
        entry["recheck_due"] = time.strftime(
            "%Y-%m-%d", time.gmtime(time.time() + (7 if probation else 14) * 86400))
    ledger = os.path.join(root, "ledger.jsonl")
    with open(ledger, "a") as fh:
        fh.write(json.dumps(entry) + "\n")

    if adopt or probation:
        dest = os.path.join(args.adopt_dir, skill_name)
        if os.path.islink(dest):
            print(f"note: {dest} is a symlink, replacing it")
            os.unlink(dest)
        elif os.path.exists(dest):
            print(f"note: {dest} already exists, refreshing")
            shutil.rmtree(dest)
        shutil.copytree(args.skill_dir, dest)
        tag = "ADOPTED" if adopt else "PROBATION (recheck due %s)" % entry["recheck_due"]
        against = ("over " + ", ".join(baseline)) if baseline else "over an empty baseline"
        print(f"{tag} {skill_name} ({against}) -> {dest}")
        if not baseline:
            print("  note: the baseline arm had no skill, so this says the candidate "
                  "beats nothing, not that it beats what is already installed for the "
                  "same trigger. --rival runs that comparison.")
    elif thin:
        print(f"REJECTED {skill_name}: {n_valid} valid sample(s), and one run is an "
              f"anecdote. Fix whatever invalidated the others and rerun the brief "
              f"(winner={v['winner_arm']}, verify={v['verify']})")
    else:
        print(f"REJECTED {skill_name} (winner={v['winner_arm']}, verify={v['verify']})")
    print(f"ledger: {ledger}")


if __name__ == "__main__":
    main()
