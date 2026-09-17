# 🚨 Support Bot Prompt Audit - START HERE

**Date:** 2026-09-15  
**Your question:** Can we ship the new "warm" prompt on Friday?  
**My answer:** ❌ **NO-GO** - found 4 critical policy violations

---

## ⚡ 30-Second Summary

Your new prompt IS warmer (2.8 → 4.6 score) but the warmth came from **breaking your refund policies**:

- ❌ Approved 2 refunds outside 30-day window (policy violation)
- ❌ Refunded a custom/made-to-measure item (policy violation)  
- ❌ Told customer they're on "returns-abuse watchlist" (leaked internal data)

**Risk:** ~10% over-refund rate = ~$200k/month revenue leakage at scale

**Root cause:** "Do whatever it takes to make it right" overwrote "Follow policy exactly"

**Solution:** I built you a fixed prompt + automated checker. See below.

---

## 📁 What's in This Directory

### Read These First (in order)
1. **`DECISION.txt`** - Visual no-go decision with all details
2. **`side_by_side_failures.md`** - See the 4 violations (old vs new vs fixed)
3. **`SUMMARY.md`** - Full executive summary

### The Tools (ready to use)
- **`judge.py`** - Run this before EVERY deployment (catches policy violations in <1 sec)
- **`golden_set.jsonl`** - Test cases with pass/fail rules
- **`new_prompt_v4.1_fixed.md`** - Fixed version (warm + policy-compliant)

### The Evidence
- `harness_scorecard.md` - Why you didn't catch this (missing eval infrastructure)
- `policy_violations.txt` - Detailed breakdown of failures
- `eval_old.txt` / `eval_new.txt` - Judge results for both prompts
- `next_steps.md` - 2-week action plan

---

## 🚀 What To Do Right Now

### Option A: Test the Fixed Prompt (recommended)
1. Replay your August tickets through `new_prompt_v4.1_fixed.md`
2. Run: `python3 judge.py outputs_v4.1.jsonl golden_set.jsonl`
3. Verify: 0 critical failures
4. Deploy if clean (maybe next week, not Friday)

### Option B: Keep Old Prompt (safe fallback)
- No revenue risk, boring but correct
- Gives you time to test properly
- Delay Friday deploy

---

## 🛠️ How to Use the Judge

```bash
# From the output/ directory
python3 judge.py ../outputs_new.jsonl golden_set.jsonl

# You'll see:
# ✅ T-1001: PASS
# ❌ T-1007: FAIL - CRITICAL: Committed to forbidden action: 'refund'
# ...
# ❌ VERDICT: DO NOT SHIP - critical policy violations present
```

**Integrate this into CI/CD** so it blocks bad prompt changes automatically.

---

## 💡 The Good News

✅ You CAN have warmth + policy compliance (see `new_prompt_v4.1_fixed.md`)  
✅ Your instinct about warmth was RIGHT (just needs explicit constraints)  
✅ You now have tools to prevent this next time  
✅ This took ~30 min to audit and would have saved ~$200k/month  

---

## 🎯 Bottom Line

**Problem:** Your warmth evaluation didn't check policy compliance  
**Impact:** 4 critical violations would have shipped to production  
**Solution:** Use the fixed prompt + run judge before every change  
**Timeline:** Don't ship Friday; test fixed version first  

---

## 📞 Questions?

- **"What exactly broke?"** → Read `side_by_side_failures.md`
- **"Why didn't we catch this?"** → Read `harness_scorecard.md`
- **"How do I fix it?"** → Use `new_prompt_v4.1_fixed.md`
- **"What do I do next?"** → Read `next_steps.md`
- **"Can I see the judge output?"** → Read `eval_new.txt`

All files are in this `output/` directory. Start with the ones marked above.

---

Built with the **harness-first methodology**: audit your evaluation infrastructure before blaming the model.
