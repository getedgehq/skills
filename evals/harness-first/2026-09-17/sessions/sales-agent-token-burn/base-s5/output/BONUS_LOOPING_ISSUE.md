# 🚨 BONUS FINDING: Agent Looping Issue

While analyzing your costs, I found a separate problem that's wasting money:

## The Issue

Some conversations are taking **way too many turns** to complete:
- **Average conversation:** ~5.3 turns
- **Worst case:** 26 turns for a single lead (Lead L-3489)
- **4 conversations hit the 200k token context limit** and failed

## Why This Costs Money

Looking at the prompt in `agent/prompts.py`, line 1 says:
> "At the start of EVERY turn, call crm_get_account to load the latest full account export"

This means:
- Every turn, the agent loads the full CRM account (probably ~10-15k tokens)
- Multi-turn conversations stack up tokens fast
- At turn 17, you hit 200k+ tokens and the API fails
- All those tokens cost money but produce no result

## Root Cause

The prompt instruction "try it again" when a tool call fails probably creates retry loops. Combined with mandatory CRM reloads every turn, this burns through context fast.

## Quick Fix Options

**Option 1: Remove the per-turn CRM reload** (recommended)
- Only call `crm_get_account` on turn 1
- Most CRM data doesn't change mid-conversation anyway
- Would cut avg tokens per conversation by ~50%

**Option 2: Add max turn limit**
- In `agent/loop.py`, add a check: `if turn > 10: return "ERROR: Max turns exceeded"`
- Prevents runaway conversations

**Option 3: Better error handling**
- Don't retry failed tool calls endlessly
- Log the error and move on after 2-3 attempts

## Estimated Additional Savings

If you fix the looping issue:
- Could cut average input tokens from ~35k to ~17k per conversation
- Would save another **~$8-9/month** on top of the Haiku savings

## What To Do

1. **First:** Switch to Haiku (already done) - saves $35.55/mo
2. **Soon:** Fix the looping issue - saves another ~$9/mo
3. **Total savings:** ~$45/mo (~84% reduction from current)

I haven't modified the code for this since you asked me to fix the model choice, but it's worth looking into next week.

---
*See leads L-3489, L-3419, L-2012, L-3032, L-2437 in the Sept 1-15 logs for examples of the looping issue.*
