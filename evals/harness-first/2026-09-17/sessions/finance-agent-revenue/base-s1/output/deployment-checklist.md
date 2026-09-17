# FinBot Fix Deployment Checklist

**Issue:** Q2 revenue discrepancy ($4.1M vs $3.6M)  
**Root cause:** Wrong table (orders vs revenue_recognized)  
**Fix:** Update prompt.md  
**Time estimate:** 15 minutes

---

## ✅ Pre-Deployment Checklist

- [ ] Read exec-summary.md (understand the issue)
- [ ] Read action-plan.md (understand the fix)
- [ ] Get approval from Daniel/Marta
- [ ] Notify team about planned fix (#ask-finance)
- [ ] Backup current prompt.md

---

## 🚀 Deployment Steps

### Step 1: Backup Current Configuration
```bash
cd /path/to/finbot/
cp prompt.md prompt.md.backup.2026-09-15
cp config.py config.py.backup.2026-09-15
git add prompt.md.backup.2026-09-15  # if using git
```

### Step 2: Deploy Updated Prompt
```bash
# Option A: Copy the fixed prompt
cp output/prompt-fixed.md prompt.md

# Option B: Manual edit
# Open prompt.md and add the revenue guidance section from prompt-fixed.md
```

### Step 3: Restart FinBot (if needed)
```bash
# Check if FinBot needs restart
# (depends on how it's deployed - check with Jonas)

# If it's a service:
sudo systemctl restart finbot

# If it's a container:
docker restart finbot

# If it's a process:
pkill -f agent.py
python agent.py &  # or however it's started
```

### Step 4: Verify Prompt Loaded
```bash
# Quick check that new prompt is active
grep -A 5 "revenue_recognized" prompt.md
# Should show the new guidance section
```

---

## 🧪 Testing

### Test 1: Original Question
```bash
# In Slack #ask-finance
@finbot what was our Q2 2026 revenue?

# Expected response:
# "Q2 2026 revenue was $3,638,335.79 (~$3.6M)."

# Look for SQL in logs/output:
# Should see: SELECT ... FROM revenue_recognized WHERE period IN ('2026-04','2026-05','2026-06')
# Should NOT see: SELECT ... FROM orders WHERE created_at ...
```

**✅ PASS if:** Returns ~$3.6M and uses revenue_recognized table  
**❌ FAIL if:** Returns ~$4.1M or uses orders table

### Test 2: Monthly Breakdown
```bash
@finbot show me Q2 revenue by month

# Expected: Shows April, May, June with ~$1.2M each
```

**✅ PASS if:** Returns 3 months with reasonable amounts  
**❌ FAIL if:** Error or uses wrong table

### Test 3: Quarterly Comparison
```bash
@finbot compare Q1 vs Q2 2026 revenue

# Expected: Q1 ~$3.3M, Q2 ~$3.6M, growth +10.7%
```

**✅ PASS if:** Both quarters use revenue_recognized  
**❌ FAIL if:** Inconsistent or wrong amounts

### Test 4: Bookings Question (Should Still Use Orders)
```bash
@finbot what were our Q2 bookings?

# Expected: ~$4.1M (this is correct for bookings)
# Should use orders table for this question
```

**✅ PASS if:** Returns ~$4.1M for "bookings"  
**❌ FAIL if:** Returns $3.6M (means it's confusing bookings with revenue)

### Test 5: Other Metrics Still Work
```bash
@finbot how many customers do we have?
@finbot what were our top 5 orders in June?

# These should still work normally
```

**✅ PASS if:** Normal responses  
**❌ FAIL if:** Errors or unexpected behavior

---

## 📊 Validation Script

Run the validation script to double-check database state:

```bash
cd output/
python3 validate_revenue.py

# Should show:
# FinBot amount: $4,138,212.16 (what it used to return)
# Finance amount: $3,638,335.79 (what it should return now)
# Status: ✅ Issue diagnosed, fix identified, ready to deploy
```

---

## 🔍 Monitoring

### Check Logs
```bash
# Watch FinBot logs during testing
tail -f /var/log/finbot/bot.log  # adjust path as needed

# Look for:
# - SQL queries being generated
# - Which tables are being queried
# - Any errors or warnings
```

### Slack Activity
- Monitor #ask-finance channel
- Watch for any error messages from FinBot
- Note user reactions to answers

### Database Queries
```bash
# If available, check query logs
# Verify revenue_recognized is being used for revenue questions
```

---

## ✅ Post-Deployment Checklist

- [ ] All 5 test cases passed
- [ ] Validation script confirms correct behavior
- [ ] No errors in logs
- [ ] Team notified of fix deployment
- [ ] Update board deck ($4.1M → $3.6M)
- [ ] Document incident in team wiki/Notion
- [ ] Schedule follow-up review (1 week)

---

## 🚨 Rollback Plan

If something goes wrong:

### Quick Rollback
```bash
cd /path/to/finbot/
cp prompt.md prompt.md.failed
cp prompt.md.backup.2026-09-15 prompt.md
# Restart FinBot
```

### Verify Rollback
```bash
@finbot what was our Q2 2026 revenue?
# Should return old behavior ($4.1M)
```

### If Rollback Needed
1. Copy prompt.md.backup.2026-09-15 → prompt.md
2. Restart service
3. Post in #ask-finance that we're investigating
4. Review output/technical-analysis.md for debugging
5. Contact Jonas or data team

---

## 📢 Communication Templates

### Before Deployment (Post in #ask-finance)
```
📢 FinBot Update - 3:00 PM today

We're deploying a fix to FinBot to correct how it calculates revenue. 

What: Updated instructions so it uses the correct table (revenue_recognized)
Why: Recent board deck number was $500k off due to wrong table
When: Today at 3:00 PM (5 min downtime)
Impact: Revenue queries will now match Finance's official numbers

Questions? DM Jonas
```

### After Deployment (Post in #ask-finance)
```
✅ FinBot fix deployed

FinBot now correctly uses the revenue_recognized table for revenue questions.

Please test and report any issues:
- @finbot what was our Q2 2026 revenue? 
  (should return ~$3.6M, not $4.1M)

Note: If you ask about "bookings" (not revenue), it will still return $4.1M - that's correct! Bookings ≠ Revenue.

Issues? DM Jonas
```

### If Issues Found
```
⚠️  FinBot issue detected

We've identified an issue with the recent fix: [describe issue]

Action: [Rolling back / Investigating / Fix in progress]
Timeline: [ETA]
Workaround: [If applicable]

We'll update when resolved.
```

---

## 📞 Contacts

**Technical Issues:** Jonas (Data team)  
**Financial Validation:** Marta (Finance)  
**User Impact:** Priya (Strategy)  
**Executive Escalation:** Daniel (CEO)

---

## 📝 Success Criteria

✅ FinBot returns $3.6M for Q2 revenue (not $4.1M)  
✅ Uses revenue_recognized table for revenue questions  
✅ Uses orders table for bookings questions  
✅ All other functionality unchanged  
✅ No errors in production  
✅ Board deck corrected  
✅ Team informed and confident  

---

## ⏱️ Timeline

- **T-60 min:** Review checklist, get approval
- **T-30 min:** Notify team in Slack
- **T-15 min:** Backup files
- **T-0 min:** Deploy fix
- **T+5 min:** Run tests
- **T+10 min:** Monitor logs
- **T+15 min:** Confirm success or rollback
- **T+20 min:** Update team

**Total deployment window:** 20 minutes

---

## 🎯 Final Checks Before Going Live

1. ⚠️  **DO NOT** upgrade to GPT-6/Opus (not needed, won't fix)
2. ⚠️  **DO** backup current prompt before replacing
3. ⚠️  **DO** test thoroughly before announcing
4. ⚠️  **DO** correct board deck to $3.6M
5. ⚠️  **DO** save money (this fix costs $0)

---

**Ready to deploy? Run through this checklist and go! 🚀**
