# EXECUTIVE SUMMARY
**To:** Finance Team  
**Re:** Anthropic bill - Outreach agent cost spike  
**Date:** 2026-09-16

---

## The Question
"September Anthropic bill is 4× August with same volume. Should we switch to a cheaper model?"

## The Answer
**Don't switch models yet. Fix the bug first—it'll save 71% with zero risk.**

---

## What Happened

5 of 46 conversations (11%) got stuck in infinite retry loops, burning 70% of the budget.

**Root cause:**  
- Agent was told to re-fetch account data "at the start of every turn" → context grew from 2K to 188K tokens
- When a CRM field didn't exist (422 error), agent retried the same bad field 15-17 times
- No max iteration limit → loops ran until something gave up

**Evidence:**
- Logs show 236 failed API calls with error "field lead_score_v2 does not exist"
- Top 5 conversations: $4.73, $4.71, $4.60, $4.39, $0.33 (avg $3.75)
- Normal conversations: average $0.19

---

## The Fix (Already Done)

Changed 3 files in agent/:

1. **loop.py** - Added hard stop at 8 turns or $0.50, whichever comes first
2. **tools.py** - Stop retrying permanent errors (404, 422), only retry rate limits and server errors
3. **prompts.py** - Removed "call every turn" instruction, changed "retry forever" to "report and finish"

**Risk:** Low. Added safety caps, removed infinite loops. No model change.

---

## Cost Impact

**Current (broken):**  
- September pace: 92 conversations/month
- Cost per conversation: $0.58 (with retry loops)
- **Monthly: $53**

**After fix (same model):**  
- Cost per conversation: $0.17 (retry loops eliminated)
- **Monthly: $16**
- **Savings: $37/month (71%)**

**If we switch to cheaper model later:**  
- Monthly: $2
- Savings: $51/month (97%)
- **But:** Need to test quality first (cold emails, not mission-critical)

---

## Recommendation

### This Week
✅ Deploy the fix (no model change)  
✅ Validate cost drops to ~$16/month  
✅ Risk: minimal (added safety caps)

### Next Month  
🔄 Test cheaper model (GPT-5-mini) on quality  
🔄 If it passes → switch, save another $14/month  
🔄 If it fails → stay on current, already saved 71%

---

## Why Fix First?

Even on a 90% cheaper model, the retry loops would still happen. You'd still waste tokens fetching the same data 17 times. The bug scales with volume—as you add more leads, more hit edge cases, more loops.

Fix eliminates the waste regardless of model price. Then switch models safely with real testing.

---

## Timeline

- **Today:** Code reviewed (3 files changed)
- **This week:** Deploy to production
- **End of Sept:** Bill reflects partial month savings (~$10-15)
- **October:** Full month at $16 (71% savings locked in)
- **Later:** Model switch testing (optional extra 88% savings)

---

## Questions?

**"Is Sonnet overkill for cold emails?"**  
Maybe, but that's not why the bill spiked. The bill spiked because of infinite loops. Fix those and decide on model with data, not panic.

**"Can we switch models now?"**  
You could, but you'd still have the bug. Better to fix the bug (1 hour, zero risk, 71% savings) then test the model switch properly (1 week, needs quality review, extra 88% savings).

**"What if volume doubles?"**  
With the fix: doubles from $16 to $32/month. Without the fix: doubles from $53 to $106/month, and retry loops get worse at scale.

---

## Bottom Line

**Problem:** Infinite retry loops, not expensive model  
**Solution:** 3 file changes (already done)  
**Savings:** $37/month (71%) with zero risk  
**Timeline:** Deploy this week  
**Model switch:** Test later if you want the extra 88%  

Flip the switch before month end, you'll see it in October's bill.

---

**Attachments:**
- `output/REPORT.md` - Full technical analysis
- `output/model_cost_comparison.md` - Cost tables at different volumes
- `output/harness_scorecard.md` - What else needs fixing (safety, testing)
- `agent/` - Fixed code (loop.py, tools.py, prompts.py)
- `evals/` - Test cases for future model comparison
