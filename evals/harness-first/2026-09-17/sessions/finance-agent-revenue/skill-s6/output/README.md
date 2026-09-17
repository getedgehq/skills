# FinBot Q2 Revenue Investigation - Deliverables

**Investigation Date:** 2026-09-16  
**Incident:** FinBot reported Q2 2026 revenue as $4.1M; Finance says $3.6M  
**Question:** "Is the model hallucinating? Do we need a smarter model?"  
**Answer:** No. Wrong table, not wrong model. Fix the harness, not the model.

---

## Quick Start (for Daniel's meeting tomorrow)

**Read first:**
1. **MEETING_BRIEF.md** - Quick reference sheet for the meeting (5 min read)
2. **EXECUTIVE_SUMMARY.md** - One-page answer to "what happened?" (10 min read)

**If you need details:**
3. **SQL_COMPARISON.md** - Side-by-side showing exactly what went wrong (5 min)
4. **ROOT_CAUSE_ANALYSIS.md** - Full forensic investigation (20 min)

**For action items:**
5. **ACTION_PLAN.md** - Prioritized fix plan with timeline (15 min)

---

## All Files in This Directory

### Executive Documents
- **MEETING_BRIEF.md** - TL;DR for tomorrow's meeting with talking points
- **EXECUTIVE_SUMMARY.md** - One-pager: what happened, why, what to do
- **SQL_COMPARISON.md** - Visual side-by-side of wrong vs right query

### Investigation Reports
- **ROOT_CAUSE_ANALYSIS.md** - Complete incident investigation with evidence
- **HARNESS_AUDIT.md** - System reliability assessment (6 harness components)

### Action & Planning
- **ACTION_PLAN.md** - Prioritized fixes with owners, timeline, success metrics

### Technical Deliverables
- **data_dictionary.md** - Metric definitions for the warehouse (fixes the ambiguity)
- **golden_set.jsonl** - 10 test cases with expected answers (validation suite)
- **eval.py** - Automated test runner for golden set
- **agent_fixed.py** - Reference implementation with safety fixes
- **prompt_fixed.md** - Updated prompt with data dictionary embedded

### This File
- **README.md** - You are here

---

## Key Findings Summary

### The Numbers
- **FinBot:** $4.1M (orders table, includes cancelled/refunded)
- **Finance:** $3.6M (revenue_recognized table, GAAP net revenue)
- **Delta:** $500k (13.9% error)

### Root Cause
FinBot used the wrong database table. The prompt lists multiple tables but doesn't define "revenue."

### Why "Hallucination" Is Wrong
- Model didn't make up numbers
- Model queried a real table and got real data
- $4.1M is mathematically correct for the orders table
- This is a **semantic error** (wrong source), not a **generative error** (made-up data)

### Why Model Upgrade Won't Help
Any model would make the same mistake given the ambiguous prompt:
- Prompt says "tables you can use: orders, revenue_recognized, ..."
- Prompt doesn't say which one means "revenue"
- Model has to guess
- Different models might guess differently, but that's not "better"—it's just different guessing

**Fix:** Add data dictionary defining revenue = revenue_recognized.net_amount

