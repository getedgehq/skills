# For Lena: Support Bot v4 "Warmth" - Go/No-Go

**Bottom line: NO-GO for Friday, but easy fix for next week**

---

## The Good News 🎉

Your instinct was RIGHT - the warmth improvements are excellent:
- Team rated it 4.6/5 vs 2.8/5 for old prompt
- The empathy feels genuine and natural
- Customers feel heard and valued
- Examples like T-1002, T-1009, T-1024 are genuinely delightful

## The Problem 🚨

**2 critical policy violations** that would cost $4-10K+ in lost revenue:

1. **T-1013**: Custom wardrobe (CUST-4402) - offered full refund for change-of-mind ❌
2. **T-1026**: Custom bookshelf (CUST-4471) - offered full refund for change-of-mind ❌

These are made-to-measure items that can't be resold. The prompt's "do whatever it takes" instruction overrides the non-refundable policy.

**Plus 4 medium issues:** Items outside 30-day window got refunds instead of store credit.

## Why This Happened

This line in new_prompt.md:
> "Our #1 goal is customer delight. If a customer is unhappy, do whatever it takes to make it right - if they want a refund, make it happen quickly and without friction."

It tells the bot to override policies. The bot took it literally.

## The Fix (1-2 hours)

I've written a fixed version that keeps ALL the warmth but adds policy guardrails:
- See `output/suggested_prompt_v4_fixed.md`
- It explicitly lists custom item rules
- Keeps the empathy and first-name usage
- Just adds "work within our policies to make things right"

## What You Need to Do

1. Review `output/suggested_prompt_v4_fixed.md`
2. Re-run your ticket replay with the fixed prompt
3. Run `python output/test_suite.py outputs_fixed.jsonl` to verify
4. Ship next week when violations = 0

## Bonus: For Future Iterations

I built `test_suite.py` - an automated checker you can run on every prompt change:
```bash
python output/test_suite.py your_outputs.jsonl
```

It catches policy violations before manual review. Should save you 30 mins on each iteration.

## Files I Created

All in `output/`:
- **README.md** - Start here
- **QUICK_SUMMARY.md** - 2-min read
- **sanity_check_report.md** - Full details with examples
- **side_by_side_comparisons.md** - Before/after for key tickets
- **suggested_prompt_v4_fixed.md** - Ready-to-test fixed prompt
- **test_suite.py** - Reusable automated policy checker
- **policy_violations.json** - Machine-readable data

## Re: Your Question

> "do we even need the old policy block?"

**Yes, you do need it** - but the new prompt can keep the warm tone while including it. The fixed version shows how: it's explicit about policies but still sounds like Oakley, not a lawyer.

---

**My recommendation: Don't ship Friday. Fix the prompt, re-test next week, then ship with confidence.**

The direction is 100% right. This is fixable in an afternoon.

Let me know if you want to discuss any of the examples or the fix!
