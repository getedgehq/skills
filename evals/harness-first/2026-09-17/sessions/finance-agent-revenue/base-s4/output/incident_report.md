# FinBot Revenue Discrepancy - Root Cause Analysis
**Date:** September 15, 2026  
**Prepared for:** Daniel Kurz (CEO)  
**Issue:** Board pre-read reported Q2 revenue as $4.1M (from finbot), but Finance closed Q2 at $3.6M

---

## Executive Summary

**The bot is NOT hallucinating. It's querying the wrong table.**

- **FinBot reported:** $4,138,212 (sum of orders created in Q2)
- **Finance reported:** $3,638,336 (GAAP revenue recognized in Q2)
- **Difference:** $499,876 (13.7% overstatement)

This is **not a model quality issue**. The model executed the query correctly, but it doesn't understand the difference between cash/bookings (orders table) and accrual accounting (revenue_recognized table).

**Recommendation:** This is a **data/prompt engineering fix**, not a model upgrade. See solutions below.

---

## Root Cause

When Priya asked "*what was our Q2 2026 revenue?*", finbot generated this SQL:

```sql
SELECT ROUND(SUM(amount), 2) AS revenue 
FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';
```

**Problem:** This query sums all order amounts created in Q2, which measures **bookings** (when customers placed orders), not **revenue** (when we recognize it per GAAP).

The correct query should use the `revenue_recognized` table:

```sql
SELECT ROUND(SUM(net_amount), 2) AS revenue 
FROM revenue_recognized 
WHERE recognized_on BETWEEN '2026-04-01' AND '2026-06-30';
```

---

## Why the $500K Difference Exists

### Breakdown of the $499,876 discrepancy:

| Component | Amount | Explanation |
|-----------|--------|-------------|
| **A. Q2 orders not yet recognized** | +$360,039 | 202 orders created in Q2 but cancelled/pending (not in revenue_recognized) |
| **B. Q2 orders recognized after Q2** | +$120,370 | 65 orders created late in Q2, recognized in Q3 (timing lag) |
| **C. Pre-Q2 orders recognized in Q2** | -$264,846 | 147 orders from Q1 that got recognized in Q2 |
| **D. Net refund impact** | +$142,584 | Difference between order refunds vs. revenue refund adjustments |
| **Total net difference** | **~$500K** | Orders table overstates Q2 GAAP revenue |

### Key Insights:

1. **Timing differences:** Revenue recognition lags order creation by days/weeks (fulfillment, payment clearing, etc.)
2. **Cancelled orders included:** Orders table includes 202 cancelled orders ($360K) that never became revenue
3. **Refund accounting:** Orders table shows point-in-time refund status; revenue_recognized tracks cumulative refund impact including refunds that happened after order date

---

## Examples from the Data

