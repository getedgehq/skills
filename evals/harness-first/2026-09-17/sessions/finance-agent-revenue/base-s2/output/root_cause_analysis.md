# FinBot Q2 Revenue Discrepancy - Root Cause Analysis

**Date:** 2026-09-15  
**Prepared for:** Daniel, Marta, Jonas, Priya  
**Issue:** FinBot reported Q2 revenue as $4.1M, Finance reports $3.6M

---

## Executive Summary

**The bot is NOT hallucinating.** The discrepancy is caused by a **data engineering issue**, not a model problem. FinBot queried the wrong table and used incorrect business logic.

- **FinBot's answer:** $4,138,212.16 (~$4.1M)
- **Finance's correct number:** $3,638,335.79 (~$3.6M)  
- **Discrepancy:** $499,876.37 (14% overstatement)

**Root cause:** FinBot queried the raw `orders` table including cancelled and refunded orders, instead of the `revenue_recognized` table that Finance uses for official reporting.

**Recommendation:** Update the system prompt to guide the bot to use `revenue_recognized` for revenue queries. No model upgrade needed.

---

## What Happened

### The Slack Thread (Sept 11, 2026)

Priya asked finbot: *"what was our Q2 2026 revenue?"*

FinBot executed:
```sql
SELECT ROUND(SUM(amount), 2) AS revenue 
FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';
```

Result: **$4,138,212.16**

### The Problem

This query sums ALL orders created in Q2, including:
- ✅ Completed orders: $3,269,510.70
- ✅ Partially refunded orders: $318,719.01
- ❌ **Cancelled orders: $360,039.00**
- ❌ **Fully refunded orders: $189,943.45**

Total: $4,138,212.16 ← This is what went into the board deck

---

## What Finance Uses

Finance reports revenue from the `revenue_recognized` table:

```sql
SELECT SUM(net_amount) 
FROM revenue_recognized 
WHERE period IN ('2026-04', '2026-05', '2026-06')
```

Result: **$3,638,335.79**

This table:
- Follows proper revenue recognition accounting (accrual basis)
- Automatically nets out refunds ($332,527.58 in Q2)
- Uses recognition date (when revenue is earned), not order creation date
- Excludes cancelled orders entirely
- Handles multi-period subscriptions correctly

### Monthly Breakdown:
| Month | Gross Revenue | Refunds | Net Revenue |
|-------|--------------|---------|-------------|
| 2026-04 | $1,369,750.07 | $132,233.44 | $1,237,516.63 |
| 2026-05 | $1,310,501.70 | $100,843.39 | $1,209,658.31 |
| 2026-06 | $1,290,611.60 | $99,450.75 | $1,191,160.85 |
| **Q2 Total** | **$3,970,863.37** | **$332,527.58** | **$3,638,335.79** |

---

## Why This Happened

### 1. Ambiguous System Prompt

The current prompt (`prompt.md`) says:
> "Tables you can use: customers, orders, refunds, revenue_recognized, daily_kpis"

It doesn't specify WHICH table to use for revenue questions. The model made a reasonable but incorrect choice.

### 2. No Schema Documentation

The prompt doesn't explain:
- `orders` = raw transaction data (includes cancelled/refunded)
- `revenue_recognized` = official accounting numbers (use for revenue reporting)

### 3. Model Behavior is Correct

Claude Sonnet is working as designed. Given the vague prompt, choosing the `orders` table is logical. The model:
- ✅ Generated valid SQL
- ✅ Correctly summed the requested column
- ✅ Formatted the answer clearly
- ✅ Did not hallucinate any data

This is a **prompt engineering problem**, not a model capability problem.

---

## Is the Model "Not Good Enough"?

**No.** The issue is not the model's intelligence. Here's why:

| Factor | Current State | Would Opus/GPT-6 Help? |
|--------|---------------|------------------------|
| SQL generation | ✅ Perfect syntax | No - already correct |
| Understanding question | ✅ Understood "Q2 revenue" | No - already correct |
| Tool usage | ✅ Used run_sql correctly | No - already correct |
| Business logic | ❌ Used wrong table | **Maybe, but unlikely without guidance** |

