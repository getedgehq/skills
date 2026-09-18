# edge-skill-bench@1.0

`edge-skill-bench@1.0` is the public, versioned name for the benchmark that measures whether the
Skills published at getedge.cc change the work an agent produces.

**Why this name.** `edge-skills` alone would collide with the Skills catalog, which is the thing
being measured rather than the measurement, so the domain noun goes before `-bench` exactly as in
`terminal-bench@2.0`, and the name then says "benchmark" without needing a footnote.

Cite it the way you would cite `terminal-bench@2.0`: "we scored X on `edge-skill-bench@1.0`". The
version is the identifier that makes a score comparable. A score against an unversioned
"Edge skills benchmark" is not comparable to anything.

Which Skills the benchmark covers, and which it deliberately does not, is in
[`eval-scope.md`](eval-scope.md).

Everything below is sourced from the research report draft dated 2026-09-17 and from the harness
and task definitions themselves. Where the method has not been pinned down, the section says
`NOT YET SPECIFIED:` and asks the question rather than inventing an answer. Those gaps are real
and are collected again at the end.

---

## 1. What a task is

A task is one realistic request, with its inputs, its grading rubric, and a deterministic checker.
The task authoring spec (`TASK_SPEC.md` in the harness) fixes the shape:

```
tasks/<skill>/<task-id>/
  task.json
  input/          # the files the user "attached"
  check.py        # the deterministic checker
  calibration/
    good/         # a hand-made deliverable the checker must pass
    bad/          # a plausible-but-flawed one it must fail
```

`task.json` carries the task id (`<skill>.<task-id>`), the skill it belongs to, a `kind` of
`direct` or `transfer`, the user prompt, an optional setup step run identically in both arms, a
rubric of 4 to 7 weighted criteria, a `why_skill_should_matter` note naming the specific procedure
in `SKILL.md` that a generic agent tends to skip, and the expected baseline failure modes.

Rules that matter for anyone reading a score:

- The prompt must not reveal the rubric, the skill's method, or the skill's name and jargon.
- Ground truth is planted in `check.py` and the rubric, never in `input/`.
- The spec calls for 3 tasks per skill: 1 `direct` (the core use case) and 2 `transfer` (a
  different domain, a trap, a missing precondition, or a case where the right answer is to stop
  and say the question cannot be settled).
- Correctness must not depend on live internet content.
- Calibration fixtures are hand-written and committed before the run. The `good` fixture must
  pass and the `bad` one must fail, and the checker is fixed until that is true.

The published runs mostly honour the 3-task rule, and one does not: the `heldout` run of
`autonomous-research` was measured on 2 tasks, not 3, which is where its 16 judged pairs come
from. The same Skill's earlier v1 run used 3 tasks. Both are published on its page, and the
disagreement between them is itself reported there. Read a per-skill `n` as tasks multiplied by
samples per task, not as an independent sample count.

### Environment

- Agent: Claude Sonnet 4.5, in a fresh E2B sandbox per attempt (Debian, Python 3.11, Node 20,
  git, jq, curl, ImageMagick).
- Judge: Claude Haiku 4.5.
- Every attempt gets a clean container, a clean filesystem, and no memory of prior attempts.
- The task's `input/` is copied to the working directory. After the agent stops, its final chat
  message and every new or modified file under the working directory are collected.

The harness task spec sets a cap of 40 turns per attempt.

**The pinned snapshots.** `@1.0` names these, and a bump of either is a bump of the benchmark:

| Role | Snapshot | Served through |
| --- | --- | --- |
| Agent | `anthropic.claude-sonnet-4-5-20250929-v1:0` | Bedrock, `us.` and `global.` inference profiles |
| Judge | `anthropic.claude-haiku-4-5-20251001-v1:0` | Bedrock, `us.` and `global.` inference profiles |

Two honest details sit behind that table. The first is that the agent snapshot is load balanced
across two regional inference profiles of the same weights, because a single profile's throughput
would not carry the run. Which profile served a given call is recorded per call in the harness
ledger, and is not recorded in the per attempt `result.json`, so an attempt can be traced to its
profile only through the ledger. We treat the two profiles as one model. If they ever diverge, that
assumption is where to look first.

