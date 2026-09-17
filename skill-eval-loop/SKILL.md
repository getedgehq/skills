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

A signature lifted from the skill's own description is refused on sight, however narrow it
looks. Width cannot tell prose from a theme: extending the stopword list pulled three
such signatures from 35-42 distinct words to 18-20, under the cap, without making one of
them more about a single theme. They describe the skill, not the mistake, so a verdict
from one would uninstall a working skill on the strength of its own marketing. Mine a
real theme with theme.py instead.

A single theme word is enough to count an episode when that word is rare in the corpus
(under an eighth of episodes); otherwise two must match.

`tests/test_recheck.py` pins all of it down on fixtures - stdlib only, no model calls,
no network - including the symlinked uninstall, both zero-evidence skips, the recency
guard and a real drop. Every case in it is a bug that reached real data first.

## backfill.py

`backfill.py` gives already-adopted skills something to be measured by: skills forged
from hand-written briefs carry no failure record, so the recheck would skip them
forever. It lifts the theme back out of the installed SKILL.md - the front-matter
description plus the user's own quoted corrections - and writes it onto the ledger row
tagged `derived_from: skill_md:<path>`. That is a matcher, never a measurement, and the
recheck's guards still decide whether it is good enough to use. `--apply` backs the
ledger up first; `--redo` re-derives signatures it wrote before.

## theme.py: when the skill has no theme worth measuring

`backfill.py` lifts a theme out of a skill's own prose, and for voice and format skills
that prose is long and ordinary: matched against real sessions those signatures claimed
33-43% of every correction the user ever made, so the recheck refuses them, correctly
and permanently. `theme.py` looks for the theme where it actually lives, in the
corrections themselves: seed from the skill, pull the episodes those seeds match, rank
the words those episodes keep returning to, then check the result is narrow, still on
the skill's subject, has a baseline before the adoption date, and is not the same
matcher another skill already has.

Expect it to refuse. Against 136 real correction episodes it derived nothing for seven
adopted skills, each for a different stated reason, and that is the finding rather than
a bug: a voice skill is corrected in words too ordinary to separate from every other
correction.

More correction history looked like the fix, so it was tried: a corpus of 340 episodes
across 296 sessions, two and a half times the size. It derived nothing there either,
and on the way it exposed two bugs the smaller corpus had hidden. So the answer does
not turn on corpus size, and a looser matcher would only return a number about the
vocabulary. Six things it took to get here, all pinned in `tests/test_theme.py`:

- **Ranking by lift is the textbook answer and carries zero information here.** In a
  136-episode corpus almost every content word inside a 30-episode subset appears
  nowhere else, so every candidate scored the identical lift of n_all/n_seed. Ranking
  now uses within-theme document frequency, which the corpus can actually support.
- **Statistics cannot tell filler from subject.** The first signatures out of the new
  ranking were "but can dont have", then "post real" - each passing every check while
  being about nothing. Fixed by extending the recheck's stopword list with English and
  German function words (the user corrects in both) and requiring at least four
  recurring words.
- **A corpus-driven theme can drift off the skill entirely.** For a skill about reusing
  existing assets it derived a real, coherent topic cluster about one website's pages.
  The derived words now have to overlap what the skill says it is about.
- **Overlapping the description is not enough, and the same case proves it.** A
  description names its subject once and spends the rest on context, so "find", "posts"
  and "visuals" were all in it while "reuse", "existing" and "assets" appeared 0-1 times
  in the whole corpus. Rarity cannot separate those either: at 136 episodes every seed
  word sits under the rare threshold. The overlap now has to include the thing the skill
  is *named* after, matched on a shared prefix so `german-umlauts` still matches the
  corpus word "umlaute".
- **A floor set as a share of the seed gets worse as the corpus grows.** Tripling the
  corpus took one skill's seed from 58 episodes to 135, so a 20% floor moved from 11 to
  27 while its most distinctive word only moved from 6 to 15: the theme word was
  discarded for being outnumbered by a seed that was too broad to begin with. The floor
  is now absolute, and the breadth it was standing in for is refused directly, one step
  earlier, by `MAX_SEED_SHARE`.
- **Two skills can pass every check and be one matcher.** On the 340-episode corpus four
  of them returned the same share and the same before/after counts to the episode,
  because all four were matching one generic cluster of content work. Comparing the
  signatures word by word misses it - two of the four shared 3 words out of 17, a
  Jaccard of 0.18 - because synonyms read as distinct vocabularies. Compared on the
  sessions each one actually matches, the same pair overlaps 74% and both are refused.

`--apply` writes the signature tagged `derived_from: corrections:<n> episodes`, so it
is never mistaken for a hand-written one, and the recheck still applies every one of
its own refusals to whatever comes out. A signature that passes the statistics and
fails inspection does not get applied.

## deploy.sh

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
