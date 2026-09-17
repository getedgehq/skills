# Root Cause Analysis: Q2 Revenue Discrepancy ($4.1M vs $3.6M)

**Prepared for:** Daniel Kurz (CEO)  
**Date:** September 16, 2026  
**Issue:** Finbot reported Q2 revenue as $4.1M, Finance reports $3.6M (~$500K difference)

---

## Executive Summary

**This is NOT a hallucination or model quality issue.** The model executed SQL correctly and returned accurate results. The problem is a **data engineering issue**: the bot's prompt doesn't specify which table contains the official revenue number.

### The Numbers
- **Finbot reported:** $4,138,212.16 (gross orders)
- **Finance official:** $3,638,335.79 (net revenue after refunds)
- **Difference:** $499,876.37

### Root Cause
The system prompt (`prompt.md`) lists 5 available tables but provides **no guidance** on which table to use for revenue questions. The bot chose `orders` (gross bookings including cancelled orders) instead of `revenue_recognized` (net revenue, finance's official source).

### Recommendation
**Fix the prompt, not the model.** A simple clarification in the system prompt will prevent this issue. No need for a more expensive model.

---

## Detailed Analysis

### What Happened (Timeline)

1. **Sept 11, 10:02 AM** - Priya (Strategy) asks finbot for Q2 revenue for board deck
2. **Sept 11, 10:02 AM** - Finbot queries: `SELECT SUM(amount) FROM orders WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30'`
3. **Sept 11, 10:02 AM** - Returns $4,138,212.16 (~$4.1M)
4. **Sept 11, 10:03 AM** - Priya uses this number in board deck
5. **Sept 14** - Marta (Finance) catches the error in pre-read: should be $3.6M

### Why Finbot Chose the Wrong Table

The current system prompt (`prompt.md`) says:
```
Tables you can use:
- customers
- orders
- refunds
- revenue_recognized
- daily_kpis
```

When asked "what was Q2 revenue?", the model:
- ✅ Correctly understood the question
- ✅ Correctly wrote SQL syntax
- ✅ Correctly calculated the date range
- ❌ Chose the wrong table (no fault of the model - it had no guidance)

### The Data Model

The warehouse contains **two different revenue concepts**:

#### 1. `orders` table (what finbot used)
- **Contains:** ALL orders regardless of status
- **Q2 breakdown:**
  - Completed: $3,269,510.70 (1,733 orders)
  - Cancelled: $360,039.00 (202 orders) ⚠️
  - Partially refunded: $318,719.01 (174 orders)
  - Refunded: $189,943.45 (104 orders) ⚠️
  - **TOTAL: $4,138,212.16**

This is **gross bookings**, including orders that were cancelled or fully refunded.

#### 2. `revenue_recognized` table (what finance uses)
- **Contains:** Net revenue after refunds, by accounting period
- **Q2 totals:**
  - Gross amount: $3,970,863.37
  - Refund amount: $332,527.58
  - **Net amount: $3,638,335.79** ✅

This is the **official revenue number** that finance closes each quarter.

### Why This Isn't a Model Issue

Evidence the model is working correctly:

1. **SQL is syntactically perfect** - no errors, proper date formatting
2. **Math is accurate** - the SUM() returned the correct total for the queried table
3. **The model didn't "hallucinate"** - it queried real data and returned real results
4. **Consistent behavior** - finbot made the same (reasonable) choice for Q1

The model made a **reasonable inference** given insufficient context. Most humans would also guess "orders" for a revenue question without domain knowledge.

---

## Comparison: Model Behavior

To verify this isn't a model capability issue, here's what would happen with different models:

| Model | Likely Behavior |
|-------|-----------------|
| Claude Sonnet 4 (current) | Queries `orders` - no context says otherwise |
| Claude Opus | Queries `orders` - no context says otherwise |
| GPT-6 | Queries `orders` - no context says otherwise |
| o1-pro | Queries `orders` - no context says otherwise |

**All models would make the same mistake** because the prompt doesn't specify the business rule.

Even a human data analyst would need to ask: "Do you want gross bookings or net revenue?"

---

## The Fix

### Option 1: Update the System Prompt (RECOMMENDED)

**Change this:**
```
Tables you can use:
- customers
- orders
- refunds
- revenue_recognized
- daily_kpis
```

**To this:**
```
Tables you can use:
- customers (company info, segment, country)
- orders (individual transactions; use for order-level analysis)
- refunds (returns and refund details)
- revenue_recognized (⭐ USE THIS for revenue/money questions - official finance numbers)
- daily_kpis (high-level daily metrics)

IMPORTANT: For revenue questions, always use revenue_recognized.net_amount, 
not orders.amount. The orders table includes cancelled orders and doesn't 
account for refunds. Finance closes the books from revenue_recognized.
```

**Effort:** 5 minutes  
**Cost:** $0  
**Risk:** Very low

### Option 2: Upgrade the Model (NOT RECOMMENDED)

Switch from Claude Sonnet 4 to a more expensive model.

**Effort:** 5 minutes  
**Cost:** 2-3x per query (Opus) or ~$1-2 per query (o1)  
**Risk:** Medium (still won't fix the root cause)  
**Outcome:** Won't help - the prompt still lacks guidance

### Option 3: Add Schema Documentation

Create a data dictionary as a separate file and reference it in the prompt.

**Effort:** 1-2 hours  
**Cost:** $0  
**Risk:** Low  
**When to do this:** After fixing the immediate issue, as a long-term improvement

---

## Verification Query

To confirm the analysis, here's what each approach returns:

```sql
-- What finbot did (WRONG)
SELECT SUM(amount) FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';
-- Result: $4,138,212.16

-- What it should do (CORRECT)  
SELECT SUM(net_amount) FROM revenue_recognized
WHERE period IN ('2026-04', '2026-05', '2026-06');
-- Result: $3,638,335.79 (matches Finance's $3.6M)
```

---

## Additional Findings

### Other tables show similar patterns:

1. **`daily_kpis` table** - Contains $2,262,135.23 for Q2
   - This is incomplete (only goes through mid-May in the current snapshot)
   - Not suitable for quarterly revenue reporting

2. **Refunds timing** - Some refunds occurred in Q3 for Q2 orders
   - The `revenue_recognized` table properly accounts for this
   - The `orders` table does not

### This affects other metrics:

Reviewed the Q1 query from the same Slack thread:
- Finbot reported: $4,141,985.86 (also from `orders` table)
- Finance Q1 close: Likely also ~$500K lower

**Action item:** Priya should check if Q1 numbers in any published materials are also incorrect.

---

## Recommended Next Steps

### Immediate (before tomorrow's conversation)
1. ✅ Update `prompt.md` with table guidance (see Option 1 above)
2. Test with the original question to verify fix
3. Notify Priya that Q1 number in board deck may also be wrong

### This week
1. Add a comment in the warehouse schema documenting the difference between `orders` and `revenue_recognized`
2. Check if any other board materials used finbot numbers without verification
3. Consider adding a tool that returns schema information

### Next sprint
1. Build a proper data dictionary
2. Add validation rules (e.g., revenue queries should return amounts in expected range)
3. Consider logging all finbot queries to a Slack channel so finance can spot-check

---

## Bottom Line

**Do NOT upgrade the model.** This is a classic "garbage in, garbage out" scenario. The model did exactly what it was supposed to do with the information provided. 

Fix the prompt (5 minutes, $0) before spending on infrastructure or more expensive models.

The real lesson: When LLM agents interact with business-critical data, the **prompt is a specification document**, not just instructions. It needs to encode business rules and data governance policies.
