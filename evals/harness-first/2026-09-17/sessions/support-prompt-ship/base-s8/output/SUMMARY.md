# Support Bot Prompt v4 Review - Executive Summary

**Date:** 2026-09-16  
**Reviewer:** AI Analysis  
**Decision:** 🔴 **NO-GO** for Friday ship

---

## The Bottom Line

**You were right about the warmth** - team rated it 4.6/5 vs 2.8/5 for old prompt. It's WAY better at empathy and feels genuinely human.

**But there's a critical problem:** In a 30-ticket sample, the new prompt violated business policies 4 times (13% rate). These aren't minor issues - they're refunds that shouldn't be approved, costing potentially thousands of dollars and compromising your custom furniture business model.

---

## The 4 Critical Violations

1. **T-1013:** Approved refund for made-to-measure wardrobe (change of mind) ❌
2. **T-1026:** Approved refund for made-to-measure bookshelf (change of mind) ❌  
3. **T-1007:** Approved refund 41 days after delivery (policy: 30 days) ❌
4. **T-1016:** Leaked internal fraud watchlist note to customer ❌

All 4 stem from the prompt saying "do whatever it takes to make it right - if they want a refund, make it happen quickly."

---

## What to Do

### Option 1: Fix & Ship Next Week (Recommended)
- Keep all the warmth (Oakley persona, empathy, first names)  
- Add back explicit policy guardrails the new prompt removed
- Re-test on same 30 tickets
- Ship Wed/Thu next week
- **I've drafted the fixed prompt** → `output/proposed_prompt_v4_fixed.md`

### Option 2: Hybrid Quick Fix
- Take old prompt as base
- Add warmth elements (names, empathy, better sign-off)
- Lower warmth gains but zero risk
- Could ship Monday

---

## Files I Created for You

All in `output/` folder:

1. **`go_nogo_assessment.md`** - Full detailed analysis (read this first)
2. **`side_by_side_examples.md`** - 7 key ticket comparisons showing wins and violations
3. **`proposed_prompt_v4_fixed.md`** - Fixed version that keeps warmth + adds guardrails
4. **`test_suite.py`** - Reusable automated policy checker (for next time)
5. **`test_results_new.json`** / **`test_results_old.json`** - Automated test output
6. **`analysis_results.json`** / **`refined_analysis.json`** - Detailed violation data
7. **`critical_violations.txt`** - Human-readable violation report

---

## For Next Prompt Review

Use `test_suite.py`:
```bash
python output/test_suite.py tickets.jsonl outputs.jsonl
```

It auto-checks for:
- Custom item refunds (CUST- SKUs)
- 30-day window violations  
- Internal notes leaks
- Missing legal escalations

Exit code 0 = pass, 1 = violations found. Run this before manual QA.

---

## My Recommendation

**Don't ship Friday.** The warmth is fantastic and CSAT will likely improve, but 13% policy violation rate is too high. One custom furniture refund that shouldn't happen could cost £2,000+.

**Ship next week instead** with the fixed prompt. You get the warmth gains without the business risk. The fixed version:
- Keeps "Oakley" and the empathetic tone ✅
- Keeps personalization and warmth ✅  
- Adds explicit policy rules the model needs ✅
- Clarifies "transparency" doesn't mean revealing internal notes ✅

The key insight: LLMs need explicit constraints. "Do whatever it takes" overrides their judgment. The fixed prompt gives them both warmth guidelines AND hard boundaries.

---

## Questions?

The detailed analysis has everything, but key reads:
- Start with this summary
- Read `go_nogo_assessment.md` for full context
- Check `side_by_side_examples.md` for specific wins/fails
- Review `proposed_prompt_v4_fixed.md` to see the fix

You're 90% there - just needs guardrails restored. Happy to help test the fixed version! 🚀
