# Technical Analysis - FinBot Revenue Query

## Database Investigation Results

### What FinBot Actually Ran

From Slack transcript (2026-09-11):
```sql
SELECT ROUND(SUM(amount), 2) AS revenue 
FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';
```

**Result:** $4,138,212.16

---

## Data Verification

### 1. Orders Table Analysis (Q2 2026)

**All orders by status:**
```sql
SELECT 
    status,
    COUNT(*) as count,
    ROUND(SUM(amount), 2) as total_amount
FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30'
GROUP BY status;
```

| Status | Count | Total Amount |
|--------|-------|--------------|
| completed | 1,733 | $3,269,510.70 |
| cancelled | 202 | $360,039.00 |
| partially_refunded | 174 | $318,719.01 |
| refunded | 104 | $189,943.45 |
| **TOTAL** | **2,213** | **$4,138,212.16** |

**Key Finding:** The orders table includes $360k in cancelled orders that should not count as revenue.

---

### 2. Revenue_Recognized Table (Correct Source)

**Q2 2026 revenue:**
```sql
SELECT 
    SUM(gross_amount) as gross_revenue,
    SUM(refund_amount) as total_refunds,
    SUM(net_amount) as net_revenue
FROM revenue_recognized 
WHERE period IN ('2026-04', '2026-05', '2026-06');
```

| Metric | Amount |
|--------|--------|
| Gross Revenue | $3,970,863.37 |
| Total Refunds | $332,527.58 |
| **Net Revenue** | **$3,638,335.79** |

**Key Finding:** This matches Finance's $3.6M (rounded to nearest $100k).

---

### 3. Monthly Breakdown

```sql
SELECT 
    period,
    COUNT(*) as order_count,
    ROUND(SUM(net_amount), 2) as net_revenue
FROM revenue_recognized
WHERE period IN ('2026-04', '2026-05', '2026-06')
GROUP BY period
ORDER BY period;
```

| Month | Order Count | Net Revenue |
|-------|-------------|-------------|
| 2026-04 | 718 | $1,237,516.63 |
| 2026-05 | 707 | $1,209,658.31 |
| 2026-06 | 681 | $1,191,160.85 |
| **Q2 Total** | **2,106** | **$3,638,335.79** |

---

### 4. Comparison Table

| Data Source | Query | Result | Notes |
|-------------|-------|--------|-------|
| **FinBot (orders)** | `SUM(amount) FROM orders WHERE created_at...` | $4,138,212 | Includes cancelled, gross amounts |
| **Orders (excl. cancelled)** | `SUM(amount) FROM orders WHERE ... AND status != 'cancelled'` | $3,778,173 | Still gross (pre-refund) |
| **Orders (completed only)** | `SUM(amount) FROM orders WHERE ... AND status = 'completed'` | $3,269,511 | Excludes partially refunded |
| **Revenue_recognized (net)** | `SUM(net_amount) FROM revenue_recognized WHERE period IN (...)` | $3,638,336 | ✅ **Correct** |
| **Finance reported** | Manual close | $3,600,000 | Rounded to $100k |

---

## Why the Discrepancy Exists

### Difference: $4,138,212 (FinBot) - $3,638,336 (Finance) = $499,876

**Breakdown of the $500k gap:**

1. **Cancelled orders:** $360,039
   - FinBot included these
   - Finance correctly excludes them
   
2. **Refunds:** $332,528
   - FinBot used gross amounts
   - Finance uses net (after refunds)
   
3. **Timing differences:** 
   - Orders table uses `created_at`
   - Revenue_recognized uses `period` (when revenue is recognized)
   - 352 orders (17%) recognized in different month than created

4. **Status complexity:**
   - FinBot counted all order statuses
   - Revenue_recognized only includes orders that should be recognized

---

## Schema Details

### orders table
```
order_id         INTEGER
customer_id      INTEGER  
created_at       TEXT (timestamp)
amount           REAL
currency         TEXT
status           TEXT (completed|cancelled|refunded|partially_refunded)
```

**Row count:** 6,136 total orders

### revenue_recognized table
```
id               INTEGER
order_id         INTEGER
recognized_on    TEXT (date)
period           TEXT (YYYY-MM format)
gross_amount     REAL
refund_amount    REAL
net_amount       REAL
```

**Row count:** 5,598 recognition records

**Key insight:** This table exists specifically for financial reporting and follows GAAP principles.

---

## Revenue Recognition Logic

Sample query showing timing differences:
```sql
SELECT 
    o.order_id,
    o.created_at,
    rr.recognized_on,
    rr.period,
    o.amount as order_amount,
    rr.net_amount
FROM revenue_recognized rr
JOIN orders o ON rr.order_id = o.order_id
WHERE rr.period = '2026-04'
AND strftime('%Y-%m', o.created_at) != rr.period
LIMIT 5;
```

**Examples:**
- Order 101980: created 2026-03-23, recognized 2026-04-01 in period 2026-04
- Order 101990: created 2026-03-23, recognized 2026-04-01 in period 2026-04
- Order 102017: created 2026-03-24, recognized 2026-04-02 in period 2026-04

**Why this matters:** Using `created_at` on orders vs `period` on revenue_recognized gives different results even for the same orders.

---

## Validation Queries

### Test 1: Are all orders accounted for?
```sql
SELECT COUNT(DISTINCT rr.order_id) as in_rev_rec,
       COUNT(DISTINCT o.order_id) as in_orders
FROM revenue_recognized rr
LEFT JOIN orders o ON rr.order_id = o.order_id
WHERE rr.period IN ('2026-04', '2026-05', '2026-06');
```

