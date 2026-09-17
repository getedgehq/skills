# Pre-Daniel Meeting Checklist

**Meeting:** Tomorrow morning  
**Topic:** Finbot revenue discrepancy  
**Prepared by:** Investigation team

---

## ✅ Documents Ready for Daniel

All documents are in the `/output` folder:

### Read First (2 minutes)
- [ ] `executive_summary.md` - One-page overview
- [ ] `decision_matrix.md` - Why not to upgrade the model

### If He Wants Details (10 minutes)
- [ ] `root_cause_analysis.md` - Complete investigation
- [ ] `URGENT_board_deck_alert.md` - Both Q1 and Q2 are wrong

### Supporting Materials
- [ ] `data_forensics.md` - Data validation
- [ ] `sql_comparison.md` - Query examples
- [ ] `action_plan.md` - Implementation steps
- [ ] `README.md` - Navigation guide

### Ready to Deploy
- [ ] `prompt_FIXED.md` - Corrected prompt file
- [ ] `test_fix.py` - Validation script

---

## 🎯 Key Messages for Daniel

### The 30-Second Version
"Not a hallucination. The bot queried the wrong table because the prompt doesn't specify. 5-minute fix, no cost, don't upgrade the model."

### The 2-Minute Version
"Finbot correctly executed SQL but chose 'orders' table (gross bookings) instead of 'revenue_recognized' (net revenue). The prompt lists both tables but doesn't say which one to use for revenue. Both Q1 and Q2 are wrong by ~$500-850K. Fix the prompt, not the model - all models need the same guidance."

### The 5-Minute Version
See `executive_summary.md`

---

## 🚨 Critical Issues to Raise

1. **Board deck urgency**
   - Q1 probably shows $4.1M (should be $3.3M)
   - Q2 probably shows $4.1M (should be $3.6M)
   - Priya needs to check/correct ASAP

2. **Not a model problem**
   - Model performed correctly
   - Don't spend on upgrades for this issue
   - Fix is 5 minutes and $0

3. **Both quarters affected**
   - Q1 off by $856K
   - Q2 off by $500K
   - Check other materials

---

## 📊 The Numbers

### Q1 2026
- Finbot: $4,141,985.86
- Correct: $3,285,493.84
- Difference: -$856,492

### Q2 2026
- Finbot: $4,138,212.16
- Correct: $3,638,335.79
- Difference: -$499,876

### H1 2026
- Finbot: ~$8.3M
- Correct: $6,923,829.63
- Difference: -$1.4M

---

## 💡 Quick Wins

Things we can do immediately:

1. **Fix prompt** (5 min)
   - Replace prompt.md with prompt_FIXED.md
   - Test with Q2 question
   - Deploy to production

2. **Verify board deck** (15 min)
   - Check what numbers are in deck
   - Get official numbers from Marta
   - Update if needed

3. **Notify team** (5 min)
   - Post in #ask-finance about the issue
   - Warn about using historical finbot numbers
   - Share corrected Q1/Q2 numbers

---

## ❓ Anticipated Questions & Answers

**Q: "Is it hallucinating?"**  
A: No. It queried real data and returned accurate results. Just the wrong table.

**Q: "Should we upgrade to Opus/GPT-6/o1?"**  
A: No (for this issue). All models need the prompt fix. Evaluate upgrades for other reasons.

**Q: "How confident are you in the fix?"**  
A: Very. The issue is clear and the fix directly addresses the root cause.

**Q: "Will this happen again?"**  
A: Not after the prompt fix. The new prompt explicitly states which table to use.

**Q: "How do we know the rest of the data is accurate?"**  
A: The warehouse data is correct. Only the table selection was wrong. Verified all tables.

**Q: "What about other finbot answers?"**  
A: Non-revenue questions are likely fine. Revenue-specific issue due to table ambiguity.

**Q: "How much will the fix cost?"**  
A: $0 upfront, $0 ongoing. Just a prompt text change.

**Q: "How long to implement?"**  
A: 5 minutes to deploy, 5 minutes to test. Can be done today.

**Q: "What if it doesn't work?"**  
A: Very low risk. Easy to revert. Have kept original prompt as backup.

**Q: "Should we still trust finbot?"**  
A: Yes, with validation for critical use. Good for quick analysis, verify for board materials.

---

## 🎬 Recommended Flow for Meeting

1. **Start with the punch line** (30 sec)
   - "Found the issue. Not a model problem, prompt problem. Can fix in 5 minutes for $0."

2. **Show the numbers** (1 min)
   - Q1: $4.1M → $3.3M
   - Q2: $4.1M → $3.6M
   - Both wrong, same root cause

3. **Explain root cause** (2 min)
   - Prompt doesn't specify which table for revenue
   - Model chose orders (reasonable but wrong)
   - Should use revenue_recognized

4. **Address model upgrade question** (2 min)
   - All models would make same mistake
   - Prompt needs business rules encoded
   - Don't spend money on wrong solution

5. **Show the fix** (1 min)
   - Old prompt: lists tables, no guidance
   - New prompt: specifies revenue_recognized is official
   - Ready to deploy

6. **Immediate actions** (1 min)
   - Fix prompt today
   - Check board deck ASAP
   - Notify team

7. **Take questions** (3 min)
   - Use anticipated Q&A above

---

## 📁 Hand-Off Materials

After meeting, Daniel should have:
- [ ] Executive summary (for his reference)
- [ ] Decision matrix (for defending "don't upgrade")
- [ ] Action plan (for team to execute)

---

## 👥 Who Needs to Do What

After Daniel approves:

**Jonas (Data team)**
- Deploy prompt fix
- Test with Q2 question
- Monitor for issues

**Priya (Strategy)**
- Check board deck numbers
- Correct if needed
- Coordinate with Marta

**Marta (Finance)**
- Confirm official Q1/Q2 numbers
- Verify corrected deck
- Sign off on fix

**Daniel (CEO)**
- Approve fix deployment
- Decide on communication plan
- Review updated board materials

---

## ⏰ Timeline

**Today (after meeting):**
- [ ] Get approval from Daniel
- [ ] Deploy prompt fix
- [ ] Test fix
- [ ] Check board deck

**Tomorrow:**
- [ ] Verify board deck corrected
- [ ] Monitor finbot usage
- [ ] Notify team if needed

**This week:**
- [ ] Add schema documentation
- [ ] Review other recent finbot queries
- [ ] Create usage guidelines

---

## 🎯 Success Criteria

Fix is successful when:
- [ ] Finbot returns $3.6M for Q2 (not $4.1M)
- [ ] Query uses revenue_recognized table
- [ ] Board deck has correct numbers
- [ ] Team understands the issue
- [ ] No model upgrade needed

---

## 📞 Emergency Contacts

If issues arise during deployment:
- **Jonas Feld** - Finbot owner
- **Marta Oyelaran** - Finance verification
- **Investigation team** - Root cause analysis

---

**Everything is ready. Good luck with the meeting!** ✨
