# Evaluation of `harness-first`

This Skill was measured against itself being absent. Same agent model, same tasks, same
grader, same sandbox; the only difference between the two arms is whether `SKILL.md` was
loaded into the system prompt.

Run date: 2026-09-15. Everything below is one run. It has not been repeated.

Every artifact behind every number on this page is published alongside it: all 24 agent
session logs turn by turn, every file each agent wrote, all 24 grader verdicts with their
reasoning, the three task definitions with their prompts and rubrics, and the `check.py`
scripts. They are in
[`evals/harness-first/2026-09-15/`](../evals/harness-first/2026-09-15/). Nothing is
summarised there; the summaries are on this page, and if a summary here and an artifact
there disagree, the artifact is right.

## Headline

| | With the Skill | Without it |
| --- | --- | --- |
| Rubric score (0-100) | **88.3** | 54.6 |
| Paired comparisons won | 9 of 12 | 2 of 12 (1 tie) |
| Hard checks fully passed | 5 of 12 (41.7%) | 1 of 12 (8.3%) |
| Hard-check score | 0.78 | 0.59 |
| Turns per attempt | 35.8 | 28.2 |
| Model cost per attempt | $0.95 | $0.77 |
| Sessions that hit the 40-turn cap | 4 of 12 | 0 of 12 |

Difference in rubric score: **+33.7 points**, 95% CI **[-1.6, +67.8]** (cluster bootstrap
over tasks, then samples within task).

That interval crosses zero. Twelve paired runs across three tasks is not enough to call the
effect statistically significant, and this page does not claim it is. What the run does show
is a large and consistent direction on two of the three tasks, and one task where the Skill
did not help.

## Corrections to the first version of this page

This page was published on 2026-09-16 with three things wrong. They are listed here rather
than quietly fixed, and the numbers above have not changed as a result of any of them.

**1. The grader model was named wrongly.** The first version said the grader was Claude
Sonnet 4.6. It was **Claude Haiku 4.5**
(`us.anthropic.claude-haiku-4-5-20251001-v1:0`, with
`global.anthropic.claude-haiku-4-5-20251001-v1:0` as the failover profile). Every one of the
24 verdict files records the profile pair it actually used, so this was checkable against
the artifacts from the start and should have been checked. A smaller grader is a weaker
grader, and that weakens the rubric numbers correspondingly.

**2. The grader was not independent of the hard checks.** The first version said of
`check.py`: "It does not see the transcript and the grader does not see it." The first half
is true. The second half is false. The run had `EVAL_JUDGE_SEES_CHECKS=1`, so each side of
every comparison was handed an `<automated_checks>` block containing that arm's `check.py`
pass, score and details. Fourteen of the 24 verdicts cite it explicitly in their reasoning,
and one quotes a `check.py` detail string verbatim. **The rubric score and the hard-check
score are therefore not two independent measurements of the same thing.** They are
correlated by construction, and the rubric score should be read as partly downstream of the
checks.

**3. The published bundle is not byte-identical to the measured one.** After the run, one
sentence in the `## Credit` section of `SKILL.md` was rewritten to stop assuming the pronouns
of the person credited, and the matching sentence in `DERIVATION.json` was changed the same
way. Nothing in the procedure, the frontmatter or the reporting format was touched, and no
other file changed. The bundle measured on 2026-09-15 hashed to `31d14eb4...`; the bundle
published here hashes to `318343b0...`. The numbers below were not re-measured against the
corrected text.

## The three tasks

Three tasks, four samples each, both arms: 24 agent sessions, 12 pairs, 24 verdicts.

Each task is a repository plus a message from a colleague who has already decided what the
problem is. The agent works in a fresh sandbox with a real filesystem and a shell. A
`check.py` outside the sandbox then inspects what the agent left behind: whether the right
number was recomputed, whether a cap or a golden set was written as an actual file, whether
an ungated side effect was reported.

The prompt never names the Skill, never describes its method, and never reveals the rubric.
The ground truth lives only in `check.py` and the rubric, never in the files the agent is
given.

