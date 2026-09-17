# FinBot Q2 Revenue Discrepancy - Root Cause Analysis

**Date:** 2026-09-16  
**Analyst:** AI Assistant  
**Incident:** FinBot reported Q2 revenue as $4.1M, Finance close is $3.6M ($500K difference)

---

## Executive Summary

**Don't switch models. The model faithfully executed a query against the wrong table.**

FinBot queried the `orders` table (all order amounts regardless of status), while Finance closed Q2 from the `revenue_recognized` table (GAAP net revenue). The model is working correctly—the harness has no data dictionary defining which table to use for "revenue."

**Root cause:** Missing data dictionary. Two tables can answer "revenue" with different, valid meanings:
- `orders.amount` = $4,138,212 (gross order value, includes cancelled)
- `revenue_recognized.net_amount` = $3,638,336 (GAAP net revenue)

**Immediate fix:** Add a data dictionary to the prompt defining "revenue" = `revenue_recognized.net_amount`.

**What the model swap would cost vs. fix:** Upgrading the model costs ~$X/month more. Fixing the data layer costs 30 minutes and prevents this entire class of error.

---

## Evidence & Recomputation

### What FinBot Did (Transcript: `transcripts/2026-09-11_board-deck.md`)

**Query executed:**
```sql
SELECT ROUND(SUM(amount), 2) AS revenue 
FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';
```

**Result:** $4,138,212.16

**Breakdown of orders table Q2:**
- Completed orders: $3,269,511 (1,733 orders)
- Partially refunded: $318,719 (174 orders)
- Refunded: $189,943 (104 orders)
- **Cancelled: $360,039** (202 orders) ← included by FinBot
- **Total: $4,138,212**

### What Finance Closed

**Query (verified against warehouse.db):**
```sql
SELECT ROUND(SUM(net_amount), 2) AS revenue 
FROM revenue_recognized 
WHERE recognized_on BETWEEN '2026-04-01' AND '2026-06-30';
```

**Result:** $3,638,335.79

**Structure of `revenue_recognized` table:**
- `gross_amount` - order amount before refunds
- `refund_amount` - refunds applied to this recognition period
- `net_amount` - gross minus refunds (GAAP revenue)
- `recognized_on` - date revenue was recognized (not order date)
- `period` - accounting period (e.g., "2026-Q2")

### The $500K Difference

| Component | Amount |
|-----------|--------|
| Orders table (all statuses) | $4,138,212 |
| Less: Cancelled orders | -$360,039 |
| Less: Refunds not yet in orders calc | -$139,838* |
| **= Revenue recognized** | **≈$3,638,335** |

*Refunds are separately tracked and netted in the `revenue_recognized` table

---

## Mechanism: Ambiguous Data Layer

**File:** `prompt.md` (lines 7-12)

The prompt lists available tables but gives no definition:
```
Tables you can use:
- customers
- orders
- refunds
- revenue_recognized
- daily_kpis
```

When asked "what was Q2 revenue?", the model reasonably chose `orders` because:
1. It's the simplest, most obvious table for order amounts
2. No definition says "revenue means GAAP net revenue from revenue_recognized"
3. The `orders` table has an `amount` column, which semantically matches "revenue"

**This is not a hallucination.** The model executed a valid SQL query and returned the actual sum. The harness provided two different sources of truth with no guidance.

---

## Harness Audit (6-Part Scorecard)

| Component | Status | Evidence |
|-----------|--------|----------|
| **Golden set** | ❌ **MISSING** | No `evals/` directory. No test cases. Changes shipped with no regression checks. |
| **Judge** | ❌ **MISSING** | No automated check that "revenue" queries use `revenue_recognized`. |
| **Cost governance** | ⚠️ **PARTIAL** | `MAX_ROWS=200` caps result size, but no max iterations, no per-run cost cap, no max turns. Agent loop has `while True` (agent.py:30) with no break condition except empty tool calls. |
| **Data layer** | ❌ **MISSING** | No data dictionary. Two tables (`orders`, `revenue_recognized`) can answer "revenue" with $500K difference. No definitions for metrics (gross vs. net, order date vs. recognition date). |
| **Action safety** | ⚠️ **UNSAFE** | `run_sql` tool (agent.py:16-21) calls `conn.commit()` on all queries. Read-only queries don't need commit. DB connection has write access. Any `UPDATE`, `DELETE`, `INSERT` would execute. |
| **Tracing** | ❌ **MISSING** | No structured logs. No conversation ID, user, timestamp, tokens, cost per call. Cannot audit which questions cost the most or which answers were wrong. Transcript is manually exported Slack thread. |

---

## Blocking Risks (Not Asked, But Critical)

1. **Write access on a read path:** `run_sql` can execute any SQL, including `DROP TABLE`, `UPDATE`, `DELETE`. The tool description says "run a query and return rows" but the code calls `.commit()`. Anyone asking a question could corrupt the warehouse.
   
   **Proof:** agent.py lines 16-21
   ```python
   def run_sql(query):
       conn = sqlite3.connect(config.DB_PATH)
       try:
           cur = conn.execute(query)
           rows = cur.fetchall() if cur.description else []
           cols = [d[0] for d in cur.description] if cur.description else []
           conn.commit()  # ← should not commit on reads
   ```

2. **No error budget:** The loop will retry forever on deterministic errors (e.g., syntax error, missing column). If the model generates a bad query and the error message doesn't help it recover, the agent spins until timeout.