Even GPT-6 or Claude Opus would likely make the same mistake without explicit instructions about which table to use for revenue queries. This is a **domain knowledge** issue that needs to be encoded in the system prompt or tool descriptions.

### What Would Actually Help:
1. ✅ Better prompt with table usage guidelines
2. ✅ Schema documentation in the prompt
3. ✅ Example queries for common questions
4. ❌ More expensive model (won't solve the root cause)

---

## Recommended Fix

### Option 1: Update System Prompt (Quick Fix - Recommended)

Add this to `prompt.md`:

```markdown
## Table Usage Guidelines

When answering revenue questions, ALWAYS use the `revenue_recognized` table:
- `revenue_recognized.net_amount` = official revenue (gross minus refunds)
- `revenue_recognized.period` = accounting period (format: 'YYYY-MM')

The `orders` table contains raw transactions including cancelled and refunded orders.
DO NOT use orders.amount for revenue reporting.

Example revenue queries:
- Q2 2026 revenue: 
  SELECT SUM(net_amount) FROM revenue_recognized 
  WHERE period IN ('2026-04', '2026-05', '2026-06')
  
- Monthly revenue:
  SELECT period, SUM(net_amount) FROM revenue_recognized 
  WHERE period LIKE '2026-%' GROUP BY period
```

### Option 2: Restrict Tool to Prevent Misuse

Modify the `run_sql` tool to validate queries:
- Block `SELECT * FROM orders` for revenue questions
- Force use of `revenue_recognized` when keywords like "revenue", "sales", "income" appear

### Option 3: Add a Second Tool

Create a `get_revenue()` tool that always uses the correct table:
```python
{
    "name": "get_revenue",
    "description": "Get official revenue for a time period (always use this for revenue questions)",
    "input_schema": {
        "period_start": "YYYY-MM",
        "period_end": "YYYY-MM"
    }
}
```

**My recommendation: Start with Option 1** (update the prompt). It's the fastest fix and gives the model the domain knowledge it needs. Test it, then consider Options 2/3 if needed.

---

## Testing the Fix

I recommend testing these queries after the fix:

1. "What was Q2 2026 revenue?" → Should return ~$3.6M
2. "Show me Q2 2026 revenue by month" → Should use revenue_recognized with breakdown
3. "How many orders did we have in Q2?" → Should use orders table (this is correct)
4. "What was Q1 revenue?" → Should return $4,142,000 (from revenue_recognized)

---

## Impact Assessment

### Who Else Might Have Wrong Numbers?

This bot has been in use since March 2026 (6 months). Anyone who asked about revenue likely got inflated numbers.

**Action item:** Review the Slack export history for revenue queries:
1. Search #ask-finance for "revenue", "sales", "income"
2. Check which responses went into decks/reports
3. Flag any that need corrections

The board deck is the immediate priority, but there may be other artifacts (investor updates, exec reviews, planning documents) with incorrect data.

---

## Lessons Learned

1. **Domain knowledge must be explicit** - Don't assume the model knows accounting rules
2. **System prompts are critical** - They're documentation for the AI, not just configuration
3. **Validate outputs** - First few weeks should have spot-checking against source systems
4. **Table naming matters** - `orders` vs `revenue_recognized` should be clear from context

---

## Next Steps

**Immediate (before board meeting):**
1. ✅ Correct the board deck to $3.6M
2. ✅ Update finbot's system prompt with table guidance
3. ✅ Test the fix with the Q2 revenue question

**This week:**
1. Audit other Slack threads for revenue queries
2. Add schema documentation to the prompt
3. Create a finbot testing suite with known-good queries
4. Set up monthly validation: compare finbot answers to finance reports

**Longer term:**
1. Consider adding query validation to prevent this class of error
2. Document which tables are "source of truth" for different metrics
3. Add logging to track which queries are being run

---

## Conclusion

**This is not a model problem.** The bot worked exactly as designed - it just wasn't designed with enough domain knowledge about which tables to use for official reporting.

**No need to upgrade to Opus or GPT-6.** The fix is a better prompt, not a smarter model.

The good news: This is a quick fix (update `prompt.md`), and we caught it before the board meeting. The bad news: The $4.1M number is in the pre-read and may have been used elsewhere.

**Recommended immediate action:** Update the prompt today, test it, and audit where else the $4.1M number might have been shared.
