#!/usr/bin/env python3
"""Blind A/B judge for a skill-forge eval pair.

Usage: judge.py <brief.json> [--model M]

1. Runs the brief's verify command in each arm's workdir (objective gate).
2. Extracts each arm's final assistant message + file manifest.
3. Shuffles arms into anonymous slots (mapping kept in mapping.private.json,
   never shown to the judge) and asks a judge model for a verdict.

Verdict JSON: {"winner": "A"|"B"|"tie", "reasons": [...], "per_criterion": {...}}
The judge only ever sees slot letters - arm identity stays on disk, private.
"""
import argparse
import json
import os
import secrets
import subprocess
import sys

JUDGE_PROMPT = """You are a blind judge comparing two AI agent runs on the same task.

TASK GIVEN TO BOTH AGENTS:
{prompt}

JUDGING CRITERIA:
{rubric}

VERIFY COMMAND RESULTS (exit 0 = task objectively completed):
- Run A: verify exit {va}, tool errors during run: {ea}
- Run B: verify exit {vb}, tool errors during run: {eb}

RUN A - final message and produced files:
{fa}

RUN B - final message and produced files:
{fb}

Judge ONLY what you can see above. If verify failed for a run, weight that heavily.
Return STRICT JSON, no fences:
{{"winner": "A"|"B"|"tie", "per_criterion": {{"<criterion>": "A"|"B"|"tie"}}, "reasons": ["<short reason>"]}}"""


def run_verify(brief, workdir):
    try:
        out = subprocess.run(["bash", "-c", brief["verify"]], cwd=workdir,
                             capture_output=True, text=True, timeout=120)
        return out.returncode, (out.stdout + out.stderr)[:500]
    except subprocess.TimeoutExpired:
        return 124, "verify timed out"


def final_message(meta):
    last = "(no final message)"
    try:
        for line in open(os.path.join(meta, "transcript.jsonl"), errors="replace"):
            try:
                d = json.loads(line)
            except ValueError:
                continue
            msg = d.get("message")
            if isinstance(msg, dict) and msg.get("role") == "assistant":
                content = msg.get("content")
                if isinstance(content, list):
                    texts = [c.get("text", "") for c in content
                             if isinstance(c, dict) and c.get("type") == "text"]
                    if any(texts):
                        last = "\n".join(t for t in texts if t)
    except OSError:
        pass
    return last[:3000]


def tool_error_count(meta):
    n = 0
    try:
        for line in open(os.path.join(meta, "transcript.jsonl"), errors="replace"):
            try:
                d = json.loads(line)
            except ValueError:
                continue
            msg = d.get("message")
            if isinstance(msg, dict) and isinstance(msg.get("content"), list):
                n += sum(1 for c in msg["content"]
                         if isinstance(c, dict) and c.get("type") == "tool_result" and c.get("is_error"))
    except OSError:
        pass
    return n


def manifest(workdir):
    skip = {".claude"}
    files = []
    for root, dirs, names in os.walk(workdir):
        dirs[:] = [d for d in dirs if d not in skip]
        for n in names:
            p = os.path.relpath(os.path.join(root, n), workdir)
            files.append(f"{p} ({os.path.getsize(os.path.join(root, n))}b)")
    return "\n".join(sorted(files)[:80]) or "(no files)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("brief")
    ap.add_argument("--model", default=os.environ.get("FORGE_JUDGE_MODEL", "claude-sonnet-4-5"))
    args = ap.parse_args()

    brief = json.load(open(args.brief))
    root = os.environ.get("FORGE_ROOT", os.path.expanduser("~/skill-forge"))
    runs = os.path.join(root, "runs", brief["id"])

    arms = {}
    for arm in ("with", "without"):
        workdir = os.path.join(runs, arm)
        meta = workdir + ".meta"
        if not os.path.isdir(workdir) or not os.path.isdir(meta):
            sys.exit(f"missing arm: {workdir}")
        code, vout = run_verify(brief, workdir)
        arms[arm] = {
            "verify_exit": code,
            "verify_out": vout,
            "tool_errors": tool_error_count(meta),
            "final": final_message(meta),
            "files": manifest(workdir),
            "run": json.load(open(os.path.join(meta, "run.json"))),
        }

    # Blind: random slot assignment, persisted privately, never reshuffled.
    map_path = os.path.join(runs, "mapping.private.json")
    if os.path.exists(map_path):
        slots = json.load(open(map_path))
    else:
        pair = ["with", "without"]
        if secrets.randbelow(2):
            pair.reverse()
        slots = {"A": pair[0], "B": pair[1]}
        json.dump(slots, open(map_path, "w"), indent=1)

    # Both arms failing the objective gate means the BRIEF is broken, not the
    # skill. A model verdict over two broken runs is noise - mark invalid.
    both_failed = all(a["verify_exit"] != 0 for a in arms.values())

    prompt = JUDGE_PROMPT.format(
        prompt=brief["prompt"], rubric=brief.get("rubric", "correctness; completeness; brief adherence"),
        va=arms[slots["A"]]["verify_exit"], vb=arms[slots["B"]]["verify_exit"],
        ea=arms[slots["A"]]["tool_errors"], eb=arms[slots["B"]]["tool_errors"],
        fa=arms[slots["A"]]["final"] + "\n\nFILES:\n" + arms[slots["A"]]["files"],
        fb=arms[slots["B"]]["final"] + "\n\nFILES:\n" + arms[slots["B"]]["files"],
    )
    import forge_llm
    text, engine = forge_llm.call_model(prompt, args.model)
    print(f"  (judged by {engine})", file=sys.stderr)
    start, end = text.find("{"), text.rfind("}")
    if start == -1:
        sys.exit(f"no JSON in judge output: {text[:300]}")
    verdict = json.loads(text[start:end + 1])

    result = {
        "brief": brief["id"],
        "slots": slots,
        "winner_slot": verdict.get("winner"),
        "winner_arm": slots.get(verdict.get("winner"), "tie"),
        "verdict": verdict,
        "verify": {a: arms[a]["verify_exit"] for a in arms},
        "tool_errors": {a: arms[a]["tool_errors"] for a in arms},
        "run": {a: arms[a]["run"] for a in arms},
    }
    if both_failed:
        result["invalid"] = True
        result["invalid_reason"] = "both arms failed verify - fix the brief, not the loop"
        result["winner_arm"] = "invalid"
    path = os.path.join(runs, "verdict.json")
    json.dump(result, open(path, "w"), indent=1)
    print(json.dumps({k: result[k] for k in ("brief", "winner_arm", "verify")}, indent=1))
    print(f"-> {path}")


if __name__ == "__main__":
    main()