The second is that the judge snapshot is recorded inside every judgment file, in a `judge_profiles`
field, rather than being asserted once in a config. Every judgment underlying every published cell
carries the Haiku pair above. So does every other judgment on disk: of the 442 judgment files the
harness has written, 440 name that pair and 2 predate the field, and none names anything else. That
was checked by reading the files rather than by trusting the setting. An earlier round of exploratory judging
used a different model and is not on disk and is not published; the field is what makes that
statement checkable instead of a claim.

**The 40-turn cap is part of the definition, frozen per version.** It is not a harness convenience
that may drift between runs of the same `@1.0`. The precedent forces this: one of the six withdrawn
results was withdrawn because a cap truncated one arm and not the other, which means the cap can
manufacture a difference between arms out of nothing. A setting that can do that is part of the
measurement, so changing it changes the benchmark and requires a version bump.

---

## 2. Arms

An arm is one of three conditions the same agent runs the same task under.

| Arm | Condition | What it estimates |
| --- | --- | --- |
| `base` | No skill present at all | The floor |
| `loaded` | Skill text placed in the prompt up front | Upper bound on the effect: the agent cannot miss it |
| `skill` | Skill installed on disk, agent must decide to find and read it | The realistic condition, including discovery failure |

Every reported figure is a comparison of one treatment arm against `base` on the same task with
the same sample index. `loaded` and `skill` are never pooled.

The gap between `loaded` and `skill` is itself a result. A skill can be good and still fail in
practice because nothing causes the agent to open it. `loaded` is an upper bound, not a usage
forecast; `skill` is the honest number for "what happens if I install this," and it is
consistently lower.

**The citable default is `skill`.** A bare "scored X on `edge-skill-bench@1.0`", with no arm named,
means the `skill` arm, and a `loaded` figure is only ever citable as "X on `edge-skill-bench@1.0`
(`loaded`)".

The choice follows from what a reader does with the number. Someone reading a score is deciding
whether to install the Skill, and after they install it the agent has to notice the Skill and open
it before any of the writing inside it can help. `skill` measures that whole path; `loaded` assumes
the hardest part away. `loaded` is consistently the higher number, which is exactly why it is the
wrong default: making the flattering arm the one you get for free is how a benchmark drifts into
marketing.

`loaded` keeps its place in the definition because the gap between the two arms is diagnostic. A
Skill that scores well `loaded` and poorly `skill` has a discovery problem, and that is a different
repair from a Skill that scores poorly in both. Naming `skill` as the default settles what a bare
number means; it does not retire the comparison.

---

## 3. The two signals

Two independent signals are collected per attempt. Independence is the point: they are built so
that agreement between them carries information.

**Checker.** A Python script per task that inspects or executes what the agent actually produced.
It installs dependencies and runs the build, parses the file and asserts facts about it, and
resolves claimed file and line references against the real repository. It does not read the
agent's prose. It runs on the host, not in the sandbox, and prints one JSON line:
`{"pass": bool, "score": 0.0-1.0, "details": [...]}`, where `pass` means every hard gate was met
and `score` is the fraction of objective items met. This is the signal that cannot be talked into
a pass.

**Judge.** A blinded pairwise comparison, never an absolute score of one trajectory. For each
side, with nothing saying which side is which, the judge sees:

- the agent's final reply,
- the files it created or changed, and the names of any binary files,
- anything it deleted,
- whether the run ended normally or was cut off by the turn cap,
- a one-line-per-call log of its first eighty tool calls.

Three properties hold it together:

1. **The judge never sees checker output.** An earlier judge could read checker results; every
   figure produced by it is superseded and not reported.
2. **Any tool call whose arguments mention the skills directory is stripped from the log**, so a
   side cannot be identified by the fact that it opened a skill.
3. **Every pair is judged in both presentation orders**, and the disagreement count is published.
   Position bias was the largest measured defect in this work: whichever answer the judge read
   first won 19 of 20 split decisions. A pair whose two orders disagree is recorded as a tie.

The judge is also date-grounded, because an earlier judge scored correct 2026 citations as
fabrications.

A pairwise judge is a deliberate refusal of the single-trajectory, named-criteria judges used
upstream. An absolute-scoring judge has nowhere to put both orders of the same pair, so adopting
one would mean retiring the control that caught the largest known bias here.

---

## 4. Sample size

**Six samples per task per arm.** With 3 tasks per skill that is 18 judged pairs per arm.

