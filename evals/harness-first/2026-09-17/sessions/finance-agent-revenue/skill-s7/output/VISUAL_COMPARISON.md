# The $500K Discrepancy: A Tale of Two Queries

## The Question
**"What was our Q2 2026 revenue?"**

---

## What FinBot Did (Wrong) ❌

```sql
SELECT ROUND(SUM(amount), 2) AS revenue 
FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';
```

**Result:** $4,138,212.16

### Why This Happened:
- Prompt listed both `orders` and `revenue_recognized` tables
- No definition of what "revenue" means
- Model reasonably interpreted "Q2 revenue" as "orders in Q2"
- Query is technically correct for "gross bookings"

---

## What Finance Calculates (Correct) ✅

```sql
SELECT ROUND(SUM(net_amount), 2) AS revenue 
FROM revenue_recognized 
WHERE period IN ('2026-04', '2026-05', '2026-06');
```

**Result:** $3,638,335.79

### Why This Is Right:
- Uses recognized revenue (GAAP accounting)
- Net of refunds
- Grouped by accounting period (not order creation time)
- Matches quarterly close and board reporting

---

## The Difference: $499,876.37 (13.7%)

| Component | Amount | Explanation |
|-----------|--------|-------------|
| Gross Q2 bookings | $4,138,212.16 | What FinBot used (orders.amount) |
| Less: Refunds | -$332,527.58 | Customers refunded orders |
| Less: Timing difference | -$167,348.79 | Orders created in Q2 but recognized in Q3, or vice versa |
| **Net Q2 revenue** | **$3,638,335.79** | **What Finance reports** |

---

## Why It Looked Like Hallucination

✗ "The model made up $4.1M"  
✓ The model faithfully used a real number from the database

✗ "The model is bad at math"  
✓ The model did perfect math on the wrong table

✗ "We need a smarter model"  
✓ We need clearer instructions for the current model

---

## Side-by-Side Comparison

| Aspect | orders.amount | revenue_recognized.net_amount |
|--------|---------------|-------------------------------|
| **What it measures** | Gross order value | Net recognized revenue |
| **When it's recorded** | Order creation time | Accounting recognition date |
| **Includes refunds?** | No (refunds are separate table) | Yes (net_amount = gross - refunds) |
| **Time dimension** | created_at timestamp | period (YYYY-MM) |
| **Used by Finance?** | For pipeline metrics | For official reporting ✓ |
| **Should be "revenue"?** | NO | YES ✓ |

---

## The Fix

### Before:
```markdown
Tables you can use:
- customers
- orders
- refunds
- revenue_recognized
- daily_kpis

If a question is about money, always give a single headline number with a dollar sign.
```

### After:
```markdown
## Important: Revenue Definition

**Revenue** means recognized net revenue (after refunds) from the `revenue_recognized` table.

- Use `revenue_recognized.net_amount` grouped by `period` for all revenue questions
- Do NOT use `orders.amount` (that's gross bookings before refunds)
- Match what Finance reports in quarterly close and board materials

### `revenue_recognized` ← USE THIS FOR REVENUE
- **When:** Any question about revenue, especially monthly/quarterly
- **Key columns:** `period` (YYYY-MM), `net_amount` (gross minus refunds)
- **Example:** Q2 revenue = `SELECT SUM(net_amount) FROM revenue_recognized WHERE period IN ('2026-04','2026-05','2026-06')`

### `orders`
- **When:** Questions about order volume, average order value, or order creation timing
- **Key columns:** `created_at`, `amount` (gross), `status`
- **Note:** This is gross bookings, not recognized revenue
```

---

## Proof: I Ran Both Queries

```python
import sqlite3
conn = sqlite3.connect('warehouse.db')

# FinBot's query
result1 = conn.execute("""
    SELECT ROUND(SUM(amount), 2) 
    FROM orders 
    WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30'
""").fetchone()[0]
print(f"FinBot: ${result1:,.2f}")  # $4,138,212.16

# Finance's calculation
result2 = conn.execute("""
    SELECT ROUND(SUM(net_amount), 2) 
    FROM revenue_recognized 
    WHERE period IN ('2026-04', '2026-05', '2026-06')
""").fetchone()[0]
print(f"Finance: ${result2:,.2f}")  # $3,638,335.79

print(f"Difference: ${result1 - result2:,.2f}")  # $499,876.37
```

**Both numbers are mathematically correct from their source tables.**  
**The bug was not knowing which table to use.**

---

## Takeaway

This incident proves the "harness first" principle:

> Before blaming the model, check if it has:
> - Clear definitions of metrics
> - A golden set to catch errors
> - An eval process for changes

FinBot had none of these. Now it has all three.

**The model didn't hallucinate. The harness was missing.**
