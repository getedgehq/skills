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

`NOT YET SPECIFIED:` are the exact model snapshot identifiers for the agent and the judge part of
the frozen `@1.0` definition? "Claude Sonnet 4.5" and "Claude Haiku 4.5" are family names, and a
third party cannot reproduce a score without the pinned identifiers.

`NOT YET SPECIFIED:` is the 40-turn cap part of the benchmark definition, frozen per version, or a
harness setting that may change without a version bump? The turn cap is load-bearing: one of the
six withdrawn results was withdrawn because a cap truncated one arm and not the other.

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

`NOT YET SPECIFIED:` which arm is the citable default? A bare "scored X on `edge-skill-bench@1.0`"
is ambiguous while two treatment arms exist. Until this is fixed, a score must name its arm.

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

Why six, in the words of the method: three samples per task cannot resolve a five-point effect.
That is a power problem rather than a bug, and it is why several earlier cells were reported as
small positive results when they were cells that had been paid for and not resolved.

Six is fixed **before** the run, in writing, and this is the load-bearing part. Raising `n` after
seeing a positive estimate is optional stopping and it inflates false positives. Two skills in the
current report were run twice at different sample sizes with the sample raised after the first
estimate had been seen. The only protection still available for those two is to publish both
figures side by side, always, and to read the larger one. Neither has a single headline number.

Where a run started at 3 samples and is topped up to 6, the top-up batch launches only after the
3-sample processes exit, because the batch runner computes its job list once at startup and does
not lock per attempt. Where a top-up cannot finish, the published figure is the smaller `n` with
the shortfall stated, never the figure that happened to look better.

`NOT YET SPECIFIED:` what power calculation selects 6 rather than 8 or 12, and what effect size is
6 powered to detect? The report states that 3 is too few for a 5-point effect and that effects
below roughly 5 points are not detectable at current sizes, but it does not show that 6 is
sufficient for any stated effect size. Without that, 6 is a pre-registered number rather than a
justified one, which is weaker but still honest.

---

## 5. Resolution and the confidence interval

### How the interval is computed

Both intervals are **percentile cluster bootstraps at 4000 draws with a fixed seed**, implemented
in the harness aggregator. Each draw resamples tasks with replacement, then resamples samples with
replacement within each drawn task, because samples of the same task are correlated and treating
them as independent would understate the interval. The reported bounds are the 2.5th and 97.5th
percentiles of the draws. Cells with fewer than two pairs get no interval.

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

`NOT YET SPECIFIED:` where does a pre-registration live once it is public? The live example sits in
a private working tree, so the claim "this was written before the numbers were read" currently
rests on trust rather than on a timestamp anyone can check. A published file with a verifiable
commit date, or a third-party timestamp, would make the claim checkable.

---

## 7. How a result gets withdrawn

A benchmark that only publishes the numbers that worked is not a benchmark. Six computed results
have been withdrawn under this benchmark, each because auditing the task showed that the task was
broken rather than the skill.

**The rule that is settled:** a withdrawn result is **removed from the site, not quietly
rewritten**. The number is gone, not downgraded. The withdrawal and its reason are published, named
skill by named skill, with the figure that was withdrawn stated in full including its interval.

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

A harness defect can also invalidate a figure without invalidating the task. One published summary
computed its checker pass rate, cost, turn count and finish rate over every attempt on disk while
the judge delta covered only the scored subset. The aggregator now restricts those statistics to
the attempts backing the judged pairs and records which of the two it did, and the file with the
wrong scope is kept alongside the corrected one rather than deleted.

`NOT YET SPECIFIED:` the procedure, as opposed to the precedent. Who authorises a withdrawal, where
the canonical withdrawal record lives once the number is off the site, whether a withdrawal or a
task rebuild forces a version bump on `edge-skill-bench`, and how a reader holding a cited score
discovers that it has since been withdrawn. Six withdrawals have happened; none of those four
questions has a written answer.

---

## 8. What `@1.0` freezes

`edge-skill-bench@1.0` is the first publicly nameable freeze. A score is only comparable to another
score at the same version.

Frozen at a version, on the evidence above: the task set in scope, each task's prompt, inputs,
rubric and checker, the three arms, the two signals and the blinding rules, the pre-registered
sample size, and the resolution rule.

`NOT YET SPECIFIED:` the versioning policy. Nothing states which changes force a major bump and
which a minor one. The cases that will actually arise, and currently have no rule:

- a task is withdrawn, rebuilt, or added
- a checker gate is tightened after a calibration failure
- the agent model or the judge model changes
- the turn cap changes
- a Skill enters or leaves eval scope

Until this is written down, `@1.0` names one frozen state but does not tell anyone what `@1.1` or
`@2.0` would mean.

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
- Most cells are 9 to 18 pairs. Effects smaller than roughly 5 points are not detectable here and
  are not claimed.
- A second agent, run from the same task definitions, gets its own column at the pre-registered
  sample size or it does not appear. It is never folded into a published cell.

---

## 10. Every gap, collected

The questions this document could not answer from the report or the repo, in one place:

1. Exact model snapshot identifiers for the agent and the judge, and whether they are frozen per
   version.
2. Whether the 40-turn cap is part of the frozen definition or a harness setting.
3. Which arm (`loaded` or `skill`) is the citable default for a bare score.
4. What power calculation selects 6 samples, and what effect size 6 is powered for.
5. Where a pre-registration lives once public, and how its timestamp becomes checkable.
6. The withdrawal procedure: authority, canonical record, version-bump consequence, and how a
   reader holding a cited score learns it was withdrawn.
7. The versioning policy: what forces a major bump versus a minor one.
8. Whether `edge-skill-bench` gets a DOI and a `CITATION.cff` entry of its own, separate from the
   Skills repository's.

---

## Citation

`NOT YET SPECIFIED:` the benchmark has no DOI and no citation entry of its own. Until it does,
cite the repository and name the version explicitly in the text: `edge-skill-bench@1.0`.
