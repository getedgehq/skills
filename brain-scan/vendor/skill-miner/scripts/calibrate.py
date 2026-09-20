#!/usr/bin/env python3
"""Turn past forge outcomes into priors the scorer can use, or refuse to.

Usage: calibrate.py [--ledger PATH] [--min-n 4] [--json] [--check]

score.py predicts P(this skill measurably improves the failing task) before any
eval is spent. Until now nothing checked those predictions against what the evals
actually decided, so the scorer could be badly wrong for weeks at full eval cost.

This reads the ledger and produces two things:

  priors  - adoption rates per bucket (failure kind, skill source, repeat attempts),
            emitted as a short block that score.py pastes into its prompt. A bucket
            with fewer than --min-n decided evals is reported as "too few to call",
            never as a rate: a 1-of-1 bucket is noise, and a prior stated with false
            confidence is worse than no prior at all.

  --check - calibration report. Joins recorded predictions (predictions.jsonl, written
            by score.py) to the decisions the evals returned, and prints mean predicted
            potential for adopted vs rejected candidates. If the scorer has signal,
            adopted candidates scored higher. With no predictions recorded yet it says
            so and exits 0 rather than inventing a number.

Only decided rows count: adopt, probation, reject, reject-final. infra-fix rows and
recheck verdicts are not eval outcomes and are excluded from every denominator.
"""
import argparse
import json
import os
import re

DECIDED = {"adopt": 1, "probation": 1, "reject": 0, "reject-final": 0}

# Below this many decided evals in total, score.py states no priors at all rather
# than a handful of buckets each small enough to be noise. Per-bucket --min-n still
# applies above it.
MIN_TOTAL_FOR_PRIORS = 8


def load(path):
    rows = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except ValueError:
                pass
    return rows


def decided(rows):
    return [r for r in rows if r.get("decision") in DECIDED and not r.get("invalid")]


def rate(bucket):
    """(wins, n, rate) where a win is adopt or probation."""
    wins = sum(DECIDED[r["decision"]] for r in bucket)
    return wins, len(bucket), (wins / len(bucket) if bucket else None)


def provenance(src):
    """Where the skill came from, as a class.

    The ledger stores a path, so bucketing on it raw produces one bucket per draft,
    every one of them n=1 and therefore reported as too few to call: a dimension that
    can never say anything. What the scorer actually needs to know is whether skills
    the loop writes itself beat ones it finds already installed or in a registry.
    """
    if not src:
        return "unknown"
    s = str(src)
    if "/drafts/" in s:
        return "drafted by the loop"
    if "/.agents/skills/" in s or "/.claude/skills/" in s:
        return "already installed locally"
    if "@" in s or s.startswith(("http://", "https://")) or (not s.startswith("/") and "/" in s):
        return "found in a registry"
    return "unknown"


def buckets(rows):
    out = {}
    for r in rows:
        kind = (r.get("failure") or {}).get("kind") or "unlabelled"
        out.setdefault(("failure kind", kind), []).append(r)
        out.setdefault(("skill source", provenance(r.get("skill_src"))), []).append(r)
    # A skill that already lost once: does trying it again pay off?
    seen, repeats = set(), []
    for r in rows:
        name = r.get("skill")
        if not name:
            continue
        if name in seen:
            repeats.append(r)
        seen.add(name)
    if repeats:
        out[("attempt", "retry of a skill already evaluated")] = repeats
    return out


def priors_text(rows, min_n):
    lines, weak = [], []
    for (dim, key), bucket in sorted(buckets(rows).items()):
        wins, n, r = rate(bucket)
        label = f"{dim} = {key}"
        if n < min_n:
            weak.append(f"{label}: {wins}/{n}")
        else:
            lines.append(f"- {label}: {wins} of {n} passed the gate ({r:.0%})")
    text = ["MEASURED PRIORS from this user's own past evals:"]
    text += lines or ["- (no bucket has enough decided evals yet)"]
    if weak:
        text.append("Too few decided evals to call, treat as no information: "
                    + "; ".join(weak))
    return "\n".join(text)


