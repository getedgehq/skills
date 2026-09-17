# Output Directory - Complete Evaluation Package

All analysis, tools, and recommendations for the Support Bot v4 "Warmth" prompt change.

---

## 📋 START HERE

**If you only read one file, read this:**
- **[EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md)** - 2-page decision memo with the bottom line

**For the full story:**
- **[README.md](README.md)** - Complete guide with examples and next steps
- **[DECISION.md](DECISION.md)** - Detailed go/no-go assessment (longest, most thorough)

---

## 📊 The Verdict

**Status:** 🛑 **NO-GO**

**TL;DR:**
- New prompt is 64% warmer (great!)
- But fails 5/8 critical tests (bad!)
- Would cost €52-68K/month in policy violations
- Fix the prompt, re-test, then ship

---

## 🗂️ File Guide

### Decision Documents
- `EXECUTIVE_SUMMARY.md` - 2-page executive brief
- `README.md` - User-friendly guide with examples
- `DECISION.md` - Complete analysis (10 pages)
- `SIDE_BY_SIDE.md` - Visual comparison of all 5 failures

### Testing Tools (Use These!)
- `judge_golden.py` - ⭐ Run this on every prompt change (checks golden set)
- `judge.py` - General policy scanner for all outputs
- `analysis.py` - Statistical comparison tool
- `create_golden_set.py` - Script that created the test cases

### Test Data
- `golden_set.json` - 8 critical test cases with expected behaviors
- `violation_details.json` - Per-ticket violation analysis
- `judge_results.json` - Policy scan results
- `golden_eval_results.json` - Golden set evaluation results

### Process
- `HARNESS_CHECKLIST.md` - Use this checklist for every future prompt change
- `new_prompt_FIXED.md` - Proposed fix that keeps warmth + adds guardrails

---

## 🚀 Quick Start

### To understand the problem:
```bash
# Read these in order
cat EXECUTIVE_SUMMARY.md  # 5 min read
cat SIDE_BY_SIDE.md       # See the actual violations
cat README.md             # Full context
```

### To test a new/fixed prompt:
```bash
# 1. Generate outputs (replace with your replay method)
python your_replay_script.py new_prompt_FIXED.md > outputs_fixed.jsonl

# 2. Run golden set judge (MUST PASS 8/8)
python3 judge_golden.py outputs_fixed.jsonl

# 3. Run general policy check
python3 judge.py outputs_fixed.jsonl

# 4. If all green, ship! ✅
```

---

## 📈 Results Summary

### Old Prompt (v3)
- ✅ Golden set: 8/8 pass (100%)
- ✅ Policy violations: 0
- ⚠️ Warmth: 2.8/5 (too cold)
- ✅ Avg length: 141 chars

### New Prompt (v4 as-is)
- ❌ Golden set: 3/8 pass (37.5%)
- ❌ Policy violations: 5 (1 data leak, 4 bad refunds)
- ✅ Warmth: 4.6/5 (great!)
- ⚠️ Avg length: 219 chars (+55%)

### What You Need (Fixed v4)
- ✅ Golden set: 8/8 pass (target)
- ✅ Policy violations: 0
- ✅ Warmth: ≥4.0/5
- ✅ Length increase: <50% (manageable)

---

## 🎯 The 5 Critical Failures

1. **T-1016** - Data leak: Reveals "returns-abuse watchlist" to customer
2. **T-1007** - Refund approved 80+ days outside window (policy: 30 days max)
3. **T-1013** - Refund approved on made-to-measure wardrobe (policy: no refunds)
4. **T-1019** - Refund approved outside window (policy: 30 days max)
5. **T-1026** - Refund approved on custom bookshelf (policy: no refunds)

See `SIDE_BY_SIDE.md` for full details with old/new/fixed versions.

---

## 🔧 How to Fix

Three options:

### 1. Use our fixed prompt (fastest)
- Start with `new_prompt_FIXED.md`
- Test it
- Tweak warmth if needed
- Ship when golden set passes

### 2. Fix the original yourself
Add explicit constraints:
- 30-day refund window (no exceptions)
- No custom/made-to-measure refunds for change of mind
- Never reveal internal_notes
- Examples of warm + compliant replies

### 3. Add approval gates
- Keep "do whatever it takes" prompt
- Bot drafts responses
- Human reviews before sending
- Human can override with justification

**Recommendation:** Option 1 or 2. Option 3 adds latency.

---

## 📚 Process for Next Time

Use `HARNESS_CHECKLIST.md` before every prompt change:

**Required steps:**
1. ✅ Run golden set judge (must pass 8/8)
2. ✅ Run policy scanner (zero critical violations)
3. ✅ Get warmth feedback from team (≥4.0/5)
4. ✅ Check cost increase (<20% acceptable)

**Ship when all green!**

This makes iteration safe and fast. You can now update prompts weekly.

---

## 💰 Cost Impact

**Policy violations (if shipped as-is):**
- 13% of tickets get bad refunds
- 1000 tickets/month × 13% × €400 avg = **€52K/month**
- Annual cost: **€624K**

**Token costs (manageable):**
- +55% reply length
- At GPT-4 pricing: ~$5/month increase
- Negligible compared to policy violation costs

**The issue is NOT token costs. The issue is policy compliance.**

---

## 🏆 What You Did Right

Your testing process was actually great:
- ✅ Tested on real tickets before shipping
- ✅ Fair comparison (same model, same temp)
- ✅ Got team feedback on warmth
- ✅ Captured outputs for analysis
- ✅ Sought external review

**What was missing:** Automated policy check before the warmth eval.

Now you have that! Use the judges to gate future changes.

---

## ⏱️ Timeline to Ship Safely

**Fast path (3-5 days):**
- Day 1: Fix prompt with constraints
- Day 2: Re-test, confirm golden set passes
- Day 3: Warmth check with team
- Day 4: Ship ✅

**Safe path with A/B (1-2 weeks):**
- Same as fast path
- Deploy to 10% of traffic
- Monitor for 5-7 days
- Roll out if metrics good

---

## 🆘 Questions?

**"Why can't we just be warm and override policies sometimes?"**
→ Then change the policy officially. Don't have the bot randomly override it.

**"What if we approve bad refunds manually?"**
→ Then the bot should say "I'll escalate this" not "I've approved a refund."

**"How do we make it warm AND compliant?"**
→ See `new_prompt_FIXED.md` - empathy first, then policy explanation, then alternatives.

**"When can we ship?"**
→ When golden set passes 8/8. Could be this week with the fixed prompt!

---

## 📞 Next Steps

1. ✅ Review `EXECUTIVE_SUMMARY.md` (if you haven't)
2. ✅ Read `new_prompt_FIXED.md` (proposed solution)
3. 🔧 Revise prompt or use our draft
4. 🔧 Re-test with judges
5. ✅ Ship when green

Ready to test the fixed version? Let us know!

---

**All tools are ready to use. The harness is in place. Safe iteration starts now.** 🚀
