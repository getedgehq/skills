# FinBot Q2 Revenue Investigation - Output

**Investigation Date:** 2026-09-16  
**Issue:** FinBot reported Q2 revenue as $4.1M, Finance close is $3.6M

---

## Quick Start

**For Daniel (CEO):** Read `EXEC_BRIEF.md`

**For Jonas (Data Team):** Read `INCIDENT_REPORT.md` then deploy `fixes/`

**For Marta (Finance):** See `evidence.json` for the recomputed numbers

---

## Files in This Directory

### Executive Summary
- **`EXEC_BRIEF.md`** - One-pager for Daniel explaining root cause and fix (no jargon)

### Technical Analysis  
- **`INCIDENT_REPORT.md`** - Full root cause analysis with evidence, mechanism, and harness audit
- **`harness_scorecard.md`** - Detailed scoring of all 6 harness components (golden set, judge, cost caps, data layer, safety, tracing)
- **`evidence.json`** - Raw recomputed numbers from both tables

### Deployable Fixes
- **`fixes/agent.py`** - Fixed agent code (read-only DB, max iterations)
- **`fixes/prompt.md`** - New prompt with full data dictionary
- **`fixes/evals/golden.jsonl`** - 6 test cases with expected answers
- **`fixes/evals/run_evals.py`** - Evaluation script to run before deployments

---

## The Core Issue

**Not a model problem. Not hallucination. Missing data dictionary.**

FinBot queried `orders.amount` (includes cancelled orders, doesn't net refunds).  
Finance closed `revenue_recognized.net_amount` (GAAP net revenue).

Both numbers are correct from their source. The model had no guidance on which table "revenue" means.

---

## What to Deploy

### Priority 1: Blocking Risks (deploy today)
1. `fixes/agent.py` - prevents data corruption (read-only mode) and runaway costs (max turns)

### Priority 2: Fix the Incident (deploy this week)
2. `fixes/prompt.md` - defines "revenue" and all metrics  
3. `fixes/evals/golden.jsonl` - test cases to prevent regressions
4. `fixes/evals/run_evals.py` - run before any future prompt/model changes

### Priority 3: Visibility (deploy this month)
5. Add structured logging (conversation ID, tokens, cost, queries)
6. Create dashboards for cost and error monitoring

---

## How to Deploy

```bash
# 1. Backup current files
cp agent.py agent.py.backup
cp prompt.md prompt.md.backup

# 2. Deploy fixes
cp fixes/agent.py ../agent.py
cp fixes/prompt.md ../prompt.md
cp -r fixes/evals ../evals

# 3. Test with golden set (requires agent environment)
cd evals
python run_evals.py

# 4. If tests pass, restart the Slack bot
# (your deployment process here)
```

---

## Key Findings

### Root Cause
**Missing data dictionary.** Two tables can answer "revenue":
- `orders.amount` = $4,138,212 (FinBot's choice)
- `revenue_recognized.net_amount` = $3,638,336 (Finance's close)

Difference: $499,876 (12% error, includes $360K cancelled orders)

### Harness Score: 6/60 (10%)
- ❌ No golden set, no judge, no tracing
- ⚠️ Partial cost governance (no max iterations)
- ⚠️ Unsafe (write access on read path)
- ❌ No data dictionary

### Model Quality
**The model is working correctly.** It faithfully executed a reasonable query. Upgrading to a better/more expensive model would not fix this bug.

---

## Questions Answered

**"Is the model hallucinating?"**  
No. It computed the correct sum from the table it queried. The table was wrong for this use case.

**"Should we upgrade to a better model?"**  
Not yet. Fix the harness first, then run evals on both models to compare quality and cost with evidence.

**"What if we had deployed this in March?"**  
This bug has been live since March (hackathon). Need to audit all Slack threads for similar issues.

**"How do we prevent this?"**  
Run `evals/run_evals.py` before deploying any prompt, model, or tool changes. The Q2 revenue test case would have caught this.

---

## Next Steps

### Immediate (today)
- [ ] Review fixes with Jonas
- [ ] Deploy agent.py (safety)
- [ ] Deploy prompt.md (data dictionary)

### This Week  
- [ ] Expand golden set to 20+ cases from Slack history
- [ ] Set up eval CI job (block deployments if tests fail)
- [ ] Audit Slack since March for other wrong answers

### This Month
- [ ] Add structured logging
- [ ] Cost/error dashboards
- [ ] Document runbook for "FinBot gave wrong answer" incidents

### Do NOT Do
- ❌ Switch models without eval evidence
- ❌ Tell users "the AI made a mistake" (we made an infrastructure mistake)
- ❌ Add more tables/tools without updating the data dictionary

---

## Contact

**Investigation by:** AI Assistant  
**Owner:** Data team (Jonas)  
**Stakeholders:** Daniel (CEO), Marta (Finance), Priya (Strategy)

For questions about this analysis or the fixes, contact the data team.
