# FinBot Q2 Revenue Discrepancy - Root Cause Analysis
**Date:** September 15, 2026  
**Prepared for:** Daniel Kurz (CEO)  
**Issue:** FinBot reported Q2 revenue as $4.1M; Finance reported $3.6M

---

## Executive Summary

**The model is NOT hallucinating.** FinBot correctly queried the database and returned accurate data. However, it used the **wrong table** due to an ambiguous prompt and incomplete system instructions.

- **FinBot reported:** $4,138,212 from the `orders` table (gross bookings, including cancelled orders)
- **Finance reported:** $3,600,000 from the `revenue_recognized` table (net revenue, rounded to nearest $100k)
- **Actual net revenue:** $3,638,336 (matches Finance when rounded)

**Root cause:** Configuration/prompt issue, NOT a model capability problem. **No need for a more expensive model.**

---

## What Happened

### Timeline
1. **Sept 11, 10:02 AM** - Priya (Strategy) asked finbot: "what was our Q2 2026 revenue?"
2. FinBot ran: `SELECT SUM(amount) FROM orders WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30'`
3. FinBot reported: **$4.1M**
4. Priya used this number in the board deck
5. **Sept 14** - Marta (Finance) flagged the discrepancy (Finance closed Q2 at $3.6M)

### What FinBot Did

```sql
SELECT ROUND(SUM(amount), 2) AS revenue 
FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';
```

**Result:** $4,138,212.16

This query:
- ✅ Correct date range
- ✅ Correct SQL syntax  
- ✅ Correct arithmetic
- ❌ Wrong table (orders vs revenue_recognized)
- ❌ Included cancelled orders ($360k)
- ❌ Used gross amounts instead of net (ignored $333k in refunds)

---

## The Numbers Breakdown

| Source | Amount | What It Represents |
|--------|--------|-------------------|
| **FinBot (orders table)** | $4,138,212 | All orders created in Q2, including cancelled |
| Orders (excl. cancelled) | $3,778,173 | Non-cancelled orders only |
| **revenue_recognized (net)** | $3,638,336 | GAAP revenue after refunds |
| **Finance reported** | $3,600,000 | revenue_recognized, rounded to nearest $100k |

### Orders Table Breakdown (Q2 2026)
- Completed: $3,269,511 (1,733 orders)
- Cancelled: $360,039 (202 orders) ← **Should not be counted as revenue**
- Partially refunded: $318,719 (174 orders)
- Refunded: $189,943 (104 orders)
- **Total: $4,138,212**

### Revenue Recognition (Accrual Accounting)
The `revenue_recognized` table is the source of truth for Finance because it:
1. Excludes cancelled orders
2. Accounts for refunds (net revenue = gross - refunds)
3. Recognizes revenue based on when it's earned, not when orders are created
4. Matches GAAP accounting principles

**Q2 Revenue (revenue_recognized):**
- Gross: $3,970,863
- Refunds: $332,528
- **Net: $3,638,336** ← This is what Finance reports

---

## Why This Happened

### 1. The Prompt Is Ambiguous
Current system prompt (`prompt.md`):
```
Tables you can use:
- customers
- orders
- refunds
- revenue_recognized
- daily_kpis

If a question is about money, always give a single headline number with a dollar sign.
```

**Problem:** No guidance on WHICH table to use for revenue questions. The model made a reasonable but incorrect choice.

### 2. "Revenue" Is Ambiguous
In business, "revenue" can mean:
- **Bookings** (orders placed) ← what FinBot reported
- **Revenue recognized** (GAAP) ← what Finance means
- **Cash collected** (cash accounting)
- **Net revenue** (after refunds)
- **Gross revenue** (before refunds)

The model couldn't know which definition to use.

### 3. Orders Table Is Not Filtered
The `orders` table includes:
- Cancelled orders (should not count as revenue)
- Orders at gross amount (before refunds applied)

---

