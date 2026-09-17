# DEPLOYMENT CHECKLIST - FinBot Fix

**Issue:** Q2 Revenue Discrepancy ($4.1M vs $3.6M)  
**Fix:** Updated system prompt  
**Deploy Date:** _________ (recommended: immediately)  
**Deployed by:** _________

---

## ⚠️ PRE-DEPLOYMENT

### [ ] Step 1: Understand the Issue (5 min)
- [ ] Read `output/TLDR.md` 
- [ ] Confirm understanding: Bot queried wrong table (not a model issue)
- [ ] Note correct Q2 revenue: $3,638,335.79 ($3.6M)

### [ ] Step 2: Backup Current Configuration
```bash
cd /home/user/work
cp prompt.md prompt.md.backup.$(date +%Y%m%d)
cp config.py config.py.backup.$(date +%Y%m%d)
```

### [ ] Step 3: Verify Test Environment Works
```bash
# This should return the WRONG number ($4.1M)
python agent.py "what was our Q2 2026 revenue?"
```
Expected current output: ~$4.1M or $4,138,212
If this doesn't work, FinBot might have other issues.

---

## 🚀 DEPLOYMENT

### [ ] Step 4: Deploy Fixed Prompt
```bash
cp output/fixed_prompt.md prompt.md
```

### [ ] Step 5: Verify Deployment
```bash
# Check the file was copied
diff output/fixed_prompt.md prompt.md
# Should show no differences (or return nothing)
```

---

## ✅ POST-DEPLOYMENT VERIFICATION

### [ ] Step 6: Test Critical Queries

#### Test 1: Q2 2026 Revenue
```bash
python agent.py "what was our Q2 2026 revenue?"
```
- [ ] Expected: ~$3.6M or $3,638,335.79
- [ ] Should NOT say: $4.1M
- [ ] Should mention: revenue_recognized table (if showing SQL)
- **Actual result:** _______________

#### Test 2: Q1 2026 Revenue  
```bash
python agent.py "what was our Q1 2026 revenue?"
```
- [ ] Expected: ~$3.3M or $3,285,493.84
- [ ] Should NOT say: $4.1M
- **Actual result:** _______________

#### Test 3: August 2026 Revenue
```bash
python agent.py "what was our August 2026 revenue?"
```
- [ ] Expected: ~$1.2M or $1,162,073.21
- **Actual result:** _______________

#### Test 4: Order Count (non-revenue query)
```bash
python agent.py "how many orders did we have in Q2 2026?"
```
- [ ] Expected: ~1,900-2,200 orders
- [ ] Should work normally
- **Actual result:** _______________

### [ ] Step 7: Run Full Test Suite
```bash
python output/test_queries.py
```
- [ ] All tests pass
- [ ] No errors in output
- **Notes:** _______________

### [ ] Step 8: Slack Test (Optional but Recommended)
If FinBot is connected to Slack:
- [ ] Post in #ask-finance: "what was our Q2 2026 revenue?"
- [ ] Verify response is $3.6M
- [ ] Check the SQL query shown (should use revenue_recognized)

---

## 📋 POST-DEPLOYMENT TASKS

### [ ] Step 9: Update Board Deck
- [ ] Change Q2 revenue from $4.1M to $3.6M
- [ ] Update any charts/graphs showing Q2 data
- [ ] Review Q1 number (should be $3.3M, not $4.1M)
- [ ] Verify QoQ growth calculation: Q2 vs Q1 = +10.7%
- **Board deck updated by:** _________

### [ ] Step 10: Verify Other Board Numbers
Review any other numbers from FinBot:
- [ ] Q1 revenue: _______________
- [ ] Q3 revenue (if mentioned): _______________
- [ ] YTD revenue: _______________
- [ ] Any annual projections: _______________

### [ ] Step 11: Notify Stakeholders
- [ ] Email Marta (VP Finance): Fix deployed, Q2 = $3.6M confirmed
- [ ] Notify Priya (Strategy): Correct number for board deck
- [ ] Notify Jonas (Data team): Prompt updated, backup saved
- [ ] Update #exec-staff thread with resolution

---

## 🔄 ROLLBACK PLAN (If Something Goes Wrong)

### If tests fail or bot stops working:

```bash
# Restore original prompt
cp prompt.md.backup.[DATE] prompt.md

# Verify rollback worked
python agent.py "what was our Q2 2026 revenue?"
# Should return the old (wrong) answer of $4.1M

# Notify team
echo "Rollback completed at $(date)" | tee rollback.log
```

Then investigate what went wrong before re-attempting.

---

## 📊 SUCCESS CRITERIA

### Must Have (Critical)
- [x] Q2 2026 revenue query returns $3.6M (not $4.1M)
- [x] SQL uses revenue_recognized table (not orders)
- [x] Other revenue queries work correctly
- [x] Board deck has correct numbers

### Should Have (Important)
- [x] All test queries pass
- [x] Slack integration works (if applicable)
- [x] No performance degradation
- [x] Documentation updated

### Nice to Have (Optional)
- [ ] Add integration tests to CI/CD
- [ ] Update warehouse schema docs
- [ ] Create finance query cookbook

---

## 📝 DEPLOYMENT NOTES

### Issues Encountered:
_________________________________________
_________________________________________

### Resolution:
_________________________________________
_________________________________________

### Final Sign-off:

**Deployed by:** _________________ Date: _________  
**Verified by:** _________________ Date: _________  
**Approved by:** _________________ Date: _________

---

## 🔮 NEXT STEPS (After Deployment)

### This Week
- [ ] Add automated tests for revenue queries
- [ ] Document revenue_recognized as source of truth
- [ ] Review query logs for other potential issues
- [ ] Schedule team post-mortem

### Next Sprint  
- [ ] Implement query validation layer
- [ ] Add schema documentation to system prompt
- [ ] Create metrics glossary
- [ ] Build finance query test suite

### Future
- [ ] Consider adding SQL query linter
- [ ] Explore adding business rules validation
- [ ] Document other high-risk queries
- [ ] Training session on using FinBot correctly

---

## 📞 SUPPORT CONTACTS

**If deployment issues:**
- Data Team (Jonas): [contact]
- Engineering: [contact]

**If business logic questions:**
- Finance (Marta): [contact]
- Accounting team: [contact]

**For urgent issues:**
- On-call engineer: [contact]
- Escalation path: Jonas → Daniel

---

## ✅ FINAL CHECKLIST

Before closing this ticket:

- [ ] Fix deployed successfully
- [ ] All tests pass
- [ ] Board deck corrected
- [ ] Stakeholders notified
- [ ] Documentation updated
- [ ] Backup created and saved
- [ ] This checklist completed and filed

**Status:** ⬜ Not Started | ⬜ In Progress | ⬜ Complete | ⬜ Rolled Back

**Completion timestamp:** _________________

---

*Keep this checklist for audit/compliance purposes.*
