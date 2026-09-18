# Withdrawn results

Every figure this benchmark has computed and then retracted, in the order the retractions happened.
Entries are appended. They are never edited, reordered or removed, because a withdrawal record that
can be rewritten is not a record.

Each entry names the Skill, the arm, the run tag, the figure exactly as it was computed, where and
for how long it was readable, which of the eight failure modes in
[`docs/BENCHMARK.md` section 7](../docs/BENCHMARK.md) it was, and what replaced it.

The attempts and judgments behind a withdrawn figure stay on disk and in the evidence bundle. A
withdrawal removes a claim, not the evidence that the claim was made. Deleting the evidence would
make the withdrawal itself unauditable.

---

## 2026-09-17: six results, all from run `v1`

All six were computed on 2026-09-16 and withdrawn on 2026-09-17, after an audit of the tasks rather
than of the Skills. In every case the task was broken and the Skill was not on trial.

**None of the six was ever published on getedge.cc.** They existed in the run summary and in drafts
of the report, for roughly one day. The site has carried no evaluation figures at any point, which is
checkable: the deployed tree predates all of this work. We record them anyway. A benchmark that only
writes down the retractions that got far enough to embarrass it is keeping a marketing document.

### cli-ux-review

| | |
| --- | --- |
| Figure | +21.4 points, 95% CI [+15.6, +28.1] |
| Arm / run | `skill` / `v1` |
| Readable | run summary and report drafts, 2026-09-16 to 2026-09-17. Never on getedge.cc |
| Failure mode | 1, the checker grades prose |
| Replaced by | rebuilt tasks, re-running as `bf-v1` |

One of three tasks gave a full pass to a UX review whose own text said it had never run the CLI it
was reviewing. The checker graded the write-up rather than the work.

### linkedin-media-prep

| | |
| --- | --- |
| Figure | +17.3 points, 95% CI [+4.9, +25.0], on 3 pairs |
| Arm / run | `skill` / `v1`. The `loaded` arm on 9 pairs was +8.3, CI [-20.5, +45.3], and did not resolve |
| Readable | run summary and report drafts, 2026-09-16 to 2026-09-17. Never on getedge.cc |
| Failure mode | 5, the judge cannot perceive what it grades |
| Replaced by | rebuilt tasks, re-running as `bf-v1` |

The judge never saw the images it was grading. It scored an image preparation task from text alone.
That does not make the result noisy, it makes it meaningless. The resolved figure also rested on
three pairs, which is thin enough on its own.

### people-search

| | |
| --- | --- |
| Figure | +12.2 points, 95% CI [-12.0, +43.1] |
| Arm / run | `skill` / `v1` |
| Readable | run summary and report drafts, 2026-09-16 to 2026-09-17. Never on getedge.cc |
| Failure mode | 4, the input contains the answer |
| Replaced by | rebuilt tasks, re-running as `bf-v1` |

Two of three tasks handed the agent the candidate list as an input file. They measured whether it
could filter a spreadsheet, not whether it could find people.

### http-error-triage

| | |
| --- | --- |
| Figure | +0.4 points, 95% CI [-3.1, +3.9] |
| Arm / run | `skill` / `v1` |
| Readable | run summary and report drafts, 2026-09-16 to 2026-09-17. Never on getedge.cc |
| Failure mode | 2, a gate is passable by hedging, together with a ceiling effect |
| Replaced by | rebuilt tasks, re-running as `bf-v1` |

Two faults at once. The no-skill baseline already scored about 96 out of 100, which leaves no room
for any Skill to show an effect. And one checker gate could be satisfied by adding any caveat
anywhere in a sentence.

### shadcn-first

| | |
| --- | --- |
| Figure | +8.8 points, 95% CI [+1.3, +17.4] |
| Arm / run | `skill` / `v1` |
| Readable | run summary and report drafts, 2026-09-16 to 2026-09-17. Never on getedge.cc |
| Failure mode | 7, a stub scores above zero |
| Replaced by | rebuilt tasks, re-running as `t2-v2` |

The tasks never compiled, rendered or clicked anything. A stub file passed the checker. A component
that did not exist scored the same as one that worked.

### security-audit-checklist

| | |
| --- | --- |
| Figure | +2.8 points, 95% CI [+0.1, +5.8] |
| Arm / run | `skill` / `v1` |
| Readable | run summary and report drafts, 2026-09-16 to 2026-09-17. Never on getedge.cc |
| Failure mode | 6, limits are not arm-neutral |
| Replaced by | rebuilt tasks, re-running as `t2-v2` |

On one task the Skill arm hit the turn cap on every single run while the baseline never did. The
Skill was cut off mid-work, so the comparison rests on a truncated answer.

---

## 2026-09-17, later the same day: four results, withdrawn by a recalibrated interval

These four were not withdrawn because a task was broken. The tasks are fine. The interval was wrong.

The percentile cluster bootstrap that every figure up to this point was read off is anti-conservative
at the small task counts this benchmark runs: measured against a known truth at 3 tasks, it excludes
zero about 15.7% of the time when the true effect is exactly zero, rather than the 5% a 95% interval
promises. The failure lives in the cluster count, so more samples per task make it worse rather than
better. [`docs/BENCHMARK.md` section 5](../docs/BENCHMARK.md) has the measurement and the three
checks behind it; section 11 has the full re-read.

