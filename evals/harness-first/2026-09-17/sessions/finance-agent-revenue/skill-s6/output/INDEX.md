# FinBot Investigation - Complete Deliverables Index

**Investigation completed:** 2026-09-16  
**For:** Daniel Kurz (CEO), board meeting tomorrow  
**Question asked:** "Is finbot hallucinating? Do we need a smarter model?"  
**Answer:** No hallucination. Wrong data source. Fix harness, not model.

---

## 🔴 START HERE (for tomorrow's meeting)

1. **MEETING_BRIEF.md** (165 lines)
   - TL;DR facts for the meeting
   - Talking points
   - Q&A prep
   - **Read time: 5 minutes**

2. **EXECUTIVE_SUMMARY.md** (62 lines)
   - One-page incident summary
   - Root cause in plain English
   - Clear recommendation
   - **Read time: 3 minutes**

---

## 📊 Understanding What Happened

3. **SQL_COMPARISON.md** (240 lines)
   - Side-by-side: wrong query vs right query
   - Shows exactly where $500k difference came from
   - Visual proof with actual SQL and results
   - **Read time: 10 minutes**

4. **ROOT_CAUSE_ANALYSIS.md** (233 lines)
   - Complete forensic investigation
   - Timeline, evidence, numbers recomputed
   - Why "hallucination" is wrong diagnosis
   - **Read time: 15 minutes**

5. **HARNESS_AUDIT.md** (392 lines)
   - Full system reliability assessment
   - Scores 6 components (golden set, judge, cost caps, data layer, safety, tracing)
   - Critical safety issues found
   - Why this was inevitable with current system
   - **Read time: 20 minutes**

---

## 🔧 What to Fix & How

6. **ACTION_PLAN.md** (361 lines)
   - Prioritized fixes: today → this week → next sprint → next quarter
   - Owners, timeline, success metrics
   - Blocking issues, urgent items, nice-to-haves
   - Model upgrade decision process
   - **Read time: 20 minutes**

7. **data_dictionary.md** (276 lines)
   - Defines every metric (revenue, bookings, refunds, etc.)
   - Which table/column to use for each question
   - Examples, edge cases, common patterns
   - **This fixes the root cause** (add to prompt)
   - **Read time: 15 minutes**

8. **golden_set.jsonl** (10 test cases)
   - Validation suite with expected answers
   - Includes the failing Q2 case
   - Ready to run for regression testing
   - **Format: JSONL, one case per line**

9. **eval.py** (197 lines)
   - Automated test runner (judge script)
   - Runs golden set, reports pass/fail
   - Checks numeric accuracy + SQL constraints
   - **Usage: `python eval.py --golden golden_set.jsonl`**

---

## 💻 Reference Implementations

10. **agent_fixed.py** (170 lines)
    - Fixed agent code with safety improvements
    - Max iterations, read-only DB, logging
    - Drop-in replacement for agent.py
    - **Deploy after testing**

11. **prompt_fixed.md** (61 lines)
    - Updated system prompt with data dictionary
    - Clear rules: revenue = revenue_recognized.net_amount
    - Examples of correct queries
    - **Deploy with agent_fixed.py**

---

## 📖 Navigation

12. **README.md** (265 lines)
    - Guide to using all these files
    - Quick start for different audiences (board, data team, finance)
    - How to run tests, deploy fixes, verify numbers yourself
    - **You're reading the index; that's the guide**

---

## File Summary by Purpose

### For Board Meeting / Executive Decision
```
MEETING_BRIEF.md          Quick reference + talking points
EXECUTIVE_SUMMARY.md      One-page answer
SQL_COMPARISON.md         Visual proof of what went wrong
```
**Total: 3 files, ~20 min reading**

### For Technical Understanding
```
ROOT_CAUSE_ANALYSIS.md    Complete investigation
HARNESS_AUDIT.md          System assessment
SQL_COMPARISON.md         Evidence with queries
```
**Total: 3 files, ~45 min reading**

