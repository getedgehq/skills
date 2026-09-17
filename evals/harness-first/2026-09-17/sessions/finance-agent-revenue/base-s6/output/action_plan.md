# ACTION PLAN: Fix Finbot Revenue Issue
**Date:** 2026-09-16  
**Owner:** Jonas (Data Team)  
**Priority:** HIGH (Board deck correction needed)

---

## Immediate Actions (Today)

### 1. ✅ Correct the Board Deck
**Owner:** Priya (Strategy)  
**Action:** Update Q2 2026 revenue from $4.1M to **$3.64M** ($3,638,335.79)  
**Verification:** Run this SQL:
```sql
SELECT ROUND(SUM(net_amount), 2) 
FROM revenue_recognized 
WHERE recognized_on BETWEEN '2026-04-01' AND '2026-06-30';
```
Result: $3,638,335.79

---

### 2. 🔧 Fix the Finbot Prompt
**Owner:** Jonas (Data)  
**Time:** 30 minutes  

**Steps:**
1. Backup current prompt:
   ```bash
   cp prompt.md prompt.md.backup-2026-09-16
   ```

2. Replace prompt.md with the fixed version:
   ```bash
   cp output/prompt_FIXED.md prompt.md
   ```

3. Restart finbot service (if needed)

**What changed:**
- Added explicit guidance to use `revenue_recognized` for revenue questions
- Warned that `orders` table includes cancelled orders
- Specified which columns to use for what

---

### 3. 🧪 Test the Fix
**Owner:** Jonas (Data)  
**Time:** 15 minutes  

Run these test queries through finbot:

**Test 1: Q2 Revenue**
```
@finbot what was our Q2 2026 revenue?
```
✅ Expected: ~$3.6M ($3,638,335.79)  
❌ Wrong: ~$4.1M ($4,138,212.16)

**Test 2: Q1 Revenue (cross-check)**
```
@finbot what was our Q1 2026 revenue?
```
✅ Expected: Should use revenue_recognized table  
Cross-check with Finance's Q1 close

**Test 3: Order counts (should still work)**
```
@finbot how many orders did we have in Q2 2026?
```
✅ Expected: 2,213 orders (includes cancelled - this is correct for this question)

---

### 4. 📧 Notify Stakeholders
**Owner:** Jonas (Data)  
**Time:** 10 minutes  

**Message to #exec-staff:**
```
Update on the Q2 revenue discrepancy:

Root cause identified: finbot was querying the orders table which includes 
$360k of cancelled orders. Orders aren't revenue.

Fixed by updating the bot's instructions to use the revenue_recognized table 
(same table Finance uses).

Correct Q2 2026 revenue: $3,638,335.79 (~$3.64M)

The model itself is fine - no need to upgrade. This was a documentation issue.

Finbot is now fixed and tested. Going forward, revenue numbers will match 
Finance's books.

- Jonas
```

---

## Short-Term Actions (This Week)

### 5. 📊 Create Test Suite
**Owner:** Jonas (Data)  
**Time:** 2-3 hours  

Create `tests/finbot_validation.py` with known-correct answers:
- Q1, Q2, Q3 2026 revenue
- Monthly revenue for recent months
- Year-over-year comparisons
- Common questions from the team

Run monthly to ensure accuracy.

---

### 6. 📝 Document the Warehouse
**Owner:** Jonas (Data)  
**Time:** 2-3 hours  

Create `warehouse_schema.md` documenting:
- Each table's purpose
- When to use which table
- Common queries
- Relationship between tables

Share with:
- Engineering team
- Data team
- Finance team
- Anyone who might query the warehouse

---

### 7. 🔍 Audit Past Responses
**Owner:** Jonas (Data)  
**Time:** 1 hour  

Review finbot's Slack history for other revenue questions:
- Did we give wrong numbers to other teams?
- Do any other decks/reports need correction?
- Were any decisions made based on incorrect numbers?

Flag any issues to Daniel and Marta.

---

## Long-Term Actions (This Month)

### 8. 🚨 Add Monitoring
**Owner:** Jonas (Data)  
**Time:** 4 hours  

Implement:
1. Log all finbot SQL queries
2. Flag queries using `orders.amount` for revenue
3. Alert if results differ significantly from Finance's numbers
4. Weekly report of unusual queries