Every cell in every summary file of every run was re-read against a correctly sized interval, a
two-sided 95% t interval on the per-task means. 47 distinct cells carry an interval. 10 change
verdict and every one of them changes the same way, from resolved to unresolved, which is the
direction the defect predicts and the only direction it can produce. No estimate moved and no count
moved. The intervals widened.

Six of those ten belong to Skills already withdrawn above for broken tasks and are not restated
here: `linkedin-media-prep` `skill` and `shadcn-first` `loaded`, each under both the original and
the independent grader, `security-audit-checklist` `loaded`, and a superseded v1 figure for
`top-down-comms` that its own page already marked as replaced. The four below are results that were
standing when the recalibration ran.

### strip-image-ai-metadata

| | |
| --- | --- |
| Figure | +35.1 points, 95% CI [+13.8, +58.6] |
| Arm / run | `loaded` / `t3-v2`, 3 tasks, 18 pairs |
| Recomputed | +35.1 points, calibrated 95% CI [-23.0, +93.2]. Does not resolve |
| Readable | run summary and report drafts, 2026-09-17, for part of one day. Never on getedge.cc |
| Failure mode | The eighth: the interval was not a 95% interval. The task set is sound |
| Replaced by | Nothing. The cell is unresolved and reads that way |

This was the largest measured effect in the benchmark. The three task means behind it have a
standard deviation of about 23 points, so the cell's estimate was never as precise as the bootstrap
interval made it look.

### top-down-comms

| | |
| --- | --- |
| Figure | +11.6 points, 95% CI [+5.0, +17.4] |
| Arm / run | `loaded` / `td-v2`, 3 tasks, 9 pairs |
| Recomputed | +11.6 points, calibrated 95% CI [-3.1, +26.2]. Does not resolve |
| Readable | run summary and report drafts, 2026-09-17, for part of one day. Never on getedge.cc |
| Failure mode | The eighth: the interval was not a 95% interval. The task set is sound |
| Replaced by | Nothing. The cell is unresolved and reads that way |

### harness-first

| | |
| --- | --- |
| Figure | +32.1 points, 95% CI [+2.5, +62.8] |
| Arm / run | `skill` / `hf-v1`, 3 tasks, 12 pairs |
| Recomputed | +32.1 points, calibrated 95% CI [-45.8, +110.0]. Does not resolve |
| Readable | `harness-first/EVALS.md`, which published it beside the 24-pair figure |
| Failure mode | The eighth: the interval was not a 95% interval. The task set is sound |
| Replaced by | Nothing. Neither sample size on that page resolves |

This one was already half-retracted. The page reported 12 pairs and 24 pairs side by side and said
the 24-pair figure, which did not resolve, was the one to believe. It read the widening interval as
a warning about the first result. It was a warning about the estimator: both figures sit on the same
3 tasks, so the samples were never the lever.

### autonomous-research

| | |
| --- | --- |
| Figure | +3.1 points, 95% CI [+0.2, +6.5] |
| Arm / run | `loaded` / `v1`, independent grader, 3 tasks, 9 pairs |
| Recomputed | +3.1 points, calibrated 95% CI [-1.4, +7.6]. Does not resolve |
| Readable | `autonomous-research/EVALS.md`, which was written around it. Never deployed to getedge.cc |
| Failure mode | The eighth: the interval was not a 95% interval. The task set is sound |
| Replaced by | Nothing. This Skill now has no resolved result on any task set |

This is the narrowest escape in the file. The bootstrap interval cleared zero by two tenths of a
point, on a +3.1 point effect, and that was enough for the cell to be published as resolved and for
the Skill's page to be written around it. A 15.7% false-positive rate is exactly the kind of defect
that produces a result like this one.

### What stands after this

One cell: `workplan`, `loaded`, +13.4 points, calibrated 95% CI [+9.4, +17.4], 3 tasks, 18 pairs.

Three further cells still resolve under the calibrated interval, and none of them is citable:
`cli-ux-review` `loaded` under both graders, and `http-error-triage` `loaded`. All three belong to
Skills withdrawn above because their v1 tasks were broken. A correct interval on a broken task is
still a broken measurement, and the recalibration does not reinstate them.

The four Skills below are measured and unresolved: `strip-image-ai-metadata`, `top-down-comms`,
`harness-first` and `autonomous-research`. An unresolved cell is not a finding of no effect. At
3 tasks this benchmark is powered at about 0.42 for a real 10-point effect, so it fails to resolve
real effects routinely, and all four Skills may well work. The correct reading is that we paid for
a measurement and did not get one. The repair is more tasks, not more samples.

---

## A note on what is not here

One published summary was corrected rather than withdrawn. It computed its checker pass rate, cost,
turn count and finish rate over every attempt on disk while the judge delta covered only the scored
subset, so two numbers in the same row described different denominators. The aggregator now
restricts those statistics to the attempts backing the judged pairs and records which of the two it
did. The file with the wrong scope is kept beside the corrected one.

That is a correction and not a withdrawal because the claim survived: the delta was right, and the
statistics printed next to it were computed over the wrong set. The distinction matters enough to
state, because the easy way to keep this file short is to call every retraction a correction.
