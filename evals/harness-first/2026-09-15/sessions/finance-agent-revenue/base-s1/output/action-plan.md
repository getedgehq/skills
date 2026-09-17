# Action Plan - Fixing FinBot Revenue Issue

## Immediate Actions (Do Today)

### 1. Correct the Board Deck (5 min)
**Owner:** Priya (Strategy)

Change Q2 revenue from **$4.1M** to **$3.6M**

**Verification:**
```sql
SELECT ROUND(SUM(net_amount)/1000000, 1) as revenue_millions
FROM revenue_recognized 
WHERE period IN ('2026-04', '2026-05', '2026-06');
-- Result: 3.6 (rounded)
```

---

### 2. Deploy Prompt Fix (15 min)
**Owner:** Jonas (Data) or engineer on call

**Steps:**
1. Backup current prompt:
   ```bash
   cp prompt.md prompt.md.backup
   ```

2. Replace with fixed version:
   ```bash
   cp output/prompt-fixed.md prompt.md
   ```

3. Restart FinBot (if needed)

**The change:** Added explicit guidance to use `revenue_recognized` table for revenue questions.

---

### 3. Test the Fix (10 min)
**Owner:** Jonas or QA

Run these test queries:

**Test 1: Original question**
```
@finbot what was our Q2 2026 revenue?
```
✅ Expected: ~$3.6M (or $3,638,335.79)  
❌ Old behavior: $4.1M

**Test 2: Monthly revenue**
```
@finbot show me revenue by month for Q2
```
✅ Expected: April $1.24M, May $1.21M, June $1.19M

**Test 3: Bookings vs Revenue**
```
@finbot what were our bookings in Q2?
```
✅ Expected: Should still use orders table, return ~$4.1M  
(Bookings ≠ revenue, this is correct)

**Test 4: Make sure it still works for other questions**
```
@finbot how many customers do we have?
@finbot what were our top 5 orders in June?
```

---

### 4. Notify Stakeholders (5 min)
**Owner:** Marta (Finance) or Daniel

Post in #exec-staff and #ask-finance:

> **FinBot revenue issue - RESOLVED**
> 
> The Q2 revenue discrepancy has been identified and fixed.
> 
> **What happened:** FinBot used the wrong table (order bookings instead of recognized revenue)
> **Correct Q2 revenue:** $3.6M (from revenue_recognized table)
> **Fix deployed:** Updated bot instructions to always use the correct table
> **Board deck:** Being updated now
> 
> The model was NOT hallucinating - it returned accurate data but from the wrong source. Simple configuration fix, no model upgrade needed.
> 
> Questions? DM Jonas or see full analysis in /output/

---

## Follow-Up Actions (This Week)

### 5. Add Data Quality Checks (1 hour)
**Owner:** Jonas (Data)

Add validation in agent.py:
```python
def run_sql(query):
    # Existing code...
    
    # Warn if querying orders for revenue
    if 'orders' in query.lower() and any(word in query.lower() for word in ['revenue', 'sales']):
        print("⚠️  WARNING: Querying orders table for revenue. Consider revenue_recognized instead.")
    
    # Rest of function...
```

---

### 6. Fix daily_kpis ETL (2 hours)
**Owner:** Data/ETL team

**Issue:** daily_kpis only has data through May 19, 2026 (missing 6+ weeks)

**Fix:** 
- Check why ETL stopped on May 19
- Backfill missing data
- OR remove table from FinBot's access if it's not maintained

---

### 7. Create Data Dictionary (2 hours)
**Owner:** Jonas (Data) + Marta (Finance)

Document in wiki or README:

| Table | Purpose | Use For | Don't Use For |
|-------|---------|---------|---------------|
| revenue_recognized | GAAP revenue reporting | Revenue, sales questions | Real-time data |
| orders | Order bookings | Order counts, bookings | Revenue (use net, not gross) |
| refunds | Refund tracking | Refund analysis | - |
| customers | Customer metadata | Customer lookups | - |
| daily_kpis | Daily operations | Trend monitoring | Quarterly reports (incomplete) |

---

### 8. Add More Examples to Prompt (30 min)
**Owner:** Jonas

Expand prompt.md with common questions:
- "What was revenue last quarter?"
- "Show me monthly revenue trend"
- "What's our run rate?"
- "How much did we book this month?" (should use orders, not revenue_recognized)

---

### 9. Review Other Metrics (1 hour)
**Owner:** Marta (Finance) + Jonas

Check if FinBot might be returning wrong data for other metrics:
- Churn rate
- MRR/ARR
- Customer counts
- Refund rates

Same root cause: unclear which table to use.

---

## Long-Term Improvements (Next Sprint)

### 10. Add Confidence Scores
Have FinBot indicate when it's uncertain:
```
Q2 2026 revenue was $3.6M (from revenue_recognized table)
⚠️  Note: orders table shows $4.1M in bookings, but revenue_recognized is the source of truth for financial reporting.
```

---

### 11. Create Finance Bot Runbook
Document:
- How FinBot works
- Which tables to use for what
- Common queries and expected results
- Troubleshooting steps
- Who owns what

---

### 12. Add Tool Usage Logging
Track which queries FinBot runs:
- Which tables get queried
- For what questions
- Results returned
- Flag anomalies (large discrepancies between tables)

---

## Success Criteria

✅ FinBot returns $3.6M for "Q2 2026 revenue"  
✅ Board deck shows correct number  
✅ Team understands root cause (not model problem)  
✅ Documentation updated  
✅ No model upgrade initiated  

---

## Cost Analysis

| Option | Cost | Timeline | Solves Problem? |
|--------|------|----------|-----------------|
| **Fix prompt (our plan)** | 1-2 eng hours | Today | ✅ Yes |
| **Upgrade to GPT-6** | ~$500-2000/month | 1 week | ❌ No |
| **Upgrade to Opus** | ~$300-1500/month | 1 week | ❌ No |
| **Hire consultant** | $10k+ | 2+ weeks | Maybe |
| **Replace with human** | $80k/year | 4+ weeks | Yes, but expensive |

**ROI of prompt fix:** Saves $500+/month vs model upgrade, fixes in 1 day vs 1 week+

---

## Owner Summary

| Task | Owner | Deadline | Status |
|------|-------|----------|--------|
| Fix board deck | Priya | Today EOD | 🟡 Pending |
| Deploy prompt | Jonas | Today EOD | 🟡 Pending |
| Test fix | Jonas | Today EOD | 🟡 Pending |
| Notify team | Marta/Daniel | Today EOD | 🟡 Pending |
| Fix daily_kpis | Data team | This week | 🟡 Pending |
| Data dictionary | Jonas + Marta | This week | 🟡 Pending |
| Code review | Engineering | Next sprint | 🟡 Pending |

---

## Questions?

- Technical details → See `technical-analysis.md`
- Full explanation → See `incident-report.md`
- Updated prompt → See `prompt-fixed.md`
- Executive summary → See `exec-summary.md`

Contact: Jonas (Data team) or file in #ask-finance
