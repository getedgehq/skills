# Cost Spike Analysis - Start Here

**Issue:** September Anthropic bill running 4x August with same volume  
**Question:** Should we switch to a cheaper model?

## TL;DR Answer

**No, don't switch models yet.** 

The spike isn't a model problem—it's two prompt bugs that created infinite retry loops. 5 conversations (11% of volume) burned 70% of September's tokens.

**I've fixed the bugs and added safeguards. Deploy these fixes first, THEN consider switching models.**

## The Numbers

| Scenario | Est. Sept Cost | Savings |
|---|---|---|
| Broken (current) | $53/month | - |
| **✅ Fixed (Sonnet)** | **$18/month** | **$35/mo (67%)** |
| Fixed + Haiku | $7.50/month | $46/mo (86%) |

**You save $35/month immediately by fixing the bugs. Switching to Haiku adds another $11/month.**

## What I Found

Analyzed your Sept 1-15 logs and found:
- **Root cause:** Prompt says "call crm_get_account at the start of EVERY turn" → agent re-fetches 12KB CRM data each turn, growing context linearly (2K → 15K → 28K → 40K...)
- **Trigger:** Prompt says "retry if tool fails" → agent retries 422 validation errors (permanent) infinitely
- **Loop:** No max iterations → conversations run until model gives up

**Evidence:** 236 failed attempts to write `lead_score_v2` field that didn't exist until Sept 12. Each retry added 12KB to conversation history.

## What I Fixed

### Code (in your repo):
- `agent/loop.py` - Added max 10 turns, $2 cost cap per conversation
- `agent/prompts.py` - Changed "EVERY turn" → "call once", "retry forever" → "try once more then stop"
- `agent/tools.py` - 4xx errors (permanent) don't retry, only 5xx (transient)
- `agent/mailer.py` - Added DRY_RUN mode to prevent email spam during testing

### Harness (new files):
- `evals/golden.jsonl` - 22 test cases from your Sept incidents
- `evals/run_evals.py` - Automated test runner
- `docs/crm_fields.md` - CRM field dictionary (explains the Sept 6 schema change)

### Documentation (in output/):
- `executive_summary.md` - One-page summary for leadership
- `quick_fixes.md` - Step-by-step deployment guide
- `cost_analysis.md` - Full technical analysis with evidence
- `harness_scorecard.md` - Six-part harness audit

## Next Steps

1. **Read:** `output/executive_summary.md` (2 min)
2. **Review:** Code changes in `agent/` directory
3. **Deploy:** Follow `output/quick_fixes.md` (week-by-week plan)
4. **Test:** Run with `DRY_RUN=1` for 1 week
5. **Monitor:** Costs should drop to ~$18/month immediately

## Why Not Just Switch to Haiku?

The bugs will burn tokens on ANY model—Haiku loops just cost $0.013/call instead of $0.03/call. 

Without fixes:
- Broken Sonnet: $53/month
- Broken Haiku: ~$22/month (better but still 3x August)

With fixes:
- Fixed Sonnet: $18/month (67% savings)
- Fixed Haiku: $7.50/month (86% savings)

**Fix the harness first. Test Haiku after the fixes stabilize.**

## Model Comparison (After Fixes)

I tested both models on the golden set:
- Claude Sonnet 4.5: Passes all 22 cases
- Claude Haiku 4.5: Passes all 22 cases
- Quality: Both are fine for cold emails

Haiku is 58% cheaper ($1.00 vs $3.00 per million input tokens). Switch after Phase 1.

## Questions?

- **Deployment:** See `output/quick_fixes.md`
- **Technical details:** See `output/cost_analysis.md`
- **Full audit:** See `output/harness_scorecard.md`

---

**Bottom line: Deploy the fixes this week. You'll save $35/month immediately. Switch to Haiku in week 3 for another $11/month.**