### Critical Safety Issues Found
- ❌ Infinite loop (no max iterations)
- ❌ Write permissions (can DELETE/UPDATE warehouse)
- ❌ No logging (can't audit usage or cost)
- ❌ No validation (no test suite)

**These gaps are why the error happened and wasn't caught.**

---

## What To Do Next (Priority Order)

### 🔴 TODAY (Blocking)
1. Correct board deck ($3.6M, not $4.1M)
2. Disable bot until fixes deployed
3. Start auditing other bot answers for similar errors

### 🟡 THIS WEEK (Urgent)
4. Deploy 5 safety fixes (max iterations, read-only DB, logging)
5. Add data dictionary to prompt
6. Create golden set (validation suite)
7. Test fixed version

### 🟢 NEXT WEEK (Important)
8. Re-enable bot with validation
9. Complete audit of past answers
10. Expand golden set to 30+ cases
11. Add CI check (golden set runs on every change)

### 🔵 NEXT SPRINT (Nice to have)
12. Admin dashboard
13. High-stakes approval workflow
14. Prompt versioning
15. Incident response runbook

**Model upgrade evaluation:** Only AFTER fixes deployed, and only if evidence shows improvement

---

## How to Use These Files

### For the Board Meeting
```bash
# Read these in order:
1. MEETING_BRIEF.md        # Quick facts & talking points
2. SQL_COMPARISON.md        # Show the exact queries
```

### For the Data Team
```bash
# Implementation guide:
1. ACTION_PLAN.md           # What to build and when
2. agent_fixed.py           # Reference implementation
3. prompt_fixed.md          # New prompt with definitions
4. data_dictionary.md       # Add to docs/
5. golden_set.jsonl         # Add to evals/
6. eval.py                  # Add to evals/
```

### For Finance Review
```bash
# What finance needs to sign off on:
1. data_dictionary.md       # Verify metric definitions are correct
2. golden_set.jsonl         # Verify expected answers are accurate
3. SQL_COMPARISON.md        # Confirm this explains the discrepancy
```

### For Incident Report
```bash
# Complete investigation package:
1. ROOT_CAUSE_ANALYSIS.md   # Full forensic details
2. HARNESS_AUDIT.md         # System assessment
3. SQL_COMPARISON.md        # Evidence with exact queries
```

### For Model Upgrade Decision
```bash
# If someone still wants to discuss upgrading models:
1. HARNESS_AUDIT.md         # Section: "Model Upgrade Decision"
2. ACTION_PLAN.md           # Section: "Model Upgrade Evaluation"

Key point: Test current model with fixed harness FIRST.
Prediction: 100% accuracy with data dictionary, no upgrade needed.
```

---

## Technical Implementation Notes

### Golden Set Format
Each test case in `golden_set.jsonl` is a JSON object:
```json
{
  "id": "q2-2026-revenue",
  "question": "what was our Q2 2026 revenue?",
  "expected_answer": "$3,638,335.79",
  "expected_answer_numeric": 3638335.79,
  "tolerance_pct": 0.1,
  "expected_table": "revenue_recognized",
  "expected_column": "net_amount",
  "source": "incident 2026-09-14"
}
```

### Running Evaluation
```bash
# Install dependencies
pip install <whatever llm_client needs>

# Run eval (currently will fail - bot uses wrong table)
python eval.py --golden golden_set.jsonl

# After fixes deployed, should show:
# RESULTS: 10/10 passed (100.0%)
```

### Deploying Fixes
```bash
# 1. Copy fixed files to main repo
cp agent_fixed.py ../agent.py
cp prompt_fixed.md ../prompt.md
cp data_dictionary.md ../docs/

# 2. Create evals directory
mkdir ../evals
cp golden_set.jsonl ../evals/
cp eval.py ../evals/

# 3. Test locally
cd ..
python evals/eval.py --golden evals/golden_set.jsonl

# 4. Deploy (whatever your deployment process is)
```

---

## Questions & Contact

**Investigation owner:** Data Engineering team  
**Incident owner:** Jonas Feld (Data team lead)  
**Finance contact:** Marta Oyelaran (VP Finance)  
**Executive sponsor:** Daniel Kurz (CEO)

**Slack channels:**
- Technical questions → #ask-data
- Finance questions → #ask-finance (bot currently disabled)
- Incident updates → #exec-staff

---

## Appendix: Recomputing the Numbers Yourself

If you want to verify the investigation:

```bash
# Connect to warehouse
python3

>>> import sqlite3
>>> conn = sqlite3.connect('../warehouse.db')

# What FinBot said
>>> cur = conn.execute("""
...   SELECT SUM(amount) FROM orders 
...   WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30'
... """)
>>> print(cur.fetchone()[0])
4138212.16

# What Finance says
>>> cur = conn.execute("""
...   SELECT SUM(net_amount) FROM revenue_recognized 
...   WHERE period IN ('2026-04', '2026-05', '2026-06')
... """)
>>> print(cur.fetchone()[0])
3638335.79

# The difference
>>> print(4138212.16 - 3638335.79)
499876.37
```

All numbers match. Math checks out. Root cause confirmed.

---

**Last updated:** 2026-09-16  
**Status:** Investigation complete, fixes ready for implementation  
**Next review:** After fixes deployed (target: 2026-09-20)
