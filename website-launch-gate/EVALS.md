# Did this Skill actually help?

We tested Website Launch Gate against an empty-skill baseline on six independent messy website
fixtures. Both arms used the same GPT-5.6 Sol agent, task, filesystem, and executable checker. The
only intended difference was whether this Skill was installed. Each baseline-versus-Skill pair was
also judged blind by GPT-6 Astra in both presentation orders.

**Across 24 attempts, the executable score rose from 50.9% to 63.2%: a +12.3 point lift. All six
task effects were nonnegative. The blind judge recorded 8 Skill wins, 2 ties, and 2 losses across
12 matched pairs.**

Run date: 2026-09-20. This is a six-task pilot and has not been independently repeated.

## The numbers

| Measure | With the Skill | Without it | Difference |
| --- | ---: | ---: | ---: |
| Executable checker | **63.2%** | 50.9% | **+12.3 points** |
| Blind judge score | **70.8** | 57.8 | **+13.0 points** |
| Blind win / tie / loss | **8 / 2 / 2** | — | — |

The task-clustered calibrated 95% interval was +0.4 to +24.2 points for the executable checker and
+6.5 to +21.5 points for the blind judge score.

## The six tasks

| Task | Baseline | Website Skill | Skill minus baseline |
| --- | ---: | ---: | ---: |
| Checkout validation | 27.8% | **50.0%** | **+22.2** |
| Developer docs and links | 62.5% | 62.5% | 0.0 |
| Local service and mobile | 61.1% | 61.1% | 0.0 |
| Newsletter consent | 37.5% | **50.0%** | **+12.5** |
| Product launch discovery | 50.0% | **77.8%** | **+27.8** |
| SaaS waitlist | 66.7% | **77.8%** | **+11.1** |

## Relevance control

We also ran 12 attempts with a same-length but irrelevant Python release Skill installed. Website
Launch Gate scored 63.2% versus 51.9% for that control, an +11.3 point difference, with no negative
task effects. The six-task 95% interval crossed zero (-2.0 to +24.7), so this is directional
evidence rather than a settled estimate. The irrelevant Skill was installed but never read; this
control tests relevance-aware Skill selection, not forced exposure to irrelevant instructions.

## What the checker required

The fixtures contained working behavior that careless launch edits could damage. Deterministic
checks inspected the final files and observable behavior across form validation, consent, mobile
layout, metadata, links, accessibility, and launch reporting. A polished report that fixed nothing
failed calibration.

## Limits

- Six independent tasks are enough for a pilot, not a universal claim.
- One of 12 Skill attempts did not read the Skill. It remains in the intent-to-treat result.
- No individual attempt achieved a perfect checker score; the claim is improvement, not complete
  launch readiness.
- One agent family and one judge family were used.
- The tasks and verifiers were authored by the publisher.
- Claude was unavailable because its subscription weekly limit was reached.
- Infrastructure-error attempts were rerun; no unfavorable completed attempt was discarded.

The task definitions and checkers, 24 baseline/Skill run records and agent transcripts, 12
irrelevant-control run records, and all 24 blind presentation-order verdicts are published in
[`evals/website-launch-gate/2026-09-20/`](../evals/website-launch-gate/2026-09-20/). The
machine-readable aggregate is in [`eval-results/summary.json`](eval-results/summary.json). If an
aggregate disagrees with a raw artifact, the raw artifact is authoritative.

Source checklist credit: [Suraj Sharma, “20 tasks for Claude before website launch”](https://x.com/suraj_sharma14/status/2101154043720876226).
