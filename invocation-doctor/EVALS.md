# Evaluation status

Status: inconclusive against an empty baseline.

On 2026-09-19, three paired Harbor runs used Codex with `openai/gpt-5.6-sol` to revise an overly broad skill description using train and held-out invocation cases. The objective gate required an unchanged skill body, explicit positive and near-miss triggers, and an accurate held-out report.

## Result

- Attempted pairs: 3
- Valid pairs: 2
- Treatment verifier passes: 2/3
- Baseline verifier passes: 2/3
- Valid blind verdicts: 2 ties
- Tool errors: 0 in both arms

Neither valid pair showed lift over the no-skill baseline. In the third pair, both arms misreported held-out predictions and split disclosure, so that pair was invalidated before winner aggregation.

This result shows the task can often be completed safely with or without the skill. It does not support an efficacy claim. The test covers one API-reference trigger task, one model, and two valid pairs. Reproducible artifacts are in `evals/invocation-doctor/2026-09-19/`.
