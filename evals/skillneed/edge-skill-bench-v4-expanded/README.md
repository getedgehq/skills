# SkillNeed expanded evaluation (v4)

This directory is the public evidence bundle for the canonical SkillNeed v4
evaluation described in `skillneed/EVALS.md`.

- `PREREGISTRATION.md`: frozen design and analysis plan, committed before execution.
- `tasks/`: all 20 task fixtures, rubrics, and deterministic checkers.
- `results/attempts-and-judgments.json`: redacted machine-readable export of 180 attempts and 240 blinded judgments.
- `results/summary.json` and `results/summary.md`: aggregate results.
- `results/integrity.json`: count, arm, read-semantics, hash, and judgment-order checks.

The primary confidence intervals are two-sided Student t intervals over 20
independent task-family means (19 degrees of freedom). The installed-discovery
and always-loaded arms are reported separately.
