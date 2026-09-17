#!/usr/bin/env python3
"""Turn a mined failure cluster into a self-contained eval brief.

Usage: brief.py <cluster.json | failures.json --index N> [--out briefs/]

Calls headless claude to synthesise a reproducible task that recreates the
context where the failure occurred. Briefs must have HEADROOM: a real,
slightly messy core-job task, completable autonomously in <20 minutes,
with a deterministic verify command. Toy prompts make evals worthless.
"""
import argparse
import json
import os
import subprocess
import sys
import time

META_PROMPT = """You are designing an A/B eval task. A Claude agent repeatedly failed in real sessions like this:

Failure kind: {kind}
Signature: {signature}
Evidence (real user corrections / errors):
{evidence}

Write ONE self-contained eval task brief that recreates a realistic context where an agent
would need to avoid this failure. Requirements:
- A real, slightly messy core-job task (headroom - not a toy prompt).
- DISCRIMINATING: the task must actively pressure the agent toward the failure mode.
  A lazy or naive approach should plausibly trigger it; a careful approach avoids it.
  If the failure is a specific tool misuse, phrase the task so shortcuts lead to it.
- Completable autonomously in under 20 minutes with only Bash/Read/Write/Edit/Glob/Grep.
- No external network services, credentials, or accounts needed.
- Produces files in ./out so success is checkable.
- The "verify" command must only check properties the prompt text EXPLICITLY states,
  and must tolerate formatting variation (grep for content, not exact headings).
  If verify demands something the prompt doesn't ask for, the eval is broken.
- Include a "verify" shell command that exits 0 on acceptable completion.

Return STRICT JSON only, no markdown fences:
{{"id": "<kebab-case-id>", "prompt": "<the full task prompt given to the agent>",
 "setup": "<shell commands to prepare the workdir, or empty string>",
 "verify": "<shell command run in the workdir, exit 0 = pass>",
 "rubric": "<3 short judging criteria, semicolon separated>"}}"""


def synth(cluster, model):
    prompt = META_PROMPT.format(
        kind=cluster["kind"],
        signature=cluster["signature"],
        evidence="\n".join(f"- {e}" for e in cluster["evidence"]),
    )
    from forge_llm import call_model
    text, engine = call_model(prompt, model)
    print(f"  (brief synthesized by {engine})", file=sys.stderr)
    # Tolerate the model wrapping JSON in prose.
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        sys.exit(f"no JSON in brief synthesis output: {text[:300]}")
    brief = json.loads(text[start:end + 1])
    for key in ("id", "prompt", "verify", "rubric"):
        if key not in brief:
            sys.exit(f"brief missing {key}: {text[:300]}")
    brief.setdefault("setup", "")
    brief["source_failure"] = {k: cluster[k] for k in ("kind", "signature", "count", "session_count")}
    brief["generated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    return brief


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", help="failures.json or a single cluster json")
    ap.add_argument("--index", type=int, default=0, help="cluster index in failures.json")
    ap.add_argument("--out", default="briefs")
    ap.add_argument("--model", default=os.environ.get("FORGE_BRIEF_MODEL", "claude-sonnet-4-5"))
    args = ap.parse_args()

    data = json.load(open(args.source))
    cluster = data["clusters"][args.index] if "clusters" in data else data
    brief = synth(cluster, args.model)
    os.makedirs(args.out, exist_ok=True)
    path = os.path.join(args.out, f"{brief['id']}.json")
    if os.path.exists(path):
        sys.exit(f"refusing to overwrite {path}")
    json.dump(brief, open(path, "w"), indent=1)
    print(path)
    print(f"  prompt: {brief['prompt'][:200]}...")
    print(f"  verify: {brief['verify']}")


if __name__ == "__main__":
    main()
