# harness-first, run `hf-v1`, 2026-09-15

> **Superseded on 2026-09-17.** The grader that produced the verdicts in this directory could see the automated checker's verdict for each side while it scored, so its +33.7 point result is withdrawn. Nothing here has been altered or removed; it is kept because the withdrawn number was published and the evidence for withdrawing it should be readable. The current measurement of this Skill is [`evals/harness-first/2026-09-17/`](../2026-09-17/), and the page both directories back is [`harness-first/EVALS.md`](../../../harness-first/EVALS.md), which explains the withdrawal.

The complete artifacts behind [`harness-first/EVALS.md`](../../../harness-first/EVALS.md).
Twenty-four agent sessions, twenty-four grader verdicts, three tasks, and the files every
session produced. Nothing here is summarised. If something here disagrees with the numbers on
the EVALS page, this directory is right.

## Layout

```
summary.json            the aggregate every headline number is computed from
summary.md             the same aggregate as the harness printed it, one row
sessions.json          index of the 24 sessions: turns, cost, stop reason, check result
binary-files.json      the two non-text files in this bundle, listed with their sizes

tasks/<task>/
  task.json            the user prompt, the rubric with weights, why the Skill should
                       matter, and the baseline failure modes expected in advance
  check.py             the hard check, verbatim, standard library only
  input/               exactly what was copied into the sandbox for both arms
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

judgments/<task>__skill__s<N>__<order>.json
                       one grader verdict. Per-criterion scores for both sides with the
                       grader's note on each, a free-text analysis, two overall scores,
                       a winner, and the grader profiles used. Each pair appears twice,
                       once per presentation order.
```

`arm` is `skill` (SKILL.md loaded) or `base` (nothing loaded). `N` is the sample, 1 to 4.

## How to read a judgment file

`A` and `B` are the two sides as the grader saw them, and which is which depends on `order`:

- `order: "base_first"` means A is the baseline session and B is the Skill session.
- `order: "skill_first"` means A is the Skill session and B is the baseline session.

The grader is never told which is which. `verdict.winner` is `"A"`, `"B"` or a tie.

## What was changed before publishing

Two classes of string were rewritten by the repo's redaction gate, everywhere they appeared:

- E2B sandbox ids, replaced with `[SANDBOX]`. These identify ephemeral machines that no
  longer exist.
- The operator's home directory path, replaced with `[HOME]`. It appears in the `A` and `B`
  fields of every judgment file, which record where each side was read from.

The gate also scans for credential-shaped strings and for third-party names. It found none of
either. Forty-eight of the 516 files were touched, all for the two reasons above. Nothing
else was edited, reordered or removed.

One thing was already truncated before this bundle existed: the harness records at most 6000
characters of each tool result in `transcript.json`. The agent saw the full output; the
transcript holds the first 6000 characters of it.

## Two things worth knowing before you read the numbers

The grader was **Claude Haiku 4.5**, not a frontier model, and it **saw each side's
`check.py` result** while scoring. Fourteen of the 24 verdicts cite that result in their
reasoning. The rubric score and the hard-check score are therefore correlated by construction
rather than independent. Both points are covered in the Corrections section of `EVALS.md`.
