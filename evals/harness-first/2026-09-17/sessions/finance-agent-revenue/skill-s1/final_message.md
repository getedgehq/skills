Perfect! I've completed the investigation. Here's what I found and delivered:

## For Daniel (CEO) - Tomorrow Morning

**NO, don't swap the model.** The bot isn't hallucinating. It used the wrong database table because "revenue" wasn't defined in the prompt. The fix takes 15 minutes to deploy.

### The Issue

- **FinBot reported:** $4.1M (used `orders.amount` = gross bookings)
- **Finance reports:** $3.6M (uses `revenue_recognized.net_amount` = GAAP revenue)
- **Gap:** $500K (12%)

The model worked correctly—it just queried the wrong table because the prompt lists both but doesn't say which one is "revenue."

### The Fix

All deliverables are in **output/** folder, ready to deploy:

**🔥 Deploy Today (15 minutes):**
1. `prompt_PATCHED.md` - Adds data dictionary defining "revenue"
2. `agent_safe.py` - Fixes safety issues (max iterations, read-only DB)
3. Update board deck: Q2 = $3.6M, Q1 = $3.3M (see `BOARD_DECK_CORRECTIONS.md`)

**📋 This Week:**
- Add test suite to CI (`evals/golden.jsonl` + `evals/judge.py`)
- Finance reviews `data_dictionary.md`
- Add logging/tracing

### The Diagnosis

**Harness Scorecard: 9/60 points**
- ❌ No golden set (test cases)
- ❌ No judge (automated testing)
- ❌ No data dictionary (caused the incident)
- ❌ No tracing
- 🟡 Partial cost governance
- 🟡 Partial action safety

This is a hackathon project that went to production without a harness. The model is fine—the infrastructure around it is missing.

### Files in output/

1. **EXECUTIVE_SUMMARY.md** ⭐ - Start here, one-page brief
2. **ACTION_ITEMS.md** - Who does what, when
3. **BOARD_DECK_CORRECTIONS.md** - Correct numbers for Priya
4. **harness_audit.md** - Full 6-component analysis
5. **data_verification.txt** - Evidence recomputed from database
6. **prompt_PATCHED.md** 🔥 - Ready to deploy
7. **agent_safe.py** 🔥 - Ready to deploy
8. **data_dictionary.md** - For Finance review
9. **evals/golden.jsonl** - 12 test cases
10. **evals/judge.py** - Test runner
11. **INVESTIGATION_LOG.md** - Complete investigation timeline

**Bottom line:** Fix the harness (15 min), don't swap the model. With the data dictionary, the current model will work perfectly.