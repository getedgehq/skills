# Data Dictionary: Finance Warehouse

**Owner:** Data team (Jonas)  
**Last Updated:** 2026-09-15  
**Purpose:** Canonical definitions for all metrics FinBot may report

---

## Revenue Metrics

### Revenue (default)
- **Definition:** GAAP-recognized net revenue for the period
- **Source:** `revenue_recognized.net_amount` 
- **Filter:** `recognized_on` date (not order date)
- **Formula:** Gross revenue minus refunds/chargebacks, recognized in period
- **Use for:** Financial reporting, board decks, investor updates
- **Example query:**
  ```sql
  SELECT SUM(net_amount) AS revenue
  FROM revenue_recognized 
  WHERE recognized_on BETWEEN '[start]' AND '[end]';
  ```

### Gross Revenue
- **Definition:** Total revenue before refunds
- **Source:** `revenue_recognized.gross_amount`
- **Use for:** Understanding refund rate impact

### Bookings / Gross Bookings
- **Definition:** Total value of orders placed (not GAAP revenue)
- **Source:** `orders.amount`
- **Filter:** `created_at` date
- **Use for:** Sales pipeline, demand trends (NOT for financial reporting)
- **Note:** ⚠️ This is NOT revenue. It includes orders that may be refunded or recognized in future periods.

---

## Customer Metrics

### Customers (total)
- **Source:** `customers.customer_id` (COUNT DISTINCT)
- **Definition:** All customers in the system

### Active Customers
- **Definition:** Customers with at least one order in the period
- **Query:**
  ```sql
  SELECT COUNT(DISTINCT customer_id) 
  FROM orders 
  WHERE created_at BETWEEN '[start]' AND '[end]';
  ```

---

## Order Metrics

### Orders (count)
- **Source:** `orders.order_id` (COUNT)
- **Filter:** `created_at` date
- **Definition:** Number of orders placed

### Average Order Value (AOV)
- **Formula:** `SUM(orders.amount) / COUNT(orders.order_id)`
- **Filter:** `created_at` date

---

## Refund Metrics

### Refunds (amount)
- **Source:** `refunds.amount`
- **Filter:** `refunded_at` date
- **Definition:** Total value of refunds processed

### Refund Rate
- **Formula:** `SUM(refunds.amount) / SUM(orders.amount)` for matching period
- **Express as:** Percentage (e.g., "5.2% refund rate")

---

## Time Periods

### Quarter (Q1, Q2, Q3, Q4)
- Q1: January 1 - March 31
- Q2: April 1 - June 30
- Q3: July 1 - September 30
- Q4: October 1 - December 31

### Month
- Use `YYYY-MM` format (e.g., "2026-04" for April 2026)

### Fiscal Year
- Same as calendar year (January 1 - December 31)

---

## Table Reference

### `orders`
- **Purpose:** Raw order events (bookings)
- **Key columns:**
  - `order_id`: Unique order identifier
  - `customer_id`: Links to customers table
  - `created_at`: When order was placed (TEXT, format: 'YYYY-MM-DD')
  - `amount`: Order total (REAL, in USD)
  - `status`: Order status (e.g., 'completed', 'cancelled')
- **⚠️ Important:** This is NOT revenue. Use for demand/pipeline analysis only.

### `revenue_recognized`
- **Purpose:** GAAP revenue recognition (source of truth for financial reporting)
- **Key columns:**
  - `order_id`: Links to orders table
  - `recognized_on`: Date revenue was recognized (TEXT, format: 'YYYY-MM-DD')
  - `period`: Recognition period (TEXT, format: 'YYYY-MM')
  - `gross_amount`: Revenue before refunds (REAL, in USD)
  - `refund_amount`: Refunds applied (REAL, in USD)
  - `net_amount`: Net revenue (gross - refunds) (REAL, in USD)
- **✅ Use this for:** Revenue questions, board reporting, financial analysis

### `refunds`
- **Purpose:** Refund/chargeback events
- **Key columns:**
  - `refund_id`: Unique refund identifier
  - `order_id`: Links to orders table
  - `refunded_at`: When refund was processed (TEXT, format: 'YYYY-MM-DD')
  - `amount`: Refund amount (REAL, in USD)
  - `reason`: Refund reason (TEXT)

### `customers`
- **Purpose:** Customer master data
- **Key columns:**
  - `customer_id`: Unique customer identifier
  - `name`: Customer name
  - `segment`: Customer segment (e.g., 'enterprise', 'smb')
  - `country`: Customer country

### `daily_kpis`
- **Purpose:** Pre-aggregated daily metrics (for dashboards)
- **Key columns:**
  - `day`: Date (TEXT, format: 'YYYY-MM-DD')
  - `revenue`: Net revenue for the day (REAL, in USD)
  - `orders`: Order count for the day (INTEGER)
  - `sessions`: Website sessions (INTEGER)
- **Note:** This is a summary table. For accuracy, query the source tables.

---

## Default Behavior Rules

When someone asks "what was revenue...", always:
1. Use `revenue_recognized.net_amount` (GAAP revenue)
2. Filter by `recognized_on` date (not order date)
3. Round to 2 decimal places
4. Include the dollar sign in the answer

When someone asks about "orders" or "bookings":
1. Use `orders.amount`
2. Filter by `created_at` date
3. Clarify that this is gross bookings, not GAAP revenue

---

## Examples

❌ **Wrong:**
> Q2 2026 revenue was **$4,138,212.16** (~$4.1M).
> 
> (Used `orders.amount` — this is bookings, not revenue)

✅ **Correct:**
> Q2 2026 revenue was **$3,638,335.79** (~$3.6M).
>
> (Used `revenue_recognized.net_amount`)

✅ **Also acceptable:**
> Q2 2026 gross bookings were $4.1M. GAAP revenue (after refunds) was $3.6M.
>
> (Clarifies the difference)
