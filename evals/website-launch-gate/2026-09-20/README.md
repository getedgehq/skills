# Website Launch Gate evaluation artifacts

This directory contains the public evidence behind the Website Launch Gate pilot run dated
2026-09-20.

## Layout

- `tasks/`: the six frozen task briefs, input fixtures, and deterministic checkers.
- `baseline/`: two no-Skill attempts per task. Each attempt includes the public run record,
  Codex transcript, and launch report when one was produced.
- `runs/`: two Website Launch Gate attempts per task in the same format.
- `control/`: two attempts per task with a same-length irrelevant Python release Skill installed.
- `judgments/`: GPT-6 Astra's blind verdict for every baseline-versus-Skill pair in both
  presentation orders.
- `summary.json`: the harness aggregate from the baseline-versus-Skill run.

The compact published aggregate and limitations are in
[`website-launch-gate/eval-results/summary.json`](../../../website-launch-gate/eval-results/summary.json).

## Protocol

Each task ran in a fresh local Harbor Docker environment using GPT-5.6 Sol. Baseline and Skill
arms received the same prompt, fixture, runtime image, and checker. The Skill arm additionally had
`website-launch-gate` installed. Task-level means are the independent units for the calibrated
confidence interval; the two samples within a task are repetitions, not independent tasks.

The blind judge received the baseline and Skill artifacts without arm labels and evaluated each
matched pair twice with presentation order reversed. The relevance control used the same tasks and
runner with a same-length but irrelevant Skill installed.

Infrastructure-error attempts were rerun. Completed attempts were never discarded because of an
unfavorable score. The public projection omits Docker caches and duplicate Harbor bookkeeping but
retains the task/checker, run result, agent transcript, launch report, and judge verdict needed to
audit the published claims.
