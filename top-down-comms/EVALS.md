# Did this Skill actually help?

We built a Skill, then measured it against not having it. Same model, same tasks, same
judge, same sandbox. The only thing that changes between an arm and its baseline is whether
the Skill is there.

This time we ran two different versions of "is there". In one, the Skill text was placed in
the prompt up front. In the other, the Skill sat on disk with its name and description in a
listing, and the agent had to decide to open it. The two versions do not give the same
answer, and that difference is the most useful thing on this page.

**Nine pairs per arm, three tasks. With the Skill in the prompt: 91.5 out of 100 against
79.9, a gap of +11.6 points, confidence interval [+5.0, +17.4], eight wins, zero ties, one
loss. With the Skill only installed: 85.6 against 81.5, a gap of +4.2 points, confidence
interval [-3.5, +10.7], six wins, two ties, one loss. The second interval includes zero, so
that arm is not resolved.**

The agent opened the Skill in 5 of the 9 runs where it had to find it.

Run date: 2026-09-17, run `td-v2`. This is one run. It has not been repeated.

## Everything is published

Every number here can be checked against the thing it came from: all 27 session logs turn by
turn, every file the agents wrote, all 36 judge verdicts with their reasoning, the three task
definitions, the checker scripts and the pre-fix copies of two of them. They are in
[`evals/top-down-comms/2026-09-17/`](../evals/top-down-comms/2026-09-17/).

Nothing is summarised there. If a summary here disagrees with an artifact there, the artifact
is right.

## The numbers

| | Skill in the prompt | Skill on disk | No Skill |
| --- | --- | --- | --- |
| Rubric score (0-100) | **91.5** | **85.6** | 79.9 / 81.5 |
| Gap against the baseline | **+11.6** [+5.0, +17.4] | **+4.2** [-3.5, +10.7] | |
| Relative uplift | 14.5% [5.9, 23.2] | 5.1% [-4.1, 13.7] | |
| Paired comparisons | 8 wins, 0 ties, 1 loss | 6 wins, 2 ties, 1 loss | |
| Win rate | 88.9% [55.6, 100.0] | 77.8% [50.0, 100.0] | |
| Hard checks fully passed | 4 of 9 (44.4%) | 6 of 9 (66.7%) | 3 of 9 (33.3%) |
| Hard-check score | 0.850 | 0.837 | 0.811 |
| Judge self-disagreements | 0 of 9 | 2 of 9 | |
| Agent opened the Skill | 9 of 9 (by construction) | 5 of 9 | 0 of 9 |
| Turns per attempt | 5.2 | 5.2 | 5.1 |
| Model cost per attempt | $0.061 | $0.076 | $0.062 |
| Sessions that ran out of turns | 0 of 9 | 0 of 9 | 0 of 9 |

The baseline column carries two rubric scores because the same nine no-Skill sessions were
judged twice, once against each arm's deliverable, in separate comparisons. The judge scored
them 79.9 in the comparison against the prompt arm and 81.5 in the comparison against the
disk arm. That spread of 1.6 points is judge noise on identical documents, and it is a useful
scale for reading the +4.2 above it.

The prompt arm's interval excludes zero. On these three tasks that effect is real, and it is
somewhere between about five and about seventeen points. Nine pairs does not buy a tighter
interval than that.

## Skill given up front versus the agent finding it

This is the number most people actually want, because installing a Skill is the realistic
case and pasting it into the prompt is not.

In the `skill` arm the agent's system prompt listed the Skill by name, description and file
path, with an instruction to read `SKILL.md` before starting when a request matches. The
folder was uploaded into the sandbox. Nothing else was different. The agent opened the file
in 5 of the 9 runs.

Where it did not open the file, it had no way to benefit from it. That drags the arm's
average toward the baseline, and the arm does not resolve: +4.2 points with an interval of
[-3.5, +10.7].

Reading was not random across tasks. It split by task, which is the least convenient way for
it to split:

| Task | Opened the Skill | Gap in this arm |
| --- | --- | --- |
| Renewal memo | 3 of 3 | +7.2 |
| Client update | 2 of 3 | -0.3 |
| Steering status | 0 of 3 | +5.6 |

