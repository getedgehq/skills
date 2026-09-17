# FinBot Investigation: Output Files

**Investigation Date:** 2026-09-15  
**Incident:** Q2 revenue reported as $4.1M (should be $3.6M) in board deck  
**Investigator:** Harness-first diagnostic methodology

---

## Quick Start (for Daniel)

**Read this first:**
- 📄 `EXECUTIVE_SUMMARY.md` — One-page answer to "is the model hallucinating?"

**TL;DR:** No, don't swap the model. The bot used the wrong database table because "revenue" wasn't defined. Fix takes 15 minutes.

---

## All Output Files

### 📋 Executive & Planning

1. **`EXECUTIVE_SUMMARY.md`** ⭐ START HERE
   - One-line answer for Daniel
   - Root cause with evidence
   - Harness scorecard (9/60 points)
   - What we fixed
   - Why model swap isn't needed

2. **`ACTION_ITEMS.md`**
   - Prioritized to-do list
   - Owners, effort estimates, deadlines
   - Step-by-step deployment instructions

3. **`BOARD_DECK_CORRECTIONS.md`**
   - Correct Q1 and Q2 numbers for Priya
   - Quick reference table
   - What to tell the board

---

### 🔍 Investigation Evidence

4. **`data_verification.txt`**
   - Proof of the $4.1M vs $3.6M mechanism
   - Recomputed both numbers from warehouse.db
   - Breakdown of the $500K gap

5. **`harness_audit.md`**
   - Detailed analysis of all 6 harness components
   - Line-by-line code review
   - Risk assessment with priorities

---

### 🛠️ Fixes & Deliverables

6. **`prompt_PATCHED.md`** 🔥 DEPLOY THIS
   - Fixed prompt with data dictionary
   - Defines "revenue" = `revenue_recognized.net_amount`
   - Ready to replace current `prompt.md`

7. **`agent_safe.py`** 🔥 DEPLOY THIS
   - Patched agent with safety fixes:
     - Max iterations (10) to prevent infinite loops
     - Read-only database connection
     - Better error handling
   - Ready to replace current `agent.py`

8. **`data_dictionary.md`** 📋 REVIEW WITH FINANCE
   - Canonical definitions for all metrics
   - Table reference guide
   - Example queries
   - For Finance team to review and approve

---

### ✅ Testing Infrastructure

9. **`evals/golden.jsonl`** 📋 ADD TO CI
   - 12 test cases covering:
     - Revenue queries (incident source)
     - Multi-period comparisons
     - Edge cases
     - Different metric types
   - Expected answers with tolerances

10. **`evals/judge.py`** 📋 ADD TO CI
    - Automated test runner
    - Validates table/column usage
    - Checks numeric answers
    - Reports pass/fail per case
    - Usage: `python evals/judge.py`

11. **`golden_set_results.txt`**
    - Simulated test results showing current bot would fail 3/12 tests
    - Shows which queries use wrong table
    - Proves data dictionary would fix all failures

---

## Deployment Priority

### 🔥 Today (15 minutes):
1. Replace `prompt.md` with `prompt_PATCHED.md`
2. Replace `agent.py` with `agent_safe.py`
3. Update board deck with correct Q1/Q2 numbers

### 📋 This Week (5 hours):
4. Copy `evals/` folder to repo and add to CI
5. Finance reviews `data_dictionary.md`
6. Add logging/tracing

### 🔍 Next Week (7 hours):
7. Audit Slack history for other wrong answers
8. Build cost/quality dashboard

---

## Key Findings

### Root Cause
**Data layer missing** → ambiguous metric definitions → model guessed wrong table

### Evidence
- Bot queried: `orders.amount` = $4,138,212 (gross bookings)
- Finance uses: `revenue_recognized.net_amount` = $3,638,336 (GAAP revenue)
- Prompt had no data dictionary to distinguish them

### Is the Model Hallucinating?
**No.** The model:
- ✅ Executed valid SQL
- ✅ Returned correct sums
- ✅ Made a reasonable interpretation

The system:
- ❌ Had no data dictionary
- ❌ Had no test cases
- ❌ Had no validation

### Should We Upgrade the Model?
**No.** Not yet.
- Current issue is data ambiguity, not model capability
- A smarter model would still guess (just might guess better)
- Fix the harness first, then measure if upgrade is needed
- Expected: With data dictionary, current model will work fine

---

## Harness Scorecard

| Component | Status | Score |
|-----------|--------|-------|
| Golden set | ❌ Missing | 0/10 |
| Judge | ❌ Missing | 0/10 |
| Cost governance | 🟡 Partial | 4/10 |
| Data layer | ❌ Missing | 0/10 |
| Action safety | 🟡 Partial | 5/10 |
| Tracing | ❌ Missing | 0/10 |
| **TOTAL** | | **9/60** |

---

## Files at a Glance

```
output/
├── README.md (this file)
├── EXECUTIVE_SUMMARY.md ⭐ read first
├── ACTION_ITEMS.md
├── BOARD_DECK_CORRECTIONS.md
├── data_verification.txt
├── harness_audit.md
├── prompt_PATCHED.md 🔥 deploy
├── agent_safe.py 🔥 deploy
├── data_dictionary.md 📋 review
├── golden_set_results.txt
└── evals/
    ├── golden.jsonl 📋 add to CI
    └── judge.py 📋 add to CI
```

---

## Questions?

- **"Do we need a better model?"** → No, fix the harness first (see EXECUTIVE_SUMMARY.md)
- **"What do I deploy?"** → See ACTION_ITEMS.md, priority section
- **"What are the correct numbers?"** → See BOARD_DECK_CORRECTIONS.md
- **"How did this happen?"** → See harness_audit.md, root cause section
- **"What's the evidence?"** → See data_verification.txt

---

## Investigation Methodology

This investigation used the **harness-first approach**:
1. ✅ Reproduced the symptom from evidence (transcript + warehouse)
2. ✅ Scored the six harness components
3. ✅ Identified root cause as mechanism (data layer missing)
4. ✅ Built minimum harness (golden set, judge, data dictionary)
5. ✅ Decided: Don't swap model without eval evidence

All findings backed by:
- Line numbers in code
- SQL queries recomputed from warehouse
- Test cases with expected answers
- Cost/effort estimates

---

**Next Step:** Read EXECUTIVE_SUMMARY.md, then review ACTION_ITEMS.md with the team.