**Result:** 2,106 orders in both tables (100% match) ✅

### Test 2: Check for data integrity
```sql
SELECT COUNT(*) 
FROM revenue_recognized
WHERE period IN ('2026-04', '2026-05', '2026-06')
AND net_amount != gross_amount - refund_amount;
```

**Result:** 0 rows (arithmetic is correct) ✅

---

## The Correct Query

FinBot should have run:
```sql
SELECT ROUND(SUM(net_amount), 2) AS q2_revenue
FROM revenue_recognized 
WHERE period IN ('2026-04', '2026-05', '2026-06');
```

**Result:** $3,638,335.79

Rounded to Finance reporting standards: **$3.6M** ✅

---

## Model Behavior Analysis

### What the model did RIGHT:
1. ✅ Understood "Q2 2026" means April 1 - June 30
2. ✅ Wrote syntactically correct SQL
3. ✅ Used BETWEEN correctly with dates
4. ✅ Applied ROUND() function appropriately
5. ✅ Returned results in requested format ($X.XM)
6. ✅ Did not hallucinate or make up numbers

### What the model did WRONG:
1. ❌ Chose `orders` table instead of `revenue_recognized`
2. ❌ Did not filter by status (included cancelled orders)
3. ❌ Used gross amounts instead of net

### Root cause:
**Insufficient guidance in system prompt.** The model had to guess which table represents "revenue" - it guessed wrong, but reasonably so.

---

## Why a More Expensive Model Won't Help

The decision tree the model followed:
1. User asks: "what was our Q2 2026 revenue?"
2. Prompt says: tables available are customers, orders, refunds, revenue_recognized, daily_kpis
3. Prompt says: "If a question is about money, always give a single headline number"
4. Model thinks: "revenue = money from orders, so I'll query the orders table"
5. Model generates: `SELECT SUM(amount) FROM orders WHERE created_at BETWEEN...`

**A more sophisticated model would:**
- Still face the same ambiguity
- Might make the same choice (orders seems reasonable)
- Might make a different wrong choice (daily_kpis, which is also incorrect)
- Still need explicit instructions to pick the right table

**The fix is not in model intelligence but in prompt specificity.**

---

## Recommended System Prompt Update

Add to `prompt.md`:

```markdown
## Important: Revenue Queries

When someone asks about "revenue", "sales", "quarterly revenue", or similar:
- ALWAYS use the `revenue_recognized` table, NOT the `orders` table
- Use the `net_amount` column (this accounts for refunds)
- Filter by the `period` column in YYYY-MM format
- For quarters, use IN clause: Q1 = ('2026-01','2026-02','2026-03')

Example queries:
- Q2 2026 revenue: SELECT SUM(net_amount) FROM revenue_recognized WHERE period IN ('2026-04','2026-05','2026-06')
- Monthly revenue: SELECT period, SUM(net_amount) FROM revenue_recognized WHERE period LIKE '2026-%' GROUP BY period

Why not use `orders` table for revenue:
- orders.amount is GROSS (before refunds)
- orders includes cancelled orders
- orders.created_at is booking date, not when revenue is recognized
- The revenue_recognized table is the source of truth for financial reporting
```

---

## Testing Plan

1. **Re-run original query:**
   ```
   User: "what was our Q2 2026 revenue?"
   Expected: "Q2 2026 revenue was $3,638,335.79 (~$3.6M)"
   Expected SQL: SELECT SUM(net_amount) FROM revenue_recognized WHERE period IN ('2026-04','2026-05','2026-06')
   ```

2. **Test edge cases:**
   - "what was revenue in April?"
   - "show me Q1 vs Q2 revenue"
   - "what were bookings in Q2?" (should still use orders table for this)

3. **Verify with Finance:**
   - Confirm $3.6M is the official Q2 number
   - Confirm they use revenue_recognized table
   - Confirm rounding conventions

---

## Additional Issues Found

### Issue 1: daily_kpis table is incomplete
```sql
SELECT MIN(day), MAX(day), COUNT(*)
FROM daily_kpis;
```

**Result:** 2026-01-01 to 2026-05-19 (139 days)

**Problem:** Missing 42 days of Q2 (May 20 - June 30)

**Impact:** If FinBot uses this table, it will underreport revenue

**Fix:** 
- Fix ETL to populate through current date, OR
- Remove from bot's available tables until fixed

### Issue 2: No data dictionary
The warehouse has no metadata table explaining:
- What each table represents
- Which tables are authoritative for which metrics
- Business definitions (revenue vs bookings vs cash collected)

**Recommendation:** Create a `table_metadata` table or external documentation.

---

## Files to Update

1. **prompt.md** - Add revenue query guidance (see above)
2. **README.md** - Document the incident and resolution
3. **config.py** - Consider adding table priority/validation
4. **#ask-finance** - Post message about the fix

---

## Summary Statistics

- **Orders in Q2:** 2,213 (created in April-June)
- **Orders recognized in Q2:** 2,106 (includes some from March)
- **Cancelled orders (excluded):** 202 orders, $360k
- **Refunds (Q2):** $333k
- **Timing mismatches:** 352 orders (17%)
- **FinBot error magnitude:** $500k (14% overstatement)
- **Fix complexity:** Low (prompt update only)
- **Model upgrade needed:** No
