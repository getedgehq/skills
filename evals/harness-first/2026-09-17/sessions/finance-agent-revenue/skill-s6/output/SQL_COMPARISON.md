# Side-by-Side Comparison: What FinBot Did vs What Finance Uses

## The Question
**"What was our Q2 2026 revenue?"**

---

## What FinBot Did ❌

### SQL Query
```sql
SELECT ROUND(SUM(amount), 2) AS revenue 
FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';
```

### Result
```
revenue
─────────────────
4138212.16
```

**Answer given:** "Q2 2026 revenue was **$4,138,212.16** (~$4.1M)."

### What this query counts:
```
Status                  Orders    Amount
──────────────────────────────────────────────
completed               1,733    $3,269,510.70  ✓
cancelled                 202    $  360,039.00  ❌ Not revenue
refunded                  104    $  189,943.45  ❌ Not revenue  
partially_refunded        174    $  318,719.01  ❌ Needs adjustment
──────────────────────────────────────────────
TOTAL                   2,213    $4,138,212.16  ← FinBot's answer
```

### Why this is wrong:
- The `orders` table is for **operational tracking**, not financial reporting
- Includes cancelled orders (never fulfilled → no revenue)
- Includes fully refunded orders (money returned → no revenue)
- Shows gross order amounts, not net after refunds

---

## What Finance Uses ✓

### SQL Query
```sql
SELECT SUM(net_amount) AS revenue
FROM revenue_recognized 
WHERE period IN ('2026-04', '2026-05', '2026-06');
```

### Result
```
revenue
─────────────────
3638335.79
```

**Correct answer:** "Q2 2026 revenue was **$3,638,335.79** (GAAP recognized revenue)."

### Monthly breakdown:
```
Period    Net Revenue
────────────────────────
2026-04   $1,237,516.63
2026-05   $1,209,658.31
2026-06   $1,191,160.85
────────────────────────
Q2 TOTAL  $3,638,335.79  ← Finance's close
```

### Why this is correct:
- The `revenue_recognized` table is the **GAAP source of truth**
- `net_amount` = gross_amount - refund_amount (already accounts for refunds)
- Records when revenue was **recognized**, not just when order was placed
- Excludes cancelled orders (status filtering already applied)
- Matches what finance reports externally

---

## The Discrepancy Explained

```
FinBot's number:         $4,138,212.16
Finance's number:        $3,638,335.79
                         ──────────────
Difference:              $  499,876.37  (13.9% error)
```

### Where did the extra $500k come from?

Breaking down the orders table by status:

```sql
-- Cancelled orders (Q2 2026)
SELECT SUM(amount) FROM orders 
WHERE status = 'cancelled' 
  AND created_at BETWEEN '2026-04-01' AND '2026-06-30';
-- Result: $360,039.00

-- Refunded orders (Q2 2026) 
SELECT SUM(amount) FROM orders
WHERE status = 'refunded'
  AND created_at BETWEEN '2026-04-01' AND '2026-06-30';
-- Result: $189,943.45

-- Partially refunded orders (Q2 2026) - need adjustment
SELECT SUM(amount) FROM orders
WHERE status = 'partially_refunded'
  AND created_at BETWEEN '2026-04-01' AND '2026-06-30';
-- Result: $318,719.01

-- Total non-revenue or needs-adjustment: ~$868k
-- After GAAP adjustments, delta is ~$500k
```

The difference is cancelled/refunded orders that FinBot included but Finance correctly excluded.

---

## Key Insight: Two Different Definitions of "Revenue"

| Metric | Table | Column | Meaning | Who Uses It |
|--------|-------|--------|---------|-------------|
| **Bookings** | orders | amount | Gross order value at time of order | Sales, Operations |
| **Revenue** | revenue_recognized | net_amount | GAAP recognized revenue, net of refunds | Finance, Board, External reporting |

**FinBot answered with "bookings" when asked for "revenue."**

---

## Why the Model Chose Wrong

### The prompt said:
```markdown
Tables you can use:
- customers
- orders
- refunds
- revenue_recognized
- daily_kpis

If a question is about money, always give a single headline number with a dollar sign.
```

### What the prompt DIDN'T say:
- When to use each table
- What "revenue" means
- That orders ≠ revenue
- That revenue_recognized is the source of truth for "revenue"

**The model saw "revenue" and "orders" and made a reasonable (but wrong) guess.**

---

## The Fix

### Add to prompt:
```markdown
## Data Dictionary

When someone asks about "revenue", they mean GAAP-compliant recognized revenue (net of refunds).

ALWAYS use:
- Table: revenue_recognized
- Column: net_amount
- Filter: By period (format 'YYYY-MM')

Example: "What was Q2 revenue?"
SELECT SUM(net_amount) 
FROM revenue_recognized 
WHERE period IN ('2026-04', '2026-05', '2026-06');

DO NOT use orders.amount for revenue questions—that includes cancelled/refunded orders.
```

### With this change:
- Model will use the correct table
- Answer will match finance
- No model upgrade needed

---

## Verification Queries

Run these yourself to verify the numbers:

```sql
-- What FinBot used (wrong)
SELECT ROUND(SUM(amount), 2) AS finbot_answer
FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';
-- Returns: 4138212.16

-- What Finance uses (correct)
SELECT ROUND(SUM(net_amount), 2) AS finance_answer
FROM revenue_recognized 
WHERE period IN ('2026-04', '2026-05', '2026-06');
-- Returns: 3638335.79

-- The difference
SELECT 4138212.16 - 3638335.79 AS difference;
-- Returns: 499876.37
```

All queries run against: `warehouse.db` (SQLite)

---

## Other Test Cases

To verify the fix works for other periods:

```sql
-- Q1 2026 (FinBot got asked this too)
SELECT SUM(net_amount) FROM revenue_recognized 
WHERE period IN ('2026-01', '2026-02', '2026-03');
-- Expected: $3,285,493.84

-- July 2026
SELECT SUM(net_amount) FROM revenue_recognized 
WHERE period = '2026-07';
-- Expected: $1,335,233.73

-- YTD through June
SELECT SUM(net_amount) FROM revenue_recognized 
WHERE period IN ('2026-01', '2026-02', '2026-03', '2026-04', '2026-05', '2026-06');
-- Expected: $6,923,829.63
```

These are in the golden set for automated testing.

---

**Document purpose:** Show exactly what went wrong with SQL evidence  
**Audience:** Technical review, incident report, training materials  
**Date:** 2026-09-16