---

### 9. 🤝 Monthly Finance Reconciliation
**Owner:** Jonas (Data) + Marta (Finance)  
**Time:** 30 min/month  

Monthly meeting to:
- Compare finbot's answers to Finance's official numbers
- Review any discrepancies
- Update bot documentation as needed
- Ensure data warehouse is in sync with accounting

---

### 10. 📚 Train the Team
**Owner:** Jonas (Data)  
**Time:** 2 hours  

Create training materials:
- "How to ask finbot questions" guide
- When to use finbot vs. asking Finance directly
- Understanding the data warehouse
- What each table represents

Present at next all-hands or team meeting.

---

## Success Metrics

### Immediate (Today)
- ✅ Board deck has correct revenue number
- ✅ Finbot gives correct answer for Q2 revenue
- ✅ Stakeholders notified

### Short-term (This Week)
- ✅ Test suite passing
- ✅ Warehouse documented
- ✅ Past responses audited

### Long-term (This Month)
- ✅ Monitoring in place
- ✅ Monthly reconciliation scheduled
- ✅ Team trained
- ✅ Zero discrepancies between finbot and Finance

---

## Risk Mitigation

### What if the fix doesn't work?
**Backup plan:**
1. Add validation code to agent.py to catch revenue queries using orders table
2. Automatically rewrite queries to use revenue_recognized
3. Log warnings for manual review

### What if there are other issues?
**Discovery process:**
1. Run verification script on all major metrics
2. Compare to Finance's official numbers
3. Fix any additional prompt issues
4. Document corrections

### What if users bypass finbot?
**Prevention:**
1. Make finbot the easiest way to get data
2. Ensure it's always accurate
3. Faster than querying directly
4. Document that it's the recommended method

---

## Communication Plan

### Today
- ✅ Update Daniel (CEO) - issue resolved
- ✅ Update Marta (Finance) - root cause identified
- ✅ Update Priya (Strategy) - correct number provided
- ✅ Post in #exec-staff - all clear

### This Week
- Update #data-team with findings
- Update #ask-finance with any changes
- Document in team wiki

### This Month
- All-hands mention: "fixed finbot accuracy issue"
- Include in monthly data quality report

---

## Cost Analysis

### This Fix
- Time: 1 day total
- Cost: $0
- Impact: Issue resolved

### Alternative: Upgrade Model
- Time: 1 hour to switch
- Cost: 2-10x monthly spend increase
- Impact: Issue NOT resolved (would still need prompt fix)

**Conclusion:** Correct fix chosen, no unnecessary spending.

---

## Lessons Learned

### What went wrong
1. Prompt lacked domain-specific guidance
2. No validation of revenue queries
3. No regular reconciliation with Finance
4. Assumed model would "figure it out"

### What went right
1. Issue was caught before board meeting
2. Data warehouse has correct data
3. Model performed as designed
4. Easy to fix once identified

### Process improvements
1. Add test suite for all financial metrics
2. Regular Finance reconciliation
3. Better documentation of data sources
4. Monitoring and alerts for discrepancies

---

## Verification Checklist

Before marking this complete:

- [ ] Board deck updated with $3.64M
- [ ] prompt.md replaced with fixed version
- [ ] Finbot tested with Q2 revenue question
- [ ] Result is $3,638,335.79 (~$3.6M)
- [ ] Daniel notified - issue resolved
- [ ] Marta notified - root cause explained
- [ ] Team notified in #exec-staff
- [ ] Test suite created
- [ ] Documentation updated
- [ ] Monitoring planned
- [ ] Monthly reconciliation scheduled

---

## Contact

**Questions about implementation:** Jonas Feld (Data Team)  
**Questions about the numbers:** Marta Oyelaran (VP Finance)  
**Questions about this analysis:** See investigation_report.md

---

## Files Delivered

All files are in `output/`:

1. **executive_summary.md** - One-pager for Daniel
2. **investigation_report.md** - Full analysis for the team
3. **technical_analysis.md** - Deep dive into the data
4. **proposed_fix.md** - Detailed fix instructions
5. **prompt_FIXED.md** - Ready-to-use corrected prompt
6. **verify_numbers.py** - Script to verify all numbers
7. **action_plan.md** - This document

To verify numbers: `python3 output/verify_numbers.py`