### Example 1: Cancelled order counted by finbot, not revenue
- Order 102301: created April 2, $2,288, status=cancelled
- ✅ Included in finbot's $4.1M
- ❌ NOT in revenue_recognized (correctly excluded from finance's $3.6M)

### Example 2: Q2 order recognized in Q3
- Order 104331: created June 23, $3,414
- ✅ Included in finbot's Q2 total
- ❌ Revenue recognized July 2 (Q3) - not in Q2 revenue

### Example 3: Q1 order recognized in Q2
- Order 101980: created March 23 (Q1), recognized April 1 (Q2), $6,914
- ❌ NOT in finbot's Q2 total (created in Q1)
- ✅ Correctly in finance's Q2 revenue (recognized in Q2)

### Example 4: Refund impact
- Order 102041: order amount $339, but customer refunded $122
- Finbot sees: $339 (full order amount)
- Finance sees: $217 (net after refund)

---

## The Model Performed Correctly

The LLM (Claude Sonnet 4-5) did exactly what it was designed to do:
- ✅ Understood the question semantically
- ✅ Generated valid, syntactically correct SQL
- ✅ Returned accurate results from the query
- ✅ Formatted the answer clearly

**The issue:** The model doesn't know that "revenue" means **GAAP revenue recognition**, not bookings. The system prompt only lists table names without explaining when to use each table.

---

## Solutions (in priority order)

### Option 1: Fix the System Prompt (RECOMMENDED - quickest fix)
**Timeline:** 30 minutes  
**Cost:** $0

Update `prompt.md` to:
```markdown
When asked about revenue, ALWAYS use the revenue_recognized table (GAAP/accrual basis).
- revenue_recognized.net_amount = recognized revenue (after refunds)
- Use recognized_on for date filtering
- The orders table shows bookings/cash, NOT recognized revenue

Tables:
- revenue_recognized (USE THIS for revenue questions)
- orders (bookings/order creation, not revenue)
- refunds
- customers  
- daily_kpis
```

### Option 2: Add Query Validation
**Timeline:** 1-2 hours  
**Cost:** Engineering time

Add a check in `agent.py` that warns/blocks queries like:
- "revenue" questions that query `orders` table
- Suggests using `revenue_recognized` instead

### Option 3: Simplify with Views
**Timeline:** 2-3 hours  
**Cost:** ETL pipeline update

Create a `quarterly_revenue` view in the ETL that pre-calculates revenue by quarter:
```sql
CREATE VIEW quarterly_revenue AS 
SELECT 
  strftime('%Y-Q', recognized_on) as quarter,
  SUM(net_amount) as revenue
FROM revenue_recognized
GROUP BY quarter;
```

Then finbot can just query this view - harder to get wrong.

### Option 4: Add Few-Shot Examples to Prompt
**Timeline:** 1 hour  
**Cost:** $0

Add example Q&As to the prompt:
```
Example:
Q: "What was Q2 revenue?"
A: SELECT SUM(net_amount) FROM revenue_recognized WHERE recognized_on BETWEEN '2026-04-01' AND '2026-06-30'
```

---

## NOT Recommended: Model Upgrade

**We do NOT need GPT-6 or Opus** for this issue. Why:

1. This is a **knowledge problem**, not a reasoning problem
2. No LLM inherently knows your company's accounting tables without being told
3. More expensive models won't magically know to use `revenue_recognized` vs `orders`
4. The current model's SQL generation is already excellent

**Analogy:** This is like blaming a calculator for giving you the wrong answer when you entered the wrong numbers. The tool worked; the inputs need fixing.

---

## Immediate Action Items

1. **Today (15min):** Update board pre-read to $3.6M with correction note
2. **Tomorrow (30min):** Deploy updated prompt.md with revenue_recognized guidance
3. **This week:** Add validation that surfaces warnings for ambiguous queries
4. **Next sprint:** Consider adding quarterly_revenue view to prevent future issues

---

## Testing the Fix

After deploying the prompt fix, test with:

```python
python agent.py "what was our Q2 2026 revenue?"
```

Expected result:
```
Q2 2026 revenue was $3,638,335.79 (~$3.6M).
```

Also test:
- "what was Q1 revenue?" → Should use revenue_recognized
- "how many orders did we get in Q2?" → Can use orders table (this is about count, not revenue)
- "what were Q2 bookings?" → Can use orders table (bookings ≠ revenue)

---

## Appendix: Full Data Comparison

### Orders Table (what finbot used):
- Total amount: **$4,138,212**
- Order count: 2,213
- Includes: cancelled orders, refunded orders (at full amount), all Q2 orders regardless of recognition timing

### Revenue_Recognized Table (what finance uses):
- Net revenue: **$3,638,336**
- Gross revenue: $3,970,863
- Refunds: $332,528
- Record count: 2,106
- Represents: GAAP-compliant recognized revenue for Q2 period

### Key Schema Details:

**orders table:**
- `order_id`, `customer_id`, `created_at`, `amount`, `status`
- Represents: when order was placed and initial amount
- Purpose: operational tracking of bookings

**revenue_recognized table:**
- `order_id`, `recognized_on`, `period`, `gross_amount`, `refund_amount`, `net_amount`
- Represents: when revenue was earned (GAAP basis)
- Purpose: financial reporting, board metrics, investor reporting

---

## Questions for Follow-up

1. Should we add a `bookings` metric that explicitly tracks orders table? (useful for sales team)
2. Should finbot warn users when they ask ambiguous questions? ("Did you mean revenue or bookings?")
3. Should we audit other finbot queries that might have similar issues?

---

**Bottom Line:** Fix the prompt, not the model. This is a 30-minute fix, not a "we need better AI" problem.
