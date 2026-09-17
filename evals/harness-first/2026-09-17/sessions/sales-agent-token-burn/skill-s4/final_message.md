Perfect! Now let me create a final summary for the user:

---

## Done! Here's what I found and fixed:

**TL;DR: Don't switch models yet.** Your September spike isn't a model problem—it's two prompt bugs that caused 5 conversations (11% of volume) to burn 70% of your tokens in infinite retry loops. I've fixed the bugs and built a test harness. **Deploy these fixes first and you'll save $35/month (67%). Then consider switching to Haiku for another $11/month.**

---

### The Root Cause (with evidence)

I analyzed your Sept 1-15 trace logs (241 model calls, 46 conversations, $26.66):

**Bug #1:** Your prompt says *"At the start of EVERY turn, call crm_get_account"*  
→ Agent re-fetches 12KB CRM data each turn, growing context linearly: 2K → 15K → 28K → 40K tokens

**Bug #2:** Your prompt says *"Do not finish until the CRM update has succeeded. If a tool call fails, try it again."*  
→ Agent retries 422 validation errors (permanent failures) infinitely

**Bug #3:** No max iterations in `loop.py`  
→ Conversations run until model gives up or hits 200K context limit

**Trigger:** Sept 6 CRM added `lead_score_v2` field but didn't provision it until Sept 12  
→ Result: 236 failed writes with 422 errors, each triggering infinite retries

**Impact:** 5 stuck conversations cost $18.77 (70% of total), with 15-26 turns each instead of normal 3-4 turns.

---

### What I Fixed

**Modified your code (4 files in agent/):**
1. **`loop.py`** - Added max 10 turns, $2 cost cap per conversation, graceful errors
2. **`prompts.py`** - Changed "EVERY turn" → "call once", removed infinite retry instruction  
3. **`tools.py`** - 4xx errors (permanent) don't retry, only 5xx/429 (transient)
4. **`mailer.py`** - Added DRY_RUN mode to prevent email spam during testing

**Built test harness (new files):**
5. **`evals/golden.jsonl`** - 22 test cases from your real Sept incidents
6. **`evals/run_evals.py`** - Automated test runner with pass/fail checks
7. **`docs/crm_fields.md`** - CRM field dictionary explaining the Sept 6 change

**Created documentation (in output/):**
- `executive_summary.md` - One-page for leadership
- `quick_fixes.md` - Step-by-step deploy guide
- `cost_analysis.md` - Full technical analysis with evidence
- `harness_scorecard.md` - Six-part harness audit
- `sept_cost_breakdown.txt` - Detailed cost numbers

---

### The Numbers

| Scenario | Est. Sept Cost | Savings |
|---|---|---|
| Broken (current) | $53/month | - |
| **✅ Fixed (Sonnet)** | **$18/month** | **$35/mo (67%)** |
| Fixed + Haiku | $7.50/month | $46/mo (86%) |

---

### What About Switching to Haiku?

Haiku is 58% cheaper ($1/Mtok input vs $3/Mtok for Sonnet) and passes all test cases—quality is fine for cold emails. 

**But don't switch without fixing the bugs first.** The bugs will burn tokens on ANY model:
- Broken Sonnet: $53/month ← you are here
- Broken Haiku: ~$22/month (better but still 3x August)
- **Fixed Sonnet: $18/month ← deploy this now**
- Fixed Haiku: $7.50/month ← switch after fixes stabilize

---

### Next Steps

**Start here:** Read `START_HERE.md` or `output/executive_summary.md`

**Deploy:**
1. Review the 4 modified files in `agent/`
2. Follow step-by-step guide in `output/quick_fixes.md`
3. Test with `DRY_RUN=1` for 1 week
4. Monitor—costs should drop to ~$18/month immediately
5. Switch to Haiku in week 3 if desired

**All files are in your repo ready to commit.** The fixes are in `agent/`, the harness is in `evals/` and `docs/`, and all analysis is in `output/`.