# FinBot Data Dictionary
**Last Updated:** 2026-09-15  
**Owner:** Data Team (Jonas)  
**Purpose:** Canonical definitions for all metrics and tables in `warehouse.db`

---

## Core Principle
When someone asks for "revenue," they mean **GAAP recognized revenue** (net of refunds, with proper timing). Use `revenue_recognized.net_amount`. Never use `orders.amount` for revenue questions.

---

## Tables and Fields

### `orders`
**Purpose:** Raw transaction log. Every customer purchase, as booked.

| Field | Type | Definition | Use For |
|-------|------|------------|---------|
| `order_id` | INTEGER | Unique order identifier | Joining to other tables |
| `customer_id` | INTEGER | FK to customers table | Customer analysis |
| `created_at` | TEXT (ISO date) | When the order was placed (UTC) | Booking date, not revenue date |
| `amount` | REAL | Gross order value in USD | **DO NOT use for revenue.** This is bookings. |
| `currency` | TEXT | Always 'USD' | Currency code |
| `status` | TEXT | completed, pending, cancelled | Order state |

**Key Point:** `orders.amount` = gross bookings (what the customer paid). This is NOT the same as recognized revenue because:
- Some orders haven't been delivered yet (pending revenue recognition)
- Some orders were refunded (reduces net revenue)
- Revenue recognition can span multiple periods

**Use this table for:** Order volume, average order value, booking trends (not revenue).

---

### `revenue_recognized`
**Purpose:** GAAP-compliant revenue. What finance reports to the board and auditors.

| Field | Type | Definition | Use For |
|-------|------|------------|---------|
| `id` | INTEGER | Record ID | Primary key |
| `order_id` | INTEGER | FK to orders table | Linking back to source order |
| `recognized_on` | TEXT (ISO date) | Date the revenue was recognized (UTC) | **Use this for period filters** |
| `period` | TEXT | Accounting period (e.g. '2026-01') | Period label (optional) |
| `gross_amount` | REAL | Order amount before refunds (USD) | Intermediate calculation |
| `refund_amount` | REAL | Total refunds applied (USD) | Refund tracking |
| `net_amount` | REAL | **Recognized revenue = gross - refunds** | **USE THIS FOR ALL REVENUE QUESTIONS** |

**Key Point:** `net_amount` is the single source of truth for revenue. 

**Important:** The `recognized_on` date may differ from `orders.created_at` due to:
- Subscription revenue recognized over time
- Products shipped after order placement
- Returns processed in a later period

**Use this table for:** Revenue (always), financial reporting, board decks, QBRs, forecasting.

---

### `refunds`
**Purpose:** Customer refunds and returns.

| Field | Type | Definition | Use For |
|-------|------|------------|---------|
| `refund_id` | INTEGER | Unique refund ID | Primary key |
| `order_id` | INTEGER | FK to orders table | Linking refund to order |
| `refunded_at` | TEXT (ISO date) | Date refund was issued (UTC) | Refund timing |
| `amount` | REAL | Refund amount in USD | Refund value |
| `reason` | TEXT | Reason code or description | Refund analysis |

**Key Point:** Refunds are already reflected in `revenue_recognized.refund_amount` and `revenue_recognized.net_amount`. Don't subtract them again.

**Use this table for:** Refund rate analysis, return reasons, customer satisfaction.

---

### `customers`
**Purpose:** Customer master data.

| Field | Type | Definition | Use For |
|-------|------|------------|---------|
| `customer_id` | INTEGER | Unique customer ID | Primary key |
| `name` | TEXT | Customer name | Display |
| `segment` | TEXT | SMB, Mid-Market, Enterprise | Segmentation |
| `country` | TEXT | ISO country code | Geography analysis |

**Use this table for:** Customer demographics, segmentation, cohort analysis.

---

### `daily_kpis`
**Purpose:** Daily rollup of key metrics (refreshed by ETL).

| Field | Type | Definition | Use For |
|-------|------|------------|---------|
| `day` | TEXT (ISO date) | Date (UTC) | Primary key |
| `revenue` | REAL | **Net recognized revenue for that day** (USD) | Daily revenue tracking |
| `orders` | INTEGER | Count of completed orders | Order volume |
| `sessions` | INTEGER | Website sessions | Traffic analysis |
| `updated_at` | TEXT (timestamp) | Last ETL update | Freshness check |

**Key Point:** `daily_kpis.revenue` matches the sum of `revenue_recognized.net_amount` for that day.

**Use this table for:** Daily trends, week-over-week growth, quick lookups.

---

## Common Queries

### Q2 2026 Revenue (Correct)
```sql
SELECT ROUND(SUM(net_amount), 2) AS revenue
FROM revenue_recognized
WHERE recognized_on >= '2026-04-01' AND recognized_on <= '2026-06-30';
-- Returns: $3,638,335.79
```

### Q2 2026 Revenue (WRONG - Don't Do This)
```sql
-- ❌ WRONG: This is gross bookings, not revenue
SELECT ROUND(SUM(amount), 2) AS revenue
FROM orders
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';
-- Returns: $4,138,212.16 (off by $500k!)
```

### Monthly Revenue (Correct)
```sql
SELECT 
    strftime('%Y-%m', recognized_on) AS month,
    ROUND(SUM(net_amount), 2) AS revenue
FROM revenue_recognized
WHERE recognized_on >= '2026-01-01'
GROUP BY month
ORDER BY month;
```

### Refund Rate (Q2 2026)
```sql
SELECT 
    ROUND(SUM(gross_amount), 2) AS gross_revenue,
    ROUND(SUM(refund_amount), 2) AS total_refunds,
    ROUND(100.0 * SUM(refund_amount) / SUM(gross_amount), 2) AS refund_rate_pct
FROM revenue_recognized
WHERE recognized_on >= '2026-04-01' AND recognized_on <= '2026-06-30';
```

---

## Glossary

| Term | Definition | Table.Field |
|------|------------|-------------|
| **Revenue** | GAAP net recognized revenue | `revenue_recognized.net_amount` |
| **Bookings** | Gross order value when placed | `orders.amount` |
| **Net Revenue** | Revenue after refunds | `revenue_recognized.net_amount` |
| **Gross Revenue** | Revenue before refunds | `revenue_recognized.gross_amount` |
| **ARR** | Annual Recurring Revenue | Not in warehouse yet (TBD) |
| **MRR** | Monthly Recurring Revenue | Not in warehouse yet (TBD) |

---

## FAQ

**Q: Why is orders.amount different from revenue_recognized.net_amount for the same period?**  
A: Three reasons: (1) revenue recognition timing (orders created in Q2 might be recognized in Q3), (2) refunds reduce net revenue, (3) some Q2 revenue comes from prior-period orders that were just delivered.

**Q: Can I use daily_kpis.revenue for monthly totals?**  
A: Yes! It's a rollup of `revenue_recognized.net_amount` by day. Faster for queries spanning many months.

**Q: What if someone asks for "gross revenue"?**  
A: Use `revenue_recognized.gross_amount` (recognized revenue before refunds). Still filter by `recognized_on`, not `orders.created_at`.

**Q: What if someone asks for "bookings"?**  
A: Use `orders.amount` filtered by `created_at`. Make it clear in your answer: "Q2 bookings were $X (note: this is gross orders, not recognized revenue)."

---

## Change Log

- **2026-09-15:** Initial version (created after Q2 board deck incident)
