# Data Forensics: Q2 2026 Revenue Discrepancy

## Quick Reference

| Source | Q2 2026 Amount | What it represents |
|--------|----------------|-------------------|
| **Finbot (wrong)** | **$4,138,212.16** | Gross orders (all statuses) |
| **Finance (correct)** | **$3,638,335.79** | Net revenue (after refunds) |
| **Difference** | **$499,876.37** | Cancelled orders + refunds |

---

## Q2 Orders Breakdown (April - June 2026)

### By Status (from `orders` table)

| Status | Count | Total Amount | Notes |
|--------|-------|--------------|-------|
| Completed | 1,733 | $3,269,510.70 | Successfully fulfilled |
| Partially Refunded | 174 | $318,719.01 | Partial refund issued |
| Cancelled | 202 | $360,039.00 | Should NOT count as revenue |
| Refunded | 104 | $189,943.45 | Should NOT count as revenue |
| **TOTAL** | **2,213** | **$4,138,212.16** | ← This is what finbot returned |

### Revenue Recognition (from `revenue_recognized` table)

| Period | Gross Amount | Refund Amount | Net Amount |
|--------|--------------|---------------|------------|
| 2026-04 | $1,369,750.07 | $132,233.44 | $1,237,516.63 |
| 2026-05 | $1,310,501.70 | $100,843.39 | $1,209,658.31 |
| 2026-06 | $1,290,611.60 | $99,450.75 | $1,191,160.85 |
| **Q2 TOTAL** | **$3,970,863.37** | **$332,527.58** | **$3,638,335.79** |

**$3,638,335.79** ← This is the correct number (Finance's $3.6M)

---

## Why the Numbers Don't Match

### The $499,876.37 difference consists of:

1. **Cancelled orders**: $360,039.00
   - Orders that were placed but cancelled before fulfillment
   - Included in `orders` table SUM, excluded from `revenue_recognized`

2. **Fully refunded orders**: $189,943.45
   - Orders that were completed but later fully refunded
   - Included in gross, but net to $0 in `revenue_recognized`

3. **Additional refunds**: Difference between refunds table and revenue_recognized
   - Some timing differences and partial refunds
   - `revenue_recognized.refund_amount` is the comprehensive number

---

## Sample Orders: How Revenue Recognition Works

Here are actual Q2 orders showing the mapping:

| Order ID | Order Date | Order Amount | Status | Gross (Rev Rec) | Refund (Rev Rec) | Net (Rev Rec) |
|----------|------------|--------------|--------|-----------------|------------------|---------------|
| 102269 | 2026-04-01 | $1,039.66 | completed | $1,039.66 | $0.00 | $1,039.66 |
| 102270 | 2026-04-01 | $3,956.19 | completed | $3,956.19 | $0.00 | $3,956.19 |
| 102273 | 2026-04-01 | $3,059.38 | refunded | $3,059.38 | $3,059.38 | **$0.00** |
| 102276 | 2026-04-01 | $2,869.77 | refunded | $2,869.77 | $2,869.77 | **$0.00** |

Notice: Refunded orders appear in `orders.amount` but net to $0 in revenue_recognized.

---

## The SQL Queries

### What Finbot Executed (WRONG)
```sql
SELECT ROUND(SUM(amount), 2) AS revenue 
FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';
```
**Result:** $4,138,212.16 (includes cancelled and refunded orders)

### What It Should Have Executed (CORRECT)
```sql
SELECT ROUND(SUM(net_amount), 2) AS revenue
FROM revenue_recognized
WHERE period IN ('2026-04', '2026-05', '2026-06');
```
**Result:** $3,638,335.79 (official finance number)

### Alternative Correct Query (by date instead of period)
```sql
SELECT ROUND(SUM(net_amount), 2) AS revenue
FROM revenue_recognized
WHERE recognized_on BETWEEN '2026-04-01' AND '2026-06-30';
```
**Result:** $3,638,335.79 (same result)

---

## Historical Context: Q1 2026

Reviewing the Slack transcript, finbot also reported Q1:

**Finbot said:** $4,141,985.86 (from `orders` table)

This is likely also ~$500K higher than the actual Q1 close. The board deck may contain an incorrect Q1 number as well.

### Recommended Q1 Verification Query
```sql
SELECT ROUND(SUM(net_amount), 2) AS revenue
FROM revenue_recognized
WHERE period IN ('2026-01', '2026-02', '2026-03');
```

---

## Data Model Documentation

### `orders` Table
- **Purpose:** Transaction log of all order events
- **Use for:** Order-level analysis, customer behavior, order status tracking
- **Do NOT use for:** Revenue totals, financial reporting
- **Key insight:** This is a transactional system-of-record, not a financial ledger

### `revenue_recognized` Table  
- **Purpose:** Official financial ledger with proper revenue recognition
- **Use for:** Revenue reporting, financial analysis, board decks
- **Key columns:**
  - `gross_amount`: Original order value
  - `refund_amount`: Total refunds/returns
  - `net_amount`: Official recognized revenue (gross - refund)
  - `period`: Accounting period (YYYY-MM format)
  - `recognized_on`: Date revenue was recognized

### `refunds` Table
- **Purpose:** Individual refund transactions
- **Relationship:** Refunds are aggregated into `revenue_recognized.refund_amount`
- **Use for:** Understanding refund reasons, customer service analysis

### `daily_kpis` Table
- **Purpose:** High-level operational dashboard
- **Current data:** Only through 2026-05-18 (incomplete)
- **Use for:** Day-to-day operations monitoring, session metrics
- **Do NOT use for:** Official revenue reporting

---

## Validation Checklist

Before reporting any revenue number from finbot:

- [ ] Did the query use `revenue_recognized` table?
- [ ] Did it sum `net_amount` (not `gross_amount` or `orders.amount`)?
- [ ] Does the result match finance's expectations (~$3-4M for a quarter)?
- [ ] For quarterly numbers, did it include all 3 months?
- [ ] Was the date range or period filter correct?

---

## Testing the Fix

After updating the prompt, test with these questions:

1. ✅ "What was Q2 2026 revenue?" → Should return $3,638,335.79
2. ✅ "How much revenue in June 2026?" → Should return $1,191,160.85
3. ✅ "Revenue for the first half of 2026?" → Should return Q1 + Q2 net amounts
4. ❌ "How many orders in Q2?" → Should use `orders` table (not revenue_recognized)

The model should now correctly distinguish between:
- **Revenue questions** → `revenue_recognized.net_amount`
- **Order count questions** → `orders` table

---

## Appendix: Full Q2 Month-by-Month

| Month | Orders (count) | Orders (amount) | Revenue (net) | Difference |
|-------|----------------|-----------------|---------------|------------|
| Apr 2026 | 718 | $1,347,485.93 | $1,237,516.63 | $109,969.30 |
| May 2026 | 755 | $1,424,060.13 | $1,209,658.31 | $214,401.82 |
| Jun 2026 | 740 | $1,366,666.10 | $1,191,160.85 | $175,505.25 |
| **Q2 Total** | **2,213** | **$4,138,212.16** | **$3,638,335.79** | **$499,876.37** |

The difference varies by month based on:
- Timing of order cancellations
- Volume of refunds in each month
- Mix of completed vs. cancelled orders