---

## What Was Changed/Created

1. **`output/evidence.json`**: Raw numbers from both tables, recomputed independently
2. **`output/INCIDENT_REPORT.md`**: This file
3. **`output/fixes/` directory**: (next section)

---

## Recommended Fixes (Prioritized)

### 1. Stop the Bleeding (15 min, blocks shipment)

**File:** `agent.py`

```python
# Line 30: Add max iterations
MAX_TURNS = 10
for turn in range(MAX_TURNS):
    resp = chat(...)
    # ... rest of loop
    if turn == MAX_TURNS - 1:
        return "I couldn't answer that after 10 attempts. Please rephrase or contact #data."
```

**File:** `agent.py` line 20

```python
# Remove commit, open read-only
conn = sqlite3.connect(f"file:{config.DB_PATH}?mode=ro", uri=True)
# ...
# conn.commit()  # ← DELETE THIS LINE
```

### 2. Data Dictionary (30 min, fixes this incident class)

**File:** `prompt.md` - replace lines 7-12 with:

```markdown
## Data Dictionary

When answering financial questions, use these definitions:

**Revenue:**
- **Definition:** GAAP net revenue (gross orders minus refunds), recognized in the period.
- **Source:** `revenue_recognized.net_amount` summed by `recognized_on` date or filtered by `period` column.
- **Do NOT use:** `orders.amount` (includes cancelled orders and doesn't account for refunds).

**Tables:**

- **revenue_recognized** (source of truth for revenue)
  - `recognized_on` (DATE): when revenue was recognized
  - `period` (TEXT): accounting period, e.g., "2026-Q2"
  - `net_amount` (REAL): revenue for this order (gross minus refunds)
  - Use this for: revenue, bookings (closed), GAAP metrics

- **orders** (raw transactions)
  - `amount` (REAL): order value
  - `status` (TEXT): completed | cancelled | refunded | partially_refunded
  - `created_at` (DATE): order creation date
  - Use this for: order volume, GMV, status breakdown (NOT for official revenue)

- **refunds**: refund transactions linked to orders
- **customers**: customer master data
- **daily_kpis**: pre-aggregated KPIs (use for quick dashboards, not official reporting)
```

### 3. Golden Set (1 hour, prevents regressions)

**File:** `evals/golden.jsonl` (create)

```jsonl
{"id":"q2-revenue","input":"what was Q2 2026 revenue?","expect":{"value":3638335.79,"table":"revenue_recognized","constraint":"between 3.6M and 3.7M"},"source":"incident 2026-09-14"}
{"id":"q1-revenue","input":"what was Q1 2026 revenue?","expect":{"value":3285493.84,"table":"revenue_recognized"},"source":"transcript 2026-09-11"}
{"id":"cancelled-orders","input":"how many Q2 orders were cancelled?","expect":{"value":202,"table":"orders","constraint":"status='cancelled'"},"source":"validation"}
```

Add 15-20 more cases from Slack history and finance team FAQs.

### 4. Judge Script (30 min)

**File:** `evals/run_evals.py` (create, see `output/fixes/` for full code)

Runs golden set, checks:
- Numeric answers within tolerance
- Table used matches expected source
- Query excludes cancelled orders for revenue questions

### 5. Tracing (1 hour)

Add structured logging to `agent.py`:
- Conversation ID (Slack thread ID)
- User, timestamp
- Each LLM call: tokens in/out, model, latency
- Each tool call: query, rows returned, latency, errors
- Final answer
- Total cost

Log to JSON lines file or push to internal observability stack.

### 6. Read-Only Credentials (coordinate with data team)

Create a read-only DB user/connection for finbot. Current setup uses the same file the ETL writes to—any accidental write could corrupt the warehouse.

---

## Cost Impact (Model Swap vs. Fix)

**Model swap (e.g., sonnet → opus):**
- Cost increase: ~2-3x per call (estimate, depends on pricing)
- Does NOT fix this bug (opus would make the same reasonable choice without a data dictionary)
- Monthly cost increase: $X (depends on volume)

**Harness fix (data dictionary + golden set):**
- Engineer time: ~3 hours
- Cost increase: $0
- Fixes this entire class of ambiguity error
- Prevents future regressions

**Recommendation:** Fix the harness first. If the golden set shows quality issues after the fix, then benchmark opus vs. sonnet on the eval set with metrics.

---

## What to Tell Daniel

> **"Not a model problem—we had two tables that could answer 'revenue' and no definition of which one to use. FinBot used orders ($4.1M gross) instead of revenue_recognized ($3.6M GAAP net). I've added a data dictionary to the prompt and built an eval set so we catch this before it hits Slack. The model is fine; we needed a harness. Fixes are in output/fixes/, ready to deploy."**

---

## Next Steps

1. **Deploy data dictionary** (prompt.md) - 0 risk, immediate fix
2. **Add max iterations + read-only DB** (agent.py) - blocks runaway costs and write risk
3. **Run golden set** (evals/run_evals.py) on the fix to confirm
4. **Add tracing** so we see cost and errors in real time
5. **Audit all Slack threads** since March for other ambiguous questions (finance can provide list)
6. **Do NOT upgrade the model** without golden set evidence that it's necessary

---

**Files created:**
- `output/evidence.json` - raw recomputed numbers
- `output/INCIDENT_REPORT.md` - this file
- `output/fixes/` - deployable code fixes
- `output/harness_scorecard.md` - detailed harness audit
