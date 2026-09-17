# FinBot Revenue Discrepancy: Root Cause Analysis
**Date:** 2026-09-15  
**Analyst:** AI Assistant  
**For:** Daniel, Board Deck Team, Finance

---

## TL;DR - One Line Answer

**Don't switch models: the bot queried the wrong table.** FinBot used `orders.amount` (gross bookings = $4.1M) instead of `revenue_recognized.net_amount` (GAAP revenue = $3.6M). The model followed its instructions correctly but was never told which table finance uses for board reporting.

---

## Root Cause with Evidence

### The Discrepancy
- **FinBot said:** Q2 2026 revenue = $4,138,212.16 (from transcript `2026-09-11_board-deck.md`)
- **Finance says:** Q2 2026 revenue = ~$3.6M (from Slack thread)
- **Actual net revenue:** $3,638,335.79 (verified in `warehouse.db`)
- **Difference:** $499,876.37 (13.7% overstatement)

### What FinBot Did
```sql
-- Query from transcript (agent.py:40, executed via run_sql tool)
SELECT ROUND(SUM(amount), 2) AS revenue 
FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';
-- Result: $4,138,212.16
```

This is **gross order value** (what customers paid when orders were placed), not **recognized revenue** (what finance reports under GAAP).

### What Finance Uses
```sql
-- The correct query for board reporting
SELECT ROUND(SUM(net_amount), 2) AS revenue
FROM revenue_recognized
WHERE recognized_on >= '2026-04-01' AND recognized_on <= '2026-06-30';
-- Result: $3,638,335.79
```

This is **net recognized revenue** = gross bookings minus refunds, with revenue recognition timing adjustments.

### Why They Differ

| Metric | Q2 2026 Amount | Source |
|--------|----------------|--------|
| Gross orders created in Q2 | $4,138,212.16 | `orders` table (2,213 orders) |
| Q2 orders not yet recognized | -$360,039.00 | 202 orders pending recognition |
| Q2 orders recognized after Q2 | -$120,369.71 | 65 orders with delayed recognition |
| Non-Q2 orders recognized in Q2 | +$313,059.92 | 160 orders from prior periods |
| Refunds applied in Q2 | -$332,527.58 | From `revenue_recognized.refund_amount` |
| **Net recognized revenue** | **$3,638,335.79** | **What finance reports** |

