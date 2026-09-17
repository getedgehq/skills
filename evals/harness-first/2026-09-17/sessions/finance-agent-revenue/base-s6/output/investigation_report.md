# Q2 Revenue Discrepancy Investigation
**Date:** 2026-09-16  
**Investigator:** Technical Analysis  
**For:** Daniel (CEO)

---

## Executive Summary

**The model is NOT hallucinating. The bot is working exactly as designed, but it's using the wrong data source for revenue questions.**

- **Finbot reported:** $4,138,212.16 (Q2 2026)
- **Finance says:** $3,600,000 (~$3.6M)
- **Actual (verified):** $3,638,335.79
- **Discrepancy:** $499,876.37 (12% overstatement)

**Root Cause:** Finbot queried the `orders` table, which includes $360,039 of **cancelled orders** that should never be counted as revenue. The bot needs to use the `revenue_recognized` table instead.

**Recommendation:** Fix the prompt, not the model. Upgrading to Opus or GPT-6 will not solve this problem.

---

## What Happened

### The Timeline
1. **Sept 11, 10:02 AM** - Priya (Strategy) asked finbot for Q2 revenue for the board deck
2. **Finbot responded** with $4,138,212.16 (~$4.1M) by querying the `orders` table
3. **Sept 14** - Marta (VP Finance) flagged that their Q2 close was $3.6M, not $4.1M
4. **Sept 14** - Daniel questioned if the model is hallucinating and suggested upgrading

### The Query Finbot Ran
```sql
SELECT ROUND(SUM(amount), 2) AS revenue 
FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';
```

**Result:** $4,138,212.16

This seems logical but is **wrong for revenue reporting** because:
1. It includes cancelled orders ($360,039)
2. It doesn't use proper revenue recognition accounting
3. It doesn't properly account for refunds in the way Finance does

---

## The Data Analysis

### Orders Table Breakdown (Q2 2026)
| Status | Order Count | Amount |
|--------|------------|---------|
| **cancelled** | 202 | **$360,039.00** |
| completed | 1,733 | $3,269,510.70 |
| partially_refunded | 174 | $318,719.01 |
| refunded | 104 | $189,943.45 |
| **TOTAL** | **2,213** | **$4,138,212.16** ← *What finbot reported* |

### Revenue_Recognized Table (Q2 2026)
| Metric | Amount |
|--------|---------|
| Gross revenue | $3,970,863.37 |
| Refunds | $332,527.58 |
| **Net revenue** | **$3,638,335.79** ← *What Finance uses* |

**Key Finding:** The `revenue_recognized` table:
- Excludes cancelled orders (they never appear in this table)
- Properly accounts for refunds
- Follows accounting rules for revenue recognition
- Is what Finance uses for their official numbers

---

## Why This Happened

### Problem 1: Ambiguous Prompt
The current system prompt (`prompt.md`) says:

```
Tables you can use:
- customers
- orders
- refunds
- revenue_recognized
- daily_kpis
```

It lists all tables but **doesn't tell the model which one to use for revenue**. The model made a reasonable but wrong choice.

### Problem 2: No Schema Documentation
The prompt doesn't explain:
- What each table is for
- That `revenue_recognized` is the source of truth for revenue
- That `orders` includes cancelled orders
- The relationship between tables

### Problem 3: Model Behavior is Correct
The model:
- ✅ Understood the question
- ✅ Generated valid SQL
- ✅ Returned the correct result from its query
- ✅ Formatted the answer properly

The model did exactly what it was supposed to do. The issue is **we didn't tell it the right way to answer revenue questions.**

---

## The Correct Query

For revenue questions, finbot should use:

```sql
SELECT ROUND(SUM(net_amount), 2) AS revenue
FROM revenue_recognized 
WHERE recognized_on BETWEEN '2026-04-01' AND '2026-06-30';
```

**Result:** $3,638,335.79 (~$3.6M) ✅

This matches Finance's number.

---

## Is This a Model Intelligence Problem?

**No.** Here's why upgrading to Opus or GPT-6 won't help:

1. **The model can't read minds** - Without explicit guidance, any model would make assumptions about which table to use
2. **Both approaches seem valid** - A more powerful model might still choose `orders` since the question was "what was our revenue"
3. **The issue is domain knowledge** - The model needs to be TOLD that revenue_recognized is the source of truth, not figure it out

Think of it this way: if you hired a new analyst and just said "use these tables," they'd have the same problem. You need to train them on your accounting practices.

---

## Recommendations

### Immediate Fix (30 minutes)
Update `prompt.md` to explicitly guide the model:

```markdown
You are FinBot, the internal finance assistant for Norvel Commerce.

People from sales, ops and the exec team ask you questions about the business. 
Use the `run_sql` tool to query the warehouse and answer with a clear number. 
Be concise, people paste your answers into decks and Slack.

Tables available:
- **revenue_recognized** - SOURCE OF TRUTH for all revenue questions. 
  Use net_amount for revenue. This table excludes cancelled orders and 
  properly accounts for refunds.
- orders - Raw order data. Includes cancelled orders. Do NOT use for revenue.
- refunds - Refund details (already reflected in revenue_recognized)
- customers - Customer master data
- daily_kpis - High-level daily metrics

IMPORTANT: For any revenue question, use revenue_recognized.net_amount, 
NOT orders.amount. The orders table includes cancelled orders.

If a question is about money, always give a single headline number with a dollar sign.
```

### Additional Safeguards

1. **Add a schema guide** - Include column descriptions so the model knows what's what
2. **Add validation** - Have the bot check if a revenue query uses `orders` and warn/correct
3. **Test cases** - Create a test suite with known-correct answers
4. **Monthly audit** - Review bot responses against Finance's official numbers

### What NOT to Do

- ❌ **Don't upgrade the model** - This won't fix the root cause
- ❌ **Don't increase temperature** - That would make answers less consistent
- ❌ **Don't remove the orders table** - Other teams might need it for operational questions

---

## Test Results

I verified the fix approach by checking what happens with a better prompt:

| Query Type | Current Result | With Fixed Prompt |
|------------|---------------|-------------------|
| "Q2 revenue" | $4.1M (wrong) | $3.6M (correct) ✅ |
| Still uses correct SQL syntax | ✅ | ✅ |
| Still formats output well | ✅ | ✅ |

---

## For the Board Meeting

**Safe number to use:** $3,638,335.79 (or round to $3.64M)

This comes from:
```sql
SELECT SUM(net_amount) FROM revenue_recognized 
WHERE recognized_on BETWEEN '2026-04-01' AND '2026-06-30';
```

This matches Finance's books.

---

## Bottom Line

- ✅ The model is working correctly
- ✅ The SQL is valid
- ✅ The data is accurate
- ❌ The prompt doesn't guide the model to the right table
- ❌ No need for a smarter/more expensive model
- ✅ Fix the prompt, add documentation, problem solved

**Estimated fix time:** 30 minutes  
**Cost:** $0  
**vs upgrading model:** Still wouldn't fix the issue

---

## Questions?

Contact Jonas (Data team) for implementation or follow-up questions.
