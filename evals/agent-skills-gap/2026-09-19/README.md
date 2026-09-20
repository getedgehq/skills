# Agent Skills Gap evaluation, 2026-09-19

This directory contains the complete direct Codex A/B run summarized in
[`agent-skills-gap/EVALS.md`](../../../agent-skills-gap/EVALS.md).

- `briefs/` contains the three frozen task definitions and objective verifiers.
- `fixtures/` contains the synthetic input logs supplied identically to both arms.
- `runs/` contains all 18 valid pairs, including outputs, metadata, transcripts, checks, and blind
  verdicts. It also retains the invalid Claude account-limit attempt that ended before either arm ran.

This is not an `edge-skill-bench@1.0` run. It uses a different agent and runtime and must not be
compared numerically with scores produced by that frozen benchmark.
