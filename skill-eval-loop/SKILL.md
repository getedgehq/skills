---
name: skill-eval-loop
description: Prove whether a candidate skill actually improves agent performance before adopting it - blind A/B evals on reconstructed real tasks, a three-tier adoption gate, and production rechecks. Use when asked to "eval this skill", "does this skill help", "test this skill before installing", "run the auto-improve loop", or "recheck probationary skills". Takes candidates from skill-miner; runs locally with the user's own agent CLI and models.
---

# skill-eval-loop

The proof half of the auto-improve loop. skill-miner finds pain and candidates;
this skill decides what earns a place in the fleet. Everything runs locally -
the user's own machine, own agent CLI, own models, own tasks.

## The loop

```bash
python3 scripts/brief.py <clusters.json> --index 0 [--knowledge-gap]   # theme -> eval brief
for n in 1 2 3; do
  FORGE_SAMPLE=$n bash scripts/run_eval.sh <brief.json> without ""     # baseline arm
  FORGE_SAMPLE=$n bash scripts/run_eval.sh <brief.json> with <skill>   # candidate arm
  python3 scripts/judge.py <brief.json> --sample $n                    # blind A/B + verify
done
python3 scripts/aggregate.py <brief.json>                              # strict majority
python3 scripts/gate.py <brief.json> <skill> [--adopt-dir DIR] [--probation --failure-rate R]
python3 scripts/recheck.py --sources claude,opencode,codex             # weekly probation review
```

Or hands-free end to end:

```bash
bash scripts/forge.sh --mode corrections --memory ~/.claude/projects/<proj>/memory   # recommended
bash scripts/forge.sh --mode corrections --dry-run          # stop before eval spend
bash scripts/forge.sh --brief briefs/x.json --skill-dir drafts/y --samples 3   # eval only
```

`forge.sh`: mine -> brief -> match -> score -> (draft) -> N samples per arm -> judge ->
aggregate -> gate. `FORGE_ADOPT_DIR` stages adoptions instead of installing to
`~/.agents/skills`.

## Knowledge-gap briefs (where skills win)

`brief.py --knowledge-gap` builds a task from a correction theme where the user's OWN
rules decide quality: realistic fixtures (a thread, notes, logs), a prompt in the user's
style that does not state the rules, and a Python verify of objective rule properties
(length caps, forbidden phrases, numbers not in the notes). Rules never go in fixtures,
so only a skill can carry them. The verify is self-tested before the brief is written:
it must pass the model's good example and fail its bad example, or the brief is rejected.

Brief fields: `{id, prompt, setup, verify, rubric, output}`. `verify` runs in the workdir
and exits 0 on acceptable output. When the deliverable is the agent's final chat reply,
verify reads it from `$FORGE_FINAL`.

## Runs on your own machine

No sandbox service, no account. Needs `python3`, `bash`, and a logged-in agent CLI -
`FORGE_AGENT=claude` (default), `codex` or `opencode` - so evals use your own
subscription or API key and your own session logs. Works on
macOS (falls back to `gtimeout` or a perl alarm when `timeout` is missing) and Linux,
or on your own cloud box. To watch and drive it in a browser, use **skill-cockpit**.

## Three-tier gate

- **ADOPT** - with-arm wins the strict majority of blind samples AND passes verify AND
  makes no more tool errors than baseline. One sample is noise: run 3.
- **PROBATION** - eval is a clean tie but the production failure is real and
  costly. Context-rot failures (buried rules, long sessions, mid-flow shortcuts)
  CANNOT be reproduced in one-shot evals: frontier models pass fresh small tasks
  with or without a skill. Probation installs the skill with a 7-day recheck date.
- **REJECT** - everything else. Losers are recorded in `ledger.jsonl` and never
  re-evaled.

## recheck.py (weekly)

Re-mines recent sessions and compares each probationary skill's failure
session-rate against its adoption baseline. Dropped >=30% -> `adopt-confirmed`.
No drop -> the skill is REMOVED from the fleet and the ledger records `revoked`.
Context-rot skills are measured in production, not sandboxes.

## Hard rules (all learned from real eval failures)

- **Blind judging is non-negotiable.** Arm identity lives in
  `mapping.private.json`; the judge sees only slot A/B.
- **Both arms failing verify means the brief is broken** - judge marks the eval
  `invalid`, never picks a winner over two broken runs. Fix the eval, not the loop.
- **Evals need headroom and pressure.** Toy tasks don't reproduce real failures.
  But note the one-shot ceiling: recoverable single-turn errors never show skill
  value - only silent-wrong-output and knowledge-gap failures discriminate.
- **Copy skills with `cp -rL`** - production skills are often symlinks; a plain
  copy gives the with-arm a dangling link and a silent no-skill run.
- **Verify only what the prompt explicitly asks**, tolerate formatting variation.
- **Share one baseline across candidates** for the same brief: copy `without` +
  `without.meta` per sample instead of re-running it.
- Budget: each sample is two headless agent runs. `FORGE_MODEL`, `FORGE_TIMEOUT`,
  `FORGE_SAMPLE` control cost and layout. Default sonnet, 1200s.

State: `$FORGE_ROOT` (default `~/skill-forge`) - runs/, ledger.jsonl.
