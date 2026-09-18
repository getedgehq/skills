# strip-image-ai-metadata, run `t3-v2`, 2026-09-17

The complete artifacts behind [`strip-image-ai-metadata/EVALS.md`](../../../strip-image-ai-metadata/EVALS.md). 36 agent sessions across 3 tasks, 36 grader verdicts behind the headline number, and the files every session produced. Nothing here is summarised. If something here disagrees with the numbers on the EVALS page, this directory is right.

## The arms

- `base`: nothing loaded
- `loaded`: the Skill text placed in the prompt up front

Every pair is one treatment session against the `base` session with the same task and sample number.

Sample numbers run 1 to 6.

## Layout

```
summary.json            the aggregate the headline numbers are computed from
summary.md              the same aggregate as the harness printed it
sessions.json           index of the 36 sessions: turns, cost, stop reason, check result
binary-files.json       every non-text file in this bundle, listed with its size
skipped.json            what was left out of the copied session outputs, and how much

tasks/<task>/
  task.json            the user prompt, the rubric with weights, why the Skill should
                       matter, and the baseline failure modes expected in advance
  check.py             the hard check, verbatim, standard library only
  input/               exactly what was copied into the sandbox for every arm
  calibration/good     a hand-written output the check must pass, written before the run
  calibration/bad      a hand-written output the check must fail
  _gen/                the generator for a task fixture, where one exists

sessions/<task>/<arm>-s<N>/
  transcript.md        the readable session log: system prompt, request, every turn,
                       every tool call with arguments, every tool result, final message
  transcript.json      the same session unrendered
  result.json          turns, cost, token usage, tool errors, stop reason, timings,
                       changed files, and the check.py verdict for this session
  final_message.md     what the agent said to the user at the end
  output/              the files that session wrote

judgments/<task>__<arm>__s<N>__<order>.json
                       36 grader verdicts, the headline set. Per-criterion scores for
                       both sides with the grader's note on each, a free-text
                       analysis, two overall scores, a winner, and the grader
                       profiles used. Each pair appears twice, once per
                       presentation order.
```

## How to read a judgment file

`A` and `B` are the two sides as the grader saw them, and which is which depends on `order`:

- `order: "base_first"` means A is the baseline session and B is the treatment session.
- `order: "skill_first"` means A is the treatment session and B is the baseline session.

The grader is never told which is which. `verdict.winner` is `"A"`, `"B"` or a tie.

A file may also carry `judge_saw_checks`. When it is `false`, the grader was handed the string `withheld: judge independently of the automated checks` in place of the hard check result, so the rubric score and the check result are two independent readings of the same deliverable. Where the field is missing the grader was run before it existed and could see the check verdict, which makes that rubric score and that check result one reading rather than two. Per directory in this bundle:

- `judgments`: `judge_saw_checks: false` in every file, so the grader was blind to the checks

## The intervals were recalibrated on 2026-09-17

Every current summary file in this bundle was regenerated that day. Nothing else
was: the judgments, the session transcripts, the task definitions and the
deliverables are byte-identical to what the run produced, and no score, verdict or
count moved. A file whose name marks it as superseded is the exception and is kept
exactly as it was written, because its whole purpose is to show what an earlier
version said.

What moved is the interval. The figures these runs first reported came from a
percentile cluster bootstrap, which resamples tasks and then samples within tasks.
That estimator is anti-conservative when the cluster count is small: measured
against a known truth at the three tasks per Skill these runs use, it excludes zero
about 15.7% of the time when the true effect is exactly zero, not 5%. The shortfall
is in the number of tasks, so more samples per task make it worse rather than
better. The measurement and its checks are in
[`docs/BENCHMARK.md`](../../../docs/BENCHMARK.md) section 5.

`delta_ci95` is now a two-sided 95% t interval on the per-task means, with k-1
degrees of freedom, and `interval_method` names it. The bootstrap value every
earlier figure was read off is kept beside it as `judge_delta_ci95_bootstrap`, and
`resolved_bootstrap_legacy` records what the old rule would have said, so the
correction can be checked against the numbers it replaces rather than taken on
trust. The `summary.md` tables carry both intervals in adjacent columns.

The publication rule is unchanged and is the pre-registered one: a cell resolves
when the 95% interval on the judge point delta excludes zero. Two changes follow
from implementing it correctly.

`resolved` no longer reports a win-rate resolution. The win rate is bounded in
[0, 100] and the t interval on its task means is not, printing bounds such as
[53.9, 101.7] and [-194.5, 282.0] in this benchmark; an interval that runs past the
range of the quantity it covers is not delivering 95% coverage near the bound. It
is published as a diagnostic in the `win rate % [95% CI]` column and resolves
nothing until a bounded interval replaces it. The bootstrap's win-rate interval is
not the replacement, being the same estimator measured above.

## What was changed before publishing

The repo's redaction gate rewrote these classes of string, everywhere they appeared. The count is the number of files in this bundle that contain the placeholder, so you can find every one of them:

- `[SANDBOX]`, an E2B sandbox id, naming an ephemeral machine that no longer exists, in 37 files
- `[HOME]`, the operator's home directory path, in 37 files

Nothing else was rewritten. No score, verdict, transcript turn or deliverable was edited, reordered or removed.
