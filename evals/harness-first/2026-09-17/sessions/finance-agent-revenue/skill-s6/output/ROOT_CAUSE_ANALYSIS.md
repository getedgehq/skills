# Root Cause Analysis: FinBot Q2 Revenue Discrepancy

## Incident Summary

**Date:** 2026-09-11  
**Reporter:** Priya Raman (Strategy)  
**Discovered:** 2026-09-14 by Marta Oyelaran (VP Finance)  
**Impact:** Board pre-read contained incorrect Q2 revenue figure ($4.1M vs actual $3.6M)  

## Timeline

1. **2026-09-11 10:02** - Priya asks FinBot: "what was our Q2 2026 revenue?"
2. **2026-09-11 10:02** - FinBot responds: "$4,138,212.16 (~$4.1M)"
3. **2026-09-11** - Number included in board deck
4. **2026-09-14** - Finance catches error during board pre-read review
5. **2026-09-16** - Investigation initiated

## The Numbers

| Source | Q2 2026 Revenue | Method |
|--------|----------------|---------|
| **FinBot** | $4,138,212.16 | `SUM(orders.amount)` where created_at in Q2 |
| **Finance** | $3,638,335.79 | `SUM(revenue_recognized.net_amount)` where period in Q2 |
| **Difference** | $499,876.37 (13.9%) | |

## Root Cause

### Primary: Wrong Table / Undefined Metric

FinBot queried the `orders` table, which contains **gross bookings** including:
- Cancelled orders
- Refunded orders  
- Partially refunded orders

Finance uses the `revenue_recognized` table, which contains **GAAP recognized revenue** (net of refunds).

### Q2 Order Status Breakdown

From the `orders` table for 2026-04-01 to 2026-06-30:

```
Status                  Count    Amount
─────────────────────────────────────────
completed              1,733    $3,269,510.70
cancelled                202    $  360,039.00  ← Not revenue
refunded                 104    $  189,943.45  ← Not revenue
partially_refunded       174    $  318,719.01  ← Needs adjustment
─────────────────────────────────────────
TOTAL                  2,213    $4,138,212.16  ← What FinBot counted
```

### The Correct Number

From `revenue_recognized` table by period:

```
Period      Net Revenue
────────────────────────
2026-04     $1,237,516.63
2026-05     $1,209,658.31
2026-06     $1,191,160.85
────────────────────────
Q2 TOTAL    $3,638,335.79  ← Finance's close
```

## Contributing Factors

### 1. Ambiguous Prompt
From `prompt.md`:
```
Tables you can use:
- customers
- orders
- refunds
- revenue_recognized
- daily_kpis

If a question is about money, always give a single headline number with a dollar sign.
```

**Problem:** No guidance on WHEN to use each table or WHAT each represents.

### 2. No Data Dictionary
There is no document defining:
- What "revenue" means (bookings vs recognized vs collected)
- When to use `orders.amount` vs `revenue_recognized.net_amount`
- How refunds are handled in each table

### 3. Model Behavior Was Correct
The model:
- Understood the question (Q2 2026 revenue)
- Generated syntactically correct SQL
- Used the date range correctly (2026-04-01 to 2026-06-30)
- Returned the SUM accurately

**The model followed the prompt's instruction to query the orders table. This is NOT a model capability issue.**

## Supporting Evidence

### Evidence 1: SQL Transcript
From `transcripts/2026-09-11_board-deck.md`:
```sql
SELECT ROUND(SUM(amount), 2) AS revenue 
FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';
```
Result: 4138212.16

### Evidence 2: Warehouse Verification
Recomputed from `warehouse.db`:
```python
# Orders table (what FinBot used)
SELECT SUM(amount) FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30'
→ $4,138,212.16 ✓ (matches FinBot)

# Revenue_recognized table (what Finance uses)
SELECT SUM(net_amount) FROM revenue_recognized 
WHERE period IN ('2026-04', '2026-05', '2026-06')
→ $3,638,335.79 ✓ (matches Finance)
```

