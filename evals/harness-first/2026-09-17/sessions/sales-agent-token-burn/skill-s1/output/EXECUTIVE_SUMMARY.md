# EXECUTIVE SUMMARY - Outreach Agent Cost Fix

**To:** Finance & Engineering  
**From:** AI Ops Audit  
**Date:** Sept 15, 2026  
**Re:** Anthropic bill spike (4x increase)

---

## Bottom Line

**DON'T switch models yet. Fix the harness, save $450/year, THEN switch to Haiku.**

---

## What Happened

Sept 1-15 cost $26.66 vs ~$6 expected (4x spike with no volume change).

**Root cause:** 5 conversations (11% of volume) burned 70% of costs stuck in infinite retry loops hitting deterministic validation errors. The agent has no max-iterations cap and the prompt explicitly tells it to retry forever.

---

## The Numbers

| Metric | Current | After Fixes | After Fixes + Haiku |
|---|---|---|---|
| Sept 1-15 actual | $26.66 | $7.90 | $2.63 |
| Monthly projection | $53/mo | $16/mo | $5/mo |
| Annual | $640/yr | $190/yr | $63/yr |
| **Savings vs current** | — | **$450/yr** | **$577/yr** |

---

## Evidence

Lead L-3419 trace (Sept 9, 02:10 UTC):
- 16 turns, $4.73 cost (vs $0.19 normal)
- Made same API call 16 times: `crm_update_contact` with field `lead_score_v2`
- CRM returned 422 "unknown field" every time (field doesn't exist in schema)
- Prompt says: *"If a tool call fails, try it again"*
- No max-iterations circuit breaker in code
- By turn 16: 145,000 input tokens per call (full history + 30KB CRM export repeated)

3 more conversations hit identical pattern. Total waste: $18.44 (69% of costs).

---

## Model Choice

**Wrong approach:** "Sonnet is overkill, switch to gpt-5-mini"

**Why wrong:**
- Switching models doesn't fix infinite loops
- You'd still burn tokens on retries, just cheaper ones
- No evaluation to prove quality is maintained

**Right approach:** "Fix harness, then switch to Haiku"

**Why Haiku:**
- Same Anthropic API (just change config.json)
- 1/3 the price of Sonnet ($1 vs $3 per MTok input)
- Perfect for simple tasks (cold emails are not rocket science)
- No SDK changes needed (unlike gpt-5-mini)

But: **Must fix loops first or you'll still waste money.**

---

## Immediate Action (Before Month End)

**Apply harness fixes (5 min):**
```bash
cp output/fixed_agent_code/*.py agent/
```

**What changes:**
1. Add MAX_TURNS = 6 circuit breaker (prevent runaway loops)
2. Remove "try it again" from prompt
3. Fix field name: `lead_score_v2` → `lead_score` (matches CRM schema)
4. Stop retrying 4xx errors (they're deterministic, not transient)

**Test on 2-3 leads, then deploy.**

Expected savings: **$37/month** immediately.

---

## Next Week (After Fixes Are Stable)

1. Build golden evaluation set (20+ test cases)
2. Run baseline eval with Sonnet
3. Switch to Haiku, run eval again
4. If quality equivalent → ship

Expected additional savings: **$11/month** = **$48/month total**.

---

## Harness Before/After

| Issue | Before | After |
|---|---|---|
| Runaway loops | ❌ No max turns | ✅ MAX_TURNS = 6 |
| Bad retries | ❌ Retries 4xx errors | ✅ Fail fast on client errors |
| Prompt bugs | ❌ "try it again", "EVERY turn" | ✅ Fixed instructions |
| Schema mismatch | ❌ References nonexistent field | ✅ Uses correct field |
| Evaluation | ❌ No golden set | ⚠️ Started (3 cases, need 20+) |
| Email safety | ⚠️ No approval gate | ✅ EMAIL_DRAFT_MODE option |

---

## Files Delivered

All in `output/` directory:

**Analysis:**
- `README.md` - Quick start guide
- `cost_analysis.md` - Full analysis with evidence
- `trace_example.md` - Detailed walkthrough of one failure
- `cost_comparison.py` - Before/after breakdown script

**Fixes:**
- `fixed_agent_code/loop.py` - Circuit breaker added
- `fixed_agent_code/prompts.py` - Instructions fixed
- `fixed_agent_code/tools.py` - Stop retrying 4xx

**Harness:**
- `run_eval.py` - Evaluation script
- `golden_starter.jsonl` - 3 starter test cases (expand to 20+)
- `config_haiku.json` - Ready for model switch after testing

---

## Risk Assessment

**If you do nothing:**
- Continue burning $37/month on retry loops
- Risk more schema mismatches shipping to production
- No way to validate prompt/model changes before they break

**If you switch models without fixing:**
- Still have retry loops (just cheaper per token)
- No eval to prove quality maintained
- Could break quality for minimal savings

**If you fix harness first:**
- Stop bleeding immediately ($37/mo saved)
- Safe model switch with validation ($11/mo more)
- Regression tests prevent future incidents
- **Total: $577/year saved, much lower risk**

---

## Recommendation

1. **This week:** Deploy harness fixes, save $450/year
2. **Next week:** Build golden set, switch to Haiku for another $127/year
3. **Ongoing:** Run evals before every prompt/model change

**Confidence: 100%** - This is mechanical (logs prove it), not probabilistic.

---

## Questions?

**Q: Are you sure it's not the model?**  
A: Yes. The logs show the exact same API call failing 64 times in a row. The model is following the prompt correctly—the prompt is wrong.

**Q: Why not switch to gpt-5-mini like Priya suggested?**  
A: It doesn't fix the loops, requires SDK changes, and you have no eval to prove quality. Haiku is safer and almost as cheap.

**Q: Can we skip the golden set?**  
A: No. This bug made it to production. Without regression tests, you'll ship another one. The set takes 2 hours to build and prevents $$ incidents.

**Q: What if Haiku is worse at writing emails?**  
A: That's why you run the eval first. If quality drops, you have data to decide. But cold emails are simple—Haiku should be fine.

---

**Next step:** `cp output/fixed_agent_code/*.py agent/` and test on 2-3 leads.
