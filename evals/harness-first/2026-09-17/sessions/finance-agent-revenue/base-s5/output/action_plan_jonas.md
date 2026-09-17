# Action Plan for Jonas (Data Team)

## Immediate Fix (Deploy Today)

### Step 1: Update the System Prompt
**File:** `prompt.md`  
**Action:** Replace with `output/prompt_UPDATED.md`

```bash
# Backup the old prompt
cp prompt.md prompt.md.backup_sept16

# Deploy the new prompt
cp output/prompt_UPDATED.md prompt.md

# Restart finbot (if needed)
# [Add your deployment command here]
```

### Step 2: Verify the Fix
```bash
# Run the validation script
python3 output/validation_tests.py

# Expected output: ✅ ALL TESTS PASSED
```

### Step 3: Test with Real Questions
Test finbot with these questions and verify it now gives correct answers:

| Question | Expected Answer | Table Used |
|----------|----------------|------------|
| "What was Q2 2026 revenue?" | $3.6M | revenue_recognized |
| "What were Q2 2026 bookings?" | $4.1M | orders |
| "How much did we make in April 2026?" | $1.2M | revenue_recognized |

---

## This Week: Validation & Documentation

### Add Automated Testing
Create a scheduled job that runs `validation_tests.py` daily:
- Compares finbot answers to known Finance numbers
- Alerts if discrepancies are found
- Catches similar issues before they reach executives

### Document the Warehouse Tables
Create a data dictionary that explains:

**revenue_recognized** (GAAP Revenue)
- What: Official recognized revenue, net of refunds
- When: Use for financial reporting, board materials, investor updates
- Fields: `net_amount` (use this), `gross_amount` (don't use)
- Date field: `recognized_on`

**orders** (Bookings/Pipeline)
- What: Gross bookings including all statuses
- When: Use for sales analysis, pipeline tracking
- ⚠️ WARNING: Includes refunded/cancelled orders
- Date field: `created_at`
- Status values: completed, refunded, cancelled, partially_refunded

**daily_kpis** (Operational Metrics)
- What: Pre-aggregated daily metrics
- **NOTE:** Q2 2026 shows $2.3M (investigate what this represents)
- Action item: Document what `daily_kpis.revenue` actually measures

### Update Slack Bot Message
Add a disclaimer to finbot responses for revenue questions:

```
Q2 2026 revenue was $3.6M.

ℹ️ Note: For board materials and official reporting, please verify with Finance.
```

---

## Next Sprint: Prevent Future Issues

### 1. Add Query Logging
Log all queries finbot generates:
- Store: question asked, SQL generated, result returned
- Enables: Audit trail, pattern analysis, training data
- Review: Weekly review of queries to catch issues

### 2. Create Finance Review Process
For board deck / investor materials:
- ✅ Get numbers from finbot (for speed)
- ✅ Flag for Finance verification (required)
- ✅ Document source in deck notes
- ❌ Never use unverified finbot numbers in external materials

### 3. Add Schema Context to Prompt
Consider adding example queries directly in the prompt:

```markdown
Common questions and correct queries:

Q: "What was Q2 revenue?"
A: SELECT SUM(net_amount) FROM revenue_recognized 
   WHERE recognized_on BETWEEN '2026-04-01' AND '2026-06-30'

Q: "What were our Q2 bookings?"
A: SELECT SUM(amount) FROM orders 
   WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30'
```

### 4. Consider Query Templates
Create a library of pre-approved SQL templates:
- `get_quarterly_revenue(quarter, year)` → uses revenue_recognized
- `get_quarterly_bookings(quarter, year)` → uses orders
- `get_monthly_revenue(month, year)` → uses revenue_recognized

Give finbot a tool to use templates instead of writing raw SQL.

---

## Long-term: Model Improvements

**Note:** These are nice-to-haves, NOT urgent. The prompt fix solves the immediate issue.

### Option 1: Query Validation Tool
Give the model a `validate_query` tool that:
- Checks SQL against business rules
- Warns: "Using orders table for revenue—did you mean revenue_recognized?"
- Returns: Suggested alternative query

### Option 2: Few-Shot Examples
Add example Q&A pairs to the prompt:
- Shows the model correct reasoning
- Demonstrates table selection logic
- Provides pattern to follow

### Option 3: Dual-Query Strategy
For revenue questions, run BOTH queries:
```
From revenue_recognized: $3.6M (GAAP revenue)
From orders: $4.1M (gross bookings)
Note: For financial reporting, use the GAAP revenue figure.
```

---

## Monitoring & Alerts

Set up alerts for:
- ❌ Any query using `orders.amount` for revenue questions
- ❌ Large discrepancies between finbot and Finance numbers
- ❌ Questions about revenue that don't use revenue_recognized
- ✅ Weekly summary of most common questions

---

## Communication Plan

### Today
- ✅ Share executive_summary.md with Daniel
- ✅ Share this action plan with data team
- ✅ Deploy the prompt update

### This Week
- Email to #ask-finance channel:
  ```
  📢 FinBot Update: We've improved how finbot handles revenue questions.
  
  For board materials and official reporting, please continue to verify 
  numbers with Finance. FinBot is great for quick estimates and trends!
  
  Questions? Ask in #data-eng
  ```

### Ongoing
- Include finbot in data quality review meetings
- Document "known issues" and "resolved issues"
- Celebrate: This is a good example of catching and fixing data issues!

---

## Success Metrics

After deploying the fix, track:
- ✅ Zero revenue discrepancies in board materials (check monthly)
- ✅ Validation tests pass daily
- ✅ Finance team confidence in finbot numbers
- ✅ Reduced "finbot was wrong" Slack messages

---

## Summary Checklist

**Today:**
- [ ] Backup current prompt.md
- [ ] Deploy prompt_UPDATED.md
- [ ] Run validation_tests.py (verify all pass)
- [ ] Test with sample questions
- [ ] Share results with Daniel

**This Week:**
- [ ] Add finbot query logging
- [ ] Document warehouse table purposes
- [ ] Create finance verification process
- [ ] Add disclaimer to bot responses

**Next Sprint:**
- [ ] Set up automated testing
- [ ] Investigate daily_kpis discrepancy
- [ ] Consider query templates
- [ ] Review monitoring/alerts

---

## Contact for Questions

**About this issue:** [Your team]  
**About finbot code:** Jonas (Data)  
**About revenue numbers:** Marta (Finance)  
**About board materials:** Priya (Strategy)

---

**Estimated time to fix:** 30 minutes  
**Estimated time to deploy:** 5 minutes  
**Risk level:** Low (prompt-only change, easily reversible)  
**Impact:** High (prevents future board deck errors)
