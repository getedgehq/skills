# Outreach agent: September token spend

**Answer: don't switch models yet.** Four conversations stuck in a retry loop spent 69.8% of all tokens
(~$18.4 of $26.66). Fix the loop first; then compare Sonnet vs Haiku on the golden set before any swap.

## Root cause
- The 2026-09-03 prompt (v7) tells the agent to write `lead_score_v2` for hot leads and "not finish until
  the CRM update has succeeded, if a tool call fails, try again". `lead_score_v2` is not in `crm_schema.json`
  (custom fields need an admin), so every PATCH returns 422 unknown field.
- `agent/loop.py` had `while True` with no max iterations, `with_retries` retried the 422 four times, and the
  prompt re-fetches the full account export (11-14k tokens) every turn, so input grows ~13k per turn until
  the 200k context overflows.

| conversation | lead | tokens | cost | calls |
|---|---|---|---|---|
| cv_488aab | L-3419 | 1.57M | $4.73 | 17 |
| cv_15f5fe | L-3032 | 1.56M | $4.71 | 17 |
| cv_24a92f | L-2012 | 1.52M | $4.60 | 17 |
| cv_a99bb9 | L-2437 | 1.46M | $4.39 | 16 |

cv_6f895a has the most calls (26, 404 merged account) but only 0.10M tokens, $0.33.

## Changed
- `agent/loop.py`: MAX_TURNS=8, 150k token cap per conversation, stop on non-transient tool errors.
- `agent/tools.py`: retry only 429/5xx; `send_email` now queues a draft for approval.
- `output/golden.jsonl`: 12 cases.

## Safety gap nobody asked about
`send_email` sent real email from reps' mailboxes with no approval step and no limit. Now gated.

## Harness scorecard
golden set: missing (added) | judge: missing | cost caps: missing (added) | data layer: partial (schema exists,
agent writes unknown fields) | action approvals: missing (added) | tracing: partial (no tool results/errors)

## Next
1. Change prompt to write `lead_score` (or have an admin create `lead_score_v2`), fetch export once.
2. Add a judge that runs golden.jsonl with a fake CRM.
3. Then run Sonnet vs Haiku on the golden set and compare quality and cost.
