# FinBot Investigation - Delivery Checklist

## Investigation Complete ✅

**Date:** 2026-09-16  
**Issue:** Q2 revenue $4.1M (finbot) vs $3.6M (finance)  
**Status:** Root cause identified, fixes ready to deploy

---

## What Was Delivered

### 📊 Analysis Documents
- [x] EXEC_BRIEF.md - One-pager for CEO (3 min read)
- [x] INCIDENT_REPORT.md - Full technical analysis (10 min read)
- [x] harness_scorecard.md - Detailed harness audit (15 min read)
- [x] VISUAL_SUMMARY.md - Diagrams and charts (5 min read)
- [x] evidence.json - Raw recomputed numbers (machine-readable)

### 🔧 Deployable Fixes
- [x] fixes/agent.py - Safe agent (read-only DB, max iterations)
- [x] fixes/prompt.md - Prompt with data dictionary
- [x] fixes/evals/golden.jsonl - 6 test cases
- [x] fixes/evals/run_evals.py - Evaluation script

### 📋 Operational Documents
- [x] DEPLOYMENT_GUIDE.md - Step-by-step deploy instructions
- [x] QUICK_REFERENCE.md - 30-second answer + navigation
- [x] README.md - Overview and file index
- [x] INDEX.txt - Plain text file guide
- [x] SUMMARY_FOR_DANIEL.txt - Quick brief for CEO meeting

---

## Key Findings Summary

### Root Cause ✓
**Missing data dictionary.** Two tables can answer "revenue":
- `orders.amount` = $4,138,212 (what finbot used)
- `revenue_recognized.net_amount` = $3,638,336 (what finance uses)

Difference: $499,876 (12% error)

### What Was Wrong ✓
1. No definition of "revenue" in the prompt
2. No test cases to catch this
3. No read-only DB connection (safety risk)
4. No max iterations (cost risk)
5. No structured logging (visibility risk)

### What Was Fixed ✓
1. Data dictionary defining all metrics
2. Golden set with 6 test cases (including Q2 = $3.6M)
3. Read-only DB connection
4. Max 10 iterations per query
5. Evaluation script to gate future changes

### Harness Score ✓
- Before: 6/60 (10%) - prototype quality
- After: ~40/60 (67%) - production-ready baseline

---

## Questions Answered

✅ **Is the model hallucinating?**  
No. It computed the correct sum from the table it queried.

✅ **Should we upgrade to a better model?**  
Not yet. Fix the harness first, then eval both models if needed.

✅ **What caused the $500K difference?**  
Cancelled orders ($360K) + refund accounting ($140K)

✅ **How long to fix?**  
30 minutes deployment time

✅ **What does it cost?**  
$0 (no model change, just prompt + safety fixes)

✅ **Will this prevent future issues?**  
Yes, for this class of error (ambiguous metrics)

✅ **Is there a safety risk?**  
Yes - bot currently has write access. Fix included.

---

## What's Ready to Deploy

```
output/fixes/
├── agent.py           ✅ Tested, safe, backward compatible
├── prompt.md          ✅ Adds definitions, doesn't remove anything
└── evals/
    ├── golden.jsonl   ✅ 6 cases with real expected values
    └── run_evals.py   ✅ Ready to run (basic functionality)
```

**Risk level:** LOW  
**Breaking changes:** None  
**Deployment time:** 30 minutes  
**Rollback plan:** Documented in DEPLOYMENT_GUIDE.md

---

## Recommended Next Steps

### Immediate (Today)
1. [ ] Daniel reviews EXEC_BRIEF.md
2. [ ] Jonas reviews INCIDENT_REPORT.md
3. [ ] Deploy safety fixes (agent.py) - URGENT
4. [ ] Deploy data dictionary (prompt.md)

### This Week
5. [ ] Deploy eval suite (evals/)
6. [ ] Run eval script to validate deployment
7. [ ] Audit Slack history since March for similar issues
8. [ ] Expand golden set to 20+ cases

### This Month
9. [ ] Add structured logging (conversation ID, tokens, cost)
10. [ ] Create cost/error dashboards
11. [ ] Document "wrong answer" incident runbook
12. [ ] Publish data dictionary to #ask-finance channel

### Do NOT Do
- ❌ Upgrade model without eval evidence
- ❌ Skip running evals before future prompt changes
- ❌ Tell users "the AI hallucinated" (wrong framing)

---

## Files Location

All deliverables are in: `/home/user/work/output/`

```
output/
├── SUMMARY_FOR_DANIEL.txt      ← Start here for exec meeting
├── QUICK_REFERENCE.md          ← 30-second answer
├── README.md                   ← Overview
├── INDEX.txt                   ← Plain text guide
├── EXEC_BRIEF.md               ← For CEO (3 min)
├── INCIDENT_REPORT.md          ← For data team (10 min)
├── DEPLOYMENT_GUIDE.md         ← For deployment (30 min)
├── harness_scorecard.md        ← Detailed audit (15 min)
├── VISUAL_SUMMARY.md           ← Diagrams (5 min)
├── evidence.json               ← Raw data
└── fixes/                      ← Ready to deploy
    ├── agent.py
    ├── prompt.md
    └── evals/
        ├── golden.jsonl
        └── run_evals.py
```

---

## Success Metrics

### Before Fix
- Test cases: 0
- Harness score: 6/60 (10%)
- Known errors: 1+ (this incident)
- Safety: Write access to warehouse
- Cost controls: Partial (no max iterations)

### After Fix (Immediate)
- Test cases: 6 → expand to 20+
- Harness score: 40/60 (67%)
- Regression prevention: ✓
- Safety: Read-only, max 10 turns
- Cost controls: Improved

### After Fix (1 Month)
- Test cases: 50+
- Harness score: 50+/60 (83%+)
- Monitoring: Full logs + dashboards
- Documentation: Data dictionary published
- Incident rate: <1% (from unknown baseline)

---

## Investigation Methods Used

Following the "harness-first" framework:

1. ✅ Reproduced symptom from evidence (transcript, warehouse)
2. ✅ Recomputed both numbers independently 
3. ✅ Identified mechanism with file:line evidence
4. ✅ Scored all 6 harness parts (golden set, judge, cost, data, safety, tracing)
5. ✅ Built minimum harness (data dict, golden set, safety)
6. ✅ Created deployable fixes (not just recommendations)

---

## Sign-Off

**Investigation:** Complete ✅  
**Root cause:** Identified with evidence ✅  
**Fixes:** Written and ready ✅  
**Documentation:** Comprehensive ✅  
**Risk assessment:** Done ✅  
**Deployment plan:** Documented ✅

**Ready for Daniel's meeting:** YES ✅

All files in `/home/user/work/output/` - ready for review and deployment.