Six was chosen on the reasoning that three samples per task could not resolve a five-point effect.
That reasoning was right about the symptom and wrong about the cause, and the calculation below,
which nobody had run at the time, shows why: the limit was never the sample count.

Six is fixed **before** the run, in writing, and this is the load-bearing part. Raising `n` after
seeing a positive estimate is optional stopping and it inflates false positives. Two skills in the
current report were run twice at different sample sizes with the sample raised after the first
estimate had been seen. The only protection still available for those two is to publish both
figures side by side, always, and to read the larger one. Neither has a single headline number.

Where a run started at 3 samples and is topped up to 6, the top-up batch launches only after the
3-sample processes exit, because the batch runner computes its job list once at startup and does
not lock per attempt. Where a top-up cannot finish, the published figure is the smaller `n` with
the shortfall stated, never the figure that happened to look better.

### The power calculation, and what it says about six

The calculation was run after the fact, in `harness/power_tasks.py`, against variance components
measured from the published judgments rather than assumed: a within-task SD of 6.3 points on a pair
delta and a between-task SD of 4.8 points, both medians over the published cells. It simulates the
calibrated interval on cells of known true effect and counts how often the interval excludes zero.

Power of the calibrated interval, at 6 samples per task:

| true effect | 3 tasks | 4 tasks | 5 tasks | 6 tasks | 8 tasks | 10 tasks |
| --- | --- | --- | --- | --- | --- | --- |
| 0 (false positive rate) | 0.05 | 0.05 | 0.05 | 0.05 | 0.05 | 0.05 |
| 3 points | 0.09 | 0.12 | 0.16 | 0.20 | 0.27 | 0.34 |
| 5 points | 0.16 | 0.25 | 0.35 | 0.44 | 0.61 | 0.73 |
| 8 points | 0.31 | 0.52 | 0.69 | 0.82 | 0.94 | 0.98 |
| 10 points | 0.42 | 0.69 | 0.86 | 0.94 | 0.99 | 1.00 |
| 15 points | 0.69 | 0.94 | 0.99 | 1.00 | 1.00 | 1.00 |

**The answer to "why six" is that six was the wrong lever.** At 3 tasks, going from 3 samples to 6
moves power on a 5-point effect from 0.14 to 0.16. Going from 3 tasks to 6 tasks, at 3 samples,
moves it from 0.14 to 0.38. Doubling the samples bought two points of power. Doubling the tasks
bought twenty-four. Samples reduce judge noise inside a task; they cannot reduce the uncertainty
that comes from having sampled 3 tasks out of the space of tasks a Skill is meant to help with, and
it is that second term the interval is dominated by.

So the honest statement of what the published design detects, at 3 tasks and 6 samples: it is
powered at roughly 0.7 for a 15-point effect, 0.42 for a 10-point effect, and 0.16 for a 5-point
effect. Below about 10 points, a null result from this benchmark is close to uninformative. That is
a weak instrument, and it is the instrument the published figures came from.

**The binding requirement going forward is 6 tasks per Skill, not 6 samples.** Six tasks at 3
samples (18 attempts per arm) is a better design than 3 tasks at 6 samples (also 18 attempts per
arm) at identical cost: 0.74 against 0.31 on an 8-point effect. This is the cheapest available
improvement to the benchmark and it requires writing tasks rather than spending compute.

Sample count stays at 6 where it is already paid for, because lowering it now would change the
design mid-wave for no gain. It is not raised further.

None of this weakens the pre-registration rule above. Fixing `n` in advance is what stops the
sample size from being chosen to suit the estimate, and that protection is worth exactly as much
when the number fixed in advance turns out to have been the wrong lever. The pre-registration did
its job. The design it committed to was underpowered, and those are two different failures with two
different fixes.

---

## 5. Resolution and the confidence interval

### How the interval is computed

**The interval that resolution keys to is a two-sided 95% t interval on the per-task means, with
k-1 degrees of freedom**, where k is the number of tasks in the cell. The cell's estimate is the
mean of the task means; its standard error is the spread of those task means divided by the square
root of k. Cells with fewer than two tasks get no interval.

Every cell also carries a **percentile cluster bootstrap at 4000 draws with a fixed seed**, which
resamples tasks with replacement and then samples with replacement inside each drawn task. That
bootstrap was the benchmark's only interval until the recalibration of 2026-09-17, every figure
computed before it was read off it, and it is kept in the output so that correction can be audited.
It is no
longer what resolution means.

