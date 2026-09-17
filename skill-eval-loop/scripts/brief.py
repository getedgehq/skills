#!/usr/bin/env python3
"""Turn a mined failure cluster into a self-contained eval brief.

Usage: brief.py <cluster.json | failures.json --index N> [--out briefs/] [--knowledge-gap]

Calls headless claude to synthesise a reproducible task that recreates the
context where the failure occurred. Briefs must have HEADROOM: a real,
slightly messy core-job task, completable autonomously in <20 minutes,
with a deterministic verify command. Toy prompts make evals worthless.

--knowledge-gap (for correction clusters from corrections.py): builds a task where
the user's OWN rules decide quality. Fixtures hold realistic materials but never the
rules, so the baseline cannot read them off the workdir - only a skill can carry them.
The synthesized verify is self-tested: it must pass the model's good example AND a thorough,
realistic one (long, names rejected options, locale numbers), and fail its bad example, or the
brief is rejected. Generic failures tie in one-shot evals;
knowledge gaps are where skills measurably win.
"""
import argparse
import json
import os
import re
import shutil
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


KG_PROMPT = """You are designing a knowledge-gap A/B eval. One arm of an agent gets a skill that
carries this user's personal rules; the other arm gets none. The user corrected their agent
like this in real sessions:

Theme: {signature}
User's own rule statements: {rules}
Correction episodes:
{evidence}

User's saved rules for this theme:
{context}

Design ONE realistic task from this user's real work where these rules decide quality.
Requirements:
- The prompt is written the way THIS user writes to their agent (their language mix, terse),
  asks for a concrete deliverable, and does NOT state the rules. Knowledge gap: a capable model
  without the rules would plausibly produce what the user corrected.
- Fixtures: realistic input files (logs, a thread, notes, past examples...) as a JSON object
  {{relative_path: file_content}}. Materials only: NEVER write the rules, a style guide, or
  hints about them into fixtures.
- No network, credentials, real accounts or side effects. Completable in a few minutes.
- output: either "final" (the agent's final chat reply is the deliverable) or a relative file
  path under out/ that the prompt explicitly names.
- verify_py: a Python snippet. Variable OUT holds the deliverable text; fixture files are
  readable from the working directory. Collect failures in a list named bad, then run
  print(bad); sys.exit(1 if bad else 0). `re`, `os`, `sys` are imported. Check ONLY objective
  properties evidenced by the user's rules (length caps, forbidden phrases or characters,
  numbers not present in the notes, required key fact from the fixtures). Tolerate formatting
  variation. Never check taste. Real agents write long, thorough deliverables, so:
  * a forbidden option must only fail when it is RECOMMENDED or USED, not when it is named as
    rejected/blocked/avoided ("gesperrt", "not", "instead of", "avoid", a comparison row);
  * parse numbers in both 1,234.56 and 1.234,56 (German) formats before comparing amounts;
  * length caps only where the user gave a figure; for "kurz"/"short" allow at least 3x the
    good example's length.
- rubric: judging criteria that quote the user's corrections verbatim.
- good_example: a deliverable the user would accept (must pass verify_py).
- good_example_thorough: another accepted deliverable written the way a strong agent really
  writes: longer, a comparison table that names the rejected options with reasons, numbers in
  the user's locale format, headings and bullets (must ALSO pass verify_py).
- bad_example: the typical output they corrected (must fail verify_py).

Return STRICT JSON only:
{{"id": "<kebab-case-id>", "prompt": "...", "fixtures": {{"path": "content"}}, "output": "final|out/...",
 "verify_py": "...", "rubric": "...", "good_example": "...", "good_example_thorough": "...", "bad_example": "..."}}"""


def verify_command(output, verify_py):
    src = "import os, re, sys\n"
    if output == "final":
        src += 'p = os.environ.get("FORGE_FINAL", "")\n'
    else:
        src += f"p = {output!r}\n"
    src += 'OUT = open(p, errors="replace").read().strip() if p and os.path.exists(p) else ""\n'
    src += verify_py.strip() + "\n"
    if "PYEOF" in src:
        sys.exit("verify_py contains the heredoc delimiter")
    return "python3 - <<'PYEOF'\n" + src + "PYEOF"


def self_test(brief, fixtures, output, examples):
    """verify must accept every good example and reject the bad one - else the eval measures nothing.
    The thorough good example catches brittle verifies (a rejected option named in a comparison,
    German decimal commas, a tight length cap) that fail BOTH arms of a real eval."""
    import subprocess, tempfile
    results = {}
    for label, text in examples.items():
        d = tempfile.mkdtemp(prefix="kg-selftest-")
        for rel, content in fixtures.items():
            path = os.path.join(d, rel)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            open(path, "w").write(content)
        env = dict(os.environ)
        target = os.path.join(d, "final.txt") if output == "final" else os.path.join(d, output)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        open(target, "w").write(text)
        if output == "final":
            env["FORGE_FINAL"] = target
        r = subprocess.run(["bash", "-c", brief["verify"]], cwd=d, env=env,
                           capture_output=True, text=True, timeout=60)
        results[label] = (r.returncode, (r.stdout + r.stderr).strip()[-300:])
        shutil.rmtree(d, ignore_errors=True)
    return results


