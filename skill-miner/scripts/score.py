#!/usr/bin/env python3
"""Score candidate skills by predicted eval performance, on enriched data.

Usage: score.py <candidates.json> <cluster.json | failures.json --index N> [--top N]

For each candidate, enriches with:
  - the actual SKILL.md content (local path or fetched from GitHub for skills.sh entries)
  - ledger history (past forge adopt/reject outcomes for this skill or failure)
  - failure-cluster evidence strength

An LLM scores P(this skill measurably improves the failing task) 0-1.
The point: spend eval runs only on candidates with real potential, and learn
from the ledger so repeat losers score low before they cost an eval.

Two things make that "learn from the ledger" real rather than aspirational:

  - calibrate.py's measured priors go into the prompt, so the model is told what
    actually passed the gate here instead of guessing from the rubric alone. A
    bucket with too few decided evals is passed through as "too few to call",
    never as a rate.
  - every score is appended to predictions.jsonl. That is what lets
    `calibrate.py --check` later join predictions to outcomes and say whether
    these numbers separate winners from losers at all. A scoring prompt that is
    not earning its cost can only be caught if the predictions were written down.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time

import forge_llm  # noqa: F401  (ensures script dir on path)
from forge_llm import call_model

import calibrate

SCORE_PROMPT = """You are deciding whether a candidate skill is worth an A/B eval run (two agent runs, real cost).

FAILURE CLUSTER (from real session logs):
- kind: {kind}
- signature: {signature}
- occurrences: {count} across {session_count} sessions
- evidence:
{evidence}

CANDIDATE SKILL: {name} (pool: {pool}, installs: {installs})
SKILL CONTENT (may be truncated):
{content}

LEDGER HISTORY for this skill/failure (may be empty):
{ledger}

{priors}

Score the candidate's potential. Hard-earned rubric:
1. REPRODUCIBILITY: would a current frontier model plausibly fail this failure mode on a
   fresh, well-scoped task? If the harness already enforces the behavior (tool errors that
   self-correct in one turn), a skill cannot beat baseline - score near 0.
2. TRIGGER QUALITY: does the description name task contexts (so it actually gets loaded),
   not the error it prevents?
3. EVIDENCE: more sessions and cleaner evidence = higher potential.
4. COST OF FAILURE: does the failure break outputs, or just waste a recoverable turn?
   Output-breaking failures make skills valuable; recoverable ones do not.
5. Past ledger rejections for this skill or failure class push the score toward 0.
6. The measured priors above are this user's own base rates. Where a bucket applies to
   this candidate, start from its rate and move only for evidence specific to this
   candidate. A bucket reported as too few to call carries no information: do not read
   a low count as a low rate.

Return STRICT JSON only: {{"potential": 0.0-1.0, "reason": "<one sentence>", "risk": "<main way this score could be wrong>"}}"""


def first_object(text):
    """The first complete JSON object in a model reply.

    Slicing from the first "{" to the last "}" is the usual shortcut and it fails on
    exactly the reply this has to survive: a model that answers with the object and
    then keeps going, a second object or a sentence with a brace in it, produces a
    slice that is valid JSON followed by more, and json.loads rejects the whole thing
    with "Extra data". Two real candidates scored 0.00 that way, which reads in the
    output as a judgement the model never made. raw_decode stops at the end of the
    first object instead, and each later "{" is tried in case the reply opens with
    prose containing one.
    """
    dec = json.JSONDecoder()
    at, err = text.find("{"), None
    while at != -1:
        try:
            obj, _ = dec.raw_decode(text[at:])
            if isinstance(obj, dict):
                return obj
        except ValueError as e:
            err = err or e
        at = text.find("{", at + 1)
    raise ValueError(err or "no JSON object in the reply")


def fetch_skill_md(name):
    """skills.sh name = owner/repo@skill. Try common SKILL.md locations."""
    if "@" not in name:
        return ""
    repo, skill = name.split("@", 1)
    for branch in ("main", "master"):
        for path in (f"{skill}/SKILL.md", f"skills/{skill}/SKILL.md", "SKILL.md"):
            url = f"https://raw.githubusercontent.com/{repo}/{branch}/{path}"
            try:
                out = subprocess.run(["curl", "-fsSL", "--max-time", "15", url],
                                     capture_output=True, text=True)
                if out.returncode == 0 and "name:" in out.stdout[:400]:
                    return out.stdout[:6000]
            except OSError:
                pass
    return ""


def load_ledger(root):
    path = os.path.join(root, "ledger.jsonl")
    if not os.path.exists(path):
        return []
    rows = []
    for line in open(path):
        try:
            rows.append(json.loads(line))
        except ValueError:
            pass
    return rows


def relevant_ledger(rows, skill_name, signature):
    sig_tokens = set(re.findall(r"[a-z0-9]+", signature.lower()))
    hits = []
    for r in rows:
        if r.get("skill") and r["skill"] in skill_name:
            hits.append(f"{r.get('decision')}: {r.get('reason') or '; '.join(r.get('reasons', []))}")
            continue
        fsig = ((r.get("failure") or {}).get("signature") or "").lower()
        if fsig and len(sig_tokens & set(re.findall(r"[a-z0-9]+", fsig))) >= 3:
            hits.append(f"{r.get('decision')}: {r.get('reason') or '; '.join(r.get('reasons', []))}")
    return hits[:5]


def priors_block(rows):
    """calibrate.py's measured priors, or an honest blank when there is nothing to say."""
    decided = calibrate.decided(rows)
    if len(decided) < calibrate.MIN_TOTAL_FOR_PRIORS:
        return (f"MEASURED PRIORS: only {len(decided)} decided evals so far, too few to state a "
                "base rate. Score from the evidence alone.")
    return calibrate.priors_text(decided, min_n=4)


