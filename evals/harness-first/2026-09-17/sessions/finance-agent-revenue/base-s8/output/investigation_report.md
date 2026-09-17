# FinBot Q2 Revenue Discrepancy - Investigation Report
**Date:** September 16, 2026  
**Investigator:** Data Engineering  
**Urgency:** High (Board pre-read correction needed)

---

## Executive Summary

**The bot is NOT hallucinating. It's querying the wrong table.**

- **FinBot reported:** $4.1M ($4,138,212.16)
- **Finance close:** $3.6M ($3,638,335.79)
- **Discrepancy:** $499,876 (13.7% overstatement)

**Root cause:** FinBot queried the `orders` table instead of the `revenue_recognized` table. The orders table includes cancelled orders and doesn't account for refunds, leading to a significantly inflated revenue figure.

**Recommendation:** This is NOT a model quality issue. The current model (Claude Sonnet 4.5) is performing correctly given the system prompt. The problem is **inadequate prompt guidance** about which tables to use for financial metrics.

---

## Technical Details

### What FinBot Did (Incorrect)

From the Slack transcript on 2026-09-11:

```sql
SELECT ROUND(SUM(amount), 2) AS revenue 
FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';
```

**Result:** $4,138,212.16

**Why this is wrong:**
1. Includes cancelled orders: $360,039.00
2. Includes fully refunded orders: $189,943.45
3. Doesn't account for partial refunds on completed orders
4. Uses order creation date, not revenue recognition date

### What FinBot Should Have Done (Correct)

```sql
SELECT ROUND(SUM(net_amount), 2) AS revenue
FROM revenue_recognized
WHERE period IN ('2026-04', '2026-05', '2026-06');
```