### For Implementation
```
ACTION_PLAN.md            What to build, when, who
agent_fixed.py            Code reference
prompt_fixed.md           Prompt reference
data_dictionary.md        Metric definitions (add to docs/)
golden_set.jsonl          Test cases (add to evals/)
eval.py                   Test runner (add to evals/)
```
**Total: 6 files + README guide**

---

## Key Numbers at a Glance

| Metric | Value |
|--------|-------|
| **FinBot's answer** | $4,138,212.16 |
| **Finance's answer** | $3,638,335.79 |
| **Error amount** | $499,876.37 |
| **Error percent** | 13.9% |
| **Root cause** | Wrong table (orders vs revenue_recognized) |
| **Files delivered** | 12 files |
| **Test cases created** | 10 (golden set) |
| **Critical safety issues** | 4 (infinite loop, write access, no logging, no validation) |
| **Days to fix** | 5 days (blocking fixes by Friday) |

---

## Bottom Line

**Is the model hallucinating?**  
→ No. Model queried real data from real table. $4.1M is correct for orders table.

**Do we need a smarter model?**  
→ No. Any model would fail given ambiguous prompt. Fix data definitions first.

**What do we need?**  
→ Data dictionary (define "revenue"), validation (test suite), safety fixes (limits, read-only, logging)

**Can we trust the bot after fixing?**  
→ Yes, with validation in place. Golden set will catch regressions.

**When can we use it again?**  
→ After fixes deployed and tested (target: Friday 2026-09-20)

---

## How to Use This Package

### If you're Daniel (CEO) preparing for tomorrow:
1. Read MEETING_BRIEF.md (5 min)
2. Skim EXECUTIVE_SUMMARY.md (3 min)
3. Optional: Glance at SQL_COMPARISON.md if board asks technical questions
4. Done. You're prepared.

### If you're Jonas (Data team) implementing fixes:
1. Read ACTION_PLAN.md for priorities
2. Use agent_fixed.py and prompt_fixed.md as reference
3. Copy golden_set.jsonl and eval.py to evals/
4. Copy data_dictionary.md to docs/
5. Test with eval.py before deploying
6. Follow timeline in ACTION_PLAN.md

### If you're Marta (Finance) reviewing:
1. Read ROOT_CAUSE_ANALYSIS.md to understand what happened
2. Review data_dictionary.md - verify all definitions are correct
3. Review golden_set.jsonl - verify expected answers match your records
4. Sign off on data dictionary before deployment

### If you're the board:
1. Read EXECUTIVE_SUMMARY.md (one page)
2. Q2 revenue is $3.6M (not $4.1M as in draft)
3. Error was wrong data source, not AI hallucination
4. Fixes in progress, bot disabled until fixed

---

## Next Steps

### Immediate (today):
- [x] Investigation complete
- [ ] Board deck corrected to $3.6M
- [ ] Bot disabled in #ask-finance
- [ ] Audit of other bot answers started

### This week:
- [ ] Deploy 5 blocking fixes (see ACTION_PLAN.md)
- [ ] Test with golden set (should pass 10/10)
- [ ] Finance reviews data dictionary
- [ ] Re-enable bot

### Next sprint:
- [ ] Expand golden set to 30+ cases
- [ ] Add CI checks
- [ ] Complete audit of historical answers
- [ ] Add cost tracking

---

**Package prepared by:** Data Engineering  
**Investigation owner:** Jonas Feld  
**Exec sponsor:** Daniel Kurz  
**Finance reviewer:** Marta Oyelaran  
**Date:** 2026-09-16  
**Status:** ✅ Investigation complete, fixes ready for implementation

---

## Questions?

- Technical: #ask-data in Slack
- Finance: #ask-finance or @marta
- Incident: #exec-staff or @jonas
- Urgent: DM Daniel directly