#### Why the bootstrap was replaced

The bootstrap does not deliver 95%. At the 3 tasks per Skill this benchmark runs, it excludes zero
about **15% of the time when the true effect is exactly zero**. A rule that says "the 95% interval
excludes zero" was, in practice, running at roughly one false positive in seven.

This is the documented small-cluster failure of the cluster bootstrap rather than anything specific
to this harness, and three independent checks in `harness/power_check.py` confirm it is real:

| tasks (clusters) | bootstrap false positive rate | t interval | bootstrap half-width | true 1.96 SD |
| --- | --- | --- | --- | --- |
| 3 | **0.157** | 0.048 | 5.26 | 6.16 |
| 4 | 0.107 | 0.045 | 4.87 | 5.34 |
| 5 | 0.107 | 0.056 | 4.50 | 4.77 |
| 10 | 0.065 | 0.057 | 3.42 | 3.38 |
| 30 | 0.038 | 0.045 | 2.08 | 1.95 |

The bootstrap converges to its nominal rate as clusters are added, which is the signature of the
small-cluster problem and not of a coding error; the t interval is correctly sized at every cluster
count; and at k=3 the bootstrap's interval is measurably narrower than the true sampling
uncertainty it is supposed to cover.

The worst part is the direction of the failure with respect to what we were doing about it. The
shortfall lives in the cluster count, so **adding samples per task makes it worse, not better**: at
3 tasks the false positive rate is 12.6% at 3 samples, 15.2% at 6, and 17.4% at 12. The wave that
was in flight when this was found had just been topped up from 3 samples to 6 specifically to
strengthen its conclusions. It was buying a narrower interval around a mean whose real uncertainty
was set by having 3 tasks.

**This is not a change to the rule.** The rule has always been "the 95% confidence interval on the
judge point delta excludes zero." The bootstrap was not a 95% interval, so this is the rule's first
correct implementation. The distinction matters because changing a rule after seeing which cells it
fails is the thing this benchmark most wants to be unable to do, and the check on that claim is the
direction of the correction: it removed two of the three standing results and added none. Section
11 lists what came down.

Two quantities carry intervals:

- **Judge point delta**, the mean of (skill rubric score minus base rubric score) across pairs, on
  a 100-point scale. Its null is 0.
- **Win rate**, where a win counts 1, a tie counts 0.5 and a loss counts 0, the standard
  convention. Its null is 50%. A pair whose two presentation orders disagree is a tie and lands at
  0.5, so order flips are absorbed here rather than hidden.

### What "resolved" means

**The normative rule: a cell counts as resolved only if the 95% confidence interval on the judge
point delta excludes zero, in either direction.** This is the rule fixed before the results were
read, and it is the rule a cited score is read against.

The harness records a finer label alongside it. It emits `pts` when the delta interval excludes 0,
`win` when the win-rate interval excludes 50, `pts+win` when both do, and `unresolved` when neither
does. That label is diagnostic and is published with each cell, but it is **not** the publication
rule. Widening the rule to "delta **or** win rate" after the results were read would be exactly the
kind of after-the-fact rule change the rest of this benchmark refuses, so the harness label stays a
second opinion rather than a second definition. Every cell published so far reads `pts+win` or
`unresolved`, so no published figure turns on the difference.

"In either direction" is load-bearing and was not always implemented. An interval sitting entirely
below zero excludes zero just as cleanly as one sitting entirely above it, and it means the Skill
measurably made the work worse. The catalog renderer originally tested `ci[0] > 0`, which could
not express that case: a resolved harm either rendered as "not resolved" or dropped its evaluation
block off the page entirely. It now tests both bounds and gives a resolved harm its own label,
"Measured regression", with the same prominence a resolved gain gets. Nothing published today
changes, because no published interval sits below zero. The rule is stated this way so that the
first one can be published rather than hidden.

### Reading an unresolved cell

Absence of a resolved effect is not evidence of no effect. Two skills carry large point estimates
and do not resolve; they are reported as unresolved, not as wins and not as nulls. An interval that
stops excluding zero when `n` doubles while the point estimate barely moves was never as tight as
the smaller sample made it look. The conservative reading is the published one.

---

