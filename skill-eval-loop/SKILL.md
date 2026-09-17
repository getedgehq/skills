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
python3 scripts/recheck.py --sources claude,opencode,codex --dry-run  # weekly review, decides nothing
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

Re-mines recent sessions and compares each skill's failure session-rate against its
adoption baseline. Dropped >=30% -> `adopt-confirmed`. No drop -> the skill is
uninstalled (symlinks unlinked, the copy moved to `$FORGE_ROOT/revoked/`) and the ledger
records `revoked`. Adopted skills get a 14-day recheck, probation 7: winning a rebuilt
eval task is not the same as reducing failures in real sessions.

Knowledge-gap skills have no tool-error signature to count, so they are measured on the
user's own corrections: `corrections.py --no-llm` re-extracts correction episodes and the
rate of corrections about that theme is compared on both sides of the adoption date, with
one matcher. A recheck never needs a model call.

Run `--dry-run` first on any machine where skills are installed: it prints every decision
and uninstalls nothing. Run it where the user actually types - a box that only runs
headless agents has no corrections to count, and the recheck will say so rather than
guess.

**A recheck never confirms or revokes on absent evidence.** No baseline, no recorded
signature, a baseline of zero, or too few sessions on either side of the adoption all
produce SKIP. The first version read "no signature" as a 0% failure rate and would have
confirmed three skills that had never been measured; the inverse bug would have
uninstalled six working skills because a rate of zero cannot drop by 30%.

Three more refusals come from watching the correction metric behave on real logs:

- **Less than five days of sessions since adoption -> SKIP.** A skill adopted this
  morning has no production record, and half a day of work cannot show a rate change.
- **Theme words that are common across all corrections are dropped before matching**,
  and a signature left with fewer than two distinct words is refused. Ordinary words
  ("post", "reply", "status") match nearly every correction, which returns noise
  wearing the costume of a measurement.
- **A signature matching on more than 20 distinct words is refused as too broad.**
  Whatever rate that produces is about vocabulary, not about one theme. On real data
  a signature lifted from a whole skill body matched 33-43% of all sessions; the three
  signatures mined as themes matched 5-18%.

A single theme word is enough to count an episode when that word is rare in the corpus
(under an eighth of episodes); otherwise two must match.

`tests/test_recheck.py` pins all of it down on fixtures - stdlib only, no model calls,
no network - including the symlinked uninstall, both zero-evidence skips, the recency
guard and a real drop. Every case in it is a bug that reached real data first.

## backfill.py and deploy.sh

`backfill.py` gives already-adopted skills something to be measured by: skills forged
from hand-written briefs carry no failure record, so the recheck would skip them
forever. It lifts the theme back out of the installed SKILL.md - the front-matter
description plus the user's own quoted corrections - and writes it onto the ledger row
tagged `derived_from: skill_md:<path>`. That is a matcher, never a measurement, and the
recheck's guards still decide whether it is good enough to use. `--apply` backs the
ledger up first; `--redo` re-derives signatures it wrote before.

`deploy.sh [--to host]` copies these skills from a checkout to an install root and
verifies each tree by digest. The loop forges skills for other tasks and had no way to
ship itself: a laptop running a three-day-old `mine.py` failed only when the timer
fired, with `unrecognized arguments: --sources`.

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
