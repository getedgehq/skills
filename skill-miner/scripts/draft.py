#!/usr/bin/env python3
"""Draft a candidate skill from a failure cluster when no existing skill matches.

Usage: draft.py <failures.json> --index N [--out $FORGE_ROOT/drafts]

The drafted skill is a CANDIDATE, not an adoption. It only reaches a real
skills directory if it wins the blind A/B eval (judge.py) and passes gate.py.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time

DRAFT_PROMPT = """A Claude agent repeatedly fails in real sessions like this:

Failure kind: {kind}
Signature: {signature}
Occurrences: {count} across {session_count} sessions
Evidence:
{evidence}

Write a SKILL.md for a small, sharp skill that prevents this specific failure.
Rules:
- YAML frontmatter with `name` (kebab-case) and `description`. The description MUST
  name the task contexts where the skill applies (e.g. "use when editing or updating
  existing files", "use when running long bash pipelines") - the agent decides to load
  a skill BEFORE it hits the failure, so a description naming the error it prevents
  ("prevents X error") will never trigger. One sentence, concrete triggers.
- Body: the minimal procedure that avoids the failure. Checklists over prose.
  Under 60 lines total. No motivational filler, no restating the tool docs.
- Scope ONLY this failure. Do not build a general best-practices document.

Return the raw SKILL.md content only, no markdown fences around the whole file."""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("--index", type=int, default=0)
    ap.add_argument("--out", default=None)
    ap.add_argument("--model", default=os.environ.get("FORGE_BRIEF_MODEL", "claude-sonnet-4-5"))
    args = ap.parse_args()

    root = os.environ.get("FORGE_ROOT", os.path.expanduser("~/skill-forge"))
    out_root = args.out or os.path.join(root, "drafts")
    data = json.load(open(args.source))
    cluster = data["clusters"][args.index] if "clusters" in data else data

    prompt = DRAFT_PROMPT.format(
        kind=cluster["kind"], signature=cluster["signature"],
        count=cluster["count"], session_count=cluster["session_count"],
        evidence="\n".join(f"- {e}" for e in cluster["evidence"]),
    )
    from forge_llm import call_model
    text, engine = call_model(prompt, args.model)
    print(f"  (drafted by {engine})", file=sys.stderr)

    m = re.search(r"name:\s*([\w-]+)", text)
    if not m:
        sys.exit(f"no frontmatter name in draft: {text[:200]}")
    name = m.group(1)
    dest = os.path.join(out_root, name)
    if os.path.exists(dest):
        sys.exit(f"refusing to overwrite {dest}")
    os.makedirs(dest)
    open(os.path.join(dest, "SKILL.md"), "w").write(text.strip() + "\n")
    meta = {"drafted": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "source_failure": {k: cluster[k] for k in ("kind", "signature", "count", "session_count")}}
    json.dump(meta, open(os.path.join(dest, ".forge-draft.json"), "w"), indent=1)
    print(dest)


if __name__ == "__main__":
    main()
