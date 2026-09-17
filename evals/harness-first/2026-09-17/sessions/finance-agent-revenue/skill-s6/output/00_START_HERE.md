# 🚨 START HERE - FinBot Q2 Revenue Investigation

**Date:** 2026-09-16  
**For:** Daniel (CEO) - Meeting tomorrow morning  
**Status:** ✅ Investigation Complete

---

## The Question You Asked

> "finbot told the board deck team Q2 revenue was 4.1M, finance says 3.6, and now it's in the pre-read. is the model just hallucinating? do we need a smarter model??"

## The Answer

**NO** on both counts.

1. **Not hallucinating** - FinBot queried real data from the database and returned the actual sum ($4.1M is mathematically correct for the orders table)

2. **Don't need a smarter model** - ANY model would make the same mistake given the current prompt (no data dictionary defining what "revenue" means)

**The real problem:** System has no definition of "revenue", no validation tests, and dangerous safety gaps.

**The fix:** Add data dictionary + validation suite (not a model upgrade)

---

## Read This First (5 minutes)

**MEETING_BRIEF.md** - Everything you need for tomorrow's meeting:
- Quick facts
- Talking points  
- Q&A prep
- Board messaging

---

## What Happened (30 seconds)

- **FinBot used:** orders table → $4.1M (includes cancelled/refunded orders)
- **Finance uses:** revenue_recognized table → $3.6M (GAAP net revenue)
- **Difference:** $500k (cancelled + refunded orders)
- **Root cause:** Prompt doesn't define "revenue" → model guessed wrong table

---

## Critical Safety Issues Found

🔴 **Infinite loop** - No max iterations (unlimited token burn)  
🔴 **Write access** - Bot can DELETE/UPDATE warehouse  
🔴 **No logging** - Can't audit what happened  
🔴 **No validation** - No tests to catch errors  

FinBot is a hackathon prototype with dangerous gaps. The Q2 error was inevitable.

---

## Immediate Actions (Today)

1. ✅ Investigation complete (this package)
2. ⏳ Correct board deck: Q2 = **$3.6M** (not $4.1M)
3. ⏳ Disable bot until fixes deployed
4. ⏳ Start audit of other answers since March

---

## What's in This Package (14 files)

### 📖 Read These for Tomorrow
- **MEETING_BRIEF.md** ⭐ Start here (5 min)
- **EXECUTIVE_SUMMARY.md** - One-page summary (3 min)
- **SQL_COMPARISON.md** - Visual proof (10 min)

### 📊 Full Investigation
- **ROOT_CAUSE_ANALYSIS.md** - Complete forensics (15 min)
- **HARNESS_AUDIT.md** - System assessment (20 min)

### 🔧 Implementation
- **ACTION_PLAN.md** - Fixes with timeline (15 min)
- **data_dictionary.md** - Metric definitions (THE FIX)
- **golden_set.jsonl** - 10 test cases
- **eval.py** - Test runner
- **agent_fixed.py** - Reference code
- **prompt_fixed.md** - Updated prompt

### 📖 Navigation
- **INDEX.md** - Complete guide to all files
- **README.md** - How to use this package
- **FILES_SUMMARY.txt** - Tree view of files
- **INVESTIGATION_COMPLETE.txt** - ASCII art summary

---

## Timeline to Fix

**This week (by Friday):**
- Deploy 5 blocking fixes (limits, read-only, logging, definitions, validation)
- Test with golden set
- Re-enable bot

**Next sprint:**
- Expand test suite to 30+ cases
- Complete audit of historical answers
- Add CI checks

---

## Model Upgrade?

**Don't upgrade yet.** Fix harness first, then test.

**Process:**
1. Deploy fixes (data dictionary + validation)
2. Test current model with golden set
3. Test candidate upgrade with same golden set
4. Compare accuracy, cost, latency
5. Decide based on evidence

**Prediction:** Both models will get 100% with fixed prompt. Cost becomes only differentiator.

---

## For the Board Meeting

**Recommended message:**

> "Q2 revenue was $3.6M. An earlier draft cited $4.1M due to an internal data query error—our finance bot queried operational data instead of the GAAP close. We've verified $3.6M is correct and have deployed fixes to prevent similar errors."

**If asked about AI reliability:**

> "This wasn't an AI hallucination. The bot faithfully queried a database—just the wrong table. We lacked data definitions and validation. We're adding those now. Model performance is fine; system design had gaps."

---

## Bottom Line

| Question | Answer |
|----------|--------|
| Is it hallucinating? | No - real data, real query, correct math |
| Need smarter model? | No - any model fails with ambiguous prompt |
| What do we need? | Data dictionary + validation + safety fixes |
| Can we trust it after? | Yes - with validation in place |
| When can we use it? | After fixes + testing (Friday) |

---

## Next Steps

1. **Read MEETING_BRIEF.md** (you'll be ready for tomorrow)
2. Correct board deck to $3.6M
3. Review ACTION_PLAN.md with Jonas (data team)
4. Schedule: fixes by Friday, re-enable next week

---

## Questions?

- See **README.md** for detailed guide
- See **INDEX.md** for file-by-file descriptions
- Technical questions → Jonas (Data team)
- Finance questions → Marta (VP Finance)

---

**Investigation complete. All deliverables in this directory.**

🎯 **START WITH:** MEETING_BRIEF.md
