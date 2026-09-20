---
name: brain-scan
description: Scan authorized Claude, Codex, or OpenCode session logs for recurring correction themes, reconstruct real tasks, and measure whether a selected Skill improves the actual output in a blinded no-Skill versus explicitly-loaded comparison. Use when someone asks for an agent brain scan, wants to know which Skills materially help their own work, or asks to test a Skill against their real sessions.
---

# Brain Scan

Measure one useful question: on tasks recovered from this person's own sessions, does the
actual output improve when the selected Skill is explicitly loaded?

## Default assessment

Use exactly two arms:

- `base`: the selected Skill is absent.
- `loaded`: the same model, task, fixtures, tools, limits, and ordinary context, with the
  selected Skill's frozen `SKILL.md` content supplied before work begins.

Do not add a discovery arm. Do not replace this comparison with current setup versus an
incremental prompt patch. Never promise uplift.

## Run

1. Confirm which local session roots the user authorizes. Raw logs stay local.
2. Extract correction episodes without a model call:

```bash
python3 <skill-dir>/vendor/skill-miner/scripts/corrections.py \
  --sources claude,opencode,codex --no-llm --out <private-dir>/corrections.json
```

3. Choose a recurring, consequential knowledge gap. Reconstruct the real task and only the
   fixtures needed to perform it. Remove credentials, unrelated customer data, known answers,
   and absolute paths. Do not turn an old correction into a synthetic checklist task.
4. Write a `skill-eval-loop` brief with `id`, `prompt`, `setup`, `verify`, and `rubric`.
   Freeze criteria before running. The verifier may check explicit correctness and safety;
   judge usefulness from the actual artifact blind.
5. Run three paired samples through the existing GetEdge evaluator:

```bash
FORGE_AGENT=opencode FORGE_SUBJECT_ISOLATION=systemd \
  FORGE_ROOT=<private-run-dir> \
  bash <skill-dir>/scripts/run_explicit_eval.sh <brief.json> <candidate-skill-dir> 3
```

The wrapper reuses the vendored GetEdge `skill-eval-loop` runner, judge, and aggregate. It
changes only the treatment delivery: the frozen Skill content is placed directly in context,
so a discovery failure cannot masquerade as no effect.

`systemd` isolation is the release-tested Linux path. It runs each subject as an unprivileged
user in a filesystem namespace that exposes only that arm at `/workspace`. Do not call a run
isolated merely because it has a fresh working directory or HOME; the subject must be unable to
traverse user homes, host temp state, other arms, or generated treatment briefs. Use an
equivalent Harbor/container sandbox on hosts without systemd isolation.

## Report inline

Return a compact terminal result:

- tasks and valid paired samples;
- base and loaded pass counts;
- loaded-minus-base percentage-point delta;
- blind wins, ties, and regressions;
- one concrete before/after output difference;
- invalid or timed-out pairs and every important limitation.

If the selected Skill did not improve the outputs, say so. Do not adopt, install, publish,
upload, or alter live configuration unless the user separately authorizes that action.

## Privacy and validity

- Never publish raw prompts, session excerpts, private filenames, paths, transcripts, or
  customer/project names. Public evidence must be redacted and reproducible from fixtures.
- Both arms use fresh workspaces and identical non-treatment inputs.
- Record the selected Skill's content hash. A baseline containing that Skill or copied
  treatment instructions invalidates the pair.
- Keep all selected tasks, ties, losses, infrastructure failures, and non-loads. Do not rerun
  until the result looks positive.
- A deterministic check is not a substitute for inspecting the actual deliverable.

The vendored evaluator and miner are exact copies of the GetEdge packages recorded in
`DERIVATION.json`; they are included so installing Brain Scan is one Skill install.
