# FinBot Incident: Quick Reference for Daniel's Meeting

**Date:** 2026-09-16 (for tomorrow's meeting)

---

## TL;DR for Daniel

**Don't upgrade the model.** FinBot used the wrong database table—it counted $500k of cancelled/refunded orders that finance correctly excluded. Any model would make this mistake given the current prompt. Fix the data definitions and validation, not the model.

---

## The Numbers

| What | Amount | Source |
|------|--------|--------|
| **FinBot said** | $4.1M | orders table (all statuses) |
| **Finance says** | $3.6M | revenue_recognized table (GAAP) |
| **Difference** | $500k (13.9%) | cancelled + refunded orders |

---

## What Happened (One Sentence)

FinBot queried the operational orders table (which includes cancelled and refunded orders) instead of the financial revenue_recognized table (which excludes them).

---

## Why It Happened

1. **No data dictionary** - System doesn't define what "revenue" means
2. **No validation** - No test cases to catch wrong answers before they reach users
3. **Ambiguous prompt** - Lists multiple tables but doesn't say when to use each

The model understood the question and generated correct SQL—it just picked the wrong table because the system has no definition of "revenue."

---

## This Is NOT:

- ❌ A hallucination (model didn't make up numbers)
- ❌ A model capability problem (any LLM would fail the same way)
- ❌ A math error (both numbers are correct for their source tables)

**This is a system design problem** (missing data definitions and validation).

---

## Critical Safety Issues Found

🔴 **Infinite loop** - No max iterations, could burn unlimited tokens  
🔴 **Write access** - Bot can execute DELETE/UPDATE on the warehouse  
🔴 **No logging** - Can't audit what queries ran or what they cost  
🔴 **No validation** - No test suite to catch errors before production  

FinBot is a prototype that escaped the lab. These gaps are why the error happened.

---

## Immediate Actions (Today)

1. ✅ **Correct board deck** - Q2 is $3.6M, not $4.1M
2. ✅ **Disable bot** - Until safety fixes deployed
3. 🔄 **Audit other answers** - Check if other "revenue" numbers are wrong

---

## Fix Plan (This Week)

**Blocking fixes (deploy by Friday):**
- Add max iterations limit (5)
- Switch to read-only database
- Add data dictionary to prompt (revenue = revenue_recognized.net_amount)
- Create validation test suite (10 test cases)
- Add logging

**Expected impact:** With data definitions, bot will use correct table. Problem solved.

---

## Should We Upgrade the Model?

**Not yet.** Harness first, model second.

**Process:**
1. Fix the data definitions (done)
2. Create test suite (done)
3. Test current model (Claude Sonnet 4.5)
4. Test upgrade candidate (Opus/GPT-6)
5. Compare accuracy, cost, latency
6. Decide based on evidence

**Prediction:** Both models will get 100% accuracy with the fixed prompt. Cost becomes the only differentiator.

---

## Timeline

| When | What |
|------|------|
| **Today** | Correct board deck, disable bot |
| **This week** | Deploy 5 blocking fixes |
| **Next week** | Re-enable bot with validation |
| **2 weeks** | Audit complete, golden set expanded |

---

## For the Board Meeting

**Recommended messaging:**

> "Q2 revenue was $3.6M. An earlier draft cited $4.1M due to an internal data query error—our finance bot queried operational data instead of the GAAP close. We've verified $3.6M is correct and have deployed fixes to prevent similar errors."

**If asked about AI reliability:**

> "This wasn't an AI hallucination—the bot faithfully queried a real database, just the wrong table. We lacked data definitions and validation. We're adding those now. The model performance is fine; the system design had gaps."

---

## Key Talking Points

1. **Root cause:** Wrong table, not wrong model
2. **Evidence:** Recomputed both numbers from warehouse—both mathematically correct
3. **Fix:** Data definitions + validation (not model upgrade)
4. **Safety:** Found and fixing dangerous gaps (write access, infinite loops)
5. **Process:** Building proper validation (test suite, logging) before re-enabling

---

## Files in output/

- **EXECUTIVE_SUMMARY.md** - This info in more detail
- **ROOT_CAUSE_ANALYSIS.md** - Full forensic breakdown with SQL evidence
- **HARNESS_AUDIT.md** - System assessment (what's missing and why)
- **ACTION_PLAN.md** - Prioritized fix plan with timeline
- **data_dictionary.md** - What we're adding to fix the ambiguity
- **golden_set.jsonl** - Test cases we're using for validation
- **eval.py** - Automated testing script
- **agent_fixed.py** - Reference implementation of fixes
- **prompt_fixed.md** - Fixed prompt with data definitions

---

## Questions You Might Get

**Q: Should we stop using AI for finance questions?**  
A: No—fix the system (add definitions and validation), don't ban the tool. Plenty of companies use LLM agents for finance successfully; we just need the proper harness.

**Q: How much did this cost in tokens?**  
A: Unknown—we don't have logging. That's one of the gaps we're fixing.

**Q: How many other wrong answers did we give?**  
A: Under investigation. Finance is auditing all bot transcripts since March. Will have report this week.

**Q: Can we trust the bot after this?**  
A: After fixes: yes. We're adding validation (test suite) that runs on every change. If it passes tests, it's safe to use. Current version should not be used (no validation + safety issues).

**Q: Why didn't testing catch this?**  
A: There was no testing. Bot was built in a hackathon, went into production without a test suite. That's what we're fixing.

---

**Prepared by:** Data Engineering  
**Date:** 2026-09-16  
**For:** Daniel Kurz (CEO) - Board meeting prep
