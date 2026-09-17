# The Problem: Side-by-Side SQL Comparison

## Question Asked
**"What was our Q2 2026 revenue?"**

---

## ❌ What FinBot Did (Wrong)

### SQL Query
```sql
SELECT ROUND(SUM(amount), 2) AS revenue 
FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';
```

### Result
**$4,138,212.16** (~$4.1M)

### What This Includes

| Order Status | Count | Amount | Should Count? |
|--------------|-------|--------|---------------|
| completed | 1,733 | $3,269,511 | ✅ Yes |
| partially_refunded | 174 | $318,719 | ✅ Yes |
| **cancelled** | **202** | **$360,039** | ❌ **No - never fulfilled** |
| **refunded** | **104** | **$189,943** | ❌ **No - fully refunded** |
| **TOTAL** | **2,213** | **$4,138,212** | |

### Why This Is Wrong
The `orders` table contains **raw order transactions**. The `amount` column is the gross order value at creation time. It includes:
- Orders that were **cancelled** before fulfillment
- Orders that were **fully refunded** after fulfillment

This is **NOT recognized revenue** by GAAP standards.

---

## ✅ What FinBot Should Do (Correct)

### SQL Query
```sql
SELECT ROUND(SUM(net_amount), 2) AS revenue
FROM revenue_recognized
WHERE period IN ('2026-04', '2026-05', '2026-06');
```

### Result  
**$3,638,335.79** (~$3.6M)

### What This Includes

| Month | Gross | Refunds | Net |
|-------|-------|---------|-----|
| 2026-04 | $1,369,750 | $132,233 | $1,237,517 |
| 2026-05 | $1,310,502 | $100,843 | $1,209,658 |
| 2026-06 | $1,290,612 | $99,451 | $1,191,161 |
| **Q2 Total** | **$3,970,864** | **$332,528** | **$3,638,336** |

### Why This Is Correct
The `revenue_recognized` table contains **accounting-period revenue**:
- Starts with gross order amount
- Subtracts refunds (partial and full)
- Excludes cancelled orders entirely
- **Formula:** `net_amount = gross_amount - refund_amount`

This matches **GAAP revenue recognition** and what finance reports.

---

## The $500K Gap Explained

```
FinBot's answer (orders table):        $4,138,212
Finance's close (revenue_recognized):  $3,638,336
                                       ──────────
Difference:                            $  499,876

Breakdown of difference:
  Cancelled orders in Q2:              $  360,039
  Fully refunded orders in Q2:         $  189,943
  Extra refunds on partial refunds:    $ ~(50,000)
                                       ──────────
  Total discrepancy:                   $  499,876
```

---

## Visual Timeline: How Orders Flow

```
ORDER CREATED
   ↓
┌─────────────────────┐
│   orders table      │  ← ❌ FinBot queried here
│   amount = $1000    │     (includes ALL statuses)
└─────────────────────┘
   ↓
   ├─→ Status: cancelled → STOP (no revenue)
   ├─→ Status: completed → fulfillment
   └─→ Status: refunded → fulfillment then refund
        ↓
   ┌─────────────────────┐
   │ revenue_recognized  │  ← ✅ FinBot should query here
   │ gross = $1000       │     (only fulfilled orders)
   │ refunds = $250      │     (includes refund adjustments)
   │ net = $750          │     (the real revenue)
   └─────────────────────┘
        ↓
   REPORTED TO FINANCE
```

---

## Why The Bot Made This Mistake

### The Current Prompt Says:
```
Tables you can use:
- customers
- orders
- refunds
- revenue_recognized
- daily_kpis
```

**That's it.** No definition of which table to use for what.

### The Fixed Prompt Says:
```
IMPORTANT: Revenue Definition

For any question about "revenue":
- Use revenue_recognized table, NOT orders table
- Sum the net_amount column (gross revenue minus refunds)

NEVER use orders.amount for revenue - that includes 
cancelled and refunded orders.
```

---

## Testing: How To Verify The Fix

### Before Fix
```bash
$ python agent.py "what was Q2 2026 revenue?"
Q2 2026 revenue was $4,138,212.16 (~$4.1M)
❌ WRONG - used orders table
```

### After Fix
```bash
$ python agent.py "what was Q2 2026 revenue?"
Q2 2026 revenue was $3,638,335.79 (~$3.6M)  
✅ CORRECT - used revenue_recognized table
```

### Golden Test
```bash
$ python output/judge.py
Running 4 test cases...
✓ q2-2026-revenue: expected $3,638,336, got $3,638,336
✓ q1-2026-revenue: expected $3,285,494, got $3,285,494
✓ q2-2026-order-count: expected 1907, got 1907
✓ total-customers: expected 420, got 420
Passed: 4/4
```

---

## The Model Is Not The Problem

Claude Sonnet 4.5 did **exactly** what it was supposed to do:
1. ✅ Read the question: "Q2 2026 revenue"
2. ✅ Saw the word "revenue"
3. ✅ Looked at available tables
4. ✅ Saw `orders.amount` looks revenue-ish
5. ✅ Wrote valid SQL with correct date range
6. ✅ Returned the exact number from the database

**The model worked perfectly.** The problem is the **system** didn't tell the model which table to use.

---

## If You Switch Models Without Fixing The Harness

### With GPT-6 (hypothetical)
```
Question: "Q2 2026 revenue?"

GPT-6 thinks: "Revenue... I see orders.amount and 
               revenue_recognized.net_amount... I'll try orders"

Query: SELECT SUM(amount) FROM orders WHERE...
Result: $4,138,212

❌ SAME ERROR, MORE EXPENSIVE
```

### With Claude Opus
```
Question: "Q2 2026 revenue?"

Opus thinks: "Revenue... hmm, I see two tables...
              Let me try revenue_recognized"

Query: SELECT SUM(net_amount) FROM revenue_recognized...
Result: $3,638,336

✅ CORRECT BY LUCK - but you paid 3x more
   and next time it might guess wrong
```

**Don't rely on the model guessing right.**  
**Define "revenue" explicitly in the prompt.**

---

## Summary

| | Before | After |
|---|--------|-------|
| **Data dictionary** | ❌ None | ✅ `data_dictionary.md` defines "revenue" |
| **Prompt clarity** | ❌ Lists tables | ✅ Says which table for revenue |
| **Test coverage** | ❌ No tests | ✅ 4 test cases including Q2 revenue |
| **Safety limits** | ❌ Infinite loop possible | ✅ Max 5 iterations |
| **DB permissions** | ⚠️ Write access | ✅ Read-only |
| **Cost risk** | ⚠️ Unbounded | ✅ Capped per query |

**Fix the harness. Then decide if you need a different model.**
