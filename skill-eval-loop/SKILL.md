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
python3 scripts/brief.py <failures.json> --index 0         # failure -> eval task brief
bash scripts/run_eval.sh <brief.json> without ""           # baseline arm
bash scripts/run_eval.sh <brief.json> with <skill-dir>     # candidate arm
python3 scripts/judge.py <brief.json>                      # blind A/B + objective verify
python3 scripts/gate.py <brief.json> <skill-dir> [--probation --failure-rate R]
python3 scripts/recheck.py                                 # weekly: probation review
```

Or hands-free end to end (mine -> brief -> match -> score -> eval -> judge -> gate,
mining stages pulled from the sibling skill-miner skill):

```bash
FORGE_PROJECTS=~/.claude/projects bash scripts/forge.sh            # full loop
FORGE_PROJECTS=~/.claude/projects bash scripts/forge.sh --dry-run  # no eval spend
```

Briefs are JSON: `{id, prompt, setup, verify, rubric}`. `setup` builds a realistic
workdir, `verify` is a shell command that exits 0 only on correct completion.

## Runs on your own machine

No sandbox service, no account. Needs `python3`, `bash`, and a logged-in `claude`
CLI - evals use your own subscription or API key and your own session logs. Works on
macOS (falls back to `gtimeout` or a perl alarm when `timeout` is missing) and Linux,
or on your own cloud box. To watch and drive it in a browser, use **skill-cockpit**.

## Three-tier gate

- **ADOPT** - with-arm wins the blind eval AND passes verify AND makes no more
  tool errors than baseline.
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
- Budget: each pair is two headless agent runs. `FORGE_MODEL`, `FORGE_TIMEOUT`
  control cost. Default sonnet, 1200s.

State: `$FORGE_ROOT` (default `~/skill-forge`) - runs/, ledger.jsonl.
