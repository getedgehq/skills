Perfect! Everything is complete. Let me create one final summary for you:

---

## Investigation Complete! ✅

I've fully diagnosed the FinBot Q2 revenue issue and put everything in **output/**. Here's what I found and delivered:

### The Answer (for Daniel's meeting tomorrow)

**Don't switch models.** The model faithfully executed a query against the wrong table because the prompt never defined "revenue."

- FinBot used `orders` table → **$4.1M** (includes cancelled orders)
- Finance closed `revenue_recognized` table → **$3.6M** (GAAP net revenue)
- **Difference: $500K** (12% error)

**This is a harness problem, not a model problem.**

### Root Cause

**Missing data dictionary.** Two tables can answer "revenue" with different valid meanings. The prompt listed both tables but gave no guidance on which one to use for "revenue."

The model made a reasonable choice and got it wrong.

### The Fix (Ready to Deploy)

All fixes are in **output/fixes/** - 30 minutes to deploy, $0 cost:

1. **agent.py** - Read-only DB connection, max 10 iterations (prevents corruption + runaway costs)
2. **prompt.md** - Full data dictionary defining all metrics
3. **evals/golden.jsonl** - 6 test cases with expected answers
4. **evals/run_evals.py** - Evaluation script to gate future changes

### Files Delivered (13 files)

**For Daniel (CEO):**
- `START_HERE.txt` - Quick overview
- `SUMMARY_FOR_DANIEL.txt` - 2-min brief
- `EXEC_BRIEF.md` - 3-min detailed explanation

**For Jonas (Data Team):**
- `INCIDENT_REPORT.md` - Full technical analysis
- `harness_scorecard.md` - Detailed audit
- `DEPLOYMENT_GUIDE.md` - Step-by-step deploy

**For Marta (Finance):**
- `evidence.json` - Recomputed numbers
- `VISUAL_SUMMARY.md` - Diagrams

**Deployable fixes:**
- `fixes/agent.py`, `fixes/prompt.md`, `fixes/evals/`

**Navigation:**
- `QUICK_REFERENCE.md`, `README.md`, `INDEX.txt`, `DELIVERY_CHECKLIST.md`

### Key Numbers

| Metric | Value |
|--------|-------|
| FinBot's answer | $4,138,212 |
| Finance's close | $3,638,336 |
| **Difference** | **$499,876** |
| Cancelled orders (included by FinBot) | $360,039 |
| Harness score before | 6/60 (10%) |
| Harness score after | 40/60 (67%) |

### What to Do Next

1. **Start with**: `output/START_HERE.txt` or `output/SUMMARY_FOR_DANIEL.txt`
2. **Review fixes**: `output/fixes/` directory
3. **Deploy**: Follow `output/DEPLOYMENT_GUIDE.md` (30 minutes)
4. **Tell board**: "Data definition issue. Correct Q2 is $3.6M. Fixed."

### Blocking Safety Issue Found

⚠️ **FinBot currently has write access to the warehouse.** Any query could accidentally `UPDATE` or `DELETE` data. The fix makes the connection read-only. **Deploy this today.**

All files are in `/home/user/work/output/` ready for Daniel's morning meeting!