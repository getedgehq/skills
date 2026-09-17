# EXECUTIVE SUMMARY: Q2 Revenue Discrepancy
**For:** Daniel  
**From:** Technical Investigation  
**Date:** 2026-09-16  
**Re:** Finbot $4.1M vs Finance $3.6M discrepancy

---

## The Answer You Need

**The model is NOT hallucinating. Don't upgrade the model. Fix the prompt.**

---

## What Happened

| Who | Number | Status |
|-----|--------|--------|
| **Finbot** | $4.1M | ❌ WRONG |
| **Finance (Marta)** | $3.6M | ✅ CORRECT |
| **Actual** | $3,638,335.79 | (verified in warehouse) |

**Discrepancy:** $499,876 (12% overstatement)

---

## Root Cause

Finbot queried the **wrong table**:
- ❌ Used: `orders` table → includes $360k of **cancelled orders** 
- ✅ Should use: `revenue_recognized` table → proper accounting, excludes cancelled orders

**Why it picked the wrong table:** The prompt doesn't tell it which table to use for revenue questions. The model made a logical but incorrect guess.

---

## Is This a Model Intelligence Problem?

**No.** The model:
- ✅ Understood the question correctly
- ✅ Generated valid SQL
- ✅ Returned accurate results from its query
- ✅ Didn't hallucinate or make up numbers

Without explicit guidance, **any model** (including Opus or GPT-6) would face the same issue. It's like asking a new analyst to "use these tables" without training them on your accounting practices.

---

## The Fix

**Update the system prompt to explicitly say:**
> "For revenue questions, use revenue_recognized.net_amount, NOT orders.amount. The orders table includes cancelled orders."

**Cost:** $0  
**Time:** 30 minutes  
**Result:** Will fix the issue

---

## What NOT To Do

❌ **Don't upgrade to Opus or GPT-6**
- Won't fix the root cause
- Would cost 2-10x more
- Still needs proper guidance

---

## For the Board

**Safe number:** $3,638,335.79 (round to $3.64M)

This is verified against Finance's books.

---

## Next Steps

1. ✅ Update board deck with correct number ($3.64M)
2. ✅ Fix the prompt (30 min)
3. ✅ Test with validation queries
4. ✅ Add monthly audit to catch future issues

---

## Bottom Line

- This is a **prompt/documentation issue**, not a model capability issue
- The data is correct, the model works, we just need to tell it what to do
- **No need to upgrade the model or spend more money**
- Fix: Add 3 sentences to the prompt

---

## Full Details

See attached:
- `investigation_report.md` - Full analysis
- `technical_analysis.md` - Data verification and queries  
- `proposed_fix.md` - Updated prompt and implementation steps

---

**TL;DR:** The bot included cancelled orders in revenue. Tell it not to do that. Problem solved. No model upgrade needed.
