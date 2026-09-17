# FinBot Data Dictionary

**CRITICAL: For any revenue question, use `revenue_recognized` table, NOT `orders` table.**

## Tables

### `revenue_recognized` ⭐ USE THIS FOR REVENUE
**Purpose:** Source of truth for all revenue reporting. Used by Finance for board reporting, investor updates, and financial statements.

| Column | Type | Definition |
|--------|------|------------|
| `id` | INTEGER | Primary key |
| `order_id` | INTEGER | Links to orders table |
| `recognized_on` | TEXT | Date revenue was recognized (YYYY-MM-DD) |
| `period` | TEXT | Accounting period (YYYY-MM format, e.g., '2026-04') |
| `gross_amount` | REAL | Total order value before refunds |
| `refund_amount` | REAL | Total refunds applied to this order |
| `net_amount` | REAL | **Net revenue = gross_amount - refund_amount** ⭐ |

**Period mapping:**
- Q1 = periods '2026-01', '2026-02', '2026-03'
- Q2 = periods '2026-04', '2026-05', '2026-06'
- Q3 = periods '2026-07', '2026-08', '2026-09'
- Q4 = periods '2026-10', '2026-11', '2026-12'

**Revenue queries MUST:**
1. Use `SUM(net_amount)` not `SUM(gross_amount)` or `orders.amount`
2. Filter by `period` column for quarterly/monthly questions
3. Never sum from `orders` table - it includes cancelled orders and doesn't subtract refunds

**Example correct queries:**
```sql
-- Q2 2026 revenue
SELECT SUM(net_amount) FROM revenue_recognized WHERE period IN ('2026-04', '2026-05', '2026-06');

-- August 2026 revenue  
SELECT SUM(net_amount) FROM revenue_recognized WHERE period = '2026-08';

-- Year-to-date 2026
SELECT SUM(net_amount) FROM revenue_recognized WHERE period LIKE '2026-%';
```

---

### `orders`
**Purpose:** Transaction log. Contains ALL orders including cancelled. DO NOT use for revenue calculations.

| Column | Type | Definition |
|--------|------|------------|
| `order_id` | INTEGER | Primary key |
| `customer_id` | INTEGER | Links to customers table |
| `created_at` | TEXT | Order creation timestamp (YYYY-MM-DD HH:MM:SS) |
| `amount` | REAL | Order value (does NOT account for refunds or cancellations) |
| `currency` | TEXT | Currency code (USD, EUR, etc.) |
| `status` | TEXT | Order status: completed, cancelled, refunded, partially_refunded |

**Use cases:**
- Order counts: `COUNT(*) FROM orders WHERE status IN ('completed', 'partially_refunded')`
- Order velocity, conversion metrics
- Customer purchase patterns

**DO NOT use for:**
- Revenue calculations (use `revenue_recognized` instead)
- Financial reporting

---

### `refunds`
**Purpose:** Refund transaction log.

| Column | Type | Definition |
|--------|------|------------|
| `refund_id` | INTEGER | Primary key |
| `order_id` | INTEGER | Links to orders table |
| `refunded_at` | TEXT | Refund timestamp (YYYY-MM-DD HH:MM:SS) |
| `amount` | REAL | Refund amount |
| `reason` | TEXT | Refund reason |

**Use cases:**
- Refund analysis by reason
- Refund volume and trends
- Customer service metrics

---

### `customers`
**Purpose:** Customer master data.

| Column | Type | Definition |
|--------|------|------------|
| `customer_id` | INTEGER | Primary key |
| `name` | TEXT | Customer name |
| `segment` | TEXT | Customer segment (enterprise, smb, consumer) |
| `country` | TEXT | Country code |

---

### `daily_kpis`
**Purpose:** Pre-aggregated daily metrics.

| Column | Type | Definition |
|--------|------|------------|
| `day` | TEXT | Date (YYYY-MM-DD) |
| `revenue` | REAL | Daily revenue snapshot |
| `orders` | INTEGER | Order count |
| `sessions` | INTEGER | Website sessions |
| `updated_at` | TEXT | Last ETL update timestamp |

## Common Mistakes to Avoid

❌ **WRONG:** `SELECT SUM(amount) FROM orders WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30'`
- Includes cancelled orders ($360k in Q2)
- Includes fully refunded orders ($190k in Q2)  
- Doesn't subtract partial refunds ($333k in Q2)
- Result: Overstates revenue by ~$500k

✅ **CORRECT:** `SELECT SUM(net_amount) FROM revenue_recognized WHERE period IN ('2026-04', '2026-05', '2026-06')`

---

## Testing Your Query

Before returning a revenue number:
1. Verify you're using `revenue_recognized.net_amount`
2. Verify you're filtering by `period` not `created_at`
3. Check: does the result make sense vs. adjacent periods?

If someone asks for "sales", "bookings", "revenue", "how much we made", they want `revenue_recognized.net_amount`.
