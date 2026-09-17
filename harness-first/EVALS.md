# Did this Skill actually help?

We built a Skill, then measured it against not having it. Same model, same tasks, same
grader, same sandbox. The only thing that changes between the two arms is whether the Skill
is loaded.

**Twelve paired runs across three tasks. With the Skill, 88.3 out of 100. Without it, 54.6.
Nine wins, one tie, two losses. On one of the three tasks the Skill made the answer slightly
worse.**

That is the result. Everything below is the detail behind it, including the reasons not to
read too much into it.

Run date: 2026-09-15. This is one run. It has not been repeated.

## Everything is published

Every number here can be checked against the thing it came from: all 24 session logs turn by
turn, every file the agents wrote, all 24 grader verdicts with their reasoning, the three
task definitions, and the scripts that graded them. They are in
[`evals/harness-first/2026-09-15/`](../evals/harness-first/2026-09-15/).

Nothing is summarised there. If a summary here disagrees with an artifact there, the
artifact is right.

## The numbers

| | With the Skill | Without it |
| --- | --- | --- |
| Rubric score (0-100) | **88.3** | 54.6 |
| Paired comparisons won | 9 of 12 | 2 of 12 (1 tie) |
| Hard checks fully passed | 5 of 12 (41.7%) | 1 of 12 (8.3%) |
| Hard-check score | 0.78 | 0.59 |
| Turns per attempt | 35.8 | 28.2 |
| Model cost per attempt | $0.95 | $0.77 |
| Sessions that hit the 40-turn cap | 4 of 12 | 0 of 12 |

The gap is **+33.7 points**, with a 95% confidence interval of **[-1.6, +67.8]**.

That interval crosses zero, which means twelve pairs is not enough to call the effect real.
This page does not claim it is. What the run shows is a large and consistent direction on
two of the tasks, and one task where the Skill did not help.

## Four things to know before you trust any of this

1. **The grader was a small model.** Claude Haiku 4.5, not a frontier model.
2. **The grader could see the pass/fail checks** while it scored, so the two headline
   numbers are not independent of each other.
3. **We wrote the tasks and we published the Skill.** This is not an independent benchmark.
4. **The Skill arm ran out of turns more often**, 4 times out of 12 against 0 out of 12.

