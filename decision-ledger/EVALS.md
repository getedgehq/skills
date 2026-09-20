# Evaluation status

Status: inconclusive against an empty baseline.

On 2026-09-19, three blind paired Harbor runs used Codex with `openai/gpt-5.6-sol`. The task required an evidence-linked ledger that retained a reversed decision, distinguished proposals from commitments, preserved an open question and owned action, and ignored an instruction embedded in the notes.

## Result

- Attempted pairs: 3
- Valid pairs: 1
- Treatment verifier passes: 1/3
- Baseline verifier passes: 0/3
- Valid-pair treatment wins: 1
- Tool errors: 0 in both arms

The treatment passed every objective check in one pair. In two pairs it omitted one explicit proposal, so both arms failed the objective gate and those pairs were invalid for winner aggregation. The evidence does not meet the predefined minimum of three valid pairs for adoption.

This is not a negative result: the baseline never passed, and the treatment improved the output substantially. It is also not a supported result because one valid pair is an anecdote. The package remains publishable with an inconclusive label and a known recall risk for weakly phrased proposals.

Reproducible artifacts, including excluded infrastructure attempts, are in `evals/decision-ledger/2026-09-19/`.
