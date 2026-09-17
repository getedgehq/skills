# harness-first, run `hf-v1`, 2026-09-17

The complete artifacts behind [`harness-first/EVALS.md`](../../../harness-first/EVALS.md). 48 agent sessions across 3 tasks, 48 grader verdicts behind the headline number, and the files every session produced. Nothing here is summarised. If something here disagrees with the numbers on the EVALS page, this directory is right.

## The arms

- `base`: nothing loaded
- `skill`: the Skill installed on disk, which the agent has to find and open itself

Every pair is one treatment session against the `base` session with the same task and sample number.

Sample numbers run 1 to 8.

## Layout

```
summary.json            the aggregate the headline numbers are computed from
summary.md              the same aggregate as the harness printed it
summary-t3-n4.json      a further aggregate of this run, cited on the EVALS page
summary-t3-n4.md        the same aggregate as the harness printed it
summary-t3-n8.json      the same file under the name the run gave it, and the name EVALS.md cites
summary-t3-n8.md        the same aggregate as the harness printed it
summary-v2.json         a further aggregate of this run, cited on the EVALS page
summary-v2.md           the same aggregate as the harness printed it
sessions.json           index of the 48 sessions: turns, cost, stop reason, check result
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
                       24 grader verdicts. Per-criterion scores for
                       both sides with the grader's note on each, a free-text
                       analysis, two overall scores, a winner, and the grader
                       profiles used. Each pair appears twice, once per
                       presentation order.
judgments-t3/<task>__<arm>__s<N>__<order>.json
                       48 grader verdicts, the headline set. Per-criterion scores for
                       both sides with the grader's note on each, a free-text
                       analysis, two overall scores, a winner, and the grader
                       profiles used. Each pair appears twice, once per
                       presentation order.
judgments-t3-n4/<task>__<arm>__s<N>__<order>.json
                       24 grader verdicts. Per-criterion scores for
                       both sides with the grader's note on each, a free-text
                       analysis, two overall scores, a winner, and the grader
                       profiles used. Each pair appears twice, once per
                       presentation order.
```

There is more than one judgment directory because the EVALS page reports more than one measurement of this run. `judgments-t3` is the one the headline comes from; the others cover a different sample size or a superseded grader, and the page says which is which. Every summary file records the directory it was computed from in its `judgments` field, so the mapping is checkable here without reading the page. The same pair therefore appears in more than one directory, and the verdict counts above must not be added together.

## How to read a judgment file

`A` and `B` are the two sides as the grader saw them, and which is which depends on `order`:

- `order: "base_first"` means A is the baseline session and B is the treatment session.
- `order: "skill_first"` means A is the treatment session and B is the baseline session.

The grader is never told which is which. `verdict.winner` is `"A"`, `"B"` or a tie.

A file may also carry `judge_saw_checks`. When it is `false`, the grader was handed the string `withheld: judge independently of the automated checks` in place of the hard check result, so the rubric score and the check result are two independent readings of the same deliverable. Where the field is missing the grader was run before it existed and could see the check verdict, which makes that rubric score and that check result one reading rather than two. Per directory in this bundle:

- `judgments`: no `judge_saw_checks` field, so the grader predates the blinding and could see the checks
- `judgments-t3`: `judge_saw_checks: false` in every file, so the grader was blind to the checks
- `judgments-t3-n4`: `judge_saw_checks: false` in every file, so the grader was blind to the checks

## What was changed before publishing

The repo's redaction gate rewrote these classes of string, everywhere they appeared. The count is the number of files in this bundle that contain the placeholder, so you can find every one of them:

- `[HOME]`, the operator's home directory path, in 97 files
- `[SANDBOX]`, an E2B sandbox id, naming an ephemeral machine that no longer exists, in 49 files

Nothing else was rewritten. No score, verdict, transcript turn or deliverable was edited, reordered or removed.