def coverage(rows, paired):
    """How many decided evals have a prediction at all, and which do not.

    Without this the report reads the same whether the data is young or the
    scorer is broken. On this ledger it read "paired 1 predictions with
    decisions" for weeks while 20 of 21 decisions had none, because score.py
    raised KeyError on every brief with no mined cluster behind it and forge.sh
    printed that as "evaluating anyway" (#41). A number that only ever goes up
    slowly looks like youth; a coverage line that says 1 of 21 does not.
    """
    have = {name for _, _, name in paired}
    missing = [r.get("skill") for r in rows if r.get("skill") not in have]
    pct = 100 * len(have) / len(rows) if rows else 0
    print(f"  coverage: {len(have)} of {len(rows)} decided evals have a prediction ({pct:.0f}%)")
    if missing:
        shown = ", ".join(sorted(set(m for m in missing if m))[:6])
        more = len(set(missing)) - 6
        print(f"  no prediction for: {shown}" + (f", and {more} more" if more > 0 else ""))
        print("  a decision with no prediction is not evidence against the scorer: "
              "check whether scoring ran at all before reading the gap above")


def check(rows, preds_path):
    if not os.path.exists(preds_path):
        print(f"no predictions recorded yet ({preds_path} does not exist)")
        print("score.py records one row per candidate it scores; rerun after the next scoring pass")
        return
    preds = load(preds_path)
    by_key = {}
    for p in preds:
        by_key.setdefault(norm(p.get("skill", "")), []).append(p)
    paired = []
    for r in rows:
        cand = by_key.get(norm(r.get("skill") or ""))
        if not cand:
            continue
        p = max(cand, key=lambda c: c.get("ts", ""))
        paired.append((p.get("potential"), DECIDED[r["decision"]], r.get("skill")))
    if not paired:
        print(f"{len(preds)} predictions and {len(rows)} decided evals, but none refer to "
              "the same skill: nothing to calibrate yet")
        return
    won = [p for p, o, _ in paired if o and p is not None]
    lost = [p for p, o, _ in paired if not o and p is not None]
    print(f"paired {len(paired)} predictions with decisions")
    coverage(rows, paired)
    for label, vals in (("passed the gate", won), ("rejected", lost)):
        if vals:
            print(f"  mean predicted potential, {label}: {sum(vals)/len(vals):.2f}  (n={len(vals)})")
    if won and lost:
        gap = sum(won) / len(won) - sum(lost) / len(lost)
        verdict = ("scores carry signal" if gap > 0.1 else
                   "scores carry no usable signal, the prompt needs work" if gap <= 0 else
                   "signal is weak")
        print(f"  gap: {gap:+.2f} -> {verdict}")
    else:
        print("  only one outcome class present, cannot separate yet")


def norm(name):
    return re.sub(r"[^a-z0-9]+", "", (name or "").lower())


def main():
    ap = argparse.ArgumentParser()
    root = os.environ.get("FORGE_ROOT", os.path.expanduser("~/skill-forge"))
    ap.add_argument("--ledger", default=os.path.join(root, "ledger.jsonl"))
    ap.add_argument("--predictions", default=os.path.join(root, "predictions.jsonl"))
    ap.add_argument("--min-n", type=int, default=4)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    rows = decided(load(args.ledger))
    if args.check:
        check(rows, args.predictions)
        return
    if args.json:
        data = {f"{dim}:{key}": dict(zip(("wins", "n", "rate"), rate(b)))
                for (dim, key), b in buckets(rows).items()}
        print(json.dumps({"decided_evals": len(rows), "buckets": data}, indent=1))
        return
    print(priors_text(rows, args.min_n))


if __name__ == "__main__":
    main()
