# FinBot Data Dictionary

**Purpose:** Define every metric, table, and field FinBot may use to answer questions. When in doubt, refer to this document.

---

## Metrics Definitions

### Revenue

**Definition:** GAAP-compliant recognized revenue, net of refunds and cancellations.

**Source:**
- **Table:** `revenue_recognized`
- **Column:** `net_amount`
- **Filter:** By `period` (format: 'YYYY-MM') for monthly, or `recognized_on` for daily

**Example queries:**
```sql
-- Q2 2026 revenue (by period)
SELECT SUM(net_amount) 
FROM revenue_recognized 
WHERE period IN ('2026-04', '2026-05', '2026-06');

-- July 2026 revenue
SELECT SUM(net_amount) 
FROM revenue_recognized 
WHERE period = '2026-07';

-- Year-to-date revenue (by recognized_on)
SELECT SUM(net_amount) 
FROM revenue_recognized 
WHERE recognized_on BETWEEN '2026-01-01' AND CURRENT_DATE;
```

**Do NOT use:**
- ❌ `orders.amount` (includes cancelled/refunded orders)
- ❌ `daily_kpis.revenue` (incomplete data, different methodology)

---

### Bookings (Gross Order Value)

**Definition:** Total value of completed orders, before refunds.

**Source:**
- **Table:** `orders`
- **Column:** `amount`
- **Filter:** `status = 'completed'` AND by `created_at` date

**Example query:**
```sql
-- Q2 bookings
SELECT SUM(amount) 
FROM orders 
WHERE status = 'completed' 
  AND created_at BETWEEN '2026-04-01' AND '2026-06-30';
```

**Note:** Bookings ≠ Revenue. Use "bookings" for operational metrics, "revenue" for financial reporting.

---

### Refunds

**Definition:** Total value of refunded orders.

**Source:**
- **Table:** `refunds`
- **Column:** `amount`
- **Filter:** By `refunded_at` date

**Example query:**
```sql
-- Q2 refunds
SELECT SUM(amount) 
FROM refunds 
WHERE refunded_at BETWEEN '2026-04-01' AND '2026-06-30';
```

---

### Orders (Count)

**Definition:** Number of orders by status.

**Source:**
- **Table:** `orders`
- **Column:** COUNT(*)
- **Filter:** By `status` and `created_at` date

**Valid statuses:**
- `completed` - Order fulfilled
- `cancelled` - Order cancelled before fulfillment
- `refunded` - Order fully refunded
- `partially_refunded` - Order partially refunded

**Example query:**
```sql
-- Q2 completed orders
SELECT COUNT(*) 
FROM orders 
WHERE status = 'completed' 
  AND created_at BETWEEN '2026-04-01' AND '2026-06-30';
```

---

### Customers (Count)

**Definition:** Number of customers (unique or total depends on context).

**Source:**
- **Table:** `customers`
- **Column:** COUNT(*)

**Note:** Ask for clarification if "active customers" vs "all-time customers" is ambiguous.

---

## Tables Reference

### `orders`
**Purpose:** Operational order tracking. Records all orders regardless of final status.

**Key columns:**
- `order_id` - Unique order identifier
- `customer_id` - Foreign key to customers
- `created_at` - Order creation timestamp (TEXT, format: 'YYYY-MM-DD HH:MM:SS')
- `amount` - Gross order value (REAL, USD)
- `currency` - Always 'USD'
- `status` - Order status (TEXT: 'completed', 'cancelled', 'refunded', 'partially_refunded')

**When to use:** Operational questions about orders, order counts, booking trends.

**When NOT to use:** Financial "revenue" questions (use `revenue_recognized` instead).

---

### `revenue_recognized`
**Purpose:** GAAP-compliant financial reporting. This is the source of truth for "revenue."

**Key columns:**
- `id` - Record identifier
- `order_id` - Foreign key to orders
- `recognized_on` - Date revenue was recognized (TEXT, format: 'YYYY-MM-DD')
- `period` - Accounting period (TEXT, format: 'YYYY-MM')
- `gross_amount` - Revenue before refunds (REAL, USD)
- `refund_amount` - Refunds applied (REAL, USD)
- `net_amount` - Net recognized revenue = gross_amount - refund_amount (REAL, USD)

**When to use:** Any question about "revenue" for reporting, board materials, or finance.

