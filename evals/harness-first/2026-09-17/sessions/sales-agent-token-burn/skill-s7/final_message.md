Excellent! Everything is complete. Let me give you the final summary:

---

## Summary

**Your question:** Should we switch from Sonnet to a cheaper model because of the 4x cost spike?

**My answer:** **NO - Don't switch models yet.** The cost spike was from 3 bugs in your agent harness, not the model being "overkill." I found and fixed the bugs instead.

### What I Found

By analyzing your Sept 1-15 trace logs, I discovered that **5 conversations (11% of leads) hit infinite retry loops and burned 70% of your budget** ($18.76 of $26.66).

**Three bugs caused this:**

1. **Bad prompt instruction** - Told the model to reload 40KB account data "at EVERY turn" → data fetched 4.1x per lead average (should be 1x)
2. **Broken retry logic** - Retried validation errors (422) that would never succeed (e.g., 64 attempts to use a non-existent field)  
3. **No safety caps** - No max iterations or cost limits → one lead ran 26 turns

### What I Fixed

✅ **Code changes** (in `agent/` directory):
- `loop.py` - Added max 8 iterations + $0.50 cost cap per lead
- `tools.py` - Smart retry logic: fail fast on 4xx, retry 5xx/429
- `prompts.py` - Changed "EVERY turn" to "ONCE", removed non-existent field

✅ **Tested** - Unit tests verify fixes work correctly

✅ **Projected savings: 84%** (from $26.66 to ~$5 for Sept 1-15 period)

### About Model Switching

I evaluated all the model options from Priya's price sheet:

- **Sonnet (current) with fixes:** ~$5 for 46 leads → **Problem solved**
- **Haiku:** ~$1.40 (saves $3.60 more) → Need quality tests first
- **GPT-5-mini:** ~$0.38 (saves $4.60 more) → Need SDK change + quality tests

**My recommendation:** Stay on Sonnet with the fixes. At your volume (~100 leads/month), switching to Haiku only saves ~$8-10/month more - not worth the quality risk without proper testing.

### Deliverables

📂 **output/** directory contains:
- `START_HERE.md` - Navigation guide
- `ANSWER.md` - Direct answer to your question
- `EXECUTIVE_SUMMARY.md` - One-pager for finance
- `cost_analysis_report.md` - Full technical analysis with evidence
- `model_comparison.md` - All model options evaluated
- `cost_breakdown.txt` - Visual before/after charts
- `golden_set_starter.jsonl` + templates for building quality tests

📂 **agent/** directory - Fixed code (ready to deploy)

The fixes solve your immediate problem. Model switching can wait until you have quality tests in place.