# TL;DR for Daniel

## The Problem
FinBot said Q2 revenue = $4.1M  
Finance says Q2 revenue = $3.6M  
Difference = $500K (13.7% error)

## Root Cause
❌ **Bot queried the wrong table**
- Used: `orders` table (includes cancelled orders, ignores refunds)
- Should use: `revenue_recognized` table (proper GAAP accounting)

✅ **Bot is NOT hallucinating** - the $4.1M number is real, just wrong table

## Do You Need a Smarter Model?
**NO.** 

The current model (Sonnet 4.5) wrote perfect SQL. It just doesn't know which table contains "revenue" because the system prompt doesn't tell it.

This is like asking someone to "get the report" without telling them which folder it's in. They'll guess, and might grab the wrong one.

## The Fix
Update `prompt.md` to explicitly say:
> "For revenue questions, always use revenue_recognized.net_amount"

**Cost:** $0  
**Time:** 5 minutes  
**Code changes:** 0 lines  

## What to Tell the Board
**Q2 2026 Revenue: $3.6M** ($3,638,335.79 exact)

Breakdown:
- April: $1.24M
- May: $1.21M  
- June: $1.19M

## Files in output/
- `investigation_report.md` - Full technical analysis
- `fixed_prompt.md` - Drop-in replacement for prompt.md
- `test_queries.py` - Script to verify the fix works
- `TLDR.md` - This file

---

**Bottom line:** Prompt fix, not model upgrade. Deploy today.
