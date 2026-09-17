# FinBot Q2 Revenue Discrepancy - Root Cause Analysis

**Date:** September 15, 2026  
**Prepared for:** Daniel Kurz  
**Issue:** FinBot reported Q2 revenue as $4.1M vs Finance's $3.6M ($500K discrepancy)

---

## Executive Summary

**The bot is NOT hallucinating. It's calculating revenue incorrectly.**

- **FinBot's answer:** $4,138,212.16 (4.1M)
- **Finance's Q2 close:** $3,638,335.79 (3.6M)  
- **Discrepancy:** $499,876.37 (~$500K)

**Root cause:** FinBot is summing ALL orders in the `orders` table, including:
- ❌ Cancelled orders: $360,039
- ❌ Refunded orders: $189,943  
- ❌ Partially refunded orders: $318,719

Finance correctly uses the `revenue_recognized` table which tracks **net revenue** (gross - refunds).

---

## What Happened

### The Slack Exchange (Sept 11)
Priya asked finbot: *"what was our Q2 2026 revenue?"*

FinBot executed:
```sql
SELECT ROUND(SUM(amount), 2) AS revenue 
FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';
```

This query:
1. ✅ Correctly identified the Q2 date range
2. ❌ Summed ALL order amounts regardless of status
3. ❌ Ignored refunds and cancellations

### The Data Breakdown

| Order Status | Count | Amount |
|-------------|-------|--------|
| Completed | 1,733 | $3,269,511 |
| Cancelled | 202 | $360,039 |
| Refunded | 104 | $189,943 |
| Partially Refunded | 174 | $318,719 |
| **TOTAL (bot's calc)** | **2,213** | **$4,138,212** |

### What Finance Uses

Finance uses the `revenue_recognized` table:
- **Gross amount:** $3,970,863
- **Refund amount:** ($332,528)
- **Net amount:** $3,638,336 ✅

Monthly breakdown:
- April: $1,237,517
- May: $1,209,658
- June: $1,191,161

---

## This is NOT a Model Quality Issue

The model (Claude Sonnet 4.5) is working correctly:
- ✅ Understands the question
- ✅ Generates syntactically correct SQL
- ✅ Correctly maps "Q2" to the date range
- ✅ Returns accurate results from the query

**The problem:** The model doesn't know which table represents "true" revenue or that orders can be cancelled/refunded.

---

## Why This Happened

Looking at the system prompt (`prompt.md`):

> "Use the `run_sql` tool to query the warehouse and answer with a clear number."

The prompt lists available tables but provides **no guidance** on:
1. Which table to use for revenue questions
2. That orders have a `status` field that matters
3. That `revenue_recognized` is the source of truth for financials
4. The relationship between orders, refunds, and recognized revenue

The bot made a reasonable guess (orders table for "order revenue") but it was the wrong table for financial reporting.

---

## Recommendations

### 1. **Fix the Prompt (Immediate - Do Today)**

Update `prompt.md` to include business context:

```markdown
## Revenue Calculations

For revenue questions, ALWAYS use the `revenue_recognized` table:
- This is the source of truth for financial reporting
- It includes net revenue (gross revenue minus refunds)
- Use the `period` column to filter by month/quarter (format: 'YYYY-MM')
- Q1 = periods '01', '02', '03'; Q2 = '04', '05', '06', etc.

The `orders` table includes cancelled and refunded orders - do NOT use it for revenue totals.

Example queries:
- Q2 2026 revenue: WHERE period IN ('2026-04', '2026-05', '2026-06')
- June 2026 revenue: WHERE period = '2026-06'
```

### 2. **Add Schema Documentation**

Expand the prompt with table descriptions:
- `revenue_recognized` - Financial reporting (net revenue after refunds)
- `orders` - All orders regardless of completion status
- `refunds` - Individual refund transactions
- `customers` - Customer master data
- `daily_kpis` - High-level daily metrics

### 3. **Add Validation (Optional)**

Consider adding a validation tool that checks if answers are within reasonable bounds (e.g., flag if revenue varies >20% QoQ without explanation).

### 4. **Test Cases**

Create a test suite with expected answers for common questions like "What was Q2 revenue?" to catch these issues before they reach production.

---

## Do You Need a Better Model?

**No.** The current model (Claude Sonnet 4.5) is appropriate for this task. The issue is insufficient business context in the prompt, not model capability.

Upgrading to Opus or GPT-6 would not fix this issue - those models would make the same incorrect table choice without proper guidance.

---

## Immediate Action Items

1. ✅ **Root cause identified** - documented in this report
2. ⏭️ **Update the prompt** - add revenue calculation guidance (10 min)
3. ⏭️ **Test the fix** - verify bot gives correct answer with updated prompt (5 min)
4. ⏭️ **Correct the board deck** - Q2 revenue is $3.6M, not $4.1M
5. ⏭️ **Add test suite** - prevent similar issues going forward

---

## Supporting Data

Full analysis data available in `output/analysis_data.json`

Query transcripts:
- Slack thread: `transcripts/2026-09-11_board-deck.md`
- Exec discussion: `notes/slack-exec-thread.txt`