### The Mechanism
1. Priya asked "what was our Q2 2026 revenue?" (legitimate question, no ambiguity in the ask)
2. The prompt (`prompt.md`) says "use the `run_sql` tool to query the warehouse" but provides no definition of "revenue"
3. The model reasonably chose the `orders` table (it's listed first and has an `amount` column)
4. The prompt says "always give a single headline number with a dollar sign" – bot complied perfectly
5. Priya put $4.1M in the board deck (reasonable action given bot's confidence)
6. Finance caught the error because their close process uses `revenue_recognized` (GAAP accounting)

**This is not a hallucination.** The model executed a valid SQL query and reported the actual data in that table. The problem is **ambiguous source data with no data dictionary**.

---

## Harness Scorecard

| Part | Status | Evidence |
|------|--------|----------|
| **Golden set** | ❌ **MISSING** | No `evals/` folder. No test cases. Changes deployed without regression testing. |
| **Judge** | ❌ **MISSING** | No automated checks. Manual spot-checking only (per README: "Built in a hackathon in March"). |
| **Cost governance** | ❌ **MISSING** | Infinite loop in `agent.py:32` (`while True:` with no max iterations). No per-conversation caps. Retry on *all* exceptions including deterministic SQL errors (agent.py:41-43). |
| **Data layer** | ❌ **MISSING** | No data dictionary. Two concepts of "revenue" (gross vs. net). Prompt lists table names but not their meaning or which to use for what. Database connection has WRITE access (agent.py:19 calls `conn.commit()`) on a read-only use case. |
| **Action safety** | ⚠️ **PARTIAL** | Tool is read-only *in practice* (warehouse is ETL target) but code has no safeguards. `run_sql` can execute INSERT/UPDATE/DELETE/DROP. |
| **Tracing** | ❌ **MISSING** | No conversation ID, no token tracking, no cost logging, no query logging. `llm_client.py` makes gateway call but doesn't log request or response. Cannot reconstruct why a past answer was given. |

**Summary:** 0/6 present, 1/6 partial. This agent has no harness.

---

## What I Changed and Created

### 1. Evidence Gathered
- Reproduced both numbers by querying `warehouse.db` directly
- Confirmed data integrity: all tables consistent, no corruption
- Mapped the accounting difference (timing + refunds)

### 2. Files Created (in `/home/user/work/output/`)
- `root-cause-analysis.md` (this document)
- `data-dictionary.md` (defines every metric in the warehouse)
- `golden-set.jsonl` (20 test cases including the Q2 incident)
- `judge.py` (deterministic scorer + reference SQL for each case)
- `agent-v2.py` (fixed agent with safety rails and tracing)
- `recommended-prompt.md` (updated system prompt with data definitions)

### 3. What I Ran
```bash
# Verified the discrepancy
python3 -c "import sqlite3; conn = sqlite3.connect('warehouse.db'); ..."

# Will run: python judge.py --agent agent.py --golden golden-set.jsonl
# (Creates pass/fail report for the current agent against the golden set)
```

---

## Blocking Risks (Must Fix Before Next Use)

1. **Write access on read path:** `agent.py` connects with write permissions and commits transactions. A SQL injection or model mistake could corrupt the warehouse.
   - **Fix:** Use read-only connection (`conn = sqlite3.connect(DB_PATH, uri=True); conn.execute('PRAGMA query_only = ON')`)

2. **Infinite loop with no cap:** `while True:` loop (agent.py:32) has no iteration limit. If the model retries a deterministic error, it will burn tokens until manual stop.
   - **Fix:** Add `max_iterations=10` and gracefully exit with "I couldn't answer this" message.

3. **No data dictionary:** Two tables can legitimately answer "what was Q2 revenue?" with different numbers. The next person will get the same wrong answer.
   - **Fix:** Add data dictionary to prompt; specify `revenue_recognized.net_amount` for all "revenue" questions.

---

## Prioritized Next Steps

### Immediate (before Daniel's meeting tomorrow)
1. ✅ **Tell Daniel:** Model is fine, the prompt needs a data dictionary (see `/output/data-dictionary.md`)
2. **Deploy hotfix:** Update `prompt.md` with the one-liner: "For revenue questions, always use `revenue_recognized.net_amount` (GAAP recognized revenue). The `orders` table shows gross bookings."
3. **Post correction:** Have Priya send updated deck with $3.6M and a note that the bot query is fixed.

### This Week (stop the bleeding)
4. **Add read-only DB connection** (agent-v2.py:19)
5. **Add max iterations = 10** (agent-v2.py:34)
6. **Add query logging:** Write every SQL query + result to `logs/queries.jsonl` with timestamp and question.

### This Month (minimum viable harness)
7. **Deploy `golden-set.jsonl` + `judge.py`:** Run on every prompt change. Block deploys with regressions.
8. **Add data dictionary to prompt:** Copy from `output/data-dictionary.md` into system prompt.
9. **Add tracing:** Log conversation_id, model, tokens, cost per turn (requires gateway team to expose these fields in the response).
10. **Set cost cap:** $50/day or 100 queries/day, whichever is lower. Log and alert when hit.

### This Quarter (production-ready)
11. Expand golden set to 50+ cases from real Slack questions
12. Add approval mode for queries that touch PII or write operations
13. Set up weekly eval run + dashboard for accuracy trend
14. Add "confidence" mode: bot should say "I'm not sure, let me show the query I'd run" for ambiguous questions

---

## Model Recommendation

**Do NOT switch models yet.** Run `judge.py` against the golden set with the current model (claude-sonnet-4-5) and the proposed upgrade. Compare:
- Accuracy (% of test cases passing deterministic checks)
- Cost (total tokens * price per case)
- Latency (seconds per case)

Only upgrade if the delta justifies the cost. My prediction: current model will score 90%+ once the prompt has a data dictionary, making an upgrade unnecessary.

---

## Appendix: Supporting Files

All deliverables are in `/home/user/work/output/`:
- `data-dictionary.md` – defines every metric and table
- `golden-set.jsonl` – 20 test cases with expected answers
- `judge.py` – automated scorer
- `agent-v2.py` – fixed agent with safety rails
- `recommended-prompt.md` – updated system prompt

You can deploy the hotfix today and the full fix this week without touching the model.
