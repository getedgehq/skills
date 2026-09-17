# Executive Summary for Daniel

**To:** Daniel Kurz (CEO)  
**From:** Technical Analysis Team  
**Date:** September 16, 2026  
**Re:** FinBot Q2 Revenue Discrepancy ($4.1M vs $3.6M)

---

## Bottom Line Up Front

✅ **The model is NOT hallucinating or broken**  
❌ **You do NOT need a more expensive model**  
✅ **Simple fix: Update the prompt (5 minutes)**

---

## What Happened

1. Priya asked finbot for Q2 revenue
2. FinBot queried the database and got back $4.1M
3. That number was **real data from the database**
4. But it was from the **wrong table** (gross bookings instead of net revenue)
5. Finance's correct number is $3.6M (from the revenue_recognized table)

**The $500K difference** = refunded + cancelled orders that shouldn't count as revenue

---

## Root Cause

The bot's instructions (`prompt.md`) didn't tell it which table to use for revenue questions.

**Current prompt says:**
> "Tables you can use: customers, orders, refunds, revenue_recognized, daily_kpis"

The model reasonably (but wrongly) chose the `orders` table. Any AI model would make this same choice without better guidance.

---

## The Fix

Update the prompt to explicitly say:
- **For revenue questions → use `revenue_recognized` table**
- **For bookings questions → use `orders` table**

I've created the updated prompt in `output/prompt_UPDATED.md` - Jonas can deploy it in 5 minutes.

---

## Model Performance

**Claude Sonnet 4.5 is fine.** The model:
- ✅ Wrote correct SQL
- ✅ Used tools properly  
- ✅ Formatted output well
- ✅ Didn't hallucinate any numbers

It just followed ambiguous instructions. GPT-6 or Opus would do the same thing without clearer direction.

---

## Correct Q2 Number

**Q2 2026 Revenue: $3,638,336** (rounds to $3.6M)

This is from the `revenue_recognized` table, which is what Finance uses for board reporting (GAAP-compliant, net of refunds).

---

## Recommended Actions

1. **Immediate** (today): Deploy updated prompt (`output/prompt_UPDATED.md`)
2. **This week**: Add validation checks to compare finbot answers against known Finance numbers
3. **Going forward**: Add disclaimer in Slack: "Verify with Finance for board materials"

---

## Full Details

See the complete analysis in:
- `output/root_cause_analysis.md` - Full explanation with all the numbers
- `output/technical_analysis.md` - Database queries and technical details
- `output/prompt_UPDATED.md` - Ready-to-deploy fixed prompt

---

**Status:** Not a model issue, not a hallucination issue. Just needed clearer instructions. Easy fix.
