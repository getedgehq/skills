# FinBot Data Dictionary

**Owner:** Data team (Jonas)  
**Last updated:** 2026-09-16  
**Purpose:** Defines every metric and table that FinBot can query. Update this when ETL changes.

---

## Metric Definitions

### Revenue

**Official definition:** Net revenue recognized in an accounting period, after refunds.

**Source:** `revenue_recognized.net_amount`, grouped by `period`

**Example query:**
```sql
SELECT period, ROUND(SUM(net_amount), 2) as revenue
FROM revenue_recognized
WHERE period = '2026-04'
GROUP BY period;
```

**NOT revenue:**
- `orders.amount` = gross bookings (before refunds, by order creation date, not accounting period)
- `daily_kpis.revenue` = daily revenue snapshot (use for quick daily trends, not official reporting)

---

## Table Reference

### `revenue_recognized`

The **source of truth** for all revenue questions.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `order_id` | INTEGER | Links to orders table |
| `recognized_on` | TEXT | Date revenue was recognized (YYYY-MM-DD) |
| `period` | TEXT | Accounting period (YYYY-MM format) |
| `gross_amount` | REAL | Order amount before refunds |
| `refund_amount` | REAL | Total refunds applied to this order |
| `net_amount` | REAL | **Use this for revenue** = gross - refunds |

**When to use:** Any question about revenue, especially for quarters, months, or board reporting.

**Example questions:**
- "What was Q2 revenue?" → sum `net_amount` where `period` IN ('2026-04', '2026-05', '2026-06')
- "Revenue in July?" → sum `net_amount` where `period` = '2026-07'

---

### `orders`

Raw order transactions by creation timestamp.

| Column | Type | Description |
|--------|------|-------------|
| `order_id` | INTEGER | Primary key |
| `customer_id` | INTEGER | Links to customers |
| `created_at` | TEXT | Order timestamp (YYYY-MM-DD HH:MM:SS) |
| `amount` | REAL | Gross order amount (before refunds) |
| `currency` | TEXT | Always 'USD' |
| `status` | TEXT | completed, cancelled, pending |

**When to use:** 
- Questions about order volume or average order value
- Questions explicitly about "bookings" or "gross sales"
- Analysis by order creation time (not revenue recognition time)

**NOT for revenue:** This table has gross amounts. Refunds are in a separate table.

---

### `refunds`

Individual refund transactions.

| Column | Type | Description |
|--------|------|-------------|
| `refund_id` | INTEGER | Primary key |
| `order_id` | INTEGER | Which order was refunded |
| `refunded_at` | TEXT | Refund timestamp |
| `amount` | REAL | Refund amount |
| `reason` | TEXT | damaged, duplicate charge, goodwill, etc. |

**When to use:** 
- "How many refunds last month?"
- "What % of orders get refunded?"
- Refund rate or reason analysis

---

### `daily_kpis`

Pre-aggregated daily metrics. Updated nightly.

| Column | Type | Description |
|--------|------|-------------|
| `day` | TEXT | Date (YYYY-MM-DD) |
| `revenue` | REAL | Daily net revenue (matches revenue_recognized for that day) |
| `orders` | INTEGER | Order count |
| `sessions` | INTEGER | Website sessions |
| `updated_at` | TEXT | ETL timestamp |

**When to use:** 
- Quick daily trends ("revenue yesterday")
- Conversion analysis (revenue per session)

**Caveat:** Revenue here is reconciled daily. For official monthly/quarterly reporting, use `revenue_recognized`.

---

### `customers`

Not documented yet - used for customer segmentation queries.

---

## Common Question Patterns

| Question | Correct Table | Correct Column | Example SQL |
|----------|---------------|----------------|-------------|
| "What was Q2 revenue?" | `revenue_recognized` | `net_amount` | `SELECT SUM(net_amount) FROM revenue_recognized WHERE period IN ('2026-04','2026-05','2026-06')` |
| "How many orders in July?" | `orders` | COUNT(*) | `SELECT COUNT(*) FROM orders WHERE created_at LIKE '2026-07%'` |
| "Refund rate last month?" | `refunds` + `orders` | JOIN both | See refunds section |
| "Revenue yesterday?" | `daily_kpis` | `revenue` | `SELECT revenue FROM daily_kpis WHERE day = '2026-09-15'` |

---

## Finance Team Alignment

**Finance uses:** `revenue_recognized.net_amount` by `period` for all official reporting (board decks, investor updates, quarterly close).

**FinBot must match Finance.** If someone asks for revenue without qualifying it, assume they mean recognized net revenue from `revenue_recognized`.

---

## Changes to Track

| Date | Change | Impact |
|------|--------|--------|
| 2026-09-16 | Created this dictionary after Q2 revenue incident | FinBot now has clear metric definitions |

**How to update:** When ETL adds/changes tables, update this doc AND re-test the golden set.