def synth_kg(cluster, model, fixtures_root, attempts=3):
    from forge_llm import call_model
    context = "\n\n".join(f"--- {os.path.basename(c)} ---\n" + open(c, errors="replace").read()[:6000]
                           for c in cluster.get("context_files", []) if os.path.exists(c)) or "(none)"
    prompt = KG_PROMPT.format(signature=cluster["signature"],
                              rules=json.dumps(cluster.get("user_rules", []), ensure_ascii=False),
                              evidence="\n".join(f"- {e}" for e in cluster["evidence"]),
                              context=context)
    feedback = ""
    for attempt in range(attempts):
        text, engine = call_model(prompt + feedback, model, timeout=900)
        print(f"  (knowledge-gap brief by {engine}, attempt {attempt + 1})", file=sys.stderr)
        start, end = text.find("{"), text.rfind("}")
        try:
            spec = json.loads(text[start:end + 1])
            missing = [k for k in ("id", "prompt", "fixtures", "output", "verify_py", "rubric",
                                   "good_example", "good_example_thorough", "bad_example") if k not in spec]
        except ValueError as e:
            spec, missing = None, [f"invalid JSON: {e}"]
        if missing:
            feedback = f"\n\nYour previous answer was unusable ({missing}). Return the full STRICT JSON."
            continue
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,60}", str(spec["id"])):
            feedback = "\n\nid must be kebab-case [a-z0-9-]."
            continue
        output = spec["output"]
        if output != "final" and (output.startswith("/") or ".." in output):
            feedback = "\n\noutput must be \"final\" or a relative path under out/."
            continue
        fixtures = {k: v for k, v in spec["fixtures"].items() if not k.startswith("/") and ".." not in k}
        brief = {"id": spec["id"], "prompt": spec["prompt"], "rubric": spec["rubric"], "output": output}
        brief["verify"] = verify_command(output, spec["verify_py"])
        res = self_test(brief, fixtures, output, {"good": spec["good_example"],
                                                  "good_thorough": spec["good_example_thorough"],
                                                  "bad": spec["bad_example"]})
        if res["good"][0] == 0 and res["good_thorough"][0] == 0 and res["bad"][0] != 0:
            fx_dir = os.path.join(fixtures_root, brief["id"])
            if os.path.exists(fx_dir):
                sys.exit(f"refusing to overwrite fixtures {fx_dir}")
            for rel, content in fixtures.items():
                path = os.path.join(fx_dir, rel)
                os.makedirs(os.path.dirname(path), exist_ok=True)
                open(path, "w").write(content)
            mk = "" if output == "final" else f" && mkdir -p {json.dumps(os.path.dirname(output) or '.')}"
            brief["setup"] = f'cp -r "$FORGE_ROOT/fixtures/{brief["id"]}/." .{mk}'
            brief["self_test"] = {k: v[1] for k, v in res.items()}
            brief["knowledge_gap"] = True
            brief["context_files"] = cluster.get("context_files", [])
            return brief
        feedback = ("\n\nSELF-TEST FAILED. verify must exit 0 on good_example AND good_example_thorough, "
                    "and non-zero on bad_example. " +
                    "; ".join(f"{k} -> exit {v[0]} ({v[1]})" for k, v in res.items()) +
                    ". Loosen brittle checks rather than trimming the thorough example; return the full JSON again.")
    sys.exit("knowledge-gap brief failed its self-test - not writing a broken eval")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", help="failures.json or a single cluster json")
    ap.add_argument("--index", type=int, default=0, help="cluster index in failures.json")
    ap.add_argument("--out", default="briefs")
    ap.add_argument("--model", default=os.environ.get("FORGE_BRIEF_MODEL", "claude-opus-5"))
    ap.add_argument("--knowledge-gap", action="store_true",
                    help="build a user-rules task with fixtures and a self-tested verify")
    args = ap.parse_args()

    data = json.load(open(args.source))
    cluster = data["clusters"][args.index] if "clusters" in data else data
    if args.knowledge_gap:
        root = os.environ.get("FORGE_ROOT", os.path.expanduser("~/skill-forge"))
        brief = synth_kg(cluster, args.model, os.path.join(root, "fixtures"))
        brief["source_failure"] = {k: cluster[k] for k in ("kind", "signature", "count", "session_count")}
        brief["generated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    else:
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