## Is This a Model Problem?

**No.** The model:
- ✅ Correctly understood the question
- ✅ Wrote valid SQL
- ✅ Selected a reasonable table given the ambiguous prompt
- ✅ Returned accurate results from that table
- ✅ Formatted the answer clearly

This is a **data/configuration problem**, not an AI capability problem.

### Why a "Smarter Model" Won't Help
- GPT-6 or Claude Opus would face the same ambiguity
- They would also have to guess which table to use
- They might even make a different (still wrong) choice
- **More expensive ≠ more accurate when the instructions are unclear**

---

## Recommended Fixes

### Option 1: Update the System Prompt (Quick Fix)
Add clear guidance to `prompt.md`:

```markdown
## Revenue Questions - IMPORTANT

When someone asks about "revenue", "sales", or "quarterly revenue":
- ALWAYS use the `revenue_recognized` table
- Use the `net_amount` column (accounts for refunds)
- Filter by the `period` column for quarters/months
- Example: Q2 2026 = periods '2026-04', '2026-05', '2026-06'

The `orders` table shows bookings, not revenue. Finance reports from revenue_recognized.
```

### Option 2: Add Table Descriptions
Modify the prompt to explain what each table is for:

```markdown
Tables:
- `customers` - customer master data
- `orders` - order bookings (gross, includes cancelled)
- `refunds` - refund transactions
- `revenue_recognized` - **USE THIS FOR REVENUE QUESTIONS** (GAAP accounting, net of refunds)
- `daily_kpis` - high-level daily metrics (may be incomplete)
```

### Option 3: Add a Validation Layer (Engineering)
Before returning revenue answers, have the bot double-check:
```python
if "revenue" in question.lower():
    # Run query on both tables and flag if they differ significantly
    # Prompt user to clarify: "bookings" vs "recognized revenue"
```

### Option 4: Restrict Tool Access (Safest)
Only allow FinBot to query `revenue_recognized` and `daily_kpis` for revenue questions. Update the tool to reject orders table queries for "revenue" questions.

---

## Immediate Action Items

1. **Correct the board deck** - Update to $3.6M (from revenue_recognized)
2. **Update prompt.md** - Add revenue table guidance (Option 1 above)
3. **Add a note to #ask-finance** - Explain the issue and new guidance
4. **Test the fix** - Re-run Priya's question: "what was our Q2 2026 revenue?"
5. **Document "revenue" definitions** - Create a data dictionary for common terms

---

## Testing the Fix

After updating the prompt, FinBot should run:

```sql
SELECT SUM(net_amount) 
FROM revenue_recognized 
WHERE period IN ('2026-04', '2026-05', '2026-06');
```

**Expected result:** $3,638,336 (~$3.6M)

This matches Finance's number.

---

## Other Observations

### The daily_kpis Table Is Incomplete
- Only has data through May 19, 2026 (Q2 ends June 30)
- Shows $2.26M for partial Q2
- **Should not be used for quarterly revenue**
- Recommend: Fix ETL or remove from bot's available tables

### Revenue Recognition Timing
- 352 orders (17%) were recognized in a different month than created
- This is normal for accrual accounting (e.g., orders created March 24, recognized April 1)
- Another reason the `orders` table (by created_at) gives wrong results

---

## Conclusion

**TL;DR:**
- ✅ Model is working correctly
- ❌ Prompt was ambiguous about which table to use
- ✅ Fix: Update prompt to specify revenue_recognized for revenue questions
- ❌ Don't upgrade model - won't solve the root cause
- ✅ Estimated fix time: 15 minutes + testing

The $500k discrepancy is explained by:
- $360k in cancelled orders (shouldn't count)
- $333k in refunds (net vs gross)
- Small timing differences (order date vs recognition date)

**Total cost to fix:** Engineer time to update prompt + re-test  
**Cost of upgrading to GPT-6/Opus:** $$$$ per month, won't solve the problem
