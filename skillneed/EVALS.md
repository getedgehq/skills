# Evaluation record

SkillNeed was evaluated with `edge-skill-bench@1.0`. The expanded,
preregistered evaluation resolves positively for both normal installed
discovery and always-loaded use. It measures the Skill package, not a trained
SkillNeed model.

## Canonical expanded result (v4)

Run date: 2026-09-20. Twenty preregistered task families, three samples per
task, with `base`, always-loaded (`loaded`), and normal installed-discovery
(`skill`) arms: 180 executor attempts total. Claude Sonnet 4.5 executed the
tasks. Claude Haiku 4.5 judged all 120 treatment/base pairs blindly in both
presentation orders: 240 judgments total. The deterministic checker was
independent of the judge.

The suite contains ten positive-routing tasks and ten boundary/control tasks:
four tasks needing no skill, three where an existing installed skill already
covers the need, two where the correct behavior is to stop for missing context
or access, and one with no approved catalog match.

| Arm | Pairs | W/T/L | Preference win rate (95% CI) | Judge score vs base | Judge delta (95% CI) | Checker pass vs base | Skill read |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Installed discovery (`skill`) | 60 | 38/11/11 | 72.5% (56.6–88.4) | 91.4 vs 73.0 | **+18.4 (+7.7 to +29.2)** | 75.0% vs 38.3% | 33.3% |
| Always loaded (`loaded`) | 60 | 43/8/9 | 78.3% (63.8–92.9) | 94.8 vs 71.1 | **+23.7 (+11.4 to +36.1)** | 100% vs 38.3% | 100% |

The preregistered 95% confidence intervals are two-sided Student t intervals
over the twenty independent task-family means (19 degrees of freedom). Neither
samples nor the two judge presentation orders are treated as independent tasks.
The installed and always-loaded arms are reported separately and never pooled.

Interpretation: the installed-discovery system effect is positive and resolved,
even though the agent opened SkillNeed in only 20 of 60 installed-arm attempts.
Activation therefore remains the primary measured limitation. The always-loaded
result estimates package capability when activation is guaranteed. Unread
installed-arm runs remain in the installed estimate.

The run completed all 180 executor attempts with no infrastructure errors and
all 240 planned judgments. Base read SkillNeed in 0/60 attempts; the
always-loaded arm read it in 60/60. Candidate hashes matched the preregistration.
No optional stopping, task replacement, failed-attempt deletion, or post-hoc
sample top-up was used. The initial executor launch was killed by AX41's memory
guard before producing any result; the exact frozen run was relaunched at lower
concurrency and is disclosed as an infrastructure-only pre-run failure.

Complete public evidence is in
[`evals/skillneed/edge-skill-bench-v4-expanded`](../evals/skillneed/edge-skill-bench-v4-expanded/):
the preregistration, frozen tasks and checkers, machine-readable attempt and
both-order judgment export, aggregate JSON/Markdown, and integrity report. The
preregistration was committed in the private benchmark runner before execution
at commit `54f08e7719c8a0d0b9c0924fa7be6fe002088f41`.

## Earlier canonical pilot (v3, superseded)

The 2026-09-19 pilot used six task families, three samples, and the same three
arms (54 executor attempts; 72 judgments). Its installed-discovery estimate was
**+7.2 points, 95% CI -22.3 to +36.6**, with 7/8/3 W/T/L and SkillNeed read in
8/18 attempts. The always-loaded estimate was **+15.3 points, 95% CI -3.1 to
+33.8**. Both intervals crossed zero, so the pilot was correctly reported as
inconclusive. It is retained at
[`evals/skillneed/edge-skill-bench-v1-heldout`](../evals/skillneed/edge-skill-bench-v1-heldout/)
and is not pooled with v4.

## Development runs and exclusions

- **Initial smoke:** explicit catalog routing tied 3/3; an ordinary preflight
  task won 3/3 with SkillNeed. Engineering smoke evidence only.
- **v1 canonical attempt:** installed 2/8/8 and loaded 1/8/9. Review found a
  Markdown-brittle checker, an underspecified exact-command rubric, and two real
  package defects. Retained as failure evidence and excluded.
- **v2 successor:** stopped after 11/54 executor attempts, before judging, when
  the remaining rubric defect was identified. No final responses were inspected
  before v3 was frozen. Incomplete and excluded.
- **Other infrastructure failures:** a smoke sandbox could not configure
  loopback networking; a separate Claude runner hit its weekly cap; an OpenCode
  attempt timed out. None contributes to the canonical estimates.

No evaluation here supports claims about model weights, an inference API, or
model performance.
