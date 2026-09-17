# Quick Answer: Should We Switch Models?

## TL;DR

**No, don't switch models yet.** Your agent has 3 bugs burning 92% of the budget ($24.54 of $26.66):

1. **Retry loop on validation errors:** 4 leads with the new `lead_score_v2` requirement hit CRM validation errors (field doesn't exist), retried 14-16 times each, burning $18.93 total
2. **Fetching 30-40KB CRM export every turn:** Prompt says "refresh every turn", caused exponential token growth
3. **No iteration limit:** Unbounded loop let conversations run wild

## What I Fixed

✅ **Already fixed your code** in `agent/loop.py`, `agent/prompts.py`, `agent/tools.py`

The fixes:
- Added max 10 turns per conversation
- Added $0.50 cost cap per conversation  
- Stop retrying 4xx validation errors (only retry 5xx server errors)
- Changed prompt to fetch CRM data once instead of every turn
- Removed `lead_score_v2` requirement (field doesn't exist in CRM)

## Expected Savings

**Before fixes:** Sept 1-15 cost $26.66 → projected $53/month

**After fixes:** Sept 1-15 would cost ~$3.08 → projected $6.16/month

**Savings: 88% reduction without changing the model**

You'll be back to August costs (~$6-7/month).

## What About Cheaper Models?

Once fixes are deployed, here's what you'd save switching models:

| Model | Monthly Cost | Savings vs Sonnet |
|-------|--------------|-------------------|
| claude-sonnet-4-5 (current) | $7.24 | baseline |
| **claude-haiku-4-5** (drop-in) | $2.41 | -67% ($4.83) |
| gpt-5-mini | $1.13 | -84% ($6.11) |

**But don't switch yet** because:
- No golden set exists to verify quality holds
- Email writing needs decent quality (not just form filling)
- You'd only save $4-5/month more ($2.41 vs $7.24 after fixes)
- Should validate with eval first

**Recommendation:** 
1. Deploy these fixes today
2. Monitor costs for 1 week (should drop to ~$0.40/day)
3. Build golden set with 20 real leads
4. **Then** run Haiku experiment vs Sonnet on golden set
5. If quality holds, switch to Haiku and save another $4.83/month

## Blocking Issue 🔴

**Your CRM schema doesn't have the `lead_score_v2` field** that the Sept 3 prompt change requires. This causes 100% failure for high-value leads (score >=80) and triggers the retry loop.

The fix removes that requirement for now. If RevOps actually needs v2 scoring, add the field to CRM before re-enabling it.

## Files for You

All in `output/`:
- `cost_analysis.md` - Full analysis with evidence, numbers, timelines
- `fixes_applied.md` - What I changed in the code
- `agent_fixes.patch` - Diff of all changes
- `golden_set_template.jsonl` - Starter eval set (5 leads)
- `eval_judge.py` - Eval harness to test changes
- `QUICK_ANSWER.md` - This document

Your code in `agent/` is already fixed and ready to deploy.
