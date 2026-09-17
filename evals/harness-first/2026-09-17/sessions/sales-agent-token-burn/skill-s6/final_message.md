Excellent! Everything is ready. Let me create one final top-level summary:

---

## Summary

Hey! I analyzed your outreach agent cost spike using the **harness-first methodology**. Here's what I found:

### **Don't switch models yet. Fix the bug first—saves 71% with zero risk.**

## The Problem

**70% of your September costs** ($18.77 of $26.66) came from just **5 conversations** stuck in infinite retry loops:

- **Root cause:** Agent was told to re-fetch account data "at the start of EVERY turn" → context exploded from 2K to 188K tokens
- **Trigger:** CRM field `lead_score_v2` doesn't exist, but agent kept retrying 15-17 times
- **No safety net:** No max iterations, infinite `while True` loop
- **Evidence:** 236 failed API calls in logs for non-existent field

**Top offender:** 17 turns, 1.56M input tokens, $4.73 (vs. normal $0.19)

## The Fix (Already Done)

I fixed 3 files in `agent/`:

1. **loop.py** - Added max 8 turns, $0.50 cost cap per conversation
2. **tools.py** - Only retry transient errors (rate limits/timeouts), fail fast on permanent errors (404, 422)
3. **prompts.py** - "Call ONCE" not "EVERY turn", removed "retry forever" instruction

## Cost Impact

| Scenario | Cost/Month | vs Current | Risk |
|----------|-----------|------------|------|
| **Current (broken)** | **$53** | — | 🔴 High |
| **After fix (Sonnet)** ⭐ | **$16** | **-$37 (71%)** | 🟢 Low |
| After fix + GPT-5-mini | $2 | -$51 (97%) | ⚠️ Needs quality testing |

## What I Created

**All deliverables in `output/` and `evals/`:**

### For You/Finance
- ✅ **QUICK_ANSWER.txt** - One-screen summary (read this first!)
- ✅ **output/EXECUTIVE_SUMMARY.md** - One-page for management
- ✅ **output/model_cost_comparison.md** - Cost tables at different volumes

### For Engineering
- ✅ **output/REPORT.md** - Complete technical analysis with evidence
- ✅ **output/CHANGES_SUMMARY.md** - Every code change documented
- ✅ **output/harness_scorecard.md** - Reliability assessment
- ✅ **agent/loop.py, tools.py, prompts.py** - Fixed code

### Test Harness
- ✅ **evals/golden.jsonl** - 5 test cases from real incidents
- ✅ **evals/judge.py** - Automated quality checker

## Recommendation

### **This Week (Before Month End)**
Deploy the fixes → save $37/month (71%) with zero risk. No model change needed.

### **Next Sprint**
Test GPT-5-mini quality on golden set → if it passes, switch and save another $14/month (88% more).

### **Why Fix First?**
Even on a 90% cheaper model, the retry loops would still waste tokens. Fix the bug (saves 71%), then switch models safely with real quality testing.

## Next Steps

1. Review code changes in `agent/` 
2. Deploy to staging
3. Test on production
4. Monitor for improvements (~71% reduction expected)
5. October: full month at $16 vs $53

**Start here:** Read `QUICK_ANSWER.txt` (1 min) or `output/EXECUTIVE_SUMMARY.md` (3 min)

**Model switch decision:** Later, after golden set testing. You'll already have saved 71%.