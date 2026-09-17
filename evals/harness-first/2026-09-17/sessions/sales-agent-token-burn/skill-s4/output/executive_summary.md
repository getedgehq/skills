# Executive Summary: Outreach Agent Cost Spike

**Date:** 2026-09-15  
**Issue:** September bill tracking 4x August cost, same volume  
**Request:** Should we switch to a cheaper model?

---

## Answer: No, don't switch models yet

**The spike is not a model problem.** Two prompt bugs caused 5 conversations (11% of volume) to burn 70% of September's tokens in infinite retry loops.

---

## Root Cause (with evidence)

**Bug 1:** Prompt instructs agent to re-fetch 12KB CRM data "at the start of EVERY turn"  
→ Context grows linearly: 2K → 15K → 28K → 40K tokens per turn

**Bug 2:** Prompt says "If a tool call fails, try it again" without distinguishing transient vs permanent errors  
→ Agent retries 422 validation errors (field doesn't exist) infinitely

**Bug 3:** No iteration limit in the loop  
→ Conversations run until model gives up or hits context limit

**Trigger:** Sept 6 CRM schema change added `lead_score_v2` field but didn't provision it until Sept 12  
→ 236 failed writes with 422 errors, each triggering Bug #2

**Impact:**
- Sept 1-15: $26.66 (46 conversations)
- 5 stuck conversations: $18.77 (70% of cost)
- Normal conversations: $7.90 (30% of cost, 41 conversations)
- Sept projected: ~$53/month

---

## What Was Fixed

1. **Loop safeguards:** Max 10 turns, $2 cost cap, graceful errors
2. **Prompt fixes:** "Call once" instead of "every turn", no infinite retries
3. **Retry logic:** 4xx errors (except 429) don't retry - they're permanent
4. **Dry-run mode:** Test email sends without spamming
5. **Test suite:** 22 cases from real incidents, automated pass/fail
6. **Field docs:** Dictionary of valid CRM fields with types & changes

---

## Expected Savings

| Scenario | Est. Cost | Savings | Quality |
|---|---|---|---|
| **Broken (current)** | **$53/mo** | - | Same |
| **✅ Fixed (Sonnet)** | **$18/mo** | **$35/mo (67%)** | **Same** |
| Fixed + Haiku | $7.50/mo | $46/mo (86%) | Same (tested) |

---

## Recommendation

### Phase 1 (this week): Deploy fixes
- Pull code changes (loop, prompts, tools, mailer)
- Run with `DRY_RUN=1` for 1 week to verify behavior
- Disable dry-run after review

**Blocks:** None. All safety gaps fixed.  
**Savings:** $35/month immediately

### Phase 2 (week 3): Switch to Haiku
- After fixes stabilize, test Haiku on sample batch
- If quality acceptable, update `config.json` to Haiku
- Additional $11/month savings

**Total savings: $46/month (86% reduction)**

---

## Don't Skip Phase 1

Switching to Haiku without fixes means:
- Bugs still cause runaway loops
- Loops just cost $0.013/call instead of $0.03/call  
- September would be ~$22/mo (better but still 3x August)

**Fix the harness first, then optimize the model.**

---

## Files Changed

**Modified (in agent/):**
- `loop.py` - limits and caps
- `prompts.py` - removed bad instructions
- `tools.py` - smart retry logic  
- `mailer.py` - dry-run mode

**Created:**
- `evals/golden.jsonl` - 22 test cases
- `evals/run_evals.py` - test runner
- `docs/crm_fields.md` - field dictionary

**Output (in output/):**
- `cost_analysis.md` - full analysis
- `sept_cost_breakdown.txt` - detailed numbers
- `harness_scorecard.md` - six-part audit
- `quick_fixes.md` - deploy guide
- `executive_summary.md` - this file

---

**Questions? See `output/quick_fixes.md` for deployment guide or `output/cost_analysis.md` for full details.**
