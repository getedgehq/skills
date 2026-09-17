Perfect! Everything is complete. Let me create a final summary for you:

---

## Investigation Complete ✅

I've finished the comprehensive investigation into the FinBot Q2 revenue discrepancy. Here's what I found and delivered:

### **The Answer (One Line)**
**Don't switch models: the bot queried the wrong table** (orders instead of revenue_recognized) because the prompt lacks a data dictionary. This is a 5-minute prompt fix, not a model problem.

### **What Happened**
- **FinBot said:** Q2 2026 revenue = $4,138,212 (from `orders.amount` - gross bookings)
- **Finance says:** Q2 2026 revenue = $3,638,336 (from `revenue_recognized.net_amount` - GAAP net revenue)
- **Difference:** $499,876 (13.7% overstatement)
- **Root cause:** The prompt lists 5 tables but doesn't define which to use for "revenue"

### **This is NOT a hallucination**
The model executed valid SQL and reported accurate data from the database. It just picked the wrong table because the instructions were ambiguous. Both numbers are real - they just represent different things (gross bookings vs. recognized revenue).

### **What I Delivered (15 files in `/output/`)**

**For Daniel's meeting tomorrow:**
- `START-HERE.md` - 2-minute quick start
- `executive-summary.md` - One-page summary with talking points
- `INDEX.md` - Complete file guide

**The Fix (ready to deploy):**
- `recommended-prompt.md` - Updated system prompt with data dictionary
- `agent-v2.py` - Hardened agent with safety rails (read-only DB, max iterations, logging)
- `deploy-hotfix.sh` - One-click deployment script

**Complete Analysis:**
- `root-cause-analysis.md` - Full technical deep-dive with evidence
- `before-after-comparison.md` - Side-by-side impact of fix
- `data-dictionary.md` - Canonical metric definitions
- `DIAGNOSTIC-COMPLETE.md` - Complete findings summary
- `INVESTIGATION-SUMMARY.txt` - Plain text executive report
- `DELIVERABLES.txt` - Complete inventory

**Testing Infrastructure:**
- `golden-set.jsonl` - 19 test cases (including the Q2 incident)
- `judge.py` - Automated pass/fail checker

**Deployment Guide:**
- `README.md` - Step-by-step deployment instructions

### **Key Findings**
1. ✅ Both numbers verified in `warehouse.db` - no data corruption
2. ✅ Model behavior is correct - it followed the ambiguous prompt
3. ✅ No model upgrade needed - this is a prompt/harness issue
4. ❌ Agent has 0/6 harness components (no tests, no cost caps, no data dictionary)
5. 🚨 Found 3 blocking safety risks (infinite loops, write access, no tracing) - all fixed in agent-v2.py

### **Deployment Path**
- **Today:** Run `bash output/deploy-hotfix.sh` (30 seconds, zero risk)
- **This week:** Deploy agent-v2.py with safety rails
- **This month:** Expand golden set, add eval dashboard

All files are in `/home/user/work/output/` and ready to use. Start with `START-HERE.md` or `executive-summary.md` for Daniel.