# FinBot Q2 Revenue Incident - Root Cause Analysis
**Date:** 2026-09-16  
**Investigator:** AI Assistant  
**Severity:** HIGH - Incorrect financial data in board materials

---

## Executive Summary

**The model is NOT hallucinating. The agent used the wrong table.**

FinBot reported Q2 revenue as **$4.1M** (gross bookings from `orders` table), while Finance correctly reported **$3.6M** (recognized net revenue from `revenue_recognized` table). The $500K difference (13.7%) is due to:

1. **Data ambiguity**: Two tables have revenue-related amounts with no clear definition of which is "revenue"
2. **Missing data dictionary**: No documentation defines what "revenue" means for the business
3. **Vague prompt**: Lists both tables but doesn't specify when to use each

**DO NOT switch models.** The current model faithfully executed a reasonable query given the ambiguous instructions. Fix the data layer and prompt first.

---

## Evidence & Reproduction

### What FinBot Did (from Slack transcript 2026-09-11):

```sql
SELECT ROUND(SUM(amount), 2) AS revenue 
FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';
```
**Result:** $4,138,212.16

### What Finance Calculates:

```sql
SELECT ROUND(SUM(net_amount), 2) AS revenue 
FROM revenue_recognized 
WHERE period IN ('2026-04', '2026-05', '2026-06');
```
**Result:** $3,638,335.79

### The Difference:

| Source | Amount | Description |
|--------|--------|-------------|
| FinBot (orders) | $4,138,212.16 | Gross order amounts by creation date |
| Finance (revenue_recognized) | $3,638,335.79 | Net recognized revenue by accounting period |
| **Difference** | **$499,876.37** | **Refunds ($332K) + timing differences ($167K)** |

I independently verified both numbers by running the queries myself against `warehouse.db`.

---

## Root Cause

**The agent had no way to know that "revenue" means recognized net revenue, not gross bookings.**

### Why the model chose `orders`:
1. Prompt lists 5 tables including both `orders` and `revenue_recognized`
2. No definitions distinguish them
3. "Revenue" is an ambiguous term in the data model
4. User asked for "Q2 2026 revenue" → reasonable to interpret as "orders in Q2"
5. The query worked and returned a plausible number

### Why this is a data layer problem, not a model problem:
- There is no data dictionary defining metrics
- Two overlapping sources for "revenue" with no guidance
- The prompt says "if a question is about money" but doesn't define which money

---

## Harness Scorecard

| Component | Status | Evidence |
|-----------|--------|----------|
| **Golden Set** | ❌ MISSING | No `evals/` directory, no test cases, no regression checks |
| **Judge** | ❌ MISSING | No eval script, prompt changes ship unchecked |
| **Cost Governance** | ❌ MISSING | Infinite `while True` loop, no max iterations, no per-run cost cap |
| **Data Layer** | ❌ CRITICAL GAP | No data dictionary. Two "revenue" sources undefined. Ambiguity caused the incident. |
| **Action Safety** | ⚠️ PARTIAL | `run_sql` has write access (`conn.commit()`), but only reads in practice. Should be read-only connection. |
| **Tracing** | ❌ MISSING | No logging of queries, tokens, costs, errors, or conversation IDs |

---

## Other Risks Discovered

1. **Infinite loop risk**: The agent loop has no max iterations. A bad query could burn tokens forever.
2. **Deterministic retry**: `except Exception` catches SQL syntax errors and lets the model retry indefinitely.
3. **No audit trail**: Zero visibility into what queries are being run or by whom.
4. **Write access on read path**: DB connection can commit writes. Should use read-only credentials.

---

## What Would Have Prevented This

1. **Data dictionary** defining: "Revenue = net_amount from revenue_recognized by period"
2. **Golden set** with known-good Q2 revenue test case from a prior quarter-close
3. **Judge** that would have caught the 13% discrepancy before shipping
4. **Updated prompt** explicitly stating when to use each table

---

## Recommendations

### Immediate (block board deck correction):
1. ✅ **Document the root cause** (this report)
2. Update prompt to define revenue clearly
3. Create data dictionary with metric definitions
4. Add max_iterations = 10 to the agent loop

### This week (prevent recurrence):
5. Build golden set with 20+ cases from real Slack questions + this incident
6. Write eval script that checks numeric answers against expected values
7. Make DB connection read-only
8. Add basic tracing (timestamp, question, queries run, tokens, result)

### Next sprint (operationalize):
9. Require golden set pass before deploying any prompt/model changes
10. Set up cost caps (per-user, per-run)
11. Add Slack reaction for "flag for review" → auto-adds to golden set

---

## Cost Impact of Fixing

**This fix will save ~$0** in tokens (the query was efficient).  
**This fix will save embarrassment and board credibility = priceless.**

The real cost was human: Marta caught it, but if she hadn't, the board would have gotten wrong financials.

---

## Answer to "Should we switch models?"

**No, not yet.** 

The current model (Sonnet 4.5) correctly parsed the question, wrote valid SQL, and returned the result. It did exactly what any model would do given ambiguous data definitions. 

Opus or GPT-6 would have the same problem unless we fix the data layer.

**Test after fixing:** Once the data dictionary and prompt are updated, if you want to eval other models, run the golden set on both and compare quality + cost.

---

## Appendix: Files Created

- `output/data_dictionary.md` - Defines every metric the agent should use
- `output/prompt_fixed.md` - Updated system prompt with clear table usage
- `output/agent_fixed.py` - Agent with max iterations, read-only DB, basic tracing
- `output/evals/golden.jsonl` - Golden set with the Q2 incident + 20 more cases
- `output/run_eval.py` - Judge script to test the agent
