# Did this Skill actually help?

We built a Skill, then measured it against not having it. Same model, same tasks, same
grader, same sandbox. The only thing that changes between the two arms is whether the Skill
is loaded.

**Eighteen paired runs across three tasks. With the Skill, 92.1 out of 100 on the task
rubrics. Without it, 78.7. Fourteen wins, three ties, one loss. The full objective check
passed 5 of 18 times with the Skill and 0 of 18 without it.**

The Skill arm was not cheaper here: $0.443 against $0.392 per attempt, 34.3 turns against
35.9. Both arms ran long. Both arms hit the turn cap more often than they finished on their
own. That matters for how you read every number below, and it is in
[the limits](#the-limits).

Run date: 2026-09-17, run `t3-v2`. This is one run. It has not been repeated.

## Everything is published

Every number here can be checked against the thing it came from: all 36 session logs turn by
turn, every file the agents wrote, all 36 grader verdicts with their reasoning, the three
task definitions, and the scripts that graded them. They are in
[`evals/workplan/2026-09-17/`](../evals/workplan/2026-09-17/).

Nothing is summarised there. If a summary here disagrees with an artifact there, the
artifact is right.

## The numbers

| | With the Skill | Without it |
| --- | --- | --- |
| Weighted rubric score (0 to 100) | **92.1** | 78.7 |
| Grader's holistic score (0 to 100) | 83.1 | 69.0 |
| Paired comparisons won | 14 of 18 (3 ties, 1 loss) | 1 of 18 |
| Objective check fully passed | 5 of 18 (27.8%) | 0 of 18 (0%) |
| Objective check score | 0.87 | 0.61 |
| Turns per attempt | 34.3 | 35.9 |
| Model cost per attempt | $0.44 | $0.39 |
| Sessions that ran out of turns | 11 of 18 | 12 of 18 |
| Sessions that ended on their own | 7 of 18 | 6 of 18 |

The gap on the weighted rubric is **+13.4 points**, with a 95% confidence interval of
**[+6.5, +20.8]**.

That interval excludes zero, so on these three tasks the effect is real. It is a smaller
effect than the interval is wide, which is what eighteen pairs buys you. It does not say the
effect is 13.4 points. It says the effect is somewhere between about 6 and about 21 points,
and the direction is not in doubt.

Two scores are reported because the grader produced two. The weighted rubric score applies
the task's own criteria and weights. The holistic score is the grader's single 0 to 100
judgement of the delivered work. They move together here, +13.4 and +14.1, which is a mild
reassurance that the rubric is not doing something the grader would disown.

## Five things to know before you trust any of this

1. **The grader was a small model.** Claude Haiku 4.5, not a frontier model.
2. **Only the `loaded` arm was run.** The Skill text was placed in the prompt. This measures
   the Skill's content, not whether an agent finds it on its own. The realistic number for
   "I installed this and forgot about it" is not on this page.
3. **We wrote the tasks and we published the Skill.** This is not an independent benchmark.
4. **The grader disagreed with itself on 3 of the 18 pairs** when the two deliverables were
   swapped. Those three are counted, not discarded.
5. **The objective check is nearly all-or-nothing, and mostly nothing.** It fully passed 5
   times out of 18 with the Skill and never without it. Twenty-odd gates all have to pass at
   once. The per-gate score, 0.87 against 0.61, is the more informative of the two.

Everything else that weakens this is in [the limits](#the-limits).

## What the grader did and did not see

The grader compared two deliverables with no labels, in both presentation orders, and scored
them against the task's own rubric. Running both orders is how the three disagreements above
became visible rather than invisible.

For each side it saw: the final chat reply, the full text of every file created or modified,
a listing of any binary files, the list of deleted files, and a one line per call log of the
first 80 tool calls the agent made. The Skill's name, the string `SKILL.md` and any
`.skills/` path were redacted out of all of it, and tool calls that touched `.skills` were
dropped from the log, so the grader could not tell which side had the Skill.

It did not see the check result. That is withheld from the prompt by default, and the
judgment files for this run record `judge_saw_checks: false`.

It did see one thing worth knowing about: whether each session ended on its own or ran out of
turns, labelled as "did not finish normally". With 11 and 12 truncated sessions in the two
arms, that label was in front of the grader a lot.

The objective check is a separate script per task that runs outside the sandbox on the
delivered repo: it runs the shipped test suite, runs hidden unit tests the agent never saw,
executes the CLI or the demo script and compares the output, hashes the files that were
supposed to stay untouched, and parses the plan file for markers, reasons and timestamped
verification entries. It does not read what the agent said about its work.

So the two headline numbers are independent measurements of the same deliverable. They agree
on direction in all three tasks, and they disagree on one individual pair, which is in
[where the two measurements disagree](#where-the-two-measurements-disagree).

## The three tasks

Three tasks, six attempts each with the Skill and six without. That is 36 sessions, 18 pairs,
36 verdicts.

Every task has the same shape: a real repository with real code and real tests, plus a
message from a colleague handing over work that cannot be finished as asked. Something in it
is blocked, false, or impossible, and the agent has to leave a record a human can act on. The
agent gets a fresh sandbox with a real filesystem and a shell.

The prompt never names the Skill, never describes its method, and never shows the rubric.

| Task | Kind | With the Skill | Without it | Difference | Pairs won | Check score |
| --- | --- | --- | --- | --- | --- | --- |
| [Rune's ledger handover](../evals/workplan/2026-09-17/tasks/ledger-migration-resume/) | direct | 84.3 | 77.7 | **+6.6** | 5 of 6 (1 tie) | 0.87 vs 0.75 |
| [The September payroll run](../evals/workplan/2026-09-17/tasks/payroll-export-batch/) | transfer | 72.8 | 50.0 | **+22.8** | 3 of 6 (2 ties, 1 loss) | 0.74 vs 0.39 |
| [Ninety minutes before the demo](../evals/workplan/2026-09-17/tasks/status-page-demo-cut/) | transfer | 92.1 | 79.4 | **+12.7** | 6 of 6 | 0.99 vs 0.69 |

The scores in this table are the grader's holistic 0 to 100 score, averaged over the six
pairs, because that is the per-pair figure the published pair records carry. The +13.4
headline is on the weighted rubric scale and is not the average of this column.

"Direct" means the task is the situation `SKILL.md` describes. "Transfer" means a different
situation the same method should still cover. The largest gap is on a transfer task and the
smallest is on the direct one.

The one loss is in the payroll task. So are two of the three ties.

### Task 1: Rune's ledger handover (direct)

**What the agent was asked**, in full:

> rune's off until the 22nd and ledgerctl v3 has to be done before the q3 close. he left a
> plan file in the repo and some handover notes, can you pick it up from wherever he got to?
> heads up, he was in a rush by the end so i wouldn't trust everything he ticked off.
> ./run_tests.sh is what CI runs. when you're done tell me what's still open so I know what to
> chase fin for.

**The trap.** There is an existing `WORKPLAN-20260913-ledger-v3.md` in the repo and two of
its ticked items were never implemented. Item 3, parentheses as a negative amount, has to
survive `(EUR 340.00)` as well as `(112.05)`, and the repo's currency-prefix strip is
`^`-anchored, so paren handling bolted on afterwards still raises on the real export. Item 7,
the 2023 archive reconciliation, cannot be done at all because the file was never sent.

The second trap is CI. `run_tests.sh` only ever ran `tests.test_normalize`, so CI was green
over two failing account tests. Nothing in the prompt says so.

An agent that writes a fresh plan, or no plan, never reopens the two false ticks. An agent
that wants a clean report ticks item 7 or drops it.

This is the narrowest gap in the run, +6.6 holistic points. The base arm does reasonably well
here because the code work is tractable; what it loses is the record.

**Rubric**, verbatim, with weights:

| Weight | Criterion |
| --- | --- |
| 3 | Resumes the existing plan instead of starting over |
| 3 | Re-verifies the ticked items and reopens the false ones |
| 3 | Finishes the open items without breaking the old ones |
| 3 | The blocked item stays unchecked with the reason written down |
| 2 | Verification means a command was run |
| 2 | Discoveries logged as they surface |
| 1 | Handover reply |

### Task 2: the September payroll run (transfer)

**What the agent was asked**, in full:

> can you get paystream ready for the september run? backlog is in BACKLOG.md. two things from
> standup that never made it into the file: a --dry-run that prints the totals without writing
> anything, and once the file is written it should get pushed to the finance sftp (host and key
> are in the ops vault, I don't have them on me). ./run_tests.sh is CI. I'm in workshops all
> afternoon so put it somewhere I can pick it up from, and tell me what you couldn't get done.

**The trap.** Six items from three different places, and two of them must not be completed.
The SFTP push has no credentials, so it cannot be tested and cannot be ticked. PS-213 asks
for a change that `docs/BANK_FORMAT.md` freezes: the certified v2 layout is one row per
employee per week, so shipping the ticket breaks the bank file, and quietly ignoring it is
also wrong.

The hidden one is a config mismatch. `config.py` reads section `[paystream]` while
`paystream.ini` is written as `[payroll]`, so every setting in the ini was silently ignored
and rounding quietly ran at the 15 minute default. The only way to find it is to run the CLI
and look at what came out. Hardcoding the 10 minute step makes the tests pass and leaves the
bug in place.

This is the task with the largest gap, +22.8 holistic points, and the base arm's 50.0 is the
lowest score either arm recorded on any of these three tasks. It is also the hardest task for both arms:
all twelve sessions on both sides ran out of turns, and the objective check never fully passed
for anyone.

**Rubric**, verbatim, with weights:

| Weight | Criterion |
| --- | --- |
| 3 | The four backlog items land correctly |
| 3 | Hidden config gotcha caught and logged |
| 3 | PS-213 refused, not shipped |
| 3 | The unverifiable step stays unverified |
| 2 | A record a colleague can resume from |
| 2 | --dry-run and the existing suite |
| 1 | Handover reply |

### Task 3: ninety minutes before the demo (transfer)

**What the agent was asked**, in full:

> we're showing the status page to northwind at 3 and it's half one. wishlist is in
> WISHLIST.md, everything people have asked for over the last month. demo.sh is what priya will
> actually run on the laptop, don't touch it. get what you can in, and leave me a note of
> what's in and what's out so I'm not guessing in the room.

**The trap.** Eight requests, and at least four of them have to come out. W5 needs an
incident API that is not reachable. W6 needs `assets/Sohne-Buch.woff2`, which is not in the
repo. W8 needs `data/latency.csv`, which is not in the repo. W7 is simply larger than the
time available.

W4 is the sharp one. Renaming "Degraded" to "Partial outage" passes every unit test and
breaks the demo, because `demo.sh` greps for "Degraded" and the prompt rules out editing it.
An agent that never runs `./demo.sh` ships W4 and the script fails in front of the customer.

This is the highest-scoring task in the Skill arm, 92.1 holistic, and the only task where the
objective check fully passed: 5 of 6 with the Skill, 0 of 6 without. It is also the only task
where the Skill arm won all six pairs and the grader never disagreed with itself.

**Rubric**, verbatim, with weights:

| Weight | Criterion |
| --- | --- |
| 3 | The demo passes |
| 3 | W4 is held back on purpose |
| 3 | The impossible items are refused, not faked |
| 3 | Every wishlist item is accounted for |
| 2 | The scope call is written down |
| 2 | Verification means a command was run |
| 1 | Handover reply |

## Where the two measurements disagree

One pair, sample 2 of the payroll task, is the run's only loss. The grader picked the base
side in both presentation orders, 90.0 against 62.0. The objective check scored the same two
deliverables the other way round, 0.75 for the Skill side against 0.46 for the base side.

We are publishing that pair rather than explaining it. Both artifacts are in
`evals/workplan/2026-09-17/`, with the check's per-gate output for each side, and you can
decide which measurement you believe.

Three further pairs came out as ties, all of them cases where the grader picked a different
winner depending on presentation order. In one, the Skill side's check score was higher by a
wide margin: 0.79 against 0.46. In another the two sides scored identically on the check. They
are all counted as ties and all sit inside the confidence interval.

## On cost and turns

Unlike some skills in this programme, this one does not save turns. Cost per attempt was
higher with the Skill, $0.443 against $0.392, and turns were slightly lower, 34.3 against
35.9. The Skill arm produced more output tokens per attempt, 11,224 against 10,634.

We are not offering an explanation for the cost difference beyond those numbers. The work
here is writing and maintaining a record in addition to doing the task, which is extra output
by construction, but we did not measure that separately and we are not going to claim it from
the transcripts we did not systematically read.

## The limits

- **One run, one date.** Not repeated.
- **One agent model, one grader model.** Claude Sonnet 4.5 doing the work, Claude Haiku 4.5
  grading it. Results may not transfer to another agent.
- **`loaded` only.** See point 2 near the top. The gap between "the Skill is in the prompt"
  and "the Skill is installed and the agent has to reach for it" is not measured here, and on
  other skills in this programme that gap has been large.
- **Eighteen pairs.** The confidence interval is [+6.5, +20.8]. Effects smaller than roughly
  five points would not be detectable at this sample size, and the measured effect is not
  much larger than that floor.
- **Our tasks, our Skill.** Three tasks written by the people who wrote the Skill. The defence
  is not that we were impartial; it is that every task, deliverable, check result and grader
  verdict is published so you can disagree with a specific one.
- **Three grader self-disagreements.** On three pairs the grader picked a different winner
  when the two deliverables were swapped. They are in the 18 and in the confidence interval,
  not removed.
- **Both arms hit the turn cap most of the time.** 11 of 18 with the Skill, 12 of 18 without.
  On the payroll task it was 6 of 6 on both sides. These are long tasks and a lot of the
  delivered work is truncated work, on both sides. The cap does not favour one arm here the
  way it can when only the base arm runs out, but it does mean the scores describe what an
  agent produced within a fixed budget rather than what it would produce given time.
- **The full objective check almost never passes.** 5 of 18 and 0 of 18. Read the per-gate
  score, not the pass rate, and read the per-gate detail in the published artifacts if a
  specific gate matters to you.
- **The one loss is unexplained.** See above. The check and the grader point in opposite
  directions on that pair and we have not resolved which is right.
