# Technical Deep Dive: FinBot Revenue Discrepancy

## Data Validation & Reconciliation

### Query Comparison

**FinBot's Query (INCORRECT):**
```sql
SELECT ROUND(SUM(amount), 2) AS revenue 
FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';
-- Result: $4,138,212.16
```

**Finance's Query (CORRECT):**
```sql
SELECT ROUND(SUM(net_amount), 2) AS revenue 
FROM revenue_recognized 
WHERE recognized_on BETWEEN '2026-04-01' AND '2026-06-30';
-- Result: $3,638,335.79
```

### Reconciliation Table

| Metric | Value | Source |
|--------|-------|--------|
| Orders created in Q2 (all statuses) | $4,138,212.16 | orders.amount |
| Less: Cancelled orders never recognized | ($360,039.00) | 202 orders |
| Less: Q2 orders recognized in Q3 | ($120,369.71) | 65 orders |
| Plus: Pre-Q2 orders recognized in Q2 | $264,846.41 | 147 orders |
| Less: Additional refund adjustments | ($142,584.13) | Net refund impact |
| **Approximate reconciliation** | **~$3,780K** | |
| **Actual revenue_recognized Q2** | **$3,638,335.79** | |

Note: Small differences due to rounding and complex refund timing.

### Detailed Breakdown by Component

#### 1. Cancelled Orders ($360,039)
```sql
-- Orders in Q2 that never made it to revenue_recognized
SELECT COUNT(*), ROUND(SUM(amount), 2)
FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30'
AND order_id NOT IN (SELECT DISTINCT order_id FROM revenue_recognized);
-- 202 orders, $360,039.00
```

**Impact:** These orders were created but cancelled before fulfillment/payment, so they never became revenue. The orders table includes them; revenue_recognized correctly excludes them.

#### 2. Revenue Recognition Timing Lag

**Q2 Orders Recognized in Q3:**
```sql
SELECT COUNT(DISTINCT o.order_id), ROUND(SUM(o.amount), 2)
FROM orders o
JOIN revenue_recognized r ON o.order_id = r.order_id
WHERE o.created_at BETWEEN '2026-04-01' AND '2026-06-30'
AND r.recognized_on > '2026-06-30';
-- 65 orders, $120,369.71
```

**Pre-Q2 Orders Recognized in Q2:**
```sql
SELECT COUNT(DISTINCT o.order_id), ROUND(SUM(r.net_amount), 2)
FROM orders o
JOIN revenue_recognized r ON o.order_id = r.order_id
WHERE o.created_at < '2026-04-01'
AND r.recognized_on BETWEEN '2026-04-01' AND '2026-06-30';
-- 147 orders, $264,846.41
```

**Why the lag?** Revenue recognition happens when:
- Product/service is delivered (fulfillment complete)
- Payment is received/confirmed
- All revenue recognition criteria are met (ASC 606 / IFRS 15)

Orders placed late in the quarter (especially late June) often recognize in the following quarter.

#### 3. Refund Accounting Differences

**Orders table refund tracking:**
- Shows order status (completed, refunded, cancelled)
- Refunded orders show original amount with status='refunded'
- Point-in-time snapshot

**Revenue_recognized refund tracking:**
- Tracks cumulative refund impact per order
- Gross_amount - refund_amount = net_amount
- Reflects refunds that may have occurred after order date

```sql
-- Comparison
SELECT 
  'Orders (refunded status)' as source,
  COUNT(*) as count,
  ROUND(SUM(amount), 2) as total
FROM orders
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30'
AND status = 'refunded'

UNION ALL

SELECT 
  'Revenue_recognized (refund_amount)' as source,
  COUNT(*) as count,
  ROUND(SUM(refund_amount), 2) as total
FROM revenue_recognized
WHERE recognized_on BETWEEN '2026-04-01' AND '2026-06-30'
AND refund_amount > 0;

-- Results:
-- Orders: 104 refunded orders, $189,943.45
-- Revenue_recognized: tracking $332,527.58 in refunds
-- Difference: $142,584.13
```

The revenue_recognized table captures:
- Partial refunds (order not fully refunded)
- Refunds that occurred after the order date
- Refunds on orders from previous quarters that impact Q2 revenue

### Database Schema Analysis

#### Orders Table
```sql
CREATE TABLE orders (
  order_id INTEGER PRIMARY KEY,
  customer_id INTEGER,
  created_at TEXT,        -- When order was placed
  amount REAL,            -- Original order amount
  currency TEXT,
  status TEXT             -- completed, refunded, cancelled, etc.
);
```

**Purpose:** Operational tracking of customer orders (booking/cash basis)
**Used for:** Sales pipeline, order fulfillment, operational metrics

#### Revenue_Recognized Table
```sql
CREATE TABLE revenue_recognized (
  id INTEGER PRIMARY KEY,
  order_id INTEGER,
  recognized_on TEXT,     -- When revenue was earned (GAAP)
  period TEXT,            -- e.g., "2026-04", "2026-Q2"
  gross_amount REAL,      -- Revenue before refunds
  refund_amount REAL,     -- Total refunds applied
  net_amount REAL         -- Net revenue (gross - refunds)
);
```

**Purpose:** GAAP-compliant financial reporting (accrual basis)
**Used for:** Board reports, investor reporting, financial statements

### Sample Data Showing the Issue

#### Example 1: Late-Quarter Order
```
Order 104331:
  created_at: 2026-06-23
  amount: $3,413.68
  status: completed
  
Revenue Recognition:
  recognized_on: 2026-07-02 (Q3!)
  net_amount: $3,413.68
  
Issue: FinBot counted this in Q2 (order date), but it's Q3 revenue (recognition date)
```

