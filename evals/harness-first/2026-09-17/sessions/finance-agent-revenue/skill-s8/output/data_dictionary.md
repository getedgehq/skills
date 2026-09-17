# FinBot Data Dictionary

**Owner:** Finance + Data team  
**Last updated:** 2026-09-16  
**Purpose:** Define the canonical source of truth for every metric FinBot reports

---

## Revenue Metrics

### Revenue (GAAP) ⭐ OFFICIAL METRIC
- **Definition:** Net revenue recognized in the period, per GAAP accrual accounting
- **Source:** `revenue_recognized.net_amount` WHERE `recognized_on` in period
- **Formula:** gross_amount - refund_amount
- **When to use:** Board reports, investor updates, financial close, any "revenue" question
- **NOT the same as:** Gross bookings, cash collected, orders placed

**Example queries:**
```sql
-- Q2 2026 revenue
SELECT ROUND(SUM(net_amount), 2) AS revenue
FROM revenue_recognized
WHERE recognized_on BETWEEN '2026-04-01' AND '2026-06-30';
-- Result: $3,638,335.79
```

### Gross Bookings
- **Definition:** Total order value placed, excluding cancelled orders
- **Source:** `orders.amount` WHERE `status NOT IN ('cancelled')`
- **When to use:** Sales pipeline analysis, order volume questions
- **NOT to use for:** Revenue questions, financial reporting

### Cash Collected
- **Definition:** Actual cash received from customers
- **Source:** TBD (not yet in warehouse)
- **When to use:** Cash flow questions, collections analysis

---

## Customer Metrics

### Active Customers
- **Definition:** Customers with at least one completed order in the period
- **Source:** `COUNT(DISTINCT customer_id) FROM orders WHERE status = 'completed'`

### New Customers
- **Definition:** Customers whose first order was in the period
- **Source:** Customers where `MIN(created_at)` falls in period

---

## Order Metrics

### Order Statuses
- **completed:** Order fulfilled, revenue recognized (unless later refunded)
- **cancelled:** Order cancelled before fulfillment, no revenue
- **refunded:** Order completed then fully refunded, revenue reversed
- **partially_refunded:** Order completed then partially refunded, revenue = net

---

## Important Notes

1. **Always use `revenue_recognized` for revenue questions**, not `orders`
2. **Always use `net_amount`**, not `gross_amount`, unless specifically asked for gross
3. **Date fields:**
   - `orders.created_at` = when order was placed
   - `revenue_recognized.recognized_on` = when revenue should be counted (use this for revenue!)
4. **Period format:** `revenue_recognized.period` uses 'YYYY-MM' format (e.g. '2026-04')

---

## Common Mistakes to Avoid

❌ `SUM(orders.amount)` for revenue → includes cancelled, uses gross not net  
✅ `SUM(revenue_recognized.net_amount)` for revenue

❌ `WHERE orders.created_at` for revenue period → wrong date field  
✅ `WHERE revenue_recognized.recognized_on` for revenue period

❌ `gross_amount` for revenue → doesn't subtract refunds  
✅ `net_amount` for revenue

---

## Glossary

- **GAAP:** Generally Accepted Accounting Principles (official accounting standards)
- **Net:** After subtracting refunds/returns
- **Gross:** Before subtracting refunds/returns
- **Recognized:** When revenue is officially counted (may differ from order date)
- **Accrual:** Count revenue when earned, not when cash is collected