On the steering status task the agent never opened the Skill in any of the three runs, and
that arm still scored +5.6 points over its baseline. So the honest reading of the four runs
where the file went unopened is not "the Skill did nothing"; those runs average +5.4 points
and the five runs that did open it average +3.2. With four and five runs, and with the split
confounded entirely with which task it was, neither of those numbers means anything on its
own. What they do show is that the arm's shortfall cannot be attributed cleanly to
non-discovery, and we are not going to claim it can.

Two things are worth saying plainly about why discovery may have failed. The three prompts
are ordinary work requests in a colleague's voice: draft an email, turn notes into a status,
write a one-pager. None of them says anything that reads as "communication method". An agent
that scans the Skill's description and decides this is a normal writing job is making a
defensible call. Whether that is a description problem or a model problem is not measured
here.

The hard checks go the other way in this arm: 6 of 9 passed with the Skill on disk against
4 of 9 with it in the prompt, and 3 of 9 with no Skill. So the arm that scores lower with
the judge passes more of the mechanical gates. The two measurements do not agree with each
other here, and the section below on length explains most of it.

## Four things to know before you trust any of this

1. **The judge was a small model.** Claude Haiku 4.5, not a frontier model. The agent doing
   the work was Claude Sonnet 4.5.
2. **Nine pairs per arm.** Three tasks, three samples each. Effects smaller than a few points
   are not detectable at this size, and the `skill` arm's +4.2 is inside that fog.
3. **We wrote the tasks and we published the Skill.** This is not an independent benchmark.
4. **The judge disagreed with itself on 2 of the 9 pairs in the `skill` arm** when the two
   deliverables were swapped. Zero in the prompt arm. The two are counted, not discarded.

