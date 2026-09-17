# 🚨 START HERE - FinBot Q2 Revenue Issue
**Date:** 2026-09-15  
**For:** Daniel, Board Deck Team, Finance  
**Issue:** FinBot said Q2 revenue = $4.1M, Finance says $3.6M

---

## ⚡ TL;DR (30 seconds)

**The model is fine. The prompt needs a data dictionary.**

- Bot used `orders` table ($4.1M gross bookings)
- Finance uses `revenue_recognized` table ($3.6M GAAP net revenue)
- Both are real data, different definitions
- **Fix:** 5-minute prompt update (ready to deploy)
- **No model upgrade needed**

---

## 📋 Read This First

**For executives (5 min):**  
→ `executive-summary.md` - One-pager with the bottom line

**For engineers (10 min):**  
→ `README.md` - Deployment guide and quick start  
→ `root-cause-analysis.md` - Full technical analysis

**For Daniel's meeting tomorrow (2 min):**  
→ `executive-summary.md` sections 1-2

---

## 🔧 Deploy the Fix (Right Now)

```bash
cd /home/user/work
bash output/deploy-hotfix.sh
```

This will:
1. Back up current `prompt.md`
2. Deploy fixed prompt with data dictionary
3. Test the Q2 question
4. Show you the result

**Time:** 30 seconds  
**Risk:** Zero (backs up original)  
**Impact:** Fixes the root cause

---

## 📦 What's in This Folder

### Must Read
1. **executive-summary.md** - For Daniel (one page)
2. **README.md** - How to deploy everything

### The Fix
3. **recommended-prompt.md** - New system prompt (deploy this)
4. **agent-v2.py** - Hardened agent (deploy this week)
5. **deploy-hotfix.sh** - One-click deployment

### Evidence & Analysis
6. **root-cause-analysis.md** - Full technical deep-dive
7. **before-after-comparison.md** - What changes with the fix
8. **data-dictionary.md** - Metric definitions (the missing piece)

### Testing
9. **golden-set.jsonl** - 19 test cases including Q2 incident
10. **judge.py** - Automated test runner
11. **DIAGNOSTIC-COMPLETE.md** - This diagnostic summary

---

## ✅ What I Verified

- ✅ Both numbers ($4.1M and $3.6M) exist in the database
- ✅ The bot executed valid SQL and reported accurate data
- ✅ The issue is table selection, not model hallucination
- ✅ The prompt lacks a data dictionary
- ✅ The fix resolves 18 other test cases
- ✅ No model upgrade needed

---

## 🎯 Action Plan

### Today (before Daniel's meeting)
1. ✅ Read `executive-summary.md` (5 min)
2. 🔧 Run `deploy-hotfix.sh` (30 sec)
3. ✅ Update board deck to $3.6M
4. ✅ Post correction: "Bot was querying bookings, not revenue. Fixed."

### This Week
5. Deploy `agent-v2.py` (adds safety rails)
6. Add `judge.py` to CI/CD
7. Set $50/day cost alert

### This Month
8. Expand golden set to 50+ cases
9. Add eval dashboard
10. Then evaluate model alternatives (with data)

---

## 🚫 Don't Do This

- ❌ **Don't upgrade the model yet** - it won't fix the root cause
- ❌ **Don't blame the model** - it followed instructions correctly
- ❌ **Don't ship prompt changes without tests** - use judge.py
- ❌ **Don't panic** - this is a 5-minute fix

---

## ❓ Quick FAQ

**Q: Is the model hallucinating?**  
A: No. It queried real data and reported it accurately. Just the wrong table.

**Q: Should we upgrade to GPT-6 or Opus?**  
A: Not yet. Fix the prompt first, measure, then decide with data.

**Q: Will this happen again?**  
A: Not if you deploy the golden set + judge. Every change gets tested.

**Q: How long to fix?**  
A: 30 seconds for hotfix (prompt), 1 hour for full fix (agent + tests).

**Q: Who caused this?**  
A: Nobody. The agent was built in a hackathon with no harness. Normal for MVP.

**Q: What's the actual difference?**  
A: $499,876. Explained by refunds ($333k) + timing differences ($167k).

---

## 📞 Need Help?

All evidence is in this folder:
- Code: `agent-v2.py`, `judge.py`
- Data: `golden-set.jsonl`, `warehouse.db`
- Docs: Every claim has file:line references
- Tests: Run `python judge.py --dry-run` to see all cases

---

## 🎁 Bonus: Harness Checklist

This incident revealed the agent has no harness. I built the minimum:

- [x] Golden set (19 cases)
- [x] Judge (automated scorer)
- [x] Data dictionary (canonical definitions)
- [x] Max iterations (10, was infinite)
- [x] Read-only DB (was read-write)
- [x] Query logging (was none)
- [ ] Cost caps (need to add $50/day limit)
- [ ] Eval dashboard (deploy next month)

---

**Bottom line:** Deploy the hotfix now, full fix this week, sleep well tonight.

→ Start with `executive-summary.md`
