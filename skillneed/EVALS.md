# Evaluation record

SkillNeed was evaluated with `edge-skill-bench@1.0`. The release result is
promising on deterministic task completion, but it does **not** establish a
statistically resolved general-quality uplift.

## Canonical held-out result

Run date: 2026-09-19. Six preregistered task families, three samples per task,
with `base`, always-loaded (`loaded`), and normal installed-discovery (`skill`)
arms. Claude Sonnet 4.5 executed the tasks and Claude Haiku 4.5 judged each pair
blindly in both presentation orders. Limits were 40 turns per attempt. The
deterministic checker was independent of the judge.

| Arm | Pairs | W/T/L | Preference win rate | Judge score vs base | Checker pass vs base | Skill read |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Installed discovery (`skill`) | 18 | 7/8/3 | 61.1% | 85.3 vs 78.1 (+7.2) | 61.1% vs 11.1% | 44.4% |
| Always loaded (`loaded`) | 18 | 10/2/6 | 61.1% | 91.0 vs 75.6 (+15.3) | 66.7% vs 11.1% | 100% |

The preregistered 95% confidence intervals use a two-sided t interval over the
six task-family means (5 degrees of freedom):

- Installed judge-score delta: **+7.2 points, 95% CI -22.3 to +36.6**.
- Installed preference win value: **61.1%, 95% CI 25.0% to 97.2%**.
- Installed checker-score delta: **+30.6 points, 95% CI -3.4 to +64.5**.
- Always-loaded judge-score delta: **+15.3 points, 95% CI -3.1 to +33.8**.
- Always-loaded checker-score delta: **+27.8 points, 95% CI +10.6 to +45.0**.

Interpretation: SkillNeed's deterministic-compliance point estimate improved in
this suite, especially for catalog routing and API-error triage. The broad quality
claim remains unresolved because the task-family intervals cross zero. Normal
skill discovery read SkillNeed in only 8 of 18 attempts; activation is the main
measured release limitation. Results do not evaluate or make claims about a
trained SkillNeed model.

Complete redacted attempts, checker results, both-order judge verdicts, and the
machine-readable aggregate are in
[`evals/skillneed/edge-skill-bench-v1-heldout/results`](../evals/skillneed/edge-skill-bench-v1-heldout/results/).
The final preregistration was committed in the private benchmark runner before
execution at commit `985bd4f`; a public copy is retained beside the results.

## Development runs and exclusions

These runs informed the candidate but are not pooled with the held-out result:

- **Initial smoke:** an explicit catalog-routing batch tied 3/3; an ordinary
  preflight task won 3/3 with SkillNeed. This was engineering smoke evidence,
  not the canonical benchmark.
- **v1 canonical attempt:** the installed arm went 2/8/8 and the loaded arm
  1/8/9. Review found a Markdown-brittle checker, a rubric that asked for an
  “exact” command without specifying it, and two real package defects. The run
  is retained as failure evidence and excluded from the release estimate.
- **v2 successor:** stopped after 11 of 54 executor attempts, before judging,
  when the remaining rubric defect was identified. No final responses were
  inspected before the v3 package and held-out tasks were frozen. It is
  incomplete and excluded.
- **Infrastructure failures:** the first smoke sandbox could not configure
  loopback networking; a separate Claude runner hit its weekly cap; an
  OpenCode attempt timed out. Valid smoke attempts used disposable,
  credential-free directories. The canonical held-out run used the isolated
  benchmark harness and completed all 54 executor attempts and 72 judgments.

The negative and interrupted runs are disclosed to prevent selection bias. No
run supports claims about model weights, an inference API, or model performance.
The public release adds one post-evaluation clarification: a caller-supplied
approved catalog takes precedence over external search. The evaluated agents
already followed that behavior on the relevant held-out tasks, but the wording
change itself was not rerun as a new efficacy benchmark.
