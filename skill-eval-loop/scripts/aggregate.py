#!/usr/bin/env python3
"""Combine repeated eval samples into one verdict for gate.py.

Usage: aggregate.py <brief.json>

Reads runs/<id>/s*/verdict.json (one blind judgment per sample pair) and
writes runs/<id>/verdict.json. One run is an anecdote; the skill only "wins"
when the with-arm wins a strict majority of valid samples AND passes verify at
least as often as baseline AND passes verify in a majority of samples.
"""
import glob
import json
import os
import sys


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    brief = json.load(open(sys.argv[1]))
    root = os.environ.get("FORGE_ROOT", os.path.expanduser("~/skill-forge"))
    runs = os.path.join(root, "runs", brief["id"])
    samples = sorted(glob.glob(os.path.join(runs, "s*", "verdict.json")))
    if not samples:
        sys.exit(f"no sample verdicts under {runs}/s*/ - run judge.py --sample N first")
    vs = [json.load(open(p)) for p in samples]
    valid = [v for v in vs if not v.get("invalid")]
    n = len(valid)
    wins = {"with": 0, "without": 0, "tie": 0}
    for v in valid:
        wins[v["winner_arm"] if v["winner_arm"] in wins else "tie"] += 1
    passes = {a: sum(1 for v in valid if v["verify"].get(a) == 0) for a in ("with", "without")}
    errors = {a: sum(v.get("tool_errors", {}).get(a, 0) for v in valid) for a in ("with", "without")}

    if n == 0:
        winner = "invalid"
    elif wins["with"] * 2 > n and passes["with"] >= passes["without"] and passes["with"] * 2 > n:
        winner = "with"
    elif wins["without"] * 2 > n:
        winner = "without"
    else:
        winner = "tie"

    result = {
        "brief": brief["id"],
        "samples": len(vs),
        "valid_samples": n,
        "wins": wins,
        "verify_pass": passes,
        "winner_arm": winner,
        # gate.py reads verify as exit codes: 0 = passed in a majority of samples
        "verify": {a: 0 if n and passes[a] * 2 > n else 1 for a in passes},
        "tool_errors": errors,
        "verdict": {"reasons": [r for v in valid for r in v.get("verdict", {}).get("reasons", [])][:12]},
        "sample_verdicts": [os.path.relpath(p, runs) for p in samples],
    }
    if n == 0:
        result["invalid"] = True
        result["invalid_reason"] = "every sample was invalid (both arms failed verify) - fix the brief"
    out = os.path.join(runs, "verdict.json")
    json.dump(result, open(out, "w"), indent=1)
    print(json.dumps({k: result[k] for k in ("brief", "valid_samples", "wins", "verify_pass", "winner_arm")}))
    print(f"-> {out}")


if __name__ == "__main__":
    main()