## 6. Pre-registration

Every wave pre-registers its sample size in a dated file before any aggregate for that wave exists.

**Convention:** `results/PREREGISTRATION-<YYYY-MM-DD>.md`, written at a point when no summary for
the runs in flight exists on disk and no judge output from them has been read. The file states the
sample size, lists every skill and run tag it binds, states why the choice is not optional
stopping, restates the resolution rule, and states what happens when a run falls short.

The live example is `results/PREREGISTRATION-2026-09-17.md` in the harness working tree on AX41,
which fixed 6 samples per task per arm for the `bf-v1`, `t2-v2` and `new-v1` run tags.

**Where it lives:** `evals/preregistrations/<YYYY-MM-DD>.md` in this repository, committed on its
own, before the runs it binds start. The commit date in the public git history is the timestamp, and
it is the whole point of the location: a claim that a sample size was fixed before the numbers were
read is worth nothing if the only witness is the person who benefits from it. Anyone can check a
commit date; nobody can check a private file.

That rule takes effect from the wave after the current one, and the current one does not satisfy it.
`PREREGISTRATION-2026-09-17.md` was written in the harness working tree on AX41 before any summary
for `bf-v1`, `t2-v2` or `new-v1` existed, and it is committed here unchanged, but it is committed
after the fact. Its commit date proves it existed by then and proves nothing about the order. We say
so rather than letting the file's presence in a public repository imply a guarantee it does not
carry. One wave of trust, then the timestamps take over.

---

## 7. How a result gets withdrawn

A benchmark that only publishes the numbers that worked is not a benchmark. Ten computed results
have been withdrawn under this benchmark. Six went because auditing the task showed that the task
was broken rather than the skill. Four went because the interval was not a 95% interval, on tasks
that are sound.

**The rule that is settled:** a withdrawn result is **removed, not quietly rewritten**. The number
is gone, not downgraded. The withdrawal and its reason are published, named skill by named skill,
with the figure that was withdrawn stated in full including its interval. The record is
[`evals/WITHDRAWN.md`](../evals/WITHDRAWN.md).

One thing that record makes plain and this section should not bury: none of the six task-defect
withdrawals was ever public. They lived in a run summary and in report drafts for about a day, and
the site has carried no evaluation figures at any point. Two of the four interval withdrawals had
been published, on the `harness-first` and `autonomous-research` Skill pages, and those pages now
carry the correction inline beside the number it retracts. Writing all of them down is the part that
matters. A benchmark that only records the retractions that got far enough to embarrass it has a
withdrawal policy in name only.

The withdrawals so far were triggered by these defects, and every rebuilt task is now written
against the list:

1. **The checker grades prose.** If a well-written description of the work can pass, the task
   measures writing. The checker must inspect or execute the real artifact.
2. **A gate is passable by hedging.** Any criterion a caveat can satisfy will be satisfied by a
   caveat.
3. **The baseline has no room to fail.** If a competent agent with no skill scores 95, the task
   cannot measure anything. Ceiling effects look like null results.
4. **The input contains the answer.** Supplying the data the task is supposed to find turns a
   search task into a filtering task.
5. **The judge cannot perceive what it grades.** Anything the judge must score has to be visible to
   the judge.
6. **Limits are not arm-neutral.** If one arm truncates and another does not, the comparison is
   between a finished answer and an unfinished one.
7. **A stub scores above zero.** Run the checker against an empty deliverable before trusting it.
   A gate phrased as an exclusion passes vacuously when there is nothing to exclude.
8. **The interval is not a 95% interval.** The first seven are properties of a task. This one is a
   property of the estimator and it invalidates every figure at once, which is why it cost four
   results rather than one. Any interval this benchmark publishes has to be measured against a
   known truth at the cluster count it will actually run at, before it is used to resolve anything.
   Section 5 is that measurement.

A harness defect can also invalidate a figure without invalidating the task. One published summary
computed its checker pass rate, cost, turn count and finish rate over every attempt on disk while
the judge delta covered only the scored subset. The aggregator now restricts those statistics to
the attempts backing the judged pairs and records which of the two it did, and the file with the
wrong scope is kept alongside the corrected one rather than deleted.

### The procedure