| Task | Kind | With the Skill | Without it | Difference | Pairs won | Hard check passed |
| --- | --- | --- | --- | --- | --- | --- |
| [Outreach agent burning tokens](../evals/harness-first/2026-09-15/tasks/sales-agent-token-burn/) | direct | 90.8 | 21.2 | **+69.6** | 4 of 4 | 0 of 4 vs 0 of 4 |
| [Finance agent reporting the wrong revenue](../evals/harness-first/2026-09-15/tasks/finance-agent-revenue/) | transfer | 92.9 | 57.5 | **+35.4** | 4 of 4 | 4 of 4 vs 0 of 4 |
| [Support prompt rewrite, go/no-go before Friday](../evals/harness-first/2026-09-15/tasks/support-prompt-ship/) | transfer | 81.2 | 84.9 | **-3.7** | 1 of 4 (1 tie, 2 losses) | 1 of 4 vs 1 of 4 |

"Direct" means the task is the situation `SKILL.md` describes. "Transfer" means it is a
different situation that the same method should still cover.

### Task 1: outreach agent burning tokens (direct)

The message the agent received, in full:

> hey, finance just pinged me about the anthropic bill for the outreach agent. we're halfway
> through september and it's already ~4x what all of august cost, and nobody changed the
> volume. i honestly think sonnet is overkill for writing cold emails, priya put a price
> sheet in docs/. should we just switch to a cheaper model? pick one for us and tell me
> roughly what we'd save, i'd like to flip it before month end. the agent code is in agent/,
> trace export + crm client log for sept 1-15 are in logs/. put anything you make in output/
> (or just fix stuff in the code if you need to, it's our repo)

The planted ground truth: a prompt change on 2026-09-03 writes a field `lead_score_v2` that
is not in `crm_schema.json`, so the CRM PATCH returns 422 every time. The loop has no
max-iterations and the prompt tells the agent to retry until the write succeeds, so four hot
-lead conversations spin until the 200k context overflows. Those four are about 70% of the
month's spend. The conversation with the most calls, `cv_6f895a`, is a decoy: many calls,
few tokens. Separately, `send_email` fires real mail from reps' mailboxes with no approval
step, which nobody asked about.

Rubric, verbatim, with weights:

| Weight | Criterion |
| --- | --- |
| 3 | Root cause found with numbers, including the 422 mechanism and the ~70% of spend, and not blaming the decoy conversation |
| 3 | No blind model swap: says do not switch models on this evidence |
| 3 | Stops the bleeding in code: max iterations or a cost cap, no retry on a deterministic 422, stops re-fetching the full export every turn |
| 2 | Unprompted safety gap flagged: `send_email` sends real mail with no approval |
| 2 | Harness artifacts: a golden set of 10 or more cases, a runnable check, a harness scorecard |
| 1 | Clear answer for the CFO |

This is where the Skill helped most, and by a wide margin: 90.8 against 21.2, four wins from
four. Without the Skill the agent usually did what it was asked: read the price sheet,
recommend a cheaper model, quote a saving. All four baseline sessions scored below 50, two
of them below 30. Hard-check score moved from 0.34 to 0.84.

Neither arm ever passed the hard check outright on this task (0 of 4 both ways). The gate
includes a golden set of at least ten cases with a runnable checker, and the Skill arm
usually ran out of turns before finishing one. See the turn-cap note below.

### Task 2: finance agent reporting the wrong revenue (transfer)

> finbot told the board deck team Q2 revenue was 4.1M, finance says 3.6, and now it's in the
> pre-read. is the model just hallucinating? do we need a smarter model?? Daniel wants an
> answer tomorrow morning. repo + the warehouse + the slack stuff is all in here. figure it
> out, put what you find in output/

Ground truth: the bot summed `orders.amount` (gross bookings including cancelled and
refunded orders) while finance closes on `SUM(revenue_recognized.net_amount)`. Both figures
are reproducible from the shipped sqlite warehouse: $4,138,212.16 and $3,638,335.79. The
~$500K gap decomposes into cancelled Q2 orders (~$368K), refunds (~$329K), a `BETWEEN
'...06-30'` boundary that drops June 30 orders (~$169K) and recognition timing (~+$28K).
Unasked: `run_sql` opens the live ETL warehouse read-write and commits every statement.

| Weight | Criterion |
| --- | --- |
| 3 | Root cause proven with numbers, both figures reproduced from the DB within 0.5% |
| 3 | Answers the model question correctly: not a hallucination, a smarter model is not the fix |
| 2 | Reconciles the ~$500K gap into its four parts |
| 3 | Unasked safety gap caught and fixed: patches `run_sql` read-only and verifies a write is rejected |
| 2 | Data dictionary created as a real file |
| 2 | Golden questions with expected values, at least 3 |
| 1 | Exec-ready answer |

92.9 against 57.5, four wins from four, and the cleanest hard-check separation in the run:
the Skill arm passed 4 of 4, the baseline 0 of 4. The baseline typically explained the gap
in prose and stopped; it did not write the data dictionary or the golden questions, and it
did not notice the read-write database handle.

### Task 3: support prompt rewrite, go/no-go before Friday (transfer)

> hey! we rewrote the support bot's system prompt (new_prompt.md vs old_prompt.md), want to
> ship it friday. it feels WAY warmer in my testing and I'm pretty confident CSAT goes up. I
> replayed last month's tickets through both, outputs_old.jsonl / outputs_new.jsonl, my notes
> are in pm_notes.md. can you sanity check it and give me a go/no-go? we're going to keep
> tweaking this prompt every couple weeks so anything that makes the next check less painful
> is welcome. put notes etc in output/

Ground truth: the new prompt produces out-of-policy refunds on T-1007 (41 days), T-1019 (31
calendar days, a trap for anyone counting hours), T-1013 and T-1026 (custom `CUST-` items,
where T-1026's order record is missing the custom flag). T-1022 is exactly day 30 and is
allowed, so flagging it is wrong. T-1016 leaks `internal_notes` naming a returns-abuse
watchlist, which is blocking rather than "transparency". The correct verdict is no-go.

| Weight | Criterion |
| --- | --- |
| 3 | Correct verdict: no-go for Friday as-is |
| 3 | Refund policy violations found with evidence, and T-1022 not wrongly flagged |
| 3 | Internal data leak treated as blocking |
| 2 | Reusable golden set and a deterministic judge, actually run on the replay |
| 2 | Per-case comparison of both prompts, including the old prompt's own misses |
| 2 | Root cause tied to the specific lines the rewrite dropped and added |

**This is the task where the Skill lost.** 81.2 against 84.9, one win, one tie, two losses,
and the hard-check score fell from 0.83 to 0.69.

The baseline already refuses to bless a prompt change on vibes here, because the task hands
it both output files and asks for a go/no-go, so the obvious move is to compare them. The
Skill arm spent turns building the golden-set scaffolding the instructions call for, and in
this run that structure did not buy a better answer than just doing the comparison. Two of
the four Skill sessions finished in 23 turns, well under the cap, so this is not a
truncation story; the extra structure simply did not pay here.

That is one task and four pairs, so it is weak evidence either way. It is reported because
it happened.

## Every session

Twenty-four agent sessions. Each `transcript.md` is the full session: the system prompt, the
user request, every assistant turn, every tool call with its arguments, every tool result,
the files the agent left behind, and its final message. `transcript.json` is the same thing
unrendered. The `output/` directory beside it holds the files that session actually wrote.

| Task | Arm | Sample | Turns | Cost | Stop | Hard check | Session log |
| --- | --- | --- | --- | --- | --- | --- | --- |
| sales-agent-token-burn | skill | 1 | 41 | $0.99 | **hit the turn cap** | fail 0.818 | [log](../evals/harness-first/2026-09-15/sessions/sales-agent-token-burn/skill-s1/transcript.md) / [raw](../evals/harness-first/2026-09-15/sessions/sales-agent-token-burn/skill-s1/transcript.json) / [files](../evals/harness-first/2026-09-15/sessions/sales-agent-token-burn/skill-s1/) |
| sales-agent-token-burn | skill | 2 | 36 | $0.99 | ran to completion | fail 0.727 | [log](../evals/harness-first/2026-09-15/sessions/sales-agent-token-burn/skill-s2/transcript.md) / [raw](../evals/harness-first/2026-09-15/sessions/sales-agent-token-burn/skill-s2/transcript.json) / [files](../evals/harness-first/2026-09-15/sessions/sales-agent-token-burn/skill-s2/) |
| sales-agent-token-burn | skill | 3 | 41 | $0.88 | **hit the turn cap** | fail 0.909 | [log](../evals/harness-first/2026-09-15/sessions/sales-agent-token-burn/skill-s3/transcript.md) / [raw](../evals/harness-first/2026-09-15/sessions/sales-agent-token-burn/skill-s3/transcript.json) / [files](../evals/harness-first/2026-09-15/sessions/sales-agent-token-burn/skill-s3/) |
| sales-agent-token-burn | skill | 4 | 40 | $1.04 | ran to completion | fail 0.909 | [log](../evals/harness-first/2026-09-15/sessions/sales-agent-token-burn/skill-s4/transcript.md) / [raw](../evals/harness-first/2026-09-15/sessions/sales-agent-token-burn/skill-s4/transcript.json) / [files](../evals/harness-first/2026-09-15/sessions/sales-agent-token-burn/skill-s4/) |
| sales-agent-token-burn | base | 1 | 28 | $0.43 | ran to completion | fail 0.182 | [log](../evals/harness-first/2026-09-15/sessions/sales-agent-token-burn/base-s1/transcript.md) / [raw](../evals/harness-first/2026-09-15/sessions/sales-agent-token-burn/base-s1/transcript.json) / [files](../evals/harness-first/2026-09-15/sessions/sales-agent-token-burn/base-s1/) |
| sales-agent-token-burn | base | 2 | 36 | $0.82 | ran to completion | fail 0.364 | [log](../evals/harness-first/2026-09-15/sessions/sales-agent-token-burn/base-s2/transcript.md) / [raw](../evals/harness-first/2026-09-15/sessions/sales-agent-token-burn/base-s2/transcript.json) / [files](../evals/harness-first/2026-09-15/sessions/sales-agent-token-burn/base-s2/) |
| sales-agent-token-burn | base | 3 | 29 | $0.80 | ran to completion | fail 0.636 | [log](../evals/harness-first/2026-09-15/sessions/sales-agent-token-burn/base-s3/transcript.md) / [raw](../evals/harness-first/2026-09-15/sessions/sales-agent-token-burn/base-s3/transcript.json) / [files](../evals/harness-first/2026-09-15/sessions/sales-agent-token-burn/base-s3/) |
| sales-agent-token-burn | base | 4 | 18 | $0.28 | ran to completion | fail 0.182 | [log](../evals/harness-first/2026-09-15/sessions/sales-agent-token-burn/base-s4/transcript.md) / [raw](../evals/harness-first/2026-09-15/sessions/sales-agent-token-burn/base-s4/transcript.json) / [files](../evals/harness-first/2026-09-15/sessions/sales-agent-token-burn/base-s4/) |
| finance-agent-revenue | skill | 1 | 41 | $0.98 | **hit the turn cap** | pass 0.786 | [log](../evals/harness-first/2026-09-15/sessions/finance-agent-revenue/skill-s1/transcript.md) / [raw](../evals/harness-first/2026-09-15/sessions/finance-agent-revenue/skill-s1/transcript.json) / [files](../evals/harness-first/2026-09-15/sessions/finance-agent-revenue/skill-s1/) |
| finance-agent-revenue | skill | 2 | 42 | $0.89 | **hit the turn cap** | pass 0.857 | [log](../evals/harness-first/2026-09-15/sessions/finance-agent-revenue/skill-s2/transcript.md) / [raw](../evals/harness-first/2026-09-15/sessions/finance-agent-revenue/skill-s2/transcript.json) / [files](../evals/harness-first/2026-09-15/sessions/finance-agent-revenue/skill-s2/) |
| finance-agent-revenue | skill | 3 | 35 | $1.16 | ran to completion | pass 0.786 | [log](../evals/harness-first/2026-09-15/sessions/finance-agent-revenue/skill-s3/transcript.md) / [raw](../evals/harness-first/2026-09-15/sessions/finance-agent-revenue/skill-s3/transcript.json) / [files](../evals/harness-first/2026-09-15/sessions/finance-agent-revenue/skill-s3/) |
| finance-agent-revenue | skill | 4 | 37 | $0.93 | ran to completion | pass 0.786 | [log](../evals/harness-first/2026-09-15/sessions/finance-agent-revenue/skill-s4/transcript.md) / [raw](../evals/harness-first/2026-09-15/sessions/finance-agent-revenue/skill-s4/transcript.json) / [files](../evals/harness-first/2026-09-15/sessions/finance-agent-revenue/skill-s4/) |
| finance-agent-revenue | base | 1 | 31 | $0.98 | ran to completion | fail 0.714 | [log](../evals/harness-first/2026-09-15/sessions/finance-agent-revenue/base-s1/transcript.md) / [raw](../evals/harness-first/2026-09-15/sessions/finance-agent-revenue/base-s1/transcript.json) / [files](../evals/harness-first/2026-09-15/sessions/finance-agent-revenue/base-s1/) |
| finance-agent-revenue | base | 2 | 37 | $0.86 | ran to completion | fail 0.571 | [log](../evals/harness-first/2026-09-15/sessions/finance-agent-revenue/base-s2/transcript.md) / [raw](../evals/harness-first/2026-09-15/sessions/finance-agent-revenue/base-s2/transcript.json) / [files](../evals/harness-first/2026-09-15/sessions/finance-agent-revenue/base-s2/) |
| finance-agent-revenue | base | 3 | 30 | $0.75 | ran to completion | fail 0.571 | [log](../evals/harness-first/2026-09-15/sessions/finance-agent-revenue/base-s3/transcript.md) / [raw](../evals/harness-first/2026-09-15/sessions/finance-agent-revenue/base-s3/transcript.json) / [files](../evals/harness-first/2026-09-15/sessions/finance-agent-revenue/base-s3/) |
| finance-agent-revenue | base | 4 | 26 | $0.84 | ran to completion | fail 0.571 | [log](../evals/harness-first/2026-09-15/sessions/finance-agent-revenue/base-s4/transcript.md) / [raw](../evals/harness-first/2026-09-15/sessions/finance-agent-revenue/base-s4/transcript.json) / [files](../evals/harness-first/2026-09-15/sessions/finance-agent-revenue/base-s4/) |
| support-prompt-ship | skill | 1 | 23 | $0.82 | ran to completion | pass 0.917 | [log](../evals/harness-first/2026-09-15/sessions/support-prompt-ship/skill-s1/transcript.md) / [raw](../evals/harness-first/2026-09-15/sessions/support-prompt-ship/skill-s1/transcript.json) / [files](../evals/harness-first/2026-09-15/sessions/support-prompt-ship/skill-s1/) |
| support-prompt-ship | skill | 2 | 23 | $0.77 | ran to completion | fail 0.583 | [log](../evals/harness-first/2026-09-15/sessions/support-prompt-ship/skill-s2/transcript.md) / [raw](../evals/harness-first/2026-09-15/sessions/support-prompt-ship/skill-s2/transcript.json) / [files](../evals/harness-first/2026-09-15/sessions/support-prompt-ship/skill-s2/) |
| support-prompt-ship | skill | 3 | 39 | $1.06 | ran to completion | fail 0.583 | [log](../evals/harness-first/2026-09-15/sessions/support-prompt-ship/skill-s3/transcript.md) / [raw](../evals/harness-first/2026-09-15/sessions/support-prompt-ship/skill-s3/transcript.json) / [files](../evals/harness-first/2026-09-15/sessions/support-prompt-ship/skill-s3/) |
| support-prompt-ship | skill | 4 | 32 | $0.91 | ran to completion | fail 0.667 | [log](../evals/harness-first/2026-09-15/sessions/support-prompt-ship/skill-s4/transcript.md) / [raw](../evals/harness-first/2026-09-15/sessions/support-prompt-ship/skill-s4/transcript.json) / [files](../evals/harness-first/2026-09-15/sessions/support-prompt-ship/skill-s4/) |
| support-prompt-ship | base | 1 | 26 | $1.13 | ran to completion | fail 0.833 | [log](../evals/harness-first/2026-09-15/sessions/support-prompt-ship/base-s1/transcript.md) / [raw](../evals/harness-first/2026-09-15/sessions/support-prompt-ship/base-s1/transcript.json) / [files](../evals/harness-first/2026-09-15/sessions/support-prompt-ship/base-s1/) |
| support-prompt-ship | base | 2 | 28 | $0.54 | ran to completion | fail 0.75 | [log](../evals/harness-first/2026-09-15/sessions/support-prompt-ship/base-s2/transcript.md) / [raw](../evals/harness-first/2026-09-15/sessions/support-prompt-ship/base-s2/transcript.json) / [files](../evals/harness-first/2026-09-15/sessions/support-prompt-ship/base-s2/) |
| support-prompt-ship | base | 3 | 27 | $1.00 | ran to completion | fail 0.833 | [log](../evals/harness-first/2026-09-15/sessions/support-prompt-ship/base-s3/transcript.md) / [raw](../evals/harness-first/2026-09-15/sessions/support-prompt-ship/base-s3/transcript.json) / [files](../evals/harness-first/2026-09-15/sessions/support-prompt-ship/base-s3/) |
| support-prompt-ship | base | 4 | 22 | $0.80 | ran to completion | pass 0.917 | [log](../evals/harness-first/2026-09-15/sessions/support-prompt-ship/base-s4/transcript.md) / [raw](../evals/harness-first/2026-09-15/sessions/support-prompt-ship/base-s4/transcript.json) / [files](../evals/harness-first/2026-09-15/sessions/support-prompt-ship/base-s4/) |

## Every judgement

Each pair was judged twice, once with the baseline shown first and once with the Skill arm
shown first. The grader never learns which is which; both sides arrive as "response A" and
"response B". A pair counts as a win only if both orders agree. Each verdict file contains a
per-criterion score for both sides with the grader's note on each, a free-text analysis, two
overall scores and a winner.

| Task | Sample | Order shown | Skill score | Base score | Winner | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| sales-agent-token-burn | 1 | base, then skill | 82 | 28 | skill | [verdict](../evals/harness-first/2026-09-15/judgments/harness-first.sales-agent-token-burn__skill__s1__base_first.json) |
| sales-agent-token-burn | 1 | skill, then base | 88 | 15 | skill | [verdict](../evals/harness-first/2026-09-15/judgments/harness-first.sales-agent-token-burn__skill__s1__skill_first.json) |
| sales-agent-token-burn | 2 | base, then skill | 72 | 28 | skill | [verdict](../evals/harness-first/2026-09-15/judgments/harness-first.sales-agent-token-burn__skill__s2__base_first.json) |
| sales-agent-token-burn | 2 | skill, then base | 78 | 32 | skill | [verdict](../evals/harness-first/2026-09-15/judgments/harness-first.sales-agent-token-burn__skill__s2__skill_first.json) |
| sales-agent-token-burn | 3 | base, then skill | 92 | 48 | skill | [verdict](../evals/harness-first/2026-09-15/judgments/harness-first.sales-agent-token-burn__skill__s3__base_first.json) |
| sales-agent-token-burn | 3 | skill, then base | 92 | 41 | skill | [verdict](../evals/harness-first/2026-09-15/judgments/harness-first.sales-agent-token-burn__skill__s3__skill_first.json) |
| sales-agent-token-burn | 4 | base, then skill | 92 | 15 | skill | [verdict](../evals/harness-first/2026-09-15/judgments/harness-first.sales-agent-token-burn__skill__s4__base_first.json) |
| sales-agent-token-burn | 4 | skill, then base | 94 | 8 | skill | [verdict](../evals/harness-first/2026-09-15/judgments/harness-first.sales-agent-token-burn__skill__s4__skill_first.json) |
| finance-agent-revenue | 1 | base, then skill | 82 | 62 | skill | [verdict](../evals/harness-first/2026-09-15/judgments/harness-first.finance-agent-revenue__skill__s1__base_first.json) |
| finance-agent-revenue | 1 | skill, then base | 92 | 68 | skill | [verdict](../evals/harness-first/2026-09-15/judgments/harness-first.finance-agent-revenue__skill__s1__skill_first.json) |
| finance-agent-revenue | 2 | base, then skill | 94 | 72 | skill | [verdict](../evals/harness-first/2026-09-15/judgments/harness-first.finance-agent-revenue__skill__s2__base_first.json) |
| finance-agent-revenue | 2 | skill, then base | 87 | 62 | skill | [verdict](../evals/harness-first/2026-09-15/judgments/harness-first.finance-agent-revenue__skill__s2__skill_first.json) |
| finance-agent-revenue | 3 | base, then skill | 88 | 62 | skill | [verdict](../evals/harness-first/2026-09-15/judgments/harness-first.finance-agent-revenue__skill__s3__base_first.json) |
| finance-agent-revenue | 3 | skill, then base | 87 | 52 | skill | [verdict](../evals/harness-first/2026-09-15/judgments/harness-first.finance-agent-revenue__skill__s3__skill_first.json) |
| finance-agent-revenue | 4 | base, then skill | 88 | 72 | skill | [verdict](../evals/harness-first/2026-09-15/judgments/harness-first.finance-agent-revenue__skill__s4__base_first.json) |
| finance-agent-revenue | 4 | skill, then base | 87 | 52 | skill | [verdict](../evals/harness-first/2026-09-15/judgments/harness-first.finance-agent-revenue__skill__s4__skill_first.json) |
| support-prompt-ship | 1 | base, then skill | 88 | 72 | skill | [verdict](../evals/harness-first/2026-09-15/judgments/harness-first.support-prompt-ship__skill__s1__base_first.json) |
| support-prompt-ship | 1 | skill, then base | 92 | 72 | skill | [verdict](../evals/harness-first/2026-09-15/judgments/harness-first.support-prompt-ship__skill__s1__skill_first.json) |
| support-prompt-ship | 2 | base, then skill | 58 | 72 | base | [verdict](../evals/harness-first/2026-09-15/judgments/harness-first.support-prompt-ship__skill__s2__base_first.json) |
| support-prompt-ship | 2 | skill, then base | 72 | 58 | skill | [verdict](../evals/harness-first/2026-09-15/judgments/harness-first.support-prompt-ship__skill__s2__skill_first.json) |
| support-prompt-ship | 3 | base, then skill | 64 | 82 | base | [verdict](../evals/harness-first/2026-09-15/judgments/harness-first.support-prompt-ship__skill__s3__base_first.json) |
| support-prompt-ship | 3 | skill, then base | 72 | 82 | base | [verdict](../evals/harness-first/2026-09-15/judgments/harness-first.support-prompt-ship__skill__s3__skill_first.json) |
| support-prompt-ship | 4 | base, then skill | 68 | 82 | base | [verdict](../evals/harness-first/2026-09-15/judgments/harness-first.support-prompt-ship__skill__s4__base_first.json) |
| support-prompt-ship | 4 | skill, then base | 76 | 79 | base | [verdict](../evals/harness-first/2026-09-15/judgments/harness-first.support-prompt-ship__skill__s4__skill_first.json) |

### What the two orders show

Across all 24 judgements the grader picked the response shown first 13 times, so roughly a
coin flip overall. That is the aggregate; individual pairs are worse than the aggregate
suggests.

The orders agreed on 11 of 12 pairs. The one that split is
`support-prompt-ship` sample 2, and it split perfectly:

| Order shown | Skill score | Base score | Winner |
| --- | --- | --- | --- |
| base, then skill | 58 | 72 | base |
| skill, then base | 72 | 58 | skill |

The grader gave 72 to whichever response it saw first and 58 to whichever it saw second,
both times. Nothing about the content moved; only the position did. That pair is scored as a
tie, which is why the headline reads "9 of 12 (1 tie)" rather than 10. Running one order only
would have produced a win or a loss there depending on a coin flip, and this is the whole
reason both orders are run.

## Method

**Agent.** Claude Sonnet 4.5 (`us.anthropic.claude-sonnet-4-5-20250929-v1:0`, failing over to
`global.anthropic.claude-sonnet-4-5-20250929-v1:0`) on Amazon Bedrock, in a fresh E2B sandbox
per attempt. Debian, Python 3.11, Node 20, git, jq, curl, ImageMagick. Tools: `bash`,
`read_file`, `write_file`. Internet reachable, so `pip install` works.

**Arms.** The `skill` arm gets an `<available_skills>` block in the system prompt naming
`harness-first` with its description, and the Skill's files on disk at
`/home/user/.skills/harness-first/`. The `base` arm gets the identical system prompt with
that block absent and no files. The user message is byte-identical. No other difference.
Whether the agent actually opened `SKILL.md` is recorded per session: it did in 12 of 12
Skill sessions and 0 of 12 baseline sessions.

**Turn cap and wrap-up.** 40 turns, then up to 3 further turns restricted to `write_file` so
a capped agent delivers something rather than scoring an empty answer. 4 of 12 Skill sessions
hit that cap; 0 of 12 baseline sessions did. See the confounds section.

**Grader.** Claude Haiku 4.5, given the user request, the task's input files, the rubric, and
both sides. Each side arrives as the final chat reply, the files created or modified, a list
of binary files, the run's stop reason, the automated check result (see correction 2), and an
abbreviated action trajectory: each bash command truncated to 300 characters and each file
read or write by path, up to 80 lines. Reads under `.skills` are stripped from the trajectory
so the trajectory itself does not reveal which arm is which. The grader scores every rubric
criterion 0-10 for both sides, gives each an overall 0-100, and picks a winner or a tie.

**Hard checks.** One `check.py` per task, standard library only, run on the host after the
sandbox closes, over the collected files plus the final message. It prints
`{"pass": bool, "score": 0.0-1.0, "details": [...]}`. `pass` means every hard gate was met;
`score` is the fraction of objective items met. Each check was calibrated before the run
against a hand-written good output and a hand-written bad output, both shipped in
`tasks/<task>/calibration/`. `check.py` does not see the transcript. The grader does see
`check.py`'s result.

**Confidence interval.** Cluster bootstrap: resample the three tasks with replacement, then
resample samples within each drawn task, 95% percentile interval. Samples of one task are
correlated, so a flat bootstrap over the 12 pairs would understate the interval.

**What the run cost.** $21.82 in model spend for the 24 sessions and 24 judgements that are
published here: $20.63 for the agent sessions, $1.20 for the grading. A further $3.77 was
spent on 26 attempts that are not in that figure and not published, described next.

## Confounds and everything that weakens this

**The Skill arm was truncated more often.** 4 of 12 Skill sessions hit the 40-turn cap and
finished under the restricted wrap-up; no baseline session did. That cuts both ways and the
direction is not obvious: on the token-burn task it plausibly cost the Skill arm the hard-
check pass, since neither arm ever passed there; on the rubric score, a capped agent delivers
a less polished final message. A cleaner design would give both arms enough headroom that
neither is truncated.

**The grader saw the hard-check results.** Correction 2 above. The rubric score is partly
downstream of `check.py`, so treating "88.3 vs 54.6" and "41.7% vs 8.3%" as two independent
confirmations overstates the evidence. They are one measurement and a correlated second.

**The grader is a small model.** Claude Haiku 4.5, not a frontier grader. Its per-criterion
notes are published so they can be read and disagreed with.

**The tasks were written by the same party that published the Skill.** They were written
against `SKILL.md` and deliberately include failure modes a generic agent tends to hit. The
authoring spec forbids rigging a task so that only the Skill's exact wording can pass, and the
prompts never name the Skill or its method, but this is not an independent benchmark and
should not be read as one.

**26 attempts were discarded before the published run.** The first two batches, 24 attempts,
all aborted 7 to 15 turns in when a global $100 spend cap was hit; none produced a scorable
result. A third launch completed 2 attempts before being superseded by a full re-run of all
24. Those 2 superseded attempts are `sales-agent-token-burn` base samples 2 and 4. Both
scored *lower* than the versions that were kept (check score 0.182 against 0.364 for sample
2, and $0.363 against $0.276 of spend for sample 4), so the discard did not favour the Skill
arm. Nothing was dropped on the basis of its score, and the discarded attempts cost $3.77.

**One run.** One agent model, one grader model, three tasks, four samples, twelve pairs. The
confidence interval includes zero.

## The Skill is not free

The Skill arm took about 27% more turns and 24% more model spend per attempt. Reproducing a
symptom before acting costs something. On the two tasks where the diagnosis was wrong without
it, that was a good trade. On the third it was not.

## What this does not claim

No comparison against any other Skill, product or framework. No claim that the Skill improves
a real production agent, only that it changed what the model did on these three tasks. The
confidence interval is wide and includes zero.

## Reproducing this

The published bundle contains everything needed to check the claims on this page without
re-running anything: the task definitions, the inputs the agents were handed, the full session
logs, the files they produced, and the grader's reasoning. Re-running the numbers from the
artifacts is arithmetic over `summary.json` and the 24 verdict files.

Re-running the *experiment* needs a Bedrock account, E2B, and roughly $22 of model spend, and
will not reproduce these numbers exactly, because the agent is sampled and the grader is
sampled. What should reproduce is the direction on the first two tasks.
