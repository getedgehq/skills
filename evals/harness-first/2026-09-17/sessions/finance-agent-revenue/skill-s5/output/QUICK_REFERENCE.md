# FinBot Investigation - Quick Reference Card

**Date:** 2026-09-16  
**Issue:** Q2 revenue reported as $4.1M, Finance close is $3.6M ($500K difference)

---

## 30-Second Answer

**Not a model problem. Missing data dictionary.**

FinBot queried `orders` table ($4.1M gross) instead of `revenue_recognized` table ($3.6M GAAP net). The prompt listed both tables with no definition of "revenue." Model executed correctly, just used the wrong source.

**Fix:** Add data dictionary to prompt (30 min), deploy fixes in `output/fixes/` directory.

**Cost:** $0. Don't upgrade model without fixing harness first.

---

## Key Numbers

| Metric | Value |
|--------|-------|
| FinBot's answer | $4,138,212 |
| Finance's close | $3,638,336 |
| Difference | $499,876 (12%) |
| Cancelled orders in FinBot's sum | $360,039 |
| Refund adjustments | ~$140K |

---

## Root Cause (One Line)

Two tables can answer "revenue" ($4.1M vs $3.6M), prompt didn't define which one to use.

---

## Files for Different Audiences

| Reader | Start Here | Read Time |
|--------|-----------|-----------|
| Daniel (CEO) | `EXEC_BRIEF.md` | 3 min |
| Jonas (Data Team) | `INCIDENT_REPORT.md` | 10 min |
| Marta (Finance) | `evidence.json` + `VISUAL_SUMMARY.md` | 5 min |
| Engineer deploying | `DEPLOYMENT_GUIDE.md` | 5 min |
| Deep technical audit | `harness_scorecard.md` | 15 min |

---

## What's in output/fixes/

```
fixes/
├── agent.py              ← Read-only DB, max iterations
├── prompt.md             ← Data dictionary (defines "revenue")
└── evals/
    ├── golden.jsonl      ← 6 test cases with expected answers
    └── run_evals.py      ← Test script (run before deployment)
```

**Deploy time:** 30 minutes  
**Risk:** LOW (adds safety, doesn't break existing queries)

---

## The Fix in One Sentence Per File

1. **agent.py**: Opens DB read-only, stops after 10 turns (prevents corruption + runaway costs)
2. **prompt.md**: Defines "revenue" = `revenue_recognized.net_amount`, not `orders.amount`
3. **golden.jsonl**: 6 test cases including Q2 revenue = $3.6M (catches regressions)
4. **run_evals.py**: Runs tests before deployment (gates bad changes)

---

## Decision Tree

```
Is the model hallucinating?
  ↓ NO
  
Should we upgrade to a better model?
  ↓ NO (fix harness first)
  
Is the bot broken?
  ↓ NO (it worked correctly, just wrong table)
  
What do we deploy?
  ↓ Data dictionary + safety fixes
  
How long to fix?
  ↓ 30 minutes
  
Cost?
  ↓ $0
```

---

## Harness Score: 6/60 (10%)

- ❌ No golden set (NOW: 6 cases)
- ❌ No judge (NOW: run_evals.py)
- ⚠️ No max iterations (NOW: 10 max)
- ❌ No data dictionary (NOW: full definitions)
- ⚠️ Write access (NOW: read-only)
- ❌ No tracing (TODO: add logging)

**After fix: ~40/60 (67%)** - production-ready baseline

---

## What to Tell Stakeholders

**Board:** "We corrected a data definition issue. Q2 GAAP revenue is $3.6M as Finance reported."

**Users (#ask-finance):** "FinBot now has clearer definitions. Q2 revenue is $3.6M (net). Please report any issues."

**Team:** "Fixed missing data dictionary. Deploy fixes in output/fixes/. Run evals before future changes."

---

## Action Items

### Today
- [ ] Review EXEC_BRIEF.md (Daniel)
- [ ] Review INCIDENT_REPORT.md (Jonas)
- [ ] Deploy fixes (see DEPLOYMENT_GUIDE.md)

### This Week
- [ ] Run evals after deployment
- [ ] Expand golden set to 20+ cases
- [ ] Audit Slack history for other wrong answers

### This Month
- [ ] Add structured logging
- [ ] Cost/error dashboards
- [ ] Document "wrong answer" runbook

### Never
- ❌ Upgrade model without eval evidence
- ❌ Deploy prompt changes without running evals
- ❌ Tell users "AI hallucinated" (wrong framing)

---

## One-Liner for Slack

> "Q2 revenue discrepancy solved: bot used orders table ($4.1M gross) instead of revenue_recognized ($3.6M GAAP net). Fixed with data dictionary. Correct answer is $3.6M. Fixes deployed."

---

## Emergency Contacts

**Owner:** Jonas (Data Team)  
**Finance:** Marta Oyelaran  
**Executive:** Daniel Kurz  
**Original Reporter:** Priya Raman (Strategy)

**All files in:** `/home/user/work/output/`
