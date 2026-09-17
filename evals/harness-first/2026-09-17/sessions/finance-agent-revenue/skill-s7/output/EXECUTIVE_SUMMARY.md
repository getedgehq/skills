# Executive Summary: FinBot Q2 Revenue Incident
**For:** Daniel Kurz (CEO)  
**Date:** 2026-09-16  
**Re:** "Is the model just hallucinating?"

---

## Bottom Line

**The model is NOT hallucinating. Don't switch models yet.**

The agent used the wrong data source because it had two "revenue" tables with no guidance on which to use. This is a **data layer problem**, not a model intelligence problem.

---

## What Happened

| Source | Q2 Revenue | What It Measures |
|--------|------------|------------------|
| **FinBot** | **$4.1M** | Gross orders (before refunds) from `orders` table |
| **Finance** | **$3.6M** | Net recognized revenue from `revenue_recognized` table |
| **Gap** | **$500K** | Refunds ($332K) + timing differences ($167K) |

I verified both numbers independently - they're both mathematically correct from their respective tables.

---

## Root Cause

**Missing data dictionary.** The agent had:
- ✅ A working model that writes correct SQL
- ✅ Two tables with revenue-related data
- ❌ No definition of which table = "revenue" 
- ❌ No test cases to catch this before it reached the board

The prompt lists both tables but doesn't say when to use each. Any model (Sonnet, Opus, GPT-6) would have the same ambiguity.

---

## What Would Have Prevented This

1. **Data dictionary** defining "revenue = revenue_recognized.net_amount"
2. **Golden test set** with Q2 revenue from a prior quarter as a known-good answer
3. **Eval script** that catches 13% discrepancies before shipping

All three were missing.

---

## Immediate Actions Taken

✅ **Root cause documented** with full evidence (see INCIDENT_REPORT.md)  
✅ **Data dictionary created** defining every metric  
✅ **Fixed prompt** that explicitly states which table to use for revenue  
✅ **Golden set built** with 20 test cases including this incident  
✅ **Eval script written** to test future changes  
✅ **Agent hardening:** Added max iterations, read-only DB, basic tracing  

---

## Should We Switch Models?

**Not yet.** The current model did exactly what it was asked - it just had ambiguous instructions.

**Test after fixing:** Once the data dictionary and prompt are deployed, if you want to compare models, run the golden set on both Sonnet and alternatives and compare pass rate + cost. I predict similar performance since this was a data problem.

---

## Other Risks Found

1. ⚠️ Infinite loop (no max iterations) - **FIXED**
2. ⚠️ No tracing/audit logs - **FIXED** 
3. ⚠️ No cost caps - needs follow-up
4. ⚠️ No change control - needs follow-up

---

## Cost Impact

**Token spend:** ~$0 saved (the query was efficient)  
**Business impact:** Avoided wrong financials in board deck = **priceless**

---

## Next Steps (1 week)

1. Deploy fixed prompt + data dictionary
2. Run golden set to baseline pass rate
3. Set up "flag for review" in Slack → auto-adds to golden set
4. Require golden set pass before any future prompt/model changes

---

**Files delivered in `/output`:**
- Full incident report with evidence
- Data dictionary
- Fixed agent code, prompt, and config
- Golden test set (20 cases)
- Eval script

Contact me if you need the analysis re-run or want to test other models.
