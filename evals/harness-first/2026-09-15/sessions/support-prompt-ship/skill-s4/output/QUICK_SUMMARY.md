# TL;DR - Prompt Change Review

## Decision: 🛑 NO-GO

**DO NOT ship new prompt v4 on Friday.**

## The Numbers

- **Old prompt:** 7/7 policy tests PASS (100%)
- **New prompt:** 4/7 policy tests PASS, **3 FAIL** (57%)

## The 3 Violations

1. **T-1013:** Offered $800+ refund on non-refundable custom wardrobe
2. **T-1026:** Offered $600+ refund on non-refundable custom bookshelf  
3. **T-1016:** Told customer they're on "returns-abuse watchlist"

## Why It Happened

New prompt removed the policy rules and added:
- "Do whatever it takes to make it right"
- "Be transparent: share what you can see"

These override the business rules when the model needs to say "no."

## What To Do

**Option A (recommended):** Fix prompt + re-test (2-3 days)
- Add back explicit custom item rule
- Add "never share internal_notes" rule
- Keep the warmth
- Run judge.py to verify
- Ship Tuesday

**Option B:** Keep old prompt, iterate more carefully

## Files Created

All in `output/`:
- `GO_NO_GO_DECISION.md` - Full report
- `violation_examples.md` - Side-by-side comparisons
- `golden_set.jsonl` - 8 test cases
- `judge.py` - Automated policy checker (use before every prompt change)
- `judge_results_*.json` - Detailed test results

## Run Tests On Next Version

```bash
cd /home/user/work
python3 output/judge.py  # Exit code 1 = violations found
```

## Bottom Line

The warmth is great. The policy violations are blocking. Fix and test before shipping.
