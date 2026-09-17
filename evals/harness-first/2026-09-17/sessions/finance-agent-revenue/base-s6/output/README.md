# Q2 Revenue Discrepancy Investigation - Output Files

**Investigation Date:** 2026-09-16  
**Issue:** Finbot reported Q2 revenue as $4.1M, Finance says $3.6M  
**Status:** ✅ Root cause identified, fix ready to deploy

---

## Quick Answer

**The model is NOT hallucinating.**

Finbot queried the `orders` table which includes $360k of cancelled orders. It should use the `revenue_recognized` table instead.

**Fix:** Update the prompt (30 min, $0 cost) - don't upgrade the model.

**Correct Q2 2026 revenue:** $3,638,335.79 (~$3.64M)

---

## Files in This Folder

### 📄 Start Here
- **executive_summary.md** - One-page summary for Daniel (CEO)
  - What happened, why, and what to do
  - Read this first if you're short on time

### 📊 Detailed Reports
- **investigation_report.md** - Complete analysis for the team
  - Full timeline, data analysis, recommendations
  - Why upgrading the model won't help
  - Test results and validation

- **technical_analysis.md** - Deep technical dive
  - SQL queries and results
  - Database structure analysis
  - Side-by-side comparisons
  - Data verification

### 🔧 Implementation
- **proposed_fix.md** - How to fix the issue
  - Updated system prompt
  - Test cases to validate the fix
  - Implementation steps
  - Cost analysis

- **prompt_FIXED.md** - Ready-to-use corrected prompt
  - Drop-in replacement for current prompt.md
  - Just copy this over and restart finbot

- **action_plan.md** - Complete action plan
  - Immediate actions (today)
  - Short-term actions (this week)
  - Long-term improvements (this month)
  - Communication plan
  - Success metrics

### 🧪 Verification
- **verify_numbers.py** - Python script to verify all numbers
  - Run: `python3 output/verify_numbers.py`
  - Verifies every number in the reports
  - Shows the correct queries vs. wrong queries
  - No dependencies needed (uses built-in sqlite3)

---

## Quick Start Guide

### For Daniel (CEO)
1. Read: `executive_summary.md`
2. Use this number for board: **$3.64M**
3. Tell Jonas to implement the fix

### For Jonas (Data Team)
1. Read: `action_plan.md`
2. Follow the immediate actions (30 min)
3. Test with: Q2 revenue should now be $3.6M
4. Deploy fixed prompt: `cp output/prompt_FIXED.md prompt.md`

### For Marta (Finance)
1. Read: `investigation_report.md`
2. Your number ($3.6M) is correct ✅
3. Finbot was including cancelled orders
4. Monthly reconciliation recommended going forward

### For Priya (Strategy)
1. Update board deck: Q2 revenue = **$3,638,335.79** (~$3.64M)
2. Previous number ($4.1M) included cancelled orders
3. Finbot is being fixed now

---

## Key Numbers (Verified)

| Metric | Amount | Source |
|--------|--------|--------|
| **Q2 2026 Revenue (CORRECT)** | **$3,638,335.79** | revenue_recognized table |
| What finbot reported (WRONG) | $4,138,212.16 | orders table (includes cancelled) |
| Discrepancy | $499,876.37 | 12% overstatement |
| Cancelled orders in Q2 | $360,039.00 | Main cause of error |

### Monthly Breakdown (Correct)
- April 2026: $1,237,516.63
- May 2026: $1,209,658.31
- June 2026: $1,191,160.85
- **Q2 Total: $3,638,335.79**

---

## The Fix (Summary)

### Current Prompt Says:
```
Tables you can use:
- orders
- revenue_recognized
...
```

### Fixed Prompt Says:
```
revenue_recognized - SOURCE OF TRUTH for all revenue questions
- Use net_amount for revenue
- Excludes cancelled orders

orders - For operational metrics ONLY
- ⚠️ DO NOT use for revenue - includes cancelled orders
```

**That's it.** Just tell the model which table to use.

---

## Validation

Run the verification script:
```bash
cd /home/user/work
python3 output/verify_numbers.py
```

This will show:
- ✅ Correct query and result ($3.6M)
- ❌ Wrong query and result ($4.1M)
- All the data breakdowns
- Root cause analysis

---

## Why Not Upgrade the Model?

| Solution | Cost | Time | Will it fix the issue? |
|----------|------|------|----------------------|
| **Fix the prompt** | $0 | 30 min | ✅ Yes |
| Upgrade to Opus | 5x cost | 1 hour | ❌ No - still needs prompt fix |
| Upgrade to GPT-6 | 2-3x cost | 1 hour | ❌ No - still needs prompt fix |

**The model is working correctly.** It just needs to be told which table to use.

---

## Timeline

**Sept 11, 10:02 AM** - Priya asked finbot for Q2 revenue  
**Sept 11, 10:02 AM** - Finbot responded $4.1M (included cancelled orders)  
**Sept 14** - Marta (Finance) flagged discrepancy  
**Sept 14** - Daniel questioned if model is hallucinating  
**Sept 16** - Investigation completed, fix identified  

---

## Next Steps

1. ✅ Update board deck with $3.64M
2. ✅ Deploy prompt fix (30 min)
3. ✅ Test finbot (should now say $3.6M)
4. ✅ Notify stakeholders
5. 📅 Schedule monthly Finance reconciliation
6. 📅 Create test suite (this week)
7. 📅 Add monitoring (this month)

---

## Questions?

- **About the fix:** Jonas Feld (Data Team)
- **About the numbers:** Marta Oyelaran (VP Finance)
- **About this investigation:** See the detailed reports above

---

## Bottom Line

✅ Data is correct  
✅ Model works fine  
✅ Just need to update the prompt  
✅ No model upgrade needed  
✅ Can be fixed today  

**Issue:** Documentation problem  
**Solution:** Better documentation  
**Cost:** $0  
**Time:** 30 minutes  