**Who authorises one.** Anyone may open a withdrawal; the repository maintainer records it. There is
deliberately no approval gate on the way out. A gate on withdrawing a number is a gate that only ever
delays bad news, and the asymmetry this benchmark has to defend against is the pull toward keeping a
flattering figure up. Publishing a figure needs a pre-registration and a resolved interval.
Retracting one needs a reason written down.

**Where the record lives.** `evals/WITHDRAWN.md` in this repository, one entry per withdrawn figure,
appended and never edited or reordered. An entry names the Skill, the arm, the run tag, the figure as
it was published, the dates it was up, the defect, which of the eight failure modes above it was, and
what replaced it, or that nothing did. The raw attempts and judgments of a withdrawn figure stay on
disk and in the evidence bundle. A withdrawal removes a claim, not the evidence that the claim was
once made; deleting the evidence would make the withdrawal itself unauditable.

**Whether it bumps the version.** A withdrawal on its own does not. Withdrawing a figure says the
measurement was wrong, and `edge-skill-bench@1.0` names a measurement procedure and a task set, not a
table of results. What does bump the version is a change to the thing being withdrawn *from*: if the
withdrawal is repaired by rebuilding a task, tightening a checker, or changing a limit, the bump comes
from that repair under the policy in section 8, not from the withdrawal.

**How a reader holding a cited score finds out.** Three places, in order of how likely someone is to
land on them. The Skill's page on getedge.cc shows only current figures and carries a link to the
withdrawal record when one of its figures has been withdrawn. `evals/WITHDRAWN.md` is the canonical
list and is searchable by the figure itself, so a reader holding "+14 points" and nothing else can
find it. And the withdrawn figure's own `EVALS.md` section is replaced by the withdrawal notice
rather than deleted, so a stale deep link lands on the correction instead of a 404.

This is the honest limit of it: nothing here reaches a reader who saved a number and never comes back.
A benchmark cannot recall a figure that is already in someone's slide deck. What it can do is make
sure that every path back to the source ends at the correction, and that is what these three do.

---

## 8. What `@1.0` freezes

`edge-skill-bench@1.0` is the first publicly nameable freeze. A score is only comparable to another
score at the same version.

Frozen at a version, on the evidence above: the task set in scope, each task's prompt, inputs,
rubric and checker, the three arms, the two signals and the blinding rules, the pre-registered
sample size, and the resolution rule.

### The versioning policy

One rule generates the whole table: **a change bumps the major version when it can move an existing
score, and the minor version when it cannot.** `@2.0` means old scores are not comparable to new
ones. `@1.1` means every `@1.0` score still stands and there is simply more of the benchmark.

| Change | Bump | Why |
| --- | --- | --- |
| A task is **added** | minor | Existing per-Skill cells are unchanged; a Skill measured on the old task set is still comparable to itself |
| A task is **withdrawn or rebuilt** | major | Every cell for that Skill was computed over a task set that no longer exists |
| A checker gate is **tightened** | major | The checker is one of the two signals, and a tightened gate changes pass rates that were already published |
| The **agent or judge model** changes | major | The score measures a Skill's effect on one model; on another model it is a different quantity wearing the same name |
| The **turn cap** changes | major | A cap that truncates one arm and not another manufactures a difference, which is why it is frozen at all |
| A **Skill enters or leaves scope** | minor | Scope is which cells exist, not how a cell is computed |
| **Sample size** rises for a future wave | minor | Each cell publishes its own `n`, and a larger `n` narrows an interval rather than moving the estimate it is around |
| The **resolution rule** changes | major | The same numbers would resolve differently, which is the definition of not comparable |

Two consequences worth stating out loud, because they are the ones that will be inconvenient.

A model change is a major bump, and models change often. That makes `edge-skill-bench@1.0` a
measurement of Claude Sonnet 4.5 specifically, not of the Skills in the abstract, and a `@2.0` on a
newer model cannot be read as the Skills having improved or decayed. This is a real limit of the
design rather than a rule we could have written our way out of: any comparison across models confounds
the Skill with the model.

And a checker repair is a major bump even when the repair is obviously correct. That is deliberate.
The tempting version of this policy exempts fixes, and "this change only made the checker more
correct" is exactly the judgment a maintainer is worst placed to make about their own benchmark
after seeing which way the numbers moved.

---

## 9. Reproducibility

Every trial page carries the prompt, the input files, the files the agent produced, the checker
output and both judge verdicts. The harness, the task definitions, the checkers and the per-run
summaries ship in this repository under `evals/`.