def record(path, rows):
    """Append one row per scored candidate, so --check can join scores to outcomes later.

    Best-effort: a scoring pass must not fail because the log could not be written,
    and an unreadable prediction log costs a calibration report, not an eval.
    """
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a") as fh:
            for r in rows:
                fh.write(json.dumps(r) + "\n")
    except OSError as e:
        print(f"  (predictions not recorded: {e})", file=sys.stderr)


def cluster_from(data, index):
    """The failure cluster, from a mined file, a bare cluster, or a brief.

    A brief carries the cluster it was built from under source_failure, which is
    what lets the skill about to be evaluated be scored without the caller
    having to find its way back to the mined file and remember the index.
    """
    if "source_failure" in data:
        return data["source_failure"]
    return data["clusters"][index] if "clusters" in data else data


def candidates_from(args):
    """The candidates to score: a matched list, or the one skill being evaluated.

    --skill-dir names a directory rather than a registry entry, and is how the
    thing that actually goes through the gate gets a prediction. Without it only
    matched candidates were ever scored, and a candidate that scores high enough
    to be used is by definition never the drafted one, so predictions.jsonl
    filled up with skills no eval would ever decide.
    """
    if args.skill_dir:
        path = os.path.abspath(args.skill_dir.rstrip("/"))
        # The ledger records a decision under the directory's basename, and
        # calibrate.py --check joins on that name. Anything else here records a
        # prediction that can never pair with its own outcome.
        return [{"name": os.path.basename(path), "pool": args.pool, "path": path}]
    return json.load(open(args.candidates))["candidates"][:args.top]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("candidates", nargs="?")
    ap.add_argument("source")
    ap.add_argument("--index", type=int, default=0)
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--out", default=None)
    ap.add_argument("--skill-dir", default=None,
                    help="score this one local skill instead of a candidates file")
    ap.add_argument("--pool", default="drafted",
                    help="provenance recorded with a --skill-dir prediction")
    args = ap.parse_args()
    if not args.candidates and not args.skill_dir:
        ap.error("give a candidates file or --skill-dir")

    root = os.environ.get("FORGE_ROOT", os.path.expanduser("~/skill-forge"))
    cands = candidates_from(args)
    data = json.load(open(args.source))
    cluster = cluster_from(data, args.index)
    ledger = load_ledger(root)
    priors = priors_block(ledger)

    scored, preds = [], []
    for c in cands:
        content = ""
        if c.get("path") and os.path.isfile(os.path.join(c["path"], "SKILL.md")):
            content = open(os.path.join(c["path"], "SKILL.md"), errors="replace").read()[:6000]
        elif c.get("pool") == "skills.sh":
            content = fetch_skill_md(c["name"])
        hist = relevant_ledger(ledger, c["name"], cluster["signature"])
        prompt = SCORE_PROMPT.format(
            kind=cluster["kind"], signature=cluster["signature"],
            count=cluster.get("count", "?"), session_count=cluster.get("session_count", "?"),
            evidence="\n".join(f"- {e}" for e in cluster.get("evidence", [])),
            name=c["name"], pool=c.get("pool", "?"), installs=c.get("installs", "n/a"),
            content=content or "(content unavailable - score from name/description only)",
            ledger="\n".join(hist) if hist else "(none)",
            priors=priors,
        )
        engine = ""
        try:
            text, engine = call_model(prompt)
            verdict = first_object(text)
            failed = False
        except (ValueError, SystemExit) as e:
            verdict = {"potential": None, "reason": f"scoring failed: {e}", "risk": ""}
            failed = True
        scored.append({**c, "potential": verdict.get("potential", 0),
                       "reason": verdict.get("reason", ""), "risk": verdict.get("risk", ""),
                       "has_content": bool(content)})
        # A failed call is not a prediction of 0, it is no prediction. Recording it
        # would drag the calibration report toward "the scorer cannot tell winners
        # from losers" for a reason that has nothing to do with the prompt.
        if not failed:
            preds.append({"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                          "skill": c["name"], "pool": c.get("pool"),
                          "potential": verdict.get("potential", 0),
                          "reason": verdict.get("reason", ""),
                          "failure_kind": cluster.get("kind"),
                          "failure_signature": cluster.get("signature"),
                          "engine": engine, "had_priors": priors.startswith("MEASURED PRIORS from")})
        shown = "    ?" if scored[-1]["potential"] is None else f"{scored[-1]['potential']:5.2f}"
        print(f"  {shown}  {c['name']}  - {scored[-1]['reason'][:90]}")

    if preds:
        record(os.path.join(root, "predictions.jsonl"), preds)
    # An unscored candidate sorts last, not as a zero. Scoring it zero would read as
    # "the model looked at this and saw no potential", which is the one thing that did
    # not happen, and would quietly retire a candidate over a parse error.
    scored.sort(key=lambda c: (c["potential"] is not None, c["potential"] or 0), reverse=True)
    # A --skill-dir pass runs after the matched candidates have already been
    # scored in the same forge run, so it must not land on their file: the
    # matched scores are what chose the skill, and overwriting them loses the
    # record of that choice.
    default = "scored-skill.json" if args.skill_dir else "scored.json"
    out = args.out or os.path.join(root, "mined", default)
    # forge.sh creates mined/ before it calls this, but SKILL.md documents running
    # score.py by hand, and that crashed here after the prediction was already
    # written: a recorded prediction and a non-zero exit is the worst of both.
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    json.dump({"failure": {k: cluster[k] for k in ("kind", "signature")},
               "scored": scored}, open(out, "w"), indent=1)
    print(f"-> {out}")


if __name__ == "__main__":
    main()