**Filtering:**
- Use `period` for monthly/quarterly aggregations (cleaner)
- Use `recognized_on` for daily or arbitrary date ranges

---

### `refunds`
**Purpose:** Track all refunds issued.

**Key columns:**
- `refund_id` - Unique refund identifier
- `order_id` - Foreign key to orders
- `refunded_at` - Refund issue timestamp (TEXT, format: 'YYYY-MM-DD HH:MM:SS')
- `amount` - Refund amount (REAL, USD)
- `reason` - Refund reason (TEXT)

**When to use:** Questions about refund volume, refund rates, refund reasons.

**Note:** Refunds may occur in a different period than the original order.

---

### `customers`
**Purpose:** Customer master data.

**Key columns:**
- `customer_id` - Unique customer identifier
- *(other columns not documented - add as needed)*

**When to use:** Questions about customer counts, customer lists.

---

### `daily_kpis`
**Purpose:** Daily aggregated metrics for dashboards.

**Key columns:**
- `day` - Date (TEXT, format: 'YYYY-MM-DD')
- `revenue` - Daily revenue (REAL, USD)
- `orders` - Daily order count (INTEGER)
- `sessions` - Daily session count (INTEGER)
- `updated_at` - ETL timestamp

**⚠️ DATA QUALITY ISSUE:** Only populated through 2026-05-19. Incomplete for Q2 and beyond.

**When to use:** Trending questions for data available (Jan-May 2026 only).

**When NOT to use:** Any date after 2026-05-19 (use `revenue_recognized` or `orders` instead).

---

## Date Filtering Best Practices

### Quarterly Ranges
```sql
-- Q1 2026: Jan 1 - Mar 31
WHERE period IN ('2026-01', '2026-02', '2026-03')
-- OR
WHERE recognized_on BETWEEN '2026-01-01' AND '2026-03-31'

-- Q2 2026: Apr 1 - Jun 30
WHERE period IN ('2026-04', '2026-05', '2026-06')
-- OR  
WHERE recognized_on BETWEEN '2026-04-01' AND '2026-06-30'

-- Q3 2026: Jul 1 - Sep 30
WHERE period IN ('2026-07', '2026-08', '2026-09')

-- Q4 2026: Oct 1 - Dec 31
WHERE period IN ('2026-10', '2026-11', '2026-12')
```

### Date formats
- All date columns are TEXT, not DATE type
- Format: 'YYYY-MM-DD HH:MM:SS' or 'YYYY-MM-DD'
- Use `BETWEEN` for ranges
- Use string comparison (works because of ISO format)

---

## Common Question Patterns

| Question | Table | Column | Filter |
|----------|-------|--------|--------|
| "Q2 revenue" | revenue_recognized | net_amount | period IN ('2026-04','2026-05','2026-06') |
| "July bookings" | orders | amount | status='completed' AND created_at LIKE '2026-07%' |
| "Total refunds in Q1" | refunds | amount | refunded_at BETWEEN '2026-01-01' AND '2026-03-31' |
| "Number of orders last month" | orders | COUNT(*) | created_at BETWEEN [first] AND [last day] |
| "YTD revenue" | revenue_recognized | net_amount | recognized_on >= '2026-01-01' |

---

## Edge Cases & Ambiguities

### "Revenue" is ambiguous without context
- **Financial/Board materials:** Use `revenue_recognized.net_amount` (GAAP)
- **Sales/Operations:** May want `orders.amount` WHERE status='completed' (bookings)
- **When in doubt:** Ask the user or default to `revenue_recognized` (conservative)

### Refunds timing
- A Q1 order may be refunded in Q2
- Finance recognizes refunds in the period they occur
- Use `revenue_recognized.net_amount` to get the correct period allocation

### Partial refunds
- Orders table shows `status = 'partially_refunded'`
- Use `revenue_recognized.net_amount` for the correct net amount
- Do NOT subtract `refunds.amount` from `orders.amount` manually (double-counting risk)

---

## Changelog

- **2026-09-16:** Initial version created after Q2 revenue incident
  - Defined "revenue" = `revenue_recognized.net_amount`
  - Documented all 5 warehouse tables
  - Added date filtering examples

---

**Owner:** Data team (Jonas)  
**Review cadence:** Monthly or after any warehouse schema change  
**Questions:** #ask-data in Slack
