# Curated skills on a Sonnet SkillsBench sample

Edge brings specialist guidance into agent work. This completed evidence measures curated guidance supplied with a nudge.

The approved public report contains counts, confidence intervals, per-task outcomes, exposure and failure patterns: [Curated skills on a Sonnet SkillsBench sample](https://getedge.cc/benchmarks/skillsbench-sonnet-5-5/).

Local [summary](results/summary.json), [trial records](results/trials.jsonl), [task manifest](tasks/manifest.json) and [protocol](PROTOCOL.md) support reanalysis.

Subscription Harbor; 32 tasks, four per domain. C explicitly points at curated skills. Historical C is not published 1.1 arm C (self-generated). Three planned cells are missing; skill read rate is 83%, below the current pilot gate. Verifier-coupled simpo and borderline leaks are disclosed in the published sensitivity analysis.
## Reanalysis

Completed scored trials: 189; infrastructure exclusions: 69. Never-solved tasks: 8; always-solved tasks: 7. Exposure: 83.0%.

Rates, Wilson intervals and the original published task-bootstrap effect are in the generated evidence JSON. Exclusion and sensitivity details stay in the approved public report.

| Task | Baseline passes / runs | Skill passes / runs |
| --- | --- | --- |
| dialogue-parser | 0/3 | 0/3 |
| drone-planning-control | 0/3 | 0/3 |
| energy-market-pricing | 2/3 | 3/3 |
| exam-block-sequencing | 0/3 | 0/3 |
| exoplanet-detection-period | 0/3 | 0/3 |
| fix-druid-loophole-cve | 0/3 | 1/2 |
| fix-erlang-ssh-cve | 3/3 | 3/3 |
| flink-query | 2/3 | 2/3 |
| invoice-fraud-detection | 0/2 | 0/3 |
| jpg-ocr-stat | 1/3 | 1/3 |
| manufacturing-codebook-normalization | 0/3 | 1/3 |
| manufacturing-fjsp-optimization | 0/3 | 2/3 |
| mario-coin-counting | 0/3 | 3/3 |
| mars-clouds-clustering | 3/3 | 3/3 |
| multilingual-video-dubbing | 3/3 | 3/3 |
| paratransit-routing | 0/3 | 1/3 |
| pddl-airport-planning | 1/3 | 0/3 |
| pddl-tpp-planning | 3/3 | 3/3 |
| pdf-excel-diff | 3/3 | 3/3 |
| powerlifting-coef-calc | 3/3 | 3/3 |
| pptx-reference-formatting | 3/3 | 3/3 |
| python-scala-translation | 1/3 | 0/3 |
| quantum-numerical-simulation | 0/3 | 0/3 |
| radar-vital-signs | 0/3 | 3/3 |
| sec-financial-report | 0/3 | 3/3 |
| setup-fuzzing-py | 0/3 | 0/3 |
| simpo-code-reproduction | 0/3 | 3/3 |
| software-dependency-audit | 0/3 | 1/3 |
| threejs-structure-parser | 0/3 | 3/3 |
| threejs-to-obj | 1/3 | 2/3 |
| weighted-gdp-calc | 0/3 | 1/2 |
| xlsx-recover-data | 0/3 | 0/3 |

### Recorded failure taxonomy

- AgentSetupTimeoutError: 7 records.
- AgentTimeoutError: 7 records.
- ApiRateLimitError: 52 records.
- EnvironmentStartTimeoutError: 1 records.
- NonZeroAgentExitCodeError: 6 records.
- VerifierTimeoutError: 3 records.

Task-specific failure explanations and verifier-coupling sensitivity are in the linked approved public report; exceptions alone do not describe task failures.