**Result:** $3,638,335.79 (matches Finance's $3.6M close)

### Breakdown by Period

| Period | Gross Revenue | Refunds | Net Revenue |
|--------|---------------|---------|-------------|
| 2026-04 | $1,369,750.07 | $132,233.44 | $1,237,516.63 |
| 2026-05 | $1,310,501.70 | $100,843.39 | $1,209,658.31 |
| 2026-06 | $1,290,611.60 | $99,450.75 | $1,191,160.85 |
| **Q2 Total** | **$3,970,863.37** | **$332,527.58** | **$3,638,335.79** |

### Order Status Breakdown (Q2)

| Status | Orders | Amount |
|--------|--------|--------|
| completed | 1,733 | $3,269,510.70 |
| partially_refunded | 174 | $318,719.01 |
| cancelled | 202 | $360,039.00 |
| refunded | 104 | $189,943.45 |
| **Total** | **2,213** | **$4,138,212.16** |

The orders table total ($4.1M) includes $550K in cancelled/refunded orders that should NOT be counted as revenue.

---

## Why This Happened

### Current System Prompt (prompt.md)

```markdown
You are FinBot, the internal finance assistant for Norvel Commerce.

People from sales, ops and the exec team ask you questions about the business. 
Use the `run_sql` tool to query the warehouse and answer with a clear number. 
Be concise, people paste your answers into decks and Slack.

Tables you can use:
- customers
- orders
- refunds
- revenue_recognized
- daily_kpis

If a question is about money, always give a single headline number with a dollar sign.
```

**The problem:** The prompt lists tables but provides ZERO guidance on:
- Which table to use for revenue questions
- The semantic difference between `orders.amount` and `revenue_recognized.net_amount`
- How to handle refunds and cancellations
- Revenue recognition principles

The model made a reasonable but incorrect assumption that "revenue" = sum of order amounts.

---

## Is This a Model Quality Issue?

**NO.** Here's why upgrading to Opus or GPT-6 won't fix this:

### Test: What Would a Smarter Model Do?

Given the current prompt, even a more advanced model would likely:
1. See "revenue" in the question
2. Look at available tables
3. Choose `orders` or `revenue_recognized` based on limited context
4. Have a ~50% chance of choosing wrong

The issue is **insufficient domain guidance**, not model capability.

### Evidence Supporting This

1. **The SQL is correct:** The model wrote valid SQL with proper date filtering
2. **The logic is sound:** Summing amounts in a transaction table is a reasonable approach
3. **Tool usage is appropriate:** The model correctly used the `run_sql` tool
4. **No hallucination:** The number $4,138,212.16 is the actual sum in the database

The model did exactly what it should do given the vague instructions.

---

## Recommended Fixes

### Option 1: Update System Prompt (Recommended - IMMEDIATE)

Replace the current prompt with:

```markdown
You are FinBot, the internal finance assistant for Norvel Commerce.

People from sales, ops and the exec team ask you questions about the business. 
Use the `run_sql` tool to query the warehouse and answer with a clear number. 
Be concise, people paste your answers into decks and Slack.

IMPORTANT - Table Usage Guidelines:

**For REVENUE questions, ALWAYS use the `revenue_recognized` table:**
- Query revenue_recognized.net_amount (never orders.amount)
- Filter by `period` column (format: 'YYYY-MM') OR `recognized_on` date
- This table reflects proper revenue recognition with refunds already netted out
- Example: SELECT SUM(net_amount) FROM revenue_recognized WHERE period IN ('2026-04', '2026-05', '2026-06')

**Other tables:**
- `orders`: Raw transaction data, includes cancelled orders (NOT for revenue reporting)
- `refunds`: Individual refund records (already incorporated in revenue_recognized)
- `daily_kpis`: Incomplete operational metrics (not for official reporting)
- `customers`: Customer master data

When asked about quarterly revenue, use the period column (Q1 = '01','02','03', Q2 = '04','05','06', etc.)

If a question is about money, always give a single headline number with a dollar sign.
```

**Impact:** 
- Zero code changes
- Zero cost increase
- Immediate deployment
- Fixes the root cause

### Option 2: Add Schema Documentation (Medium-term)

Extend the prompt to include column-level descriptions:

```sql
CREATE TABLE revenue_recognized (
  -- THIS IS THE SOURCE OF TRUTH FOR REVENUE REPORTING
  id INTEGER PRIMARY KEY,
  order_id INTEGER,
  recognized_on TEXT,  -- Date revenue was recognized
  period TEXT,         -- Format: 'YYYY-MM', use this for month/quarter queries
  gross_amount REAL,   -- Before refunds
  refund_amount REAL,  -- Total refunds applied
  net_amount REAL      -- ALWAYS USE THIS for revenue queries
)
```

### Option 3: Add Validation Layer (Long-term)

Create a post-query validation check:

```python
def validate_query(query, question):
    if 'revenue' in question.lower() and 'orders.amount' in query.lower():
        return {
            'error': 'Revenue questions should query revenue_recognized.net_amount, not orders.amount'
        }
    return None
```

---

## Testing the Fix

I recommend testing the updated prompt with these questions:

1. "What was our Q2 2026 revenue?" → Should return $3.6M
2. "What was our Q1 2026 revenue?" → Should return sum from revenue_recognized for Jan-Mar
3. "How many orders did we have in Q2?" → Can use orders table (count is fine)
4. "What were total refunds in Q2?" → Should use refunds or revenue_recognized.refund_amount

---

## Action Items for Daniel

### Immediate (Before Board Meeting)
- [ ] **DO NOT** upgrade to a more expensive model (won't solve this)
- [ ] Update `prompt.md` with the recommended guidance above
- [ ] Verify the fix: Run `python agent.py "what was Q2 2026 revenue?"` → should now return ~$3.6M
- [ ] Correct the board pre-read with: **"Q2 2026 Revenue: $3.6M"**

### Short-term (This Week)
- [ ] Add integration tests for common finance queries
- [ ] Document the `revenue_recognized` table as the source of truth
- [ ] Review other numbers in the board deck that came from FinBot

### Medium-term (Next Sprint)
- [ ] Add query validation logic
- [ ] Create a finance metrics glossary in the prompt
- [ ] Consider adding example queries to the system prompt

---

## Appendix: Full Data Comparison

```
Table: orders (what FinBot used)
├── All orders Q2:           $4,138,212.16
├── Completed only:          $3,269,510.70
├── Partially refunded:        $318,719.01
├── Cancelled (should exclude): $360,039.00 ❌
└── Refunded (should exclude):  $189,943.45 ❌

Table: revenue_recognized (what Finance uses)
├── Gross revenue:           $3,970,863.37
├── Less: Refunds:             $332,527.58
└── Net revenue:             $3,638,335.79 ✓

Table: daily_kpis (incomplete data)
└── Q2 revenue:              $2,262,135.23 (only 49 days, missing June)
```

---

## Bottom Line

**This is a data engineering problem, not an AI problem.**

The model is working as designed. It just needs clearer instructions about your company's accounting rules. Spending more on a better model is like buying a Ferrari when you need a map.

Fix the prompt today, verify with Finance, and move on. Total fix time: 15 minutes.
