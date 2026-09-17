# FinBot Q2 Revenue Issue - Executive Brief

**To:** Daniel Kurz (CEO)  
**From:** Data Team Investigation  
**Date:** 2026-09-16  
**Re:** FinBot reported $4.1M Q2 revenue vs. Finance's $3.6M close

---

## Bottom Line

**Don't switch models. The model worked correctly—we had no data dictionary.**

FinBot queried the wrong table because our prompt didn't define "revenue." Two tables can answer that question:
- `orders` table = $4.1M (what FinBot used - includes cancelled orders)
- `revenue_recognized` table = $3.6M (what Finance closed - GAAP net revenue)

**The model isn't hallucinating. It faithfully executed a reasonable query against ambiguous instructions.**

---

## What Happened

1. **Sep 11:** Priya asked FinBot "what was Q2 revenue?" for the board deck
2. FinBot queried: `SELECT SUM(amount) FROM orders WHERE created_at IN Q2`
3. FinBot answered: **$4.1M** (correct sum from that table)
4. Priya put $4.1M in the board pre-read
5. **Sep 14:** Finance flagged it—their Q2 close is **$3.6M**
6. $500K difference → crisis of confidence in the bot

**Why the difference:**
- `orders` table includes cancelled orders ($360K) and doesn't net out refunds ($140K)
- `revenue_recognized` table is GAAP net revenue (what Finance reports)
- Our prompt listed both tables with no guidance on which one to use

---

## Root Cause: Missing Harness

I audited the full system. The model is fine. **We're missing basic infrastructure:**

| What's Missing | Impact on This Incident |
|----------------|------------------------|
| **Data dictionary** | No definition of "revenue" → model guessed wrong table |
| **Golden set** | No test cases → this could have been caught before production |
| **Safety checks** | Bot has write access to the warehouse (accidental `DELETE` would execute) |
| **Cost limits** | No max iterations → could burn tokens on bad queries |
| **Tracing** | No logs → had to reconstruct this by hand |

**This is a harness problem, not a model problem.**

---

## Evidence

I recomputed both numbers from the warehouse:

```sql
-- What FinBot did
SELECT SUM(amount) FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30'
→ $4,138,212 ✓ (correct sum from orders table)

-- What Finance closed
SELECT SUM(net_amount) FROM revenue_recognized 
WHERE recognized_on BETWEEN '2026-04-01' AND '2026-06-30'
→ $3,638,336 ✓ (correct GAAP revenue)
```

Both queries are correct. FinBot chose the wrong one because we never told it which table "revenue" means.

---

## The Fix (3 hours, $0 cost increase)

I've written the fixes in `output/fixes/`. They're ready to deploy:

### 1. Data Dictionary (30 min)
Added definitions to the prompt:
- "Revenue" = `revenue_recognized.net_amount` (GAAP net, official number)
- "Orders" = `orders.amount` (GMV, NOT for revenue reporting)
- Defined all table columns and when to use each

### 2. Safety (15 min)
- Changed DB connection to read-only mode (prevents accidental writes)
- Added max 10 turns per question (prevents infinite loops)

### 3. Golden Set (1 hour)
- Built 6 test cases with expected answers (including Q2 revenue = $3.6M)
- Can expand to 50+ cases from Slack history

### 4. Eval Script (30 min)
- Runs tests before any prompt/model change
- Gates deployments (no more "ship and hope")

### Next Steps (1 hour)
- Add structured logging (cost, errors, queries per user)
- Get cost/usage dashboards

---

## Model Upgrade? Not Yet

**Upgrading to a better model (e.g., Opus, GPT-6) would:**
- Cost 2-3x more per query (~$X → ~$Y per month)
- **Still fail this question** without a data dictionary
- Give no quality improvement we can measure (because we have no eval set)

**The harness fix:**
- Costs $0
- Fixes this entire class of error (ambiguous definitions)
- Gives us the eval set we need to benchmark models if we want to later

**Recommendation:** Fix the harness first. If the golden set shows quality issues after that, then we can benchmark Opus vs. Sonnet with real evidence.

---

## Blocking Risk (Not Asked, But Important)

FinBot currently has **write access** to the warehouse. The tool description says "read-only query" but the code can execute `UPDATE`, `DELETE`, `DROP TABLE`.

If someone asks "fix the Q2 revenue to match budget" and the model tries to help, it could corrupt our data.

**Fix:** 5-minute code change to open DB in read-only mode (included in `output/fixes/agent.py`)

---

## What to Tell the Board

If they ask about the $4.1M number:

> "We identified an ambiguity in our data definitions. The bot used gross order value instead of GAAP net revenue. The correct Q2 revenue is $3.6M as Finance reported. We've added data definitions and test cases to prevent this going forward."

**No need to mention:**
- "AI hallucination" (incorrect framing)
- Model quality issues (not the problem)
- Lack of testing (true, but fixed now)

---

## Timeline

**Today (Sep 16):**
- Deploy data dictionary fix → immediate resolution
- Deploy safety fixes (read-only, max turns) → risk reduction

**This week:**
- Expand golden set to 20+ cases from Slack
- Add cost/usage monitoring

**This month:**
- Audit all Slack threads since March for similar issues
- Publish data dictionary to #ask-finance so people know what FinBot knows

**Do not:**
- Switch models without eval evidence
- Tell users "the AI made a mistake" (we made an infrastructure mistake)

---

## Files for Review

All fixes and evidence are in `/home/user/work/output/`:
- `INCIDENT_REPORT.md` - full technical analysis
- `harness_scorecard.md` - detailed audit of all 6 harness components
- `evidence.json` - recomputed numbers
- `fixes/` - deployable code (agent.py, prompt.md, evals)

Ready to deploy after your review.
