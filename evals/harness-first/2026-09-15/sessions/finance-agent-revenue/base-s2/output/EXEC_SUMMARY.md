# Executive Summary: FinBot Q2 Revenue Issue

**For:** Daniel  
**Date:** September 15, 2026  
**Re:** Q2 revenue discrepancy ($4.1M vs $3.6M)

---

## Bottom Line

**The bot is not hallucinating. It's a fixable data/prompt issue, not a model problem.**

- ❌ Don't upgrade to Opus/GPT-6 (won't help)
- ✅ Do update the system prompt (fixes the root cause)
- ⏱️ Fix takes 5 minutes to deploy

---

## What Happened

| Source | Q2 Revenue | Method |
|--------|-----------|--------|
| **FinBot** | $4.1M | ❌ Wrong: Summed ALL orders (including cancelled/refunded) |
| **Finance** | $3.6M | ✅ Correct: Used revenue_recognized table (proper accounting) |
| **Difference** | $500K | = Cancelled orders ($360K) + Refunded orders ($190K) |

---

## Root Cause

The bot's system prompt doesn't specify which database table to use for revenue queries.

- The warehouse has **two tables**: 
  - `orders` = raw transactions (includes cancelled orders)
  - `revenue_recognized` = official accounting numbers
  
- The prompt just lists both tables without guidance
- The model made a logical but wrong choice
- **This is prompt engineering, not AI capability**

---

## The Fix

**File:** `prompt.md`

**Add this guidance:**
```
For revenue questions, ALWAYS use revenue_recognized.net_amount
DO NOT use orders.amount (includes cancelled/refunded orders)
```

That's it. See `output/prompt_FIXED.md` for the complete updated prompt.

---

## Why Not Upgrade the Model?

| Issue | Claude Sonnet | Opus/GPT-6 |
|-------|--------------|-------------|
| SQL syntax | ✅ Perfect | ✅ Perfect (same) |
| Question understanding | ✅ Perfect | ✅ Perfect (same) |
| **Business logic** | ❌ Guessed wrong table | ❌ **Would likely guess wrong too** |

**The model doesn't know your accounting rules.** Even GPT-6 would need explicit guidance about which table is the source of truth.

Think of it like asking a new employee "what was Q2 revenue?" without telling them which system to check. They'd guess. A senior employee would guess too, just more expensively.

---

## Impact

**Known issues:**
- ✅ Board deck (flagged by Marta)
- ❓ Q1 number is also wrong ($4.1M vs actual $3.3M)

**Potential issues:**
- Anyone who asked finbot about revenue since March 2026
- Check #ask-finance Slack history for other revenue queries
- Could affect investor updates, planning docs, exec reviews

---

## Action Plan

### Today (before board meeting):
1. Update `prompt.md` with the fixed version
2. Test: Run `python agent.py "what was Q2 2026 revenue?"`
3. Verify it returns ~$3.6M
4. Correct the board deck

### This Week:
1. Audit #ask-finance Slack for other revenue queries
2. Check what other artifacts might have wrong numbers
3. Set up validation: monthly spot-check finbot vs finance reports

### Optional:
- Add query validation to block obvious errors
- Create test suite with known-good queries
- Document "source of truth" tables for different metrics

---

## Files Delivered

All analysis is in `output/`:

1. **root_cause_analysis.md** - Full technical breakdown
2. **prompt_FIXED.md** - Updated prompt that fixes the issue
3. **verification_queries.sql** - SQL to reproduce the analysis
4. **test_finbot_fix.py** - Test script to verify the fix works

---

## Questions?

- "Why did this happen?" → Prompt didn't specify which table to use
- "Is the model broken?" → No, it works as designed
- "Should we upgrade?" → No, won't help without better prompt
- "How long to fix?" → 5 min to update prompt, 10 min to test
- "Could this happen again?" → Not for revenue (prompt now explicit), but review other metrics

---

**Recommendation:** Deploy the prompt fix today. The model is fine.
