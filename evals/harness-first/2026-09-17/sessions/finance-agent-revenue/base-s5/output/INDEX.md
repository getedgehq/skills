# FinBot Q2 Revenue Discrepancy - Investigation Files

**Issue:** FinBot reported Q2 revenue as $4.1M, Finance says $3.6M  
**Status:** ✅ Root cause identified, fix ready to deploy  
**Date:** September 16, 2026

---

## 🚀 START HERE

**For Daniel (CEO):** Read `executive_summary.md`  
**For Jonas (Data):** Read `action_plan_jonas.md`  
**For everyone else:** Read `root_cause_analysis.md`

---

## 📄 Files in This Directory

### 1. **README.txt**
Plain text overview of the issue and files.

### 2. **executive_summary.md** 
One-page summary for Daniel.
- Bottom line: Not a model problem, simple prompt fix
- No need for expensive model upgrade
- 5-minute fix available

### 3. **root_cause_analysis.md**
Complete analysis with context and recommendations.
- What happened and why
- The three different revenue numbers in the warehouse
- Why this isn't a hallucination/model issue
- Recommended actions for all teams

### 4. **technical_analysis.md**
Deep dive into the database and queries.
- Exact queries finbot ran vs. what it should run
- Breakdown of Q2 orders by status
- Comparison of all three revenue tables
- Sample data and verification queries

### 5. **visual_comparison.md**
Side-by-side comparison of wrong vs. right approach.
- What finbot did (wrong)
- What finance does (correct)
- The $500K gap explained
- Before/after the fix

### 6. **prompt_UPDATED.md** ⭐
Ready-to-deploy fixed system prompt.
- Clear guidance on which tables to use
- Examples of correct queries
- Warnings about common mistakes
- Jonas can deploy this immediately

### 7. **action_plan_jonas.md**
Step-by-step deployment and follow-up plan.
- Immediate fix (today)
- This week's tasks
- Long-term improvements
- Success metrics

### 8. **validation_tests.py**
Python script to verify finbot gives correct answers.
- Tests Q2 revenue, Q1 revenue, bookings, etc.
- Run from parent directory: `python3 output/validation_tests.py`
- Use after deploying prompt update

---

## 🔍 The Issue in 30 Seconds

**What happened:**
- Priya asked finbot for Q2 revenue
- FinBot said $4.1M (from `orders` table)
- Finance says $3.6M (from `revenue_recognized` table)
- $500K difference went into the board deck

**Root cause:**
- System prompt didn't specify which table to use
- Model reasonably (but wrongly) chose `orders` table
- That table includes refunded/cancelled orders

**The fix:**
- Update prompt to say "use revenue_recognized for revenue questions"
- 5-minute deployment
- No model upgrade needed

---

## ✅ Key Findings

1. **Model is NOT hallucinating** - It reported real data from the database
2. **Model is NOT broken** - It wrote correct SQL and executed properly
3. **No need for expensive model** - GPT-6/Opus would make the same mistake
4. **Simple prompt fix** - Just needed clearer instructions
5. **Systemic issue** - Warehouse has 3 different "revenue" numbers

---

## 📊 The Numbers

| Source | Q2 2026 Amount | What It Represents |
|--------|----------------|-------------------|
| **FinBot** | $4,138,212 | Gross bookings (includes cancelled/refunded) |
| **Finance** | $3,638,336 | GAAP revenue (net of refunds) ✅ |
| **Difference** | $499,876 | Refunded + cancelled orders |

---

## 🎯 Next Steps

**Immediate (Today):**
1. Jonas deploys `prompt_UPDATED.md`
2. Run `validation_tests.py` to verify
3. Test with sample questions

**This Week:**
1. Add query logging
2. Document table purposes  
3. Create verification process

**Long-term:**
1. Automated testing
2. Query templates
3. Monitoring/alerts

---

## 📞 Questions?

All analysis based on:
- `warehouse.db` - 2,213 orders in Q2 2026
- `transcripts/2026-09-11_board-deck.md` - Original finbot conversation
- `notes/slack-exec-thread.txt` - Executives discovering the issue
- `agent.py`, `prompt.md`, `config.py` - FinBot code

**The root cause is clear and the fix is simple.**

---

## 🧪 Testing the Fix

After deploying the updated prompt:

```bash
# From the repository root
python3 output/validation_tests.py
```

Expected output:
```
✅ Q2 2026 Revenue: $3,638,335.79 PASS
✅ Q1 2026 Revenue: $3,285,493.84 PASS
✅ Q2 2026 Bookings: $4,138,212.16 PASS
✅ ALL TESTS PASSED
```

---

Generated: September 16, 2026  
Investigation Team: Technical Analysis
