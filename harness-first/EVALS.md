# Evaluation of `harness-first`

This Skill was measured against itself being absent. Same model, same tasks, same
grader; the only difference between the two arms is whether `SKILL.md` was loaded.

Run date: 2026-09-15. Everything below is one run. It has not been repeated.

## Headline

| | With the Skill | Without it |
| --- | --- | --- |
| Rubric score (0-100) | **88.3** | 54.6 |
| Paired comparisons won | 9 of 12 | 2 of 12 (1 tie) |
| Hard checks fully passed | 41.7% | 8.3% |
| Hard-check score | 0.78 | 0.59 |
| Turns per attempt | 35.8 | 28.2 |
| Model cost per attempt | $0.95 | $0.77 |

Difference in rubric score: **+33.7 points**, 95% CI **[-1.6, +67.8]**.

That interval crosses zero. Twelve paired runs across three tasks is not enough
to call the effect statistically significant, and this page does not claim it is.
What the run does show is a large and consistent direction on two of the three
tasks, and one task where the Skill did not help.

## The tasks

Three tasks, four samples each, both arms: 24 agent sessions, 12 pairs.

Each task is a repository plus a message from a colleague who has already decided
what the problem is. The agent works in a sandbox with a real filesystem and a
shell. A `check.py` outside the sandbox then inspects what the agent left behind:
whether the right number was recomputed, whether a cap or a golden set was written
as an actual file, whether an ungated side effect was reported.

| Task | Kind | With the Skill | Without it | Difference | Pairs won |
| --- | --- | --- | --- | --- | --- |
| Outreach agent burning tokens | direct | 90.8 | 21.2 | **+69.6** | 4 of 4 |
| Finance agent reporting the wrong revenue | transfer | 92.9 | 57.5 | **+35.4** | 4 of 4 |
| Support prompt rewrite, go/no-go before Friday | transfer | 81.2 | 84.9 | **-3.7** | 1 of 4 |

"Direct" means the task is the situation `SKILL.md` describes. "Transfer" means it
is a different situation that the same method should still cover.

### Where it helped most

On the token-burn task the request is "pick a cheaper model and tell me what we
save". Without the Skill the agent usually did exactly that: read a price sheet,
recommend Haiku, quote a saving. With the Skill it aggregated the traces per
conversation first, found the mechanism that was actually multiplying the spend,
and said so before answering the model question. Hard-check score on that task
moved from 0.34 to 0.84.

### Where it did not help

On the support-prompt task the Skill arm scored slightly lower and won only one of
four pairs, with one tie and two losses. The baseline already refuses to bless a prompt change on vibes here,
because the task hands it both output files and asks for a go/no-go, so the
obvious move is to compare them. The Skill arm spent turns building the golden-set
scaffolding the instructions call for, and in this run that structure did not buy
a better answer than just doing the comparison. The hard-check score also fell,
0.83 to 0.69.

That is one task and four pairs, so it is weak evidence either way. It is reported
because it happened.

## The Skill is not free

The Skill arm took about 27% more turns and 24% more model spend per attempt.
Reproducing a symptom before acting costs something. On the two tasks where the
diagnosis was wrong without it, that was a good trade. On the third it was not.

## Method

- Agent: Claude Sonnet 4.5, in an isolated e2b sandbox per attempt, with file and
  shell access and no network to the outside.
- Grader: Claude Sonnet 4.6, scoring against a per-task rubric written before the
  run, and separately choosing a preferred transcript in each pair. Pair order is
  shuffled and both orders are voted, so a grader that simply prefers the first
  transcript shows up as a disagreement rather than as a win.
- Hard checks: a `check.py` per task, run on the host after the sandbox closes, on
  the files the agent wrote. It does not see the transcript and the grader does not
  see it.
- Arms: `skill` loads `SKILL.md` into the system prompt. `base` is the identical
  harness with nothing loaded. No other difference.
- Cost of the run: $21.82.

## What this does not claim

No comparison against any other Skill, product or framework. No claim that the
Skill improves a real production agent, only that it changed what the model did on
these three tasks. One run, one agent model, one grader model, twelve pairs. The
confidence interval is wide and includes zero.