Two constraints on reading a published number:

- **The published package has to be the measured build.** Each Skill on the site carries a commit,
  a digest, a file list and the file contents a reader installs. These had drifted apart and have
  been rebuilt from one checkout so that all four describe one thing. `DERIVATION.json` is excluded
  from both the file list and the digest, so the digest is checkable from the page's own contents
  alone.
- **Our tasks.** The tasks were written for our own Skills. That is a real conflict of interest, and
  it is why every task, every deliverable, every checker output and both judge verdicts are
  published per trial rather than summarised.

Known limits that a citing reader should carry:

- One agent model and one judge model. Results may not transfer. "This skill helps our agent" is a
  much weaker claim than "this skill helps agents."
- Most cells are 9 to 18 pairs spread over 3 tasks, and 3 tasks is the binding constraint. The
  design is powered at about 0.42 for a 10-point effect and 0.16 for a 5-point effect. Below
  roughly 10 points, a null result here is close to uninformative and is not a null finding.
- A second agent, run from the same task definitions, gets its own column at the pre-registered
  sample size or it does not appear. It is never folded into a published cell.

---

## 10. Every gap, and where it was closed

The first version of this document carried eight questions it could not answer, each marked in
place. All eight are now answered. The list is kept because which questions a benchmark could not
answer at first is itself worth knowing, and because one of the answers turned out to invalidate
published results.

| # | Question | Answer | Section |
| --- | --- | --- | --- |
| 1 | Exact model snapshots, and are they frozen | Sonnet 4.5 `20250929`, Haiku 4.5 `20251001`, both frozen per version | 1 |
| 2 | Is the 40-turn cap part of the definition | Yes, frozen per version | 1 |
| 3 | Which arm is the citable default | `skill` | 2 |
| 4 | What power calculation selects 6 samples | None did, and the sample count was the wrong lever; the task count binds | 4 |
| 5 | Where a pre-registration lives once public | `evals/preregistrations/`, committed before the run it binds | 6 |
| 6 | The withdrawal procedure | Section 7, four parts, record at `evals/WITHDRAWN.md` | 7 |
| 7 | The versioning policy | Major when a change can move an existing score, minor when it cannot | 8 |
| 8 | A DOI of its own | No; versioned by this repository's tags and cited through its `CITATION.cff` | Citation |

Answering question 4 is what surfaced the miscalibrated interval in section 5, which is the largest
defect this benchmark has found in itself. It was found by trying to justify a number that had
already been published rather than by anyone challenging it from outside. That is an argument for
writing the gaps down.

---

## 11. Corrections to published results

### 2026-09-17: the interval was recalibrated, and four standing results came down

Section 5 documents the defect: the percentile cluster bootstrap that every figure before this date
was read off is anti-conservative at 3 tasks, excluding zero about 15% of the time at a true effect
of zero rather than 5%. Every cell was re-read against the calibrated interval. The estimates did
not move. The intervals widened.

The first pass of this re-reading was itself wrong, and the error is worth recording because it
is the same species as the one being corrected. It read each run's `summary.json` and reported 19
cells, 4 of which changed verdict. But several published pages cite a different summary file in the
same run: an independent-grader aggregate, or an aggregate over a sample-limited subset. Re-reading
only the default file skipped exactly the cells that some pages were built on, including the one
result `autonomous-research` had. The sweep below reads every summary file in every run.

47 distinct cells carry an interval, where a cell is a (run, Skill, arm, judged pair set) and not a
file, so the same aggregate written to several files is counted once. **10 of the 47 change verdict,
and every one of them changes the same way: resolved under the bootstrap, unresolved under the
calibrated interval. Not one goes the other way**, which is the direction the defect predicts and
the only direction it can produce.

Six of the ten belong to Skills already withdrawn for broken tasks: `linkedin-media-prep` `skill`
and `shadcn-first` `loaded` under each of the two graders, `security-audit-checklist` `loaded`, and
a superseded v1 figure for `top-down-comms`. The other four were standing results.

