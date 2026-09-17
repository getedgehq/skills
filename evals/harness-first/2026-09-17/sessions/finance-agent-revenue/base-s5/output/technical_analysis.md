# Technical Data Analysis - Revenue Discrepancy

## Database Investigation Results

### Query Comparison

#### What FinBot Did (WRONG)
```sql
SELECT ROUND(SUM(amount), 2) AS revenue 
FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';
```
**Result:** $4,138,212.16

#### What Finance Uses (CORRECT)
```sql
SELECT ROUND(SUM(net_amount), 2) AS revenue 
FROM revenue_recognized 
WHERE recognized_on BETWEEN '2026-04-01' AND '2026-06-30';
```
**Result:** $3,638,335.79

---

## Q2 2026 Orders Breakdown

### By Status
| Status | Count | Total Amount | Included in FinBot? | Included in Finance? |
|--------|-------|--------------|---------------------|---------------------|
| Completed | 1,733 | $3,269,510.70 | ✅ | ✅ (net of any refunds) |
| Refunded | 104 | $189,943.45 | ✅ | ❌ (excluded) |
| Cancelled | 202 | $360,039.00 | ✅ | ❌ (excluded) |
| Partially Refunded | 174 | $318,719.01 | ✅ | ⚠️ (included at net amount) |
| **TOTAL** | **2,213** | **$4,138,212.16** | | |

### The $500K Gap
```
FinBot (orders sum):        $4,138,212.16
Finance (revenue_recognized): $3,638,335.79
                            ─────────────
Difference:                   $499,876.37
```

This difference consists of:
- Fully refunded orders: $189,943
- Cancelled orders: $360,039
- Partial refund amounts: ~$50K (difference between gross and net for partially refunded)

---

## Revenue Recognized Table Structure

```sql
CREATE TABLE revenue_recognized (
    id INTEGER PRIMARY KEY, 
    order_id INTEGER, 
    recognized_on TEXT,     -- Date revenue was recognized
    period TEXT,            -- Period (e.g., '2026-04')
    gross_amount REAL,      -- Original order amount
    refund_amount REAL,     -- Amount refunded
    net_amount REAL         -- gross_amount - refund_amount
)
```

### Sample Entries (Q2 2026)
| Order | Period | Gross | Refund | Net | Status |
|-------|--------|-------|--------|-----|--------|
| 102075 | 2026-04 | $2,396.08 | $2,396.08 | $0.00 | refunded |
| 102041 | 2026-04 | $339.28 | $122.07 | $217.21 | partially_refunded |
| 102269 | 2026-04 | $1,039.66 | $0.00 | $1,039.66 | completed |

### Monthly Breakdown (from revenue_recognized)
```
April 2026:   $1,237,516.63
May 2026:     $1,209,658.31
June 2026:    $1,191,160.85
              ─────────────
Q2 2026:      $3,638,335.79
```

---

## The Three Revenue Numbers Explained

### 1. Orders Table - $4.1M (GROSS BOOKINGS)
- **Source:** `SUM(amount) FROM orders`
- **Includes:** Everything - completed, refunded, cancelled, partial refunds
- **Use case:** Sales pipeline, booking trends
- **For board deck:** ❌ NO

### 2. Revenue_Recognized Table - $3.6M (GAAP REVENUE)
- **Source:** `SUM(net_amount) FROM revenue_recognized`
- **Includes:** Net revenue after refunds and cancellations
- **Use case:** Financial reporting, board materials, GAAP compliance
- **For board deck:** ✅ YES

### 3. Daily_KPIs Table - $2.3M (UNKNOWN METRIC)
- **Source:** `SUM(revenue) FROM daily_kpis`
- **Includes:** Unclear - doesn't match orders or revenue_recognized
- **Use case:** ⚠️ Needs investigation
- **For board deck:** ❌ NO

---

## Database Schema

```
warehouse.db contains:

├── customers (customer_id, name, segment, country)
├── orders (order_id, customer_id, created_at, amount, currency, status)
├── refunds (refund_id, order_id, refunded_at, amount, reason)
├── revenue_recognized (id, order_id, recognized_on, period, gross_amount, refund_amount, net_amount)
└── daily_kpis (day, revenue, orders, sessions, updated_at)
```

