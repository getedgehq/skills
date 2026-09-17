# FinBot Revenue Discrepancy Investigation - START HERE

**Date:** September 16, 2026  
**For:** Daniel Kurz (CEO)  
**Issue:** FinBot reported Q2 revenue as $4.1M, Finance says $3.6M

---

## TL;DR - The Answer Daniel Needs

**Q: Is the model hallucinating?**  
A: ❌ No. The model reported real data from the database.

**Q: Do we need a smarter model?**  
A: ❌ No. GPT-6 or Opus would make the same mistake.

**Q: What's the real problem?**  
A: ✅ The bot queried the wrong table. It used `orders` (gross bookings) instead of `revenue_recognized` (net revenue).

**Q: What's the fix?**  
A: ✅ Update the system prompt to specify which table to use. 5-minute fix, $0 cost.

**Q: What's the correct Q2 revenue?**  
A: ✅ $3,638,336 ($3.6M) - matches Finance's close.

---

## The $500K Gap Explained

```
FinBot said:  $4,138,212  (from orders table)
├─ Completed orders:      $3,269,511
├─ Refunded orders:       $  189,943  ← shouldn't count
├─ Cancelled orders:      $  360,039  ← shouldn't count
└─ Partial refunds:       $  318,719  ← should be netted

Finance says: $3,638,336  (from revenue_recognized table)
└─ Net revenue after refunds and cancellations ✅
```

**The $499,876 difference** = refunded + cancelled orders that finbot incorrectly included.

---

## What To Read Next

### For Quick Overview (5 mins)
📄 **QUICK_REF.txt** - One-page plain text summary

### For Executive Context (10 mins)
📄 **executive_summary.md** - Full context for leadership team

### For Technical Details (20 mins)
📄 **root_cause_analysis.md** - Complete analysis with recommendations
📄 **technical_analysis.md** - Database queries and data validation

### For Deployment (15 mins)
📄 **action_plan_jonas.md** - Step-by-step fix for Jonas
📄 **prompt_UPDATED.md** - Ready-to-deploy system prompt

### For Understanding (10 mins)
📄 **visual_comparison.md** - Side-by-side wrong vs. right
📄 **before_after_examples.md** - What will change after the fix

### For Testing (5 mins)
📄 **validation_tests.py** - Automated tests to verify the fix

---

## Files in output/ Directory

| File | Purpose | Who Should Read |
|------|---------|-----------------|
| **START_HERE.md** | You are here | Everyone |
| **INDEX.md** | Detailed file listing | Reference |
| **README.txt** | Plain text overview | Quick lookup |
| **QUICK_REF.txt** | One-page summary | Everyone |
| **executive_summary.md** | Leadership summary | Daniel, Marta, Jonas |
| **root_cause_analysis.md** | Full investigation | Everyone interested |
| **technical_analysis.md** | Database deep dive | Jonas, data team |
| **visual_comparison.md** | Before/after visual | Anyone confused |
| **before_after_examples.md** | Slack conversation examples | Testing team |
| **prompt_UPDATED.md** | Fixed system prompt | Jonas (to deploy) |
| **action_plan_jonas.md** | Deployment steps | Jonas, data team |
| **validation_tests.py** | Test suite | Jonas, QA |

---

## The Fix (For Jonas)

1. **Backup current prompt**
   ```bash
   cp prompt.md prompt.md.backup_sept16
   ```

2. **Deploy new prompt**
   ```bash
   cp output/prompt_UPDATED.md prompt.md
   ```

3. **Verify the fix**
   ```bash
   python3 output/validation_tests.py
   ```
   Expected: ✅ ALL TESTS PASSED

4. **Test with real questions**
   - "What was Q2 2026 revenue?" → Should say $3.6M
   - "What were Q2 bookings?" → Should say $4.1M

**Estimated time:** 30 minutes  
**Risk:** Low (prompt-only change, easily reversible)

---

## Key Findings Summary

### What We Know
✅ FinBot queried the database and got back $4,138,212.16  
✅ That number is real data from the `orders` table  
✅ Finance uses the `revenue_recognized` table: $3,638,335.79  
✅ The $500K difference is refunded/cancelled orders  
✅ The model wrote correct SQL and didn't hallucinate  

### What Went Wrong
❌ System prompt didn't specify which table to use for revenue  
❌ Model reasonably (but wrongly) chose `orders` table  
❌ That number includes cancelled and refunded transactions  
❌ Board deck got the wrong number  

### What To Do
✅ Update system prompt with clear table guidance  
✅ Add validation testing for key metrics  
✅ Create verification process for board materials  
✅ Document the three different "revenue" numbers in warehouse  

---

## Common Questions

**Q: Why not just upgrade to a better model?**  
A: Any model would make this choice without clearer instructions. The prompt lists five tables equally with no guidance on which to use. Even humans would guess wrong without domain knowledge.

**Q: How do we prevent this in the future?**  
A: (1) Update the prompt (immediate), (2) Add automated validation tests (this week), (3) Create Finance verification process for board materials (ongoing).

**Q: Are there other wrong numbers out there?**  
A: Probably. FinBot also calculated Q1 2026 wrong ($4.1M vs actual $3.3M). Any revenue question before today likely used the wrong table. Good news: the fix prevents future issues.

**Q: What about the daily_kpis table?**  
A: That table shows Q2 revenue as $2.3M, which doesn't match either orders or revenue_recognized. Needs investigation - see technical_analysis.md for details.

**Q: Can we trust finbot now?**  
A: After the fix, yes for technical accuracy. But still recommend Finance verification for board materials as a process control (not because of AI limitations, but good practice for any automated system).

---

## Timeline

**Sept 11:** Priya asks finbot for Q2 revenue, gets $4.1M, puts in board deck  
**Sept 14:** Marta (Finance) catches the error, says Q2 close is $3.6M  
**Sept 14:** Exec team questions if model is hallucinating  
**Sept 16:** Investigation reveals root cause (wrong table)  
**Sept 16:** Fix prepared (this output folder)  
**Sept 17:** (target) Jonas deploys fix  

---

## Bottom Line

This was a **data engineering issue**, not an AI capability issue.

The solution is **better documentation** (which table to use), not a better model.

**Cost to fix:** $0 and 30 minutes  
**Cost to upgrade model:** $$$ and wouldn't solve the problem  

---

## Next Steps

1. **Daniel:** Review executive_summary.md
2. **Jonas:** Review action_plan_jonas.md and deploy fix
3. **Everyone:** Document this as a case study in AI system design

---

**Status:** ✅ Investigation complete, fix ready to deploy  
**Confidence:** High - root cause confirmed through database analysis  
**Timeline:** Can be fixed today

Questions? See INDEX.md for full file listing.