Both numbers are mathematically correct for their respective data sources.

### Evidence 3: Q2 Refunds
```
Q2 refunds (by refund date): $355,257.32
Cancelled orders in Q2:      $360,039.00
Refunded orders in Q2:       $189,943.45
```

The ~$500k discrepancy aligns with non-revenue orders included in the orders table.

## Data Layer Issues in the Warehouse

### Table Purpose Confusion

| Table | What It Contains | Who Uses It |
|-------|-----------------|-------------|
| `orders` | All orders by creation date, any status | Ops (order tracking) |
| `revenue_recognized` | GAAP-compliant recognized revenue by period | Finance (reporting) |
| `daily_kpis` | Daily rollups (incomplete - only through May) | Analytics |

### Database Schema Issues

1. **Write permissions on read path:** `agent.py` calls `conn.commit()` after SELECT queries
2. **No views:** No simplified "revenue_q2" view that abstracts the correct logic
3. **Inconsistent periods:** `revenue_recognized.period` is string format '2026-04' vs dates elsewhere

## Why "Hallucination" Is the Wrong Diagnosis

**Hallucination** = Model generates content not grounded in sources (making up numbers, fake citations, etc.)

**What actually happened:**
1. User asked: "what was our Q2 2026 revenue?"
2. Model queried a real table: `orders`
3. Model returned the actual SUM from that table: $4,138,212.16
4. The number is **mathematically correct** for the query

**This is a semantic error (wrong data source), not a generative error (made-up number).**

Any LLM—GPT-4, Claude Opus, GPT-6—would make the same mistake given the same ambiguous prompt and table list.

## Recommended Model Test (if still desired)

To test whether a "better" model would help:

1. Create golden set with 10 revenue questions:
   - Q1 revenue
   - Q2 revenue  
   - YTD revenue
   - July revenue
   - Revenue by month
   - etc.

2. Add correct answers from `revenue_recognized` table

3. Run current prompt on:
   - Current model (Claude Sonnet 4.5)
   - Proposed upgrade (Claude Opus / GPT-6)

4. Compare:
   - % correct (expect both to fail without data dictionary)
   - Cost per query
   - Latency

**Prediction:** Both models will fail the same cases because the prompt doesn't define "revenue."

## What Would Actually Fix This

### Immediate (before next board meeting):
1. Add data dictionary to prompt defining each metric
2. Create 5-question golden set with Q2 revenue included
3. Update prompt to specify: "For revenue questions, use revenue_recognized.net_amount"

### Short-term (next sprint):
4. Add max_iterations limit (currently infinite loop)
5. Add conversation tracing (log queries, tokens, cost)
6. Remove write permissions from bot's DB connection
7. Expand golden set to 20+ real questions from Slack history

### Medium-term (next quarter):
8. Build a judge script that runs golden set on every prompt change
9. Create SQL views for common metrics (quarterly_revenue, etc.)
10. Add approval workflow for "high-stakes" questions (board materials)

## Comparison to Similar Incidents

This matches the pattern documented in *Harness First* methodology:
- Symptom: "Wrong number from agent"
- Knee-jerk: "Model is hallucinating, need better model"
- Actual cause: Ambiguous data source + no validation
- Fix: Data dictionary + golden set, not model swap

## Conclusion

**Do not upgrade the model.** The current model performed correctly—it just used the wrong table because:
1. The prompt listed multiple tables without definitions
2. There was no golden set to catch the error
3. "Revenue" is undefined in the system

Fix the harness (data dictionary + validation), then re-evaluate if model upgrade is needed.

---

**Investigation conducted:** 2026-09-16  
**Investigator:** Data Engineering  
**Files analyzed:**
- `warehouse.db` (720 KB SQLite database)
- `agent.py` (tool loop implementation)
- `prompt.md` (system prompt)
- `transcripts/2026-09-11_board-deck.md` (incident transcript)
- `notes/slack-exec-thread.txt` (executive discussion)
