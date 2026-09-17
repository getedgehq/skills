Perfect! Let me create one final summary for you.

## Investigation Complete ✅

I've thoroughly investigated the FinBot Q2 revenue discrepancy and put all findings in `output/`. Here's what you need to know:

---

## **The Answer for Daniel's Meeting Tomorrow**

**❌ NOT a model problem. Don't upgrade the model.**

The model isn't hallucinating. FinBot used the wrong database table because the prompt was ambiguous. This is a **data layer problem**, not a model capability problem.

---

## **What Happened**

- **FinBot said:** $4,138,212 (Q2 revenue)
- **Finance says:** $3,638,336 (Q2 revenue)
- **Difference:** $499,876 (14% overstatement)

**Root cause:** FinBot queried the `orders` table (includes cancelled/refunded orders) instead of the `revenue_recognized` table (GAAP net revenue). The prompt said "use orders or revenue_recognized" but didn't specify which one for revenue questions.

---

## **The Fix (Ready to Deploy)**

✅ **Data dictionary** - defines which table/field for each metric  
✅ **Updated prompt** - explicit rules for revenue questions  
✅ **Loop safety** - max iterations, retry detection  
✅ **Tracing** - logs every query/answer  
✅ **Golden set** - 10 test cases to catch regressions  

**Still needed:** Manual review of past 30 days (Jonas + Marta, 1-2 days) to find other wrong answers.

---

## **All Deliverables in output/**

**For Daniel (start here):**
- `QUICK_REFERENCE.txt` - One-page cheat sheet
- `EXECUTIVE_SUMMARY.md` - 5-minute read
- `README.md` - Index of everything

**Technical:**
- `FINDINGS.md` - Full investigation with evidence
- `HARNESS_SCORECARD.md` - 6-component audit (before/after)
- `evidence.sql` - SQL queries proving both numbers

**The Fix:**
- `data_dictionary.md` - Metric definitions (THE KEY FIX)
- `prompt_fixed.md` - Updated instructions
- `agent_fixed.py` - Code with safety improvements

**Testing:**
- `evals/golden.jsonl` - 10 test cases
- `evals/run_eval.py` - Test runner

**Deployment:**
- `DEPLOYMENT_CHECKLIST.md` - Step-by-step guide
- `DELIVERABLES.txt` - Complete summary

---

## **Bottom Line**

Model is fine. Data layer was broken. Fix ready. Manual review needed (1-2 days). Then deploy and clear for use.

**Cost:** $0 to fix. Model upgrade not needed (would cost 3-5x more and fail the same way).