# Support Bot v4 "Warmth" - Sanity Check Results

**Reviewed:** 2026-09-15  
**Deployment Target:** Friday 2026-09-19 9am  
**Recommendation:** ❌ **NO-GO** (fixable, see below)

---

## 📊 Quick Stats

| Metric | Result |
|--------|--------|
| Total tickets analyzed | 30 |
| ✅ Policy compliant | 24 (80%) |
| 🔴 Critical violations | **2** (custom item refunds) |
| 🟡 Medium issues | 4 (30-day window) |
| Team warmth rating | 4.6 / 5 (was 2.8) |

## 🚨 Blocking Issues

**2 custom/made-to-measure items were offered full refunds for change-of-mind**

This violates your core business model. Custom items cost 2-3x to produce and cannot be resold.

- T-1013: Custom wardrobe - $2-5K loss
- T-1026: Custom bookshelf - $1-3K loss

**Root cause:** The prompt says "do whatever it takes... if they want a refund, make it happen" which overrides policies.

## ✅ What's Working

The warmth improvements are **genuinely excellent**:
- Empathy is natural and authentic
- First name usage feels personal
- Customers feel heard and valued
- Team rated 4.6/5 vs 2.8/5 for old prompt

## 🔧 How to Fix

1. Use `suggested_prompt_v4_fixed.md` - keeps all warmth, adds policy guardrails
2. Re-run your ticket replay
3. Run `python output/test_suite.py outputs_new.jsonl` to verify
4. Ship when violations = 0

**Time to fix:** 1-2 hours for prompt update + re-test

## 📁 Files in This Directory

- **`QUICK_SUMMARY.md`** - Start here, 2-min read
- **`sanity_check_report.md`** - Full detailed analysis
- **`side_by_side_comparisons.md`** - Before/after examples
- **`policy_violations.json`** - Machine-readable violation data
- **`test_suite.py`** - Automated checker (reuse for future prompts!)
- **`suggested_prompt_v4_fixed.md`** - Fixed prompt ready to test

## 💡 For Future Iterations

The `test_suite.py` script will save you time on every prompt change:

```bash
# Run it on any new output
python output/test_suite.py your_outputs.jsonl

# Exit code 0 = pass, 1 = violations found
```

Add it to your workflow: replay tickets → run test suite → manual review → ship.

## Bottom Line

**The direction is 100% right.** Warmth massively improves CSAT. Just need to preserve the policy boundaries that protect the business model.

**Don't ship Friday, but you can ship next week** after the quick fix.