Everything else that weakens this is in [the limits](#the-limits).

## What the judge did and did not see

The judge never saw the hard-check result. Every judgment record in the published folder
carries `judge_saw_checks: false`. For each side, with no label saying which side is which,
it saw the agent's final reply, the files the agent created or changed, the names of any
binary files, anything it deleted, whether the run ended normally or was cut off by the turn
cap, and a one line per call log of the agent's first eighty tool calls. It scored the two
sides against the task's own rubric, in both presentation orders. Running both orders is how
the two disagreements above became visible rather than invisible.

One detail of that tool call log matters more on this page than on most: any call whose
arguments mention the skills directory is stripped out before the judge sees it. Without
that, a side would be identifiable from the single fact that it opened a skill, and the
comparison would not be blind at all. That filter is doing real work in the `skill` arm,
which is exactly the arm where the agent has to go and open the Skill for itself.

The hard check is a separate script that opens the delivered document and looks for specific
strings, dates, figures and their position in the text: whether the bank form appears in the
first 130 words, whether the memo uses 1 October rather than the superseded end of October,
whether a figure nobody has quoted is presented as fact. It does not read the judge's
verdict, and the judge does not read it.

## A correction: four checker gates were wrong, and they were fixed before scoring

Before `td-v2` was scored, four gates in the checkers were marking correct work as failed.
All four were in every arm, including the baseline. The pre-fix checker scripts, the pre-fix
check results and the pre-fix summary are published alongside the run so the claim can be
checked rather than taken on trust.

The four:

1. **A ticket number read as a euro amount.** The renewal checker's money scanner matched
   `88417` inside the ticket reference `TS-88417` and reported it as an invented next-year
   price. It fired on three attempts.
2. **A saving, a threshold and a competitor's quote read as next year's price.** The same
   gate flagged `13,000` in "Cutting to 40 seats saves EUR 13,000 to 16,000", `50,000` in a
   kill condition reading "If Tallow quotes above EUR 50,000 for 40 seats", and `31k` in a
   line about the Cobbleworth alternative. None of them is a claim about what Tallow will
   charge.
3. **A correct 1 October deadline read as the wrong one.** The gate that looks for the
   superseded "end of October" deadline fired on the sentence
   "**Contract notice deadline:** 1 October (30 days before 31 Oct renewal)", because the
   clause mentions 31 October at all. It hit one attempt in each of the three arms.
4. **An option list read as recommending its first option.** The client-update checker
   required option B's EUR 6,200 to appear before option A's EUR 18,400 in the text. Listing
   A before B and then recommending B was scored as leading with A's price. This one failed
   all nine client-update attempts: three in each arm.

Counted per arm, before the fixes: the option gate failed 3 of 3 in each of the three arms,
the invented-figure gate failed 3 in the prompt arm and 2 each in the disk arm and the
baseline, and the deadline gate failed 1 in each arm. After the fixes the option gate and the
deadline gate fail nowhere, and the invented-figure gate fires twice. Both remaining hits are
projected prices in a prominent position: a baseline memo telling the reader to budget EUR
53k for 60 seats, and a prompt-arm memo whose title is a recommendation to renew at 40 seats
and expect EUR 38k to 42k. Whether the surrounding hedging should have exempted them is a
judgement call, and we left the gate where it was rather than widen it until it stopped
firing.

What this moved: the hard-check pass rate went from 0 of 9 to 4 of 9 in the prompt arm, from
2 of 9 to 6 of 9 in the disk arm, and from 1 of 9 to 3 of 9 in the baseline. Hard-check
scores moved from 0.811 to 0.850, from 0.797 to 0.837, and from 0.778 to 0.811.

What this could not move: any judge number. The judge never receives checker output, so
rescoring the checkers cannot change a verdict that was produced without them. The published
pre-fix summary shows exactly that. Every judge figure is byte-identical before and after:
91.5 against 79.9, +11.6 [+5.0, +17.4], 8 wins and 1 loss, zero order disagreements in the
prompt arm; 85.6 against 81.5, +4.2 [-3.5, +10.7], 6 wins, 2 ties and 1 loss in the disk arm.
The checker fixes changed the checker column and nothing else.

**This run replaces an earlier v1 figure of +10.5 points [+4.8, +15.6].** That figure was
measured on the earlier version of these tasks, which have since been rebuilt. It is not the
same measurement and the two should not be averaged or compared.

## The three tasks

Three tasks, three attempts each in each arm plus three baseline attempts. That is 27
sessions, 18 pairs and 36 verdicts, since every pair is judged in both orders.

Every task has the same shape: a folder of raw material, a Slack export, a contract extract,
last week's status document, an emailed thread, a usage export, plus a short request in a
colleague's voice. The material contains a decision nobody has made, a fact that has been
superseded, and several items that are louder than the one that matters. The agent gets a
fresh sandbox with a real filesystem and a shell.

The prompt never names the Skill, never describes its method, and never shows the rubric.

| Task | Kind | Prompt arm | Disk arm | Baseline | Prompt gap | Disk gap |
| --- | --- | --- | --- | --- | --- | --- |
| Client update from a thread | direct | 90.3 | 85.0 | 85.0 / 85.3 | **+5.3** | -0.3 |
| Steering status with a buried blocker | transfer | 91.7 | 91.4 | 79.2 / 85.8 | **+12.5** | +5.6 |
| Renewal memo with a missing price | transfer | 92.5 | 80.6 | 75.6 / 73.3 | **+16.9** | +7.2 |

"Direct" means the task is the situation `SKILL.md` describes. "Transfer" means a different
situation the same method should still cover. Both transfer tasks show a larger gap than the
direct one in both arms, which is the opposite of the usual worry about a skill that only
works on its own example. The direct task is the one where the disk arm went slightly
negative.

### Task 1: the client update from a thread (direct)

**What the agent was asked**, in full:

> hey, can you draft the update email to Rosa at Halden about the migration dry run? slack
> export from our internal channel is in the folder plus last week's call notes. she reads
> these on her phone. put the draft in output/ (subject line + body), I'll send it myself

**The trap.** The thread is a chronology with every conclusion left unmade and every
decision-relevant fact superseded at least once. The full validation run failed 312,000
records, 13% of 2.4M, but that number is only in a pasted log tail while an earlier 40k
sample figure sits in prose. The re-scoped price is EUR 6,200, not the rough 9k mentioned
earlier. The deadline is Fri Sep 18, not the "by the 25th" someone said informally. The
person who signs is Mira Castellanos under SOW 7.2, not Tomasz, who is on parental leave, and
not Rosa, who is the sponsor and does not sign change requests.

The second trap is what the thread wants added. Two things were proposed in the channel and
nobody objected: an opening line establishing that the data problem comes from Halden's
legacy system and is not our fault, and a pitch for the ops dashboard redesign. Both are
socially easy to include and both serve a different purpose than the email.

**Rubric**, verbatim, with weights:

| Weight | Criterion |
| --- | --- |
| 3 | Rosa learns what we recommend and what she has to do before anything else |
| 3 | Every fact used is the current one |
| 2 | Why it cannot wait is made concrete |
| 2 | Both options are visible and one of them is chosen |
| 2 | Nothing in the email is serving a different purpose |
| 1 | Short, and ends on one specific action |

This is the task where the hard check separates most cleanly: 3 of 3 passed with the Skill in
the prompt, 2 of 3 with it on disk, 1 of 3 without it.

### Task 2: the steering status with a buried blocker (transfer)

**What the agent was asked**, in full:

> can you turn the leads' notes into this week's steering status for the Ledgerline program?
> goes to Dana (CFO) and the steering group, she chairs at 9 tomorrow. last week's version is
> in the folder, roughly the same shape is fine, plus the other bits Lea dumped in there.
> mostly green this week I think, nice change from August. put it in output/

**The trap.** Two instructions in the request pull against the finding. "Roughly the same
shape is fine" points at last week's eight-row RAG table, and "mostly green this week I
think" points at repeating the leads' self-ratings. The material contains one thing that
undoes both: Hollis Bank form HB-17 is unsigned, it has to reach the bank by Fri Sep 25, and
Dana, the person reading the document, is the one who has to sign it. Marcus Reinholt is the
only other mandate holder and he is travelling until Oct 9, so the EA pool cannot route it
around her. Miss it and the Oct 30 payroll run for 1,140 employees stays on the legacy
system, about EUR 22,000 of licence extension plus roughly 60 hours of reconciliation, and
cutover moves to Nov 27.

A second trap sits in the small print: a superseded "end of month" deadline, and a training
figure of 212 of 240 that the PMO has since corrected to 198.

A third is volume. An EUR 41,000 invoice dispute, an internal audit observation, an OCR
template, a super-user resigning in Malmo and an office move are all real and all louder in
the notes than the bank form.

**Rubric**, verbatim, with weights:

| Weight | Criterion |
| --- | --- |
| 3 | A reader who stops after the opening knows what is at risk and what they must do |
| 3 | Correct owner and correct date |
| 2 | Cost of missing it is quantified |
| 2 | Status not misreported |
| 1 | Everything else is accurate and kept subordinate |
| 1 | Readable in two minutes |

The central gate of this task is whether the unsigned bank form appears in the first 130
words. All three baseline attempts failed it. No prompt-arm attempt failed it. In the disk
arm, where the Skill went unopened on all three runs, 2 of 3 failed it.

Full passes are another matter: 0 of 3 in the prompt arm, 1 of 3 in the disk arm, 0 of 3 in
the baseline. What the prompt arm kept failing is the gate requiring the overall status not
to be reported as plain green or on track, 3 of 3, against 2 of 3 in the baseline. In the
published detail for the prompt arm's first sample, the checker records the bank form arriving
at word 50 and the Sep 25 deadline at word 56, and still fails that attempt for reporting the
overall status as green. Leading with the risk and labelling the programme green are not
mutually exclusive, and several documents did both. The separate length item, which the
checker scores at 500 prose words or fewer, failed on all three attempts in all three arms.

### Task 3: the renewal memo with a missing price (transfer)

**What the agent was asked**, in full:

> Priya wants a one-pager by Thursday on the Tallow CRM renewal: do we renew or not, and
> what's it going to cost us next year. everything I've got is in the folder, the contract
> bit, the emails with their account guy, the ops channel scroll and the seat usage export.
> she makes the call, she hates long docs. output/ is fine

**The trap.** The user asks what it will cost next year, and the answer is that nobody can
know in time. Clause 3.2 makes next year's price Tallow's then-current list price, that list
is published in early October, and Lukas is out until 28 Sep. The notice window under clause
9.2 closes thirty days before the 31 Oct term end, so 1 October, before the price exists.
Doing nothing is therefore a decision to renew for twelve months at a number nobody has seen.

The material has already answered the question the easy way. Marek's EUR 52,800 is a 10%
guess, three people in the ops channel repeat it, and it is already in the FY27 board pack.
There is also a wrong deadline in circulation, "we have until the end of October", and a
decoy in clause 9.4's sixty-day cure period for material breach, which is not the notice
period. Tallow's own account manager told Jonas that a seat reduction applies at the renewal
date, which is not what clause 3.3 says: it has to be requested in writing before the same
1 October deadline, and 38 of 60 seats were active in the August export.

**Rubric**, verbatim, with weights:

| Weight | Criterion |
| --- | --- |
| 3 | The date Priya has to act by is the first thing she gets |
| 3 | The question 'what will it cost' is answered honestly |
| 2 | The bind is spelled out |
| 2 | Next steps are specific and can fail |
| 1 | Uses the evidence in the folder |
| 1 | One page |

This is the task with the largest judge gap, +16.9 points in the prompt arm, and it is also
the one place where the judge and the checker point in opposite directions. The prompt arm
scored 0.765 on the hard check against the baseline's 0.843. Two scored items account for
it. The one-page item, which the checker scores at 500 prose words or fewer, failed on 2 of 3
prompt-arm attempts and on none of the baseline attempts: mean prose length was 545 words
with the Skill in the prompt and 722 with it on disk, against 365 without it. The other is
the item asking the memo to state the bind explicitly, which failed on all three prompt-arm
attempts and on 2 of 3 baseline attempts.

The plain reading is that the Skill makes these memos longer and more structured, that the
judge rewards the structure, and that the length gate penalises it. Both readings are in the
published artifacts.

## The limits

- **One run, one date.** Not repeated.
- **One agent model, one judge model.** Claude Sonnet 4.5 doing the work, Claude Haiku 4.5
  judging it. Results may not transfer to another agent.
- **Nine pairs per arm.** The prompt arm's interval is [+5.0, +17.4] and the disk arm's is
  [-3.5, +10.7]. Effects smaller than roughly five points are not detectable here.
- **The disk arm is not resolved.** Its interval includes zero. The honest statement for
  "I installed this and forgot about it" is that this run did not establish an effect, not
  that it established a small one.
- **The rubrics overlap the Skill's first rule.** Every task has a weight-3 criterion that
  amounts to "the reader learns the decision and the action before anything else", and the
  Skill's Rule 1 is "the governing thought goes first". We wrote both. A judge scoring
  against that rubric will reward a document written to that rule, and some of the measured
  gap is that overlap rather than a better document. The defence is weak on its own and the
  mitigation is partial: the hard checks test specific facts, dates, owners and figures
  rather than structure, and they also favour the Skill arms, 4 of 9 and 6 of 9 against 3 of
  9. Read the gap as evidence about facts and decisions surviving the rewrite, and treat the
  structural part of the rubric as contaminated.
- **Our tasks, our Skill.** Three tasks written by the people who wrote the Skill. The
  defence is not that we were impartial; it is that every task, deliverable, check result and
  judge verdict is published so you can disagree with a specific one.
- **Two judge self-disagreements in the disk arm.** On two pairs the judge picked a different
  winner when the two deliverables were swapped. They are in the nine and in the confidence
  interval, not removed.
- **The checkers were wrong until shortly before scoring.** Four gates were fixed on the day.
  The fixes are published as a diff against the pre-fix copies, and they cannot have touched
  the judge numbers, but a reader who wants to distrust the check column has a reason to
  start there rather than take the post-fix numbers as settled.
- **The Skill makes documents longer.** On the renewal task, mean prose length went from 365
  words without it to 545 with it in the prompt and 722 with it on disk, against a task that
  asks for one page. That is a real cost and it is not reflected in the judge score.
- **No arm hit an operational limit.** Every one of the 27 sessions finished normally and
  none ran out of turns, so none of the gap here is truncated work.
