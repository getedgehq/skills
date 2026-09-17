# FinBot Revenue Discrepancy - Root Cause Analysis
**Date:** September 16, 2026  
**Prepared for:** Daniel Kurz (CEO), Marta Oyelaran (VP Finance), Jonas Feld (Data)

---

## Executive Summary

**The model is NOT hallucinating.** FinBot correctly queried the database and reported the number it found. The issue is that **FinBot queried the wrong table** (`orders` instead of `revenue_recognized`), resulting in reporting gross bookings ($4.1M) instead of GAAP revenue ($3.6M).

**You do NOT need a smarter/more expensive model.** You need to fix the system prompt to direct the bot to the correct table for revenue queries.

---

## The Numbers

| Source | Q2 2026 Amount | What It Represents |
|--------|----------------|-------------------|
| **FinBot's answer** | **$4,138,212** | Gross bookings (all orders regardless of status) |
| **Finance close** | **$3,638,336** | GAAP revenue (net of refunds & cancellations) |
| **Difference** | **$499,876** | Refunded + cancelled + partial refund amounts |

---

## What Happened

### 1. Priya asked finbot for Q2 revenue (Sept 11)
```
@finbot what was our Q2 2026 revenue? need it for the board deck by EOD
```

### 2. FinBot queried the `orders` table
```sql
SELECT ROUND(SUM(amount), 2) AS revenue 
FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';
```
**Result:** $4,138,212.16

This includes:
- ✅ Completed orders: $3,269,511
- ❌ Refunded orders: $189,943
- ❌ Cancelled orders: $360,039
- ❌ Partially refunded orders: $318,719

### 3. FinBot correctly reported what it found
```
Q2 2026 revenue was **$4,138,212.16** (~$4.1M).
```

### 4. Priya put it in the board deck

### 5. Finance caught the error
- Finance's official Q2 close: **$3.6M**
- This comes from the `revenue_recognized` table
- Accounts for refunds and cancellations (net revenue)

---

## The Root Cause

The problem is in **`prompt.md`** (the system prompt):

```markdown
Tables you can use:
- customers
- orders
- refunds
- revenue_recognized
- daily_kpis

If a question is about money, always give a single headline number with a dollar sign.
```

**The prompt doesn't specify which table to use for revenue questions.** The model made a reasonable but incorrect assumption that "revenue" meant summing order amounts.

---

## Why This Isn't a Model Problem

✅ The model correctly:
- Used the `run_sql` tool
- Wrote valid SQL
- Interpreted the user's question
- Formatted the output clearly
- Did NOT make up numbers or hallucinate

❌ The model was never told:
- That `revenue_recognized` is the source of truth for revenue
- That `orders` includes cancelled/refunded transactions
- The difference between bookings vs. recognized revenue

**A more expensive model (GPT-6, Opus, etc.) would make the same mistake** without better guidance in the prompt.

---

## The Fix

### Immediate Fix (5 minutes)
Update `prompt.md` to specify the correct table for revenue:

```markdown
Tables you can use:
- customers
- orders
- refunds
- revenue_recognized ← SOURCE OF TRUTH for revenue metrics
- daily_kpis

**IMPORTANT**: 
- For revenue questions, ALWAYS use the `revenue_recognized` table
- Use `net_amount` (not `gross_amount`) for revenue calculations
- The `orders` table contains gross bookings and includes cancelled/refunded orders
- Use the `recognized_on` date field for date-based revenue queries

If a question is about money, always give a single headline number with a dollar sign.
```

### Recommended SQL for Q2 Revenue
```sql
SELECT ROUND(SUM(net_amount), 2) AS revenue 
FROM revenue_recognized 
WHERE recognized_on BETWEEN '2026-04-01' AND '2026-06-30';
```
**Result:** $3,638,335.79 ✅ (matches Finance's $3.6M)

---

## Additional Findings

The warehouse has **three different revenue numbers** for Q2:

1. **Orders table (gross bookings):** $4.1M
   - All orders including cancelled/refunded
   - Good for: Pipeline/bookings analysis
   - Bad for: Financial reporting

2. **Revenue_recognized (GAAP revenue):** $3.6M ✅
   - Net revenue after refunds
   - What Finance uses
   - **This is the correct number for board reporting**

3. **Daily_KPIs table:** $2.3M
   - Purpose unclear from schema
   - Doesn't match either bookings or recognized revenue
   - Needs documentation or investigation

---

## Recommended Actions

### For Jonas (Data Team) - Critical
1. ✅ Update `prompt.md` with clear guidance on which tables to use for revenue
2. ✅ Add SQL examples in the prompt for common queries
3. ⚠️ Document what `daily_kpis.revenue` represents (it's $1M+ different from other metrics)
4. ⚠️ Consider renaming `orders.amount` to `orders.gross_amount` to avoid confusion

### For the Team - Process
1. ✅ Test the updated prompt with historical questions
2. ✅ Create a validation script that compares finbot answers to known finance numbers
3. ✅ Add a warning in Slack: "FinBot is for quick estimates. Verify with Finance for board materials."

### What NOT to Do
- ❌ Don't upgrade to a more expensive model - won't solve the problem
- ❌ Don't blame the model - it did exactly what it was told
- ❌ Don't immediately shut down finbot - it's fixable

---

## Correct Q2 2026 Revenue

**$3,638,335.79** (rounds to **$3.6M**)

Source: `revenue_recognized` table, net_amount, April-June 2026

---

## Questions?

Contact: [Your analysis team]  
Data sources: `warehouse.db`, Slack transcripts from #ask-finance and #exec-staff
