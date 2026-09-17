# Expected Behavior After Fix

## BEFORE THE FIX (What Happened on Sept 11)

**Priya Raman (Strategy)** 10:02
@finbot what was our Q2 2026 revenue? need it for the board deck by EOD

**finbot** 10:02
> tool_use `run_sql`
> ```sql
> SELECT ROUND(SUM(amount), 2) AS revenue FROM orders WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';
> ```
> tool_result `{"columns": ["revenue"], "rows": [[4138212.16]]}`

**finbot** 10:02
Q2 2026 revenue was **$4,138,212.16** (~$4.1M).

❌ **WRONG** - Used orders table, included refunded/cancelled orders

---

## AFTER THE FIX (Expected Behavior)

**Priya Raman (Strategy)** 10:02
@finbot what was our Q2 2026 revenue? need it for the board deck by EOD

**finbot** 10:02
> tool_use `run_sql`
> ```sql
> SELECT ROUND(SUM(net_amount), 2) AS revenue FROM revenue_recognized WHERE recognized_on BETWEEN '2026-04-01' AND '2026-06-30';
> ```
> tool_result `{"columns": ["revenue"], "rows": [[3638335.79]]}`

**finbot** 10:02
Q2 2026 revenue was **$3,638,335.79** (~$3.6M).

✅ **CORRECT** - Used revenue_recognized table, net revenue

---

## Other Test Cases

### Test 1: Bookings vs Revenue

**User:** @finbot what were our Q2 2026 bookings?

**finbot (after fix):**
> tool_use `run_sql`
> ```sql
> SELECT ROUND(SUM(amount), 2) AS bookings FROM orders WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';
> ```

Q2 2026 bookings were **$4,138,212.16** (~$4.1M) across 2,213 orders.

✅ **CORRECT** - For bookings, orders table is appropriate

---

### Test 2: Monthly Revenue

**User:** @finbot how much revenue in April 2026?

**finbot (after fix):**
> tool_use `run_sql`
> ```sql
> SELECT ROUND(SUM(net_amount), 2) AS revenue FROM revenue_recognized WHERE period = '2026-04';
> ```

April 2026 revenue was **$1,237,516.63** (~$1.2M).

✅ **CORRECT** - Used revenue_recognized with period field

---

### Test 3: QoQ Comparison

**User:** @finbot what was Q1 vs Q2 revenue?

**finbot (before fix - WRONG):**
> Q1: $4,141,985.86
> Q2: $4,138,212.16
> Q2 was flat vs Q1 (-0.1% QoQ)

❌ Both numbers wrong (from orders table)

**finbot (after fix - CORRECT):**
> tool_use `run_sql` (for Q1)
> ```sql
> SELECT ROUND(SUM(net_amount), 2) FROM revenue_recognized WHERE recognized_on BETWEEN '2026-01-01' AND '2026-03-31';
> ```
> tool_use `run_sql` (for Q2)
> ```sql
> SELECT ROUND(SUM(net_amount), 2) FROM revenue_recognized WHERE recognized_on BETWEEN '2026-04-01' AND '2026-06-30';
> ```

Q1 2026 revenue was **$3,285,493.84** (~$3.3M).
Q2 2026 revenue was **$3,638,335.79** (~$3.6M).
Q2 grew **10.7% QoQ**.

✅ **CORRECT** - Both from revenue_recognized, accurate growth calc

---

## Edge Cases to Test

### Ambiguous Question

**User:** @finbot how much did we make in Q2?

**Expected:** Should interpret "make" as revenue → use revenue_recognized

**finbot (after fix):**
Q2 2026 revenue was **$3.6M**.

✅ Interprets "make" as revenue, not bookings

---

### Completed Orders Only

**User:** @finbot what was the value of completed orders in Q2?

**Expected:** Should use orders table with status filter

**finbot (after fix):**
> ```sql
> SELECT ROUND(SUM(amount), 2) FROM orders WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30' AND status = 'completed';
> ```

Completed orders in Q2 2026 totaled **$3,269,510.70** (~$3.3M).

✅ **CORRECT** - Used orders table but filtered by status

---

### Refund Analysis

**User:** @finbot how much did we refund in Q2?

**Expected:** Could use refunds table OR revenue_recognized.refund_amount

**finbot (after fix):**
> ```sql
> SELECT ROUND(SUM(refund_amount), 2) FROM revenue_recognized WHERE recognized_on BETWEEN '2026-04-01' AND '2026-06-30';
> ```

Q2 2026 refunds totaled **$[amount]**.

✅ **ACCEPTABLE** - Multiple valid approaches

---

## Key Differences

| Aspect | Before Fix | After Fix |
|--------|------------|-----------|
| Revenue queries | ❌ orders.amount | ✅ revenue_recognized.net_amount |
| Bookings queries | ✅ orders.amount | ✅ orders.amount |
| Date field (revenue) | ❌ orders.created_at | ✅ revenue_recognized.recognized_on |
| Includes refunded? | ❌ Yes | ✅ No |
| Matches Finance? | ❌ No ($500K off) | ✅ Yes |

---

## Validation Commands

After deploying the fix, test with these questions:

```
1. "What was Q2 2026 revenue?"
   Expected: ~$3.6M from revenue_recognized ✅

2. "What were Q2 2026 bookings?"
   Expected: ~$4.1M from orders ✅

3. "What was April 2026 revenue?"
   Expected: ~$1.2M from revenue_recognized ✅

4. "How much did we refund in Q2?"
   Expected: Check refund_amount column ✅
```

All should now give correct answers matching Finance's numbers.

---

Generated: 2026-09-16