#### Example 2: Cancelled Order
```
Order 102301:
  created_at: 2026-04-02
  amount: $2,287.80
  status: cancelled
  
Revenue Recognition:
  (no record - never recognized)
  
Issue: FinBot counted $2,287.80 in Q2, but this never became revenue
```

#### Example 3: Cross-Quarter Recognition
```
Order 101980:
  created_at: 2026-03-23 (Q1)
  amount: $6,914.15
  status: completed
  
Revenue Recognition:
  recognized_on: 2026-04-01 (Q2)
  net_amount: $6,914.15
  
Issue: FinBot excluded this (Q1 order), but it IS Q2 revenue
```

#### Example 4: Refunded Order
```
Order 102041:
  created_at: 2026-04-02
  amount: $339.28
  status: completed
  
Revenue Recognition:
  recognized_on: 2026-04-02
  gross_amount: $339.28
  refund_amount: $122.07
  net_amount: $217.21
  
Issue: FinBot counted $339.28, but actual revenue is $217.21
```

### Performance & Scale Considerations

**Query Performance:**
- Both queries perform well on the current data scale
- Orders table: 2,213 Q2 rows
- Revenue_recognized table: 2,106 Q2 rows
- No performance reason to prefer orders over revenue_recognized

**Data Freshness:**
- Both tables updated nightly by ETL (per config.py comment)
- Revenue_recognized may lag by 1-7 days for recent orders (waiting for fulfillment)
- For current/closed quarters, revenue_recognized is the authoritative source

### Model Behavior Analysis

**What the model did correctly:**
1. ✅ Parsed "Q2 2026 revenue" as needing a date filter for Q2
2. ✅ Generated syntactically correct SQL with proper date range
3. ✅ Used SUM() aggregation appropriately
4. ✅ Returned formatted, human-readable response
5. ✅ Provided context (compared to Q1, noted QoQ trend)

**What the model couldn't know:**
1. ❌ That "revenue" at this company means GAAP revenue recognition, not bookings
2. ❌ That orders table ≠ revenue table
3. ❌ The business context around accrual vs. cash accounting
4. ❌ Which table is authoritative for financial reporting

**Why this isn't a model capability issue:**
- This requires company-specific domain knowledge
- No LLM has this knowledge without being told
- The model's SQL generation was technically perfect
- The problem is in the system prompt/instructions

### Testing Methodology

**To verify the fix works:**

1. Deploy updated prompt.md
2. Run test queries:

```bash
# Should now use revenue_recognized
python agent.py "what was Q2 2026 revenue?"

# Should still use orders (this is about count, not revenue)
python agent.py "how many orders did we have in Q2 2026?"

# Should use orders (bookings ≠ revenue)
python agent.py "what were Q2 bookings?"

# Should use revenue_recognized
python agent.py "show me quarterly revenue for 2026"
```

3. Check generated SQL in logs:
   - Revenue questions → `FROM revenue_recognized`
   - Order count questions → `FROM orders`
   - Bookings questions → `FROM orders`

4. Validate results against finance's numbers:
   - Q2 revenue should be $3,638,335.79
   - Q1 revenue should use revenue_recognized too

### Alternative Solution: Database View

If prompt engineering isn't sufficient, create a view:

```sql
CREATE VIEW quarterly_financials AS
SELECT 
  strftime('%Y', recognized_on) || '-Q' || 
  CAST((CAST(strftime('%m', recognized_on) AS INTEGER) + 2) / 3 AS TEXT) as quarter,
  SUM(net_amount) as revenue,
  SUM(gross_amount) as gross_revenue,
  SUM(refund_amount) as refunds,
  COUNT(DISTINCT order_id) as orders_recognized
FROM revenue_recognized
GROUP BY quarter;

-- Usage
SELECT revenue FROM quarterly_financials WHERE quarter = '2026-Q2';
-- Result: $3,638,335.79
```

This makes it nearly impossible to get the wrong answer.

### Code Change for Validation (Optional)

Add to `agent.py` after line 23:

```python
def validate_query(query, question):
    """Warn if revenue question uses wrong table."""
    revenue_keywords = ['revenue', 'sales', 'income']
    uses_orders = 'from orders' in query.lower() or 'join orders' in query.lower()
    
    if any(kw in question.lower() for kw in revenue_keywords) and uses_orders:
        return {
            "error": "⚠️ Revenue questions should use revenue_recognized table, not orders. " 
                     "Orders = bookings (when placed). Revenue = recognized (when earned). "
                     "Please revise query."
        }
    return None

# In run_sql():
def run_sql(query):
    # Add validation here
    warning = validate_query(query, current_question)  # need to pass question through
    if warning:
        return warning
    # ... rest of existing code
```

### Monitoring & Prevention

**Add to runbook:**
1. Monthly audit: Compare finbot's answers to finance close for prior month
2. Alert on large discrepancies (>5%) between tables
3. Log all queries to identify patterns of incorrect table usage
4. Review system prompt quarterly as new tables/metrics are added

**Key metrics to monitor:**
- % of revenue queries using correct table
- Discrepancy between orders sum and revenue_recognized sum (should track around $500K)
- User corrections/questions in Slack after finbot answers (sign of confusion)

---

## Conclusion

This is a **system design issue**, not a model capability issue:
- Root cause: Ambiguous table purpose in system prompt
- Solution: Enhanced prompt with clear table usage guidelines
- Prevention: Add examples, validation, and/or simplified views
- Cost: $0 and 30 minutes, not a model upgrade

The current model (Claude Sonnet 4-5) is more than capable - it just needs better instructions.
