# FinBot Data Dictionary

## Metrics

### Revenue
**Definition:** Net revenue after refunds, recognized in the accounting period.

**Source:** `revenue_recognized.net_amount` 
- Use `period` field to filter by month (format: 'YYYY-MM')
- Or use `recognized_on` field to filter by date

**Formula:** `gross_amount - refund_amount`

**NEVER use:** `orders.amount` - this is gross order value including cancelled and refunded orders. The orders table does NOT represent recognized revenue.

### Order Count
**Definition:** Number of completed orders (excluding cancelled and fully refunded).

**Source:** `orders` table where `status NOT IN ('cancelled', 'refunded')`

**Valid statuses:**
- `completed` - order fulfilled, no refunds
- `partially_refunded` - order fulfilled, some items refunded

**Invalid statuses for revenue:**
- `cancelled` - order never fulfilled
- `refunded` - order fully refunded

## Tables

### orders
- **Purpose:** Raw order transactions
- **Key columns:**
  - `order_id` - unique identifier
  - `created_at` - order creation timestamp
  - `amount` - gross order amount (before refunds)
  - `status` - order state (completed, cancelled, refunded, partially_refunded)
- **Warning:** Do NOT sum `amount` for revenue - use `revenue_recognized` instead

### revenue_recognized
- **Purpose:** Accounting-period revenue (GAAP compliant)
- **Key columns:**
  - `period` - accounting month (YYYY-MM format)
  - `recognized_on` - recognition date
  - `gross_amount` - initial order amount
  - `refund_amount` - total refunds applied
  - `net_amount` - gross - refunds (USE THIS for revenue)
- **Usage:** This is the authoritative source for revenue figures

### refunds
- **Purpose:** Refund transaction details
- **Key columns:**
  - `order_id` - links to orders
  - `refunded_at` - refund timestamp
  - `amount` - refund amount
  - `reason` - refund reason

### customers
- **Purpose:** Customer master data
- **Key columns:**
  - `customer_id` - unique identifier
  - `name` - customer name
  - `segment` - business segment
  - `country` - customer location

### daily_kpis
- **Purpose:** Pre-aggregated daily metrics
- **Key columns:**
  - `day` - date
  - `revenue` - daily revenue (matches revenue_recognized)
  - `orders` - order count
  - `sessions` - web sessions

## Common Queries

### Quarterly Revenue (CORRECT)
```sql
SELECT SUM(net_amount) 
FROM revenue_recognized 
WHERE period IN ('2026-04', '2026-05', '2026-06')
```

### Quarterly Revenue (WRONG - DO NOT USE)
```sql
-- ❌ WRONG: includes cancelled and refunded orders
SELECT SUM(amount) 
FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30'
```

### Monthly Revenue
```sql
SELECT SUM(net_amount) 
FROM revenue_recognized 
WHERE period = '2026-04'
```

### Order Count (by creation date)
```sql
SELECT COUNT(*) 
FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30'
AND status NOT IN ('cancelled', 'refunded')
```
