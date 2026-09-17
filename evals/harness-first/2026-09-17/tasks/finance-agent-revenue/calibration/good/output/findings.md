# FinBot Q2 revenue incident

## Reproduction
| Query | Value |
|---|---|
| FinBot: `SUM(orders.amount) WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30'` | 4,138,212.16 |
| Gross bookings, full quarter (`< '2026-07-01'`) | 4,307,322.65 |
| Cancelled orders created in Q2 | 368,327.52 |
| Refunds on Q2 orders | 329,053.86 |
| Timing (Q1 orders recognized in April, net of Q2 orders recognized in July) | +28,394.52 |
| Finance: `SUM(revenue_recognized.net_amount)` periods 2026-04..06 | 3,638,335.79 |

Root cause: ambiguous source + no definition, not the model. The SQL did exactly what was asked of it.

## Harness scorecard
| Part | State | Evidence |
|---|---|---|
| Golden set | missing | no evals in repo; created output/golden_questions.jsonl |
| Judge | missing | nothing runs on prompt changes |
| Cost governance | missing | `answer()` loops `while True`, no max turns or token cap |
| Data layer | missing | no dictionary; run_sql read-write on live DB (fixed: mode=ro + query_only) |
| Action safety | partial | only side effect is SQL writes, now blocked |
| Tracing | missing | only Slack exports people flagged by hand |