---

## Verification Queries

### Test Q2 Revenue
```sql
-- CORRECT WAY (Finance's method)
SELECT 
    ROUND(SUM(net_amount), 2) AS q2_revenue
FROM revenue_recognized 
WHERE recognized_on BETWEEN '2026-04-01' AND '2026-06-30';
-- Expected: $3,638,335.79

-- WRONG WAY (What finbot did)
SELECT 
    ROUND(SUM(amount), 2) AS q2_bookings
FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';
-- Result: $4,138,212.16 (includes refunded/cancelled)
```

### Compare to Q1 (for context)
```sql
-- Q1 2026 Revenue (correct method)
SELECT 
    ROUND(SUM(net_amount), 2) AS q1_revenue
FROM revenue_recognized 
WHERE recognized_on BETWEEN '2026-01-01' AND '2026-03-31';
-- Result: $3,285,493.84

-- QoQ Growth
-- Q1: $3,285,493.84
-- Q2: $3,638,335.79
-- Growth: +10.7% QoQ
```

Note: FinBot also calculated Q1 wrong in the transcript:
- FinBot said Q1 was $4,141,985.86 (from orders table)
- Correct Q1 revenue: $3,285,493.84 (from revenue_recognized)
- FinBot also overstated Q1 by ~$850K

---

## Model Behavior Analysis

### What the Model Did Right
1. ✅ Understood the user's intent (find Q2 revenue)
2. ✅ Correctly selected date range (2026-04-01 to 2026-06-30)
3. ✅ Wrote syntactically correct SQL
4. ✅ Used the run_sql tool properly
5. ✅ Formatted the response clearly
6. ✅ Followed up correctly for Q1 comparison
7. ✅ Did not make up any numbers

### What the Model Did Wrong
1. ❌ Selected the wrong table (`orders` instead of `revenue_recognized`)
2. ❌ Didn't account for refunds/cancellations

### Why It Made This Choice
Looking at `prompt.md`:
```markdown
Tables you can use:
- customers
- orders
- refunds
- revenue_recognized
- daily_kpis
```

The prompt:
- Lists all tables equally (no hierarchy)
- Doesn't specify which table is authoritative for revenue
- Doesn't explain the difference between them
- The word "orders" intuitively sounds like revenue to a language model

**Conclusion:** The model made a reasonable inference given ambiguous instructions. Any model would likely make the same choice without better guidance.

---

## Recommended Prompt Update

Add this to `prompt.md` after the table list:

```markdown
**Table Usage Guidelines:**

REVENUE QUESTIONS → Use `revenue_recognized` table
- Query the `net_amount` column (NOT gross_amount)
- Use `recognized_on` for date filtering
- This is the official GAAP revenue (net of refunds/cancellations)

BOOKINGS/PIPELINE QUESTIONS → Use `orders` table
- This shows gross bookings including cancelled/refunded orders
- Good for sales trends, but NOT for revenue reporting

REFUND ANALYSIS → Use `refunds` table
- Links to orders via order_id

KPIs/METRICS → Use `daily_kpis` table
- Pre-aggregated daily metrics
- Note: Ask Data team if unclear which metric to use
```

---

## Test Cases for Validation

After updating the prompt, test with these questions:

```
1. "What was Q2 2026 revenue?"
   Expected: ~$3.6M from revenue_recognized

2. "What were our bookings in Q2 2026?"
   Expected: ~$4.1M from orders (including cancelled)

3. "How much did we refund in Q2 2026?"
   Expected: Check refunds table or refund_amount in revenue_recognized

4. "What was completed order value in Q2 2026?"
   Expected: ~$3.3M from orders WHERE status='completed'
```

---

## Files Analyzed
- `warehouse.db` - 2,213 orders in Q2 2026
- `transcripts/2026-09-11_board-deck.md` - Original finbot conversation
- `notes/slack-exec-thread.txt` - Executive team discovering the issue
- `agent.py` - FinBot implementation
- `prompt.md` - System prompt (source of issue)
- `config.py` - Using claude-sonnet-4-5 (adequate model)

---

Generated: 2026-09-16
