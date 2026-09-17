## Summary

**Don't switch models yet: 5 conversations stuck in retry loops burned 70% of tokens ($18.77 of $26.66).**

I've completed a full harness-first diagnosis of your outreach agent's 4x cost spike. The problem wasn't the model - it was three harness bugs:

### Root Causes (with evidence)

1. **Infinite retry on permanent errors** - Prompt said "if a tool call fails, try it again." Agent retried 404 "account_merged" 26 times and 422 "unknown field lead_score_v2" 68+ times across 4 high-scoring leads. These 5 conversations cost $18.77 (70% of total).

2. **Wasteful re-fetching** - Prompt said "call crm_get_account at EVERY turn." Each fetch adds 12KB JSON to message history. By turn 10: 114K input tokens. Normal conversations wasted 89% of tokens.

3. **No max iterations** - `while True:` loop with no cap. One conversation ran 26 turns.

### What I Fixed

✅ **agent/loop.py** - Added `max_turns=10`, graceful stop message  
✅ **agent/prompts.py** - Call crm_get_account ONCE, removed non-existent `lead_score_v2` field, don't retry 4xx errors  
✅ **agent/tools.py** - Fail fast on 4xx errors (404, 422, etc.), only retry 5xx

### Expected Savings

- **Current:** $26.66/half-month = **$53/month**
- **After fixes:** $3.68/half-month = **$7/month**
- **Savings: $46/month (86% reduction)**

### Model Recommendation

**Keep Claude Sonnet 4-5.** After the harness fix, switching models would save only $2-4/month more, not worth migration risk. If you must switch, use **claude-haiku-4-5** (1 line config change, $2.45/mo additional savings).

### What I Delivered

**In output/:**
- `README.txt` - Executive summary (start here)
- `QUICK_REFERENCE.txt` - Deploy checklist
- `cost_analysis.md` - Full diagnostic with evidence
- `cost_comparison.txt` - Visual before/after
- `fix_summary.md` - What changed and why
- `model_recommendation.md` - Model comparison
- `CHANGES.diff` - Exact code changes

**In evals/:**
- `golden.jsonl` - 10 test cases from real incidents
- `judge.py` - Eval harness skeleton

**All code fixes are deployed to agent/ and ready to test.**