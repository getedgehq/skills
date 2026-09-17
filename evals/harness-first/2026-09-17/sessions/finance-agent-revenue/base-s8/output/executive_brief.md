# Executive Brief: FinBot Revenue Discrepancy
**For: Daniel Kurz (CEO)**  
**From: Data Engineering**  
**Date: September 16, 2026**  
**Re: Q2 Revenue Discrepancy ($4.1M vs $3.6M)**

---

## What Happened

On September 11, Priya asked FinBot for Q2 revenue for the board deck.  
FinBot responded: **$4.1M**  
Finance says the Q2 close is: **$3.6M**  
The board pre-read went out with the wrong number.

## Root Cause

**FinBot queried the wrong database table.**

| What FinBot Did | What It Should Have Done |
|----------------|--------------------------|
| ❌ Queried: `orders` table | ✅ Should query: `revenue_recognized` table |
| ❌ Result: $4,138,212 | ✅ Correct result: $3,638,336 |
| ❌ Includes cancelled orders | ✅ Excludes cancellations |
| ❌ Ignores refunds | ✅ Nets out refunds |
| ❌ Wrong by $500K (13.7%) | ✅ Matches Finance close |

**The bot is not hallucinating.** The $4.1M number exists in the database—it's just from the wrong table.

## Why Did This Happen?

The system prompt tells the bot which tables exist but **doesn't explain what they mean**:

**Current prompt (vague):**
> Tables you can use: customers, orders, refunds, revenue_recognized, daily_kpis

That's like telling someone "the files are in folders A, B, C, D, E" without saying which folder has what they need.

The model made an educated guess and picked `orders` (reasonable but wrong).

## Do We Need a Smarter Model?

**No.**

This isn't a model intelligence problem—it's a **specification problem**.

| Scenario | Will Upgrading Help? |
|----------|---------------------|
| Model wrote invalid SQL | ✅ Yes |
| Model hallucinated numbers | ✅ Yes |
| Model ignored instructions | ✅ Yes |
| **Model followed vague instructions perfectly** | **❌ No** |

The current model (Claude Sonnet 4.5) is performing correctly. It just needs better instructions.

**Analogy:** You wouldn't buy a faster car when what you actually need is a map.

## The Fix

**Update the system prompt to explicitly state:**
> "For revenue questions, always use revenue_recognized.net_amount"

**Changes required:**
- Lines of code: 0
- Cost increase: $0
- Deploy time: 5 minutes

I've prepared the updated prompt in `output/fixed_prompt.md`—it's a drop-in replacement.

## Correct Board Numbers

**Q2 2026 Revenue: $3,638,335.79**

Rounded: **$3.6M**

Monthly breakdown:
- April: $1,237,517
- May: $1,209,658
- June: $1,191,161

This matches Finance's close and is ready for the board.

## What's in output/

1. **TLDR.md** - One-page summary (this file)
2. **investigation_report.md** - Full technical analysis with data tables
3. **fixed_prompt.md** - Updated system prompt (ready to deploy)
4. **test_queries.py** - Verification script to test the fix
5. **executive_brief.md** - This document

## Recommended Actions

### Today (Before Board Meeting)
1. ✅ Correct the board pre-read: Q2 Revenue = $3.6M
2. ✅ Deploy fixed prompt: `cp output/fixed_prompt.md prompt.md`
3. ✅ Verify: `python agent.py "what was Q2 2026 revenue?"` should return ~$3.6M

### This Week
- Review any other board deck numbers that came from FinBot
- Add test suite for critical finance queries
- Document revenue_recognized as the source of truth

### Next Sprint
- Add query validation to catch this type of error automatically
- Consider adding schema documentation to the warehouse

## Bottom Line

✅ **Not a hallucination** - real number from wrong table  
✅ **Not a model problem** - current model is fine  
✅ **Is a prompt problem** - fix takes 5 minutes  
✅ **Correct answer is $3.6M** - ready for board  

**Don't spend money on a better model. Spend 5 minutes fixing the prompt.**

---

## Questions?

See `investigation_report.md` for complete technical details including:
- Full SQL queries showing the discrepancy
- Month-by-month revenue breakdown
- Order status analysis
- Comparison of all warehouse tables
- Long-term architectural recommendations
