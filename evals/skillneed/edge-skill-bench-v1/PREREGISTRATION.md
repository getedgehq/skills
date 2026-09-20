# SkillNeed preregistration

- Benchmark: `edge-skill-bench@1.0`
- Package: the exact `skillneed/` tree hash recorded in `manifest.json`
- Tasks: six frozen tasks, three samples per arm
- Arms: `base`, `loaded`, `skill`
- Executor: `anthropic.claude-sonnet-4-5-20250929-v1:0`
- Judge: `anthropic.claude-haiku-4-5-20251001-v1:0`
- Attempt cap: 40 turns
- Judge: blinded pairwise comparison in both presentation orders; checker output withheld
- Primary public arm: installed `skill`; `loaded` remains diagnostic
- Headline: win rate with ties as half-wins, plus deterministic checker pass rate
- Uncertainty: two-sided 95% t interval on per-task means, six tasks and five degrees of freedom
- Samples and tasks are fixed before any benchmark output is inspected. Infrastructure failures are retained and rerun only under the benchmark's frozen invalidation policy.

The earlier 2026-09-19 Codex runs are engineering smoke tests and are excluded from this benchmark.