| Skill | Arm / run | Delta | Bootstrap 95% | Calibrated 95% | Outcome |
| --- | --- | --- | --- | --- | --- |
| `workplan` | `loaded` / `t3-v2` | +13.4 | [6.5, 20.8] | [9.4, 17.4] | **stands** |
| `strip-image-ai-metadata` | `loaded` / `t3-v2` | +35.1 | [13.8, 58.6] | [-23.0, 93.2] | withdrawn |
| `top-down-comms` | `loaded` / `td-v2` | +11.6 | [5.0, 17.4] | [-3.1, 26.2] | withdrawn |
| `harness-first` | `skill` / `hf-v1`, 12 pairs | +32.1 | [2.5, 62.8] | [-45.8, 110.0] | withdrawn |
| `autonomous-research` | `loaded` / `v1`, indep. grader | +3.1 | [0.2, 6.5] | [-1.4, 7.6] | withdrawn |

**One Skill has a resolved effect on this benchmark: `workplan`, `loaded`, +13.4 points, 95% CI
[9.4, 17.4].** The report that preceded this correction said three, and the Skill pages between them
claimed two more. All four of those were artifacts of an interval that was too narrow.

Three other cells still resolve under the calibrated interval and none is citable: `cli-ux-review`
`loaded` under both graders, and `http-error-triage` `loaded`. All three are from run `v1` and
belong to Skills withdrawn because their tasks were broken. A correct interval on a broken task is
still a broken measurement, and the recalibration does not reinstate them.

`autonomous-research` is the entry to read twice. Its bootstrap interval cleared zero by two tenths
of a point on a +3.1 point effect, and that was enough for the cell to be published as resolved and
for the Skill's page to be written around it. At a 15.7% false-positive rate, a result that clears
the bar by 0.2 points is roughly what you would expect to manufacture.

The one that survived is the one with the *smaller* point estimate. `strip-image-ai-metadata` was
the largest effect on the board at +35.1 points and it is gone, while `workplan` at +13.4 stands.
That is what an anti-conservative interval does and it is worth stating plainly, because it is the
opposite of the intuition that big effects are the safe ones: the bootstrap was narrow relative to
the truth everywhere, so the cells it wrongly resolved were the ones whose spread across tasks was
widest, and a wide spread across tasks tends to come with a large and unreliable mean.

The withdrawn figures and the reasoning are recorded in
[`evals/WITHDRAWN.md`](../evals/WITHDRAWN.md). Two of the four had never been published on
getedge.cc; the `harness-first` and `autonomous-research` figures had been, on their Skill pages,
and both pages now carry the correction inline beside the retracted number.

One further consequence of implementing the rule correctly. The win rate no longer resolves
anything. It is bounded between 0 and 100%, and a t interval on its per-task means is not: across
these runs it prints bounds such as [53.9, 101.7] and [-194.5, 245.4]. An interval that runs past
the range of the quantity it covers is not delivering 95% coverage near the bound, and the first of
those two would have resolved the weakest arm in the benchmark. The win rate is published as a
point estimate, the bootstrap's win-rate interval is not a substitute because it is the same
estimator measured in section 5, and a bounded interval is a pre-registration item rather than
something to improvise after seeing the numbers. Under this rule no published cell resolves on the
win rate, and the one cell that stands resolves on the point delta.

Under the policy in section 8 this would be a major bump, because the same numbers now resolve
differently. It is not one, because `edge-skill-bench@1.0` has never been released: there is no tag,
no DOI, and no deployed page carrying a figure from it. A version nobody can have cited is corrected
in place rather than by burning a number. `@1.0` therefore means the calibrated interval, and the
bootstrap era has no version name at all. This is the one time that reasoning is available, and it
is available only because the correction happened before the first release.

---

## Citation

**The benchmark does not get a separate DOI.** It is versioned by this repository's git tags and
cited through this repository's `CITATION.cff`, with the benchmark version named explicitly in the
text: `edge-skill-bench@1.0`. The tag is what makes that resolvable, because everything `@1.0`
freezes (the tasks, the rubrics, the checkers, the harness, the pre-registrations) lives in this tree
and is pinned by the same commit.

A second DOI would claim the benchmark is separable from the repository, and it is not: there is no
state in which someone has `edge-skill-bench@1.0` and does not have this tree. Minting two
identifiers for one artifact creates exactly one new thing, which is the possibility of them
disagreeing.

Until the first tagged release is cut and deposited, there is no DOI to give and the citation is the
repository URL plus the benchmark version. That is a missing artifact rather than an undecided
question.
