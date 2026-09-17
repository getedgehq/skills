# SQL Query Comparison: Wrong vs. Right

## The Discrepancy

| What | Amount | Source |
|------|--------|--------|
| Finbot reported | $4,138,212.16 | `orders` table |
| Finance official | $3,638,335.79 | `revenue_recognized` table |
| **Difference** | **$499,876.37** | Cancelled orders + refunds |

---

## Query 1: What Finbot Executed ❌

```sql
SELECT ROUND(SUM(amount), 2) AS revenue 
FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';
```

**Result:** `$4,138,212.16`

**Why this is wrong:**
- Includes ALL orders regardless of status
- Includes 202 cancelled orders ($360K)
- Includes 104 fully refunded orders ($190K)  
- Doesn't account for partial refunds
- This is **gross bookings**, not revenue

**When to use this:**
- Order volume analysis
- Understanding gross transaction flow
- NOT for financial reporting

---

## Query 2: What It Should Execute ✅

```sql
SELECT ROUND(SUM(net_amount), 2) AS revenue
FROM revenue_recognized
WHERE period IN ('2026-04', '2026-05', '2026-06');
```

**Result:** `$3,638,335.79`

**Why this is correct:**
- Official finance source of truth
- Net of refunds (gross - refunds)
- Excludes cancelled orders
- Matches quarterly close
- This is **recognized revenue** per accounting rules

**When to use this:**
- Financial reporting
- Board decks
- Revenue analysis
- Any "how much money did we make" questions

---

## Alternative Correct Query ✅

If you prefer date-based filtering instead of period:

```sql
SELECT ROUND(SUM(net_amount), 2) AS revenue
FROM revenue_recognized
WHERE recognized_on BETWEEN '2026-04-01' AND '2026-06-30';
```

**Result:** `$3,638,335.79` (same)

Both approaches work because the data is aligned by both period and date.

---

## Breakdown Queries

### See the difference in detail:

```sql
-- All Q2 orders by status
SELECT 
    status,
    COUNT(*) as order_count,
    ROUND(SUM(amount), 2) as total_amount
FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30'
GROUP BY status
ORDER BY total_amount DESC;
```

**Results:**
| Status | Count | Amount |
|--------|-------|--------|
| completed | 1,733 | $3,269,510.70 |
| cancelled | 202 | $360,039.00 |
| partially_refunded | 174 | $318,719.01 |
| refunded | 104 | $189,943.45 |

---

### Revenue recognition breakdown:

```sql
-- Q2 revenue by month with refunds
SELECT 
    period,
    ROUND(SUM(gross_amount), 2) as gross,
    ROUND(SUM(refund_amount), 2) as refunds,
    ROUND(SUM(net_amount), 2) as net_revenue
FROM revenue_recognized
WHERE period IN ('2026-04', '2026-05', '2026-06')
GROUP BY period
ORDER BY period;
```

**Results:**
| Period | Gross | Refunds | Net Revenue |
|--------|-------|---------|-------------|
| 2026-04 | $1,369,750.07 | $132,233.44 | $1,237,516.63 |
| 2026-05 | $1,310,501.70 | $100,843.39 | $1,209,658.31 |
| 2026-06 | $1,290,611.60 | $99,450.75 | $1,191,160.85 |
| **Total** | **$3,970,863.37** | **$332,527.58** | **$3,638,335.79** |

---

## Common Revenue Queries (Use These)

### Q2 2026 Revenue
```sql
SELECT ROUND(SUM(net_amount), 2) as revenue
FROM revenue_recognized
WHERE period IN ('2026-04', '2026-05', '2026-06');
-- Result: $3,638,335.79
```

### Q1 2026 Revenue
```sql
SELECT ROUND(SUM(net_amount), 2) as revenue
FROM revenue_recognized
WHERE period IN ('2026-01', '2026-02', '2026-03');
-- Result: Run this to verify Q1 in board deck
```

### Single Month Revenue (e.g., June 2026)
```sql
SELECT ROUND(SUM(net_amount), 2) as revenue
FROM revenue_recognized
WHERE period = '2026-06';
-- Result: $1,191,160.85
```

### YTD Revenue (Jan - June 2026)
```sql
SELECT ROUND(SUM(net_amount), 2) as revenue
FROM revenue_recognized
WHERE period BETWEEN '2026-01' AND '2026-06';
-- Result: Q1 + Q2 net amounts
```

### Revenue with Breakdown
```sql
SELECT 
    period,
    ROUND(SUM(net_amount), 2) as net_revenue,
    COUNT(DISTINCT order_id) as order_count,
    ROUND(AVG(net_amount), 2) as avg_revenue_per_order
FROM revenue_recognized
WHERE period BETWEEN '2026-01' AND '2026-06'
GROUP BY period
ORDER BY period;
```

---

## What About the Other Tables?

### `daily_kpis` Table
```sql
-- Q2 from daily_kpis
SELECT ROUND(SUM(revenue), 2)
FROM daily_kpis
WHERE day BETWEEN '2026-04-01' AND '2026-06-30';
-- Result: $2,262,135.23
```

**Why this doesn't match:**
- Incomplete data (only through mid-May in current snapshot)
- Daily operational metric, not official close
- Don't use for quarterly reporting

### `refunds` Table
```sql
-- Refunds issued in Q2
SELECT 
    COUNT(*) as refund_count,
    ROUND(SUM(amount), 2) as total_refunded
FROM refunds r
JOIN orders o ON r.order_id = o.order_id
WHERE o.created_at BETWEEN '2026-04-01' AND '2026-06-30';
-- Result: 278 refunds, $316,434.46
```

This is useful for understanding refund volume, but `revenue_recognized.refund_amount` 
is the comprehensive number that includes all adjustments.

---

## Testing the Fix

After updating the prompt, finbot should automatically generate the correct query:

**Test Question:** "What was our Q2 2026 revenue?"

**Expected Response:**
> [Tool use: run_sql]
> ```sql
> SELECT ROUND(SUM(net_amount), 2) AS revenue
> FROM revenue_recognized  
> WHERE period IN ('2026-04', '2026-05', '2026-06');
> ```
> [Tool result: {"columns": ["revenue"], "rows": [[3638335.79]]}]
> 
> Q2 2026 revenue was **$3,638,335.79** (~$3.6M).

✅ This matches Finance's official number.

---

## Validation Checklist

Before trusting a revenue number from finbot:

- [ ] Check the query it generated
- [ ] Verify it uses `revenue_recognized` table
- [ ] Verify it sums `net_amount` (not `gross_amount` or `orders.amount`)
- [ ] Check the date/period filter is correct
- [ ] Sanity check: Q2 revenue should be $3-4M range
- [ ] If critical (board deck), verify with Finance

---

## Key Takeaway

**For revenue: Always use `revenue_recognized.net_amount`**

The `orders` table is a transaction log. The `revenue_recognized` table is the financial ledger.