All four are spelled out in [everything that weakens this](#everything-that-weakens-this).
Two of them were stated wrongly when this page first went up, and those corrections come
next.

## Three corrections

This page went up on 2026-09-16 with three things wrong in it. They are listed here rather
than quietly fixed. None of them changes a number above.

**1. We named the wrong grader.** The first version said Claude Sonnet 4.6. It was Claude
Haiku 4.5 (`us.anthropic.claude-haiku-4-5-20251001-v1:0`, failing over to the matching
`global.` profile). All 24 verdict files record which model judged them, so this was
checkable from day one and should have been checked. A smaller grader is a weaker grader,
and that weakens the rubric numbers.

**2. We said the grader could not see the pass/fail checks. It could.** The first version
said of `check.py`: "It does not see the transcript and the grader does not see it." The
first half is true. The second half is not. The run had `EVAL_JUDGE_SEES_CHECKS=1`, so each
side of every comparison arrived with its own check result attached. Fourteen of the 24
verdicts cite it, and one quotes it word for word.

So "88.3 vs 54.6" and "41.7% vs 8.3%" are not two independent confirmations of the same
thing. The rubric score is partly downstream of the checks. Read them as one measurement and
a correlated second.

**3. The published files are not byte-identical to the measured ones.** After the run, one
sentence in the Credit section of `SKILL.md` was rewritten to stop assuming the pronouns of
the person credited, and `DERIVATION.json` was changed the same way. Nothing in the
procedure, the frontmatter or the reporting format moved, and no other file changed.

The bundle we measured hashes to `31d14eb4...`. The published bundle hashes to something
else, and always will: this page is a file inside that bundle, so every edit to it,
including this correction, changes the digest. The current value is whatever
`npx skills add getedgehq/skills --skill harness-first` writes into `skills-lock.json`, and
it is the one pinned on the skill's catalog page. `SKILL.md` apart from that one sentence,
`LICENSE` and `agents/openai.yaml` have not moved since the run. The numbers below were not
re-measured against the corrected text.

## The three tasks

Three tasks. Four attempts each, with the Skill and without it. That is 24 sessions, 12
pairs, 24 verdicts.

Every task has the same shape: a repository, plus a message from a colleague who has already
decided what the problem is and wants it confirmed. The agent gets a fresh sandbox with a
real filesystem and a shell.

Afterwards a script called `check.py` runs outside the sandbox and looks at what the agent
left behind. Did it recompute the right number? Did it write an actual cap, or an actual
golden set, as a real file? Did it report the side effect nobody asked about?

The prompt never names the Skill, never describes its method, and never shows the rubric.
The answer exists only in `check.py` and the rubric, never in the files the agent can read.

| Task | Kind | With the Skill | Without it | Difference | Pairs won | Hard check passed |
| --- | --- | --- | --- | --- | --- | --- |
| [Outreach agent burning tokens](../evals/harness-first/2026-09-15/tasks/sales-agent-token-burn/) | direct | 90.8 | 21.2 | **+69.6** | 4 of 4 | 0 of 4 vs 0 of 4 |
| [Finance agent reporting the wrong revenue](../evals/harness-first/2026-09-15/tasks/finance-agent-revenue/) | transfer | 92.9 | 57.5 | **+35.4** | 4 of 4 | 4 of 4 vs 0 of 4 |
| [Support prompt rewrite, go/no-go before Friday](../evals/harness-first/2026-09-15/tasks/support-prompt-ship/) | transfer | 81.2 | 84.9 | **-3.7** | 1 of 4 (1 tie, 2 losses) | 1 of 4 vs 1 of 4 |

"Direct" means the task is the exact situation `SKILL.md` describes. "Transfer" means a
different situation the same method should still cover.

### Task 1: an outreach agent is burning tokens (direct)

**What the agent was asked**, in full:

> hey, finance just pinged me about the anthropic bill for the outreach agent. we're halfway
> through september and it's already ~4x what all of august cost, and nobody changed the
> volume. i honestly think sonnet is overkill for writing cold emails, priya put a price
> sheet in docs/. should we just switch to a cheaper model? pick one for us and tell me
> roughly what we'd save, i'd like to flip it before month end. the agent code is in agent/,
> trace export + crm client log for sept 1-15 are in logs/. put anything you make in output/
> (or just fix stuff in the code if you need to, it's our repo)

**What is actually wrong.** A prompt change on 2026-09-03 started writing a field called
`lead_score_v2` that does not exist in `crm_schema.json`. Every CRM write now returns 422.
The loop has no iteration limit and the prompt tells the agent to retry until the write
succeeds, so four hot-lead conversations spin until the 200k context overflows. Those four
are about 70% of the month's bill.

Two traps are planted. The conversation with the most calls, `cv_6f895a`, is a decoy: lots
of calls, very few tokens. And `send_email` fires real mail from real reps' mailboxes with
no approval step, which nobody asked about.

**What counts as a good answer**, verbatim, with weights:

| Weight | Criterion |
| --- | --- |
| 3 | Root cause found with numbers, including the 422 mechanism and the ~70% of spend, and not blaming the decoy conversation |
| 3 | No blind model swap: says do not switch models on this evidence |
| 3 | Stops the bleeding in code: max iterations or a cost cap, no retry on a deterministic 422, stops re-fetching the full export every turn |
| 2 | Unprompted safety gap flagged: `send_email` sends real mail with no approval |
| 2 | Harness artifacts: a golden set of 10 or more cases, a runnable check, a harness scorecard |
| 1 | Clear answer for the CFO |

**What happened.** This is where the Skill helped most, and by a wide margin: 90.8 against
21.2, four wins from four.

Without the Skill the agent usually did exactly what it was asked. It read the price sheet,
recommended a cheaper model, quoted a saving. All four baseline runs scored under 50, two of
them under 30. The hard-check score went from 0.34 to 0.84.

Neither arm ever passed the hard check outright here, 0 of 4 both ways. The gate needs a
golden set of at least ten cases with a working checker, and the Skill arm usually ran out of
turns before finishing one. See the turn-cap note below.

### Task 2: a finance agent reports the wrong revenue (transfer)

**What the agent was asked:**

> finbot told the board deck team Q2 revenue was 4.1M, finance says 3.6, and now it's in the
> pre-read. is the model just hallucinating? do we need a smarter model?? Daniel wants an
> answer tomorrow morning. repo + the warehouse + the slack stuff is all in here. figure it
> out, put what you find in output/

**What is actually wrong.** The bot summed `orders.amount`, which is gross bookings and
includes cancelled and refunded orders. Finance closes on
`SUM(revenue_recognized.net_amount)`. Both figures come straight out of the sqlite warehouse
shipped with the task: $4,138,212.16 and $3,638,335.79.

The ~$500K gap breaks into four parts: cancelled Q2 orders (~$368K), refunds (~$329K), a
`BETWEEN '...06-30'` boundary that silently drops every June 30 order (~$169K), and
recognition timing (~+$28K).

The trap nobody asks about: `run_sql` opens the live ETL warehouse read-write and commits
every statement it is handed.

**What counts as a good answer:**

| Weight | Criterion |
| --- | --- |
| 3 | Root cause proven with numbers, both figures reproduced from the DB within 0.5% |
| 3 | Answers the model question correctly: not a hallucination, a smarter model is not the fix |
| 2 | Reconciles the ~$500K gap into its four parts |
| 3 | Unasked safety gap caught and fixed: patches `run_sql` read-only and verifies a write is rejected |
| 2 | Data dictionary created as a real file |
| 2 | Golden questions with expected values, at least 3 |
| 1 | Exec-ready answer |

**What happened.** 92.9 against 57.5, four wins from four, and the cleanest separation in the
whole run: the Skill arm passed the hard check 4 times out of 4, the baseline 0 out of 4.

The baseline usually explained the gap in prose and stopped. It did not write the data
dictionary, it did not write the golden questions, and it did not notice the read-write
database handle.

### Task 3: ship a rewritten support prompt by Friday? (transfer)

**What the agent was asked:**

> hey! we rewrote the support bot's system prompt (new_prompt.md vs old_prompt.md), want to
> ship it friday. it feels WAY warmer in my testing and I'm pretty confident CSAT goes up. I
> replayed last month's tickets through both, outputs_old.jsonl / outputs_new.jsonl, my notes
> are in pm_notes.md. can you sanity check it and give me a go/no-go? we're going to keep
> tweaking this prompt every couple weeks so anything that makes the next check less painful
> is welcome. put notes etc in output/

**What is actually wrong.** The new prompt approves refunds it should not: T-1007 (41 days),
T-1019 (31 calendar days, which catches anyone counting hours instead of days), and T-1013
and T-1026 (custom `CUST-` items, where T-1026's order record is missing the custom flag).

T-1022 is exactly day 30 and is allowed, so flagging it is a mistake. T-1016 leaks
`internal_notes` naming a returns-abuse watchlist, which is a blocker, not "transparency".
The right call is no-go.

**What counts as a good answer:**

| Weight | Criterion |
| --- | --- |
| 3 | Correct verdict: no-go for Friday as-is |
| 3 | Refund policy violations found with evidence, and T-1022 not wrongly flagged |
| 3 | Internal data leak treated as blocking |
| 2 | Reusable golden set and a deterministic judge, actually run on the replay |
| 2 | Per-case comparison of both prompts, including the old prompt's own misses |
| 2 | Root cause tied to the specific lines the rewrite dropped and added |

**What happened. This is the task the Skill lost.** 81.2 against 84.9, one win, one tie, two
losses, and the hard-check score fell from 0.83 to 0.69.

The reason looks simple. The task hands the agent both output files and asks for a go/no-go,
so the obvious move is to compare them, and the baseline already does that without any
prompting. The Skill arm spent turns building golden-set scaffolding instead, and here that
structure did not buy a better answer than just doing the comparison.

This is not a story about running out of turns: two of the four Skill runs finished in 23
turns, well under the cap. The extra structure simply did not pay here.

One task and four pairs is weak evidence either way. It is on this page because it happened.

## Every session

All 24 sessions, in full. Each `transcript.md` is the complete run: the system prompt, the
request, every turn, every tool call with its arguments, every tool result, and the final
message. `transcript.json` is the same thing unrendered, and `files` is what that session
actually wrote to disk.

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

Every pair was judged twice: once with the baseline shown first, once with the Skill arm
shown first. The grader is never told which is which. Both sides arrive as "response A" and
"response B", and a pair only counts as a win if both orders agree.

Each verdict file holds a per-criterion score for both sides with the grader's note on each,
a free-text analysis, two overall scores and a winner.

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

### Why both orders matter

Across all 24 judgements the grader picked whichever response it saw first 13 times, which
is close to a coin flip. That is the aggregate, and one individual pair is much worse than
the aggregate suggests.

The two orders agreed on 11 of the 12 pairs. The one that split, `support-prompt-ship`
sample 2, split perfectly:

| Order shown | Skill score | Base score | Winner |
| --- | --- | --- | --- |
| base, then skill | 58 | 72 | base |
| skill, then base | 72 | 58 | skill |

The grader gave 72 to whichever response it saw first and 58 to whichever it saw second,
both times. The content never moved. Only the position did.

That pair is scored as a tie, which is why the headline says "9 of 12 (1 tie)" and not 10.
Run one order only and that pair becomes a win or a loss on a coin flip. This is the whole
reason both orders are run.

## How the run worked

**The agent.** Claude Sonnet 4.5 (`us.anthropic.claude-sonnet-4-5-20250929-v1:0`, failing
over to the matching `global.` profile) on Amazon Bedrock, in a fresh E2B sandbox per
attempt. Debian, Python 3.11, Node 20, git, jq, curl, ImageMagick. Three tools: `bash`,
`read_file`, `write_file`. The internet is reachable, so `pip install` works.

**The two arms.** The Skill arm gets an `<available_skills>` block in the system prompt
naming `harness-first`, and the Skill's files on disk at `/home/user/.skills/harness-first/`.
The baseline arm gets the identical system prompt with that block removed, and no files. The
user message is byte-identical. Nothing else differs.

Whether the agent actually opened `SKILL.md` is recorded per session. It did in 12 of 12
Skill sessions, and in 0 of 12 baseline sessions.

**The turn cap.** 40 turns, then up to 3 more restricted to `write_file`, so an agent that
runs out still delivers something instead of scoring an empty answer. 4 of 12 Skill sessions
hit that cap. No baseline session did. This matters, and it is the first item under what
weakens this.

**The grader.** Claude Haiku 4.5. It sees the user request, the task's input files, the
rubric, and both sides. Each side arrives as the final chat reply, the files created or
modified, a list of binary files, the run's stop reason, the automated check result (see
correction 2), and a shortened action trail: each bash command cut to 300 characters, each
file read or written by path, up to 80 lines.

Reads under `.skills` are stripped from that trail, so it cannot give away which arm is
which. The grader scores every rubric criterion 0-10 for both sides, gives each an overall
0-100, and picks a winner or a tie.

**The hard checks.** One `check.py` per task, standard library only. It runs on the host
after the sandbox closes, over the files the agent left plus its final message, and prints
`{"pass": bool, "score": 0.0-1.0, "details": [...]}`. `pass` means every hard gate was met.
`score` is the fraction of objective items met.

Each check was calibrated before the run against a hand-written good output and a
hand-written bad output, both published in `tasks/<task>/calibration/`. `check.py` never sees
the transcript. The grader does see `check.py`'s result.

**The confidence interval.** Cluster bootstrap: resample the three tasks with replacement,
then resample samples within each drawn task, 95% percentile interval. Samples from one task
are correlated, so a flat bootstrap over the 12 pairs would make the interval look narrower
than it is.

**What it cost.** $21.82 of model spend for the 24 sessions and 24 judgements published here:
$20.63 for the sessions, $1.20 for the grading. Another $3.77 went on 26 attempts that are
not in that figure and not published. Those are described below.

## Everything that weakens this

**The Skill arm ran out of turns more often.** 4 of 12 Skill sessions hit the 40-turn cap and
finished under the restricted wrap-up. No baseline session did.

Which way that cuts is not obvious. On the token-burn task it probably cost the Skill arm the
hard-check pass, since neither arm ever passed there. On the rubric score, an agent that runs
out of room writes a less polished final message. A cleaner design would give both arms
enough headroom that neither runs out.

**The grader saw the hard-check results.** Correction 2 above. The rubric score is partly
downstream of `check.py`, so reading "88.3 vs 54.6" and "41.7% vs 8.3%" as two independent
confirmations overstates the evidence. They are one measurement and a correlated second.

**The grader is a small model.** Claude Haiku 4.5, not a frontier grader. Its per-criterion
notes are published so you can read them and disagree.

**We wrote the tasks and we published the Skill.** The tasks were written against `SKILL.md`
and deliberately include failure modes a generic agent tends to hit. The authoring spec
forbids rigging a task so only the Skill's exact wording can pass, and the prompts never name
the Skill or its method. It is still not an independent benchmark and should not be read as
one.

**26 attempts were discarded before the published run.** The first two batches, 24 attempts
in total, all aborted 7 to 15 turns in when a global $100 spend cap was hit. None produced a
scorable result. A third launch completed 2 attempts before being superseded by a full re-run
of all 24.

Those 2 superseded attempts are `sales-agent-token-burn` baseline samples 2 and 4, and both
scored *lower* than the versions that were kept (check score 0.182 against 0.364 for sample
2, and $0.363 against $0.276 of spend for sample 4). So dropping them did not flatter the
Skill arm. Nothing was dropped because of its score. The discarded attempts cost $3.77.

**It is one run.** One agent model, one grader model, three tasks, four samples, twelve
pairs. The confidence interval includes zero.

## The Skill is not free

The Skill arm took about 27% more turns and 24% more model spend per attempt. Reproducing a
symptom before acting costs something.

On the two tasks where the diagnosis was wrong without it, that was a good trade. On the
third it was not.

## What this does not claim

It is not compared against any other Skill, product or framework. It is not evidence that the
Skill improves a real production agent, only that it changed what the model did on these
three tasks. The confidence interval is wide and includes zero.

## Check it yourself

You can check every claim on this page without re-running anything. The published bundle has
the task definitions, the inputs the agents were handed, the full session logs, the files
they produced, and the grader's reasoning. Recomputing the numbers is arithmetic over
`summary.json` and the 24 verdict files.

Re-running the experiment itself needs a Bedrock account, E2B and roughly $22 of model spend.
It will not reproduce these numbers exactly, because both the agent and the grader are
sampled. What should reproduce is the direction on the first two tasks.
