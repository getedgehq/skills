# FinBot Q2 Revenue Discrepancy - Investigation Results

**Investigation Date:** September 15, 2026  
**Issue:** FinBot reported Q2 revenue as $4.1M, Finance says $3.6M  
**Status:** ✅ Root cause identified, fix ready to deploy

---

## Quick Summary

**The bot is NOT hallucinating.** It queried the wrong database table.

- FinBot used `orders` table → $4.1M (includes cancelled/refunded orders)
- Finance uses `revenue_recognized` table → $3.6M (correct accounting)
- Fix: Update the system prompt to specify which table to use
- **No model upgrade needed**

---

## Files in This Directory

### 📄 EXEC_SUMMARY.md
**→ START HERE for Daniel**

One-page executive summary with:
- What happened and why
- Why upgrading the model won't help
- The fix and action plan
- Impact assessment

### 📄 root_cause_analysis.md
**→ Full technical analysis**

Comprehensive report including:
- Detailed breakdown of the $500K discrepancy
- SQL queries showing the exact problem
- Why this is a prompt issue, not a model issue
- Recommended fixes (3 options)
- Testing plan
- Lessons learned

### 📄 prompt_FIXED.md
**→ The solution**

Updated system prompt with:
- Clear table usage guidelines
- Schema documentation
- Example queries for revenue questions
- Rules to prevent this issue

**To deploy:** Replace `/prompt.md` with this file

### 🐍 test_finbot_fix.py
**→ Verification script**

Run this to verify the fix works:
```bash
python test_finbot_fix.py
```

Tests:
- ✅ Q2 revenue returns $3.6M (not $4.1M)
- ✅ Monthly breakdowns are correct
- ✅ Order count queries still work
- Shows before/after comparison

### 📊 verification_queries.sql
**→ SQL analysis**

SQL queries to reproduce the investigation:
- What finbot queried (wrong)
- What finance uses (correct)
- Breakdown by order status
- Sample cancelled orders

Run in any SQL client against `warehouse.db`

### 📊 detailed_analysis.csv
**→ Spreadsheet-friendly breakdown**

CSV with:
- Side-by-side comparison of methods
- Order status breakdown
- Monthly revenue details
- What should/shouldn't be counted

### 📊 quarterly_comparison.csv
**→ Q1 and Q2 comparison**

Shows the problem affected both quarters:
- Q1: $4.1M (finbot) vs $3.3M (finance) - 26% error
- Q2: $4.1M (finbot) vs $3.6M (finance) - 14% error

---

## How to Fix This

### Step 1: Deploy the fix (5 minutes)
```bash
# Backup current prompt
cp prompt.md prompt.md.backup

# Deploy fixed prompt
cp output/prompt_FIXED.md prompt.md
```

### Step 2: Test it (2 minutes)
```bash
# Test Q2 query
python agent.py "what was Q2 2026 revenue?"
# Should return: ~$3.6M

# Run full test suite
python output/test_finbot_fix.py
# Should show: ✓ FINBOT FIX VERIFIED
```

### Step 3: Correct the board deck
- Update Q2 revenue from $4.1M to $3.6M
- Update Q1 revenue from $4.1M to $3.3M (also wrong)
- Note: Q2 was actually DOWN 11% QoQ, not flat

### Step 4: Audit other uses (this week)
- Search #ask-finance for "revenue", "sales", "income"
- Check which responses went into other documents
- Flag anything that needs correction

---

## Key Findings

### The Numbers
| Metric | FinBot | Finance | Difference |
|--------|--------|---------|------------|
| Q2 2026 Revenue | $4,138,212 | $3,638,336 | $499,876 (14% high) |
| Q1 2026 Revenue | $4,141,986 | $3,285,494 | $856,492 (26% high) |

### Why FinBot Was Wrong
FinBot counted ALL orders created in Q2, including:
- ✅ Completed orders: $3.27M
- ✅ Partially refunded: $0.32M
- ❌ **Cancelled orders: $0.36M** ← Should not count
- ❌ **Refunded orders: $0.19M** ← Should not count

### Why Finance Is Right
Finance uses the `revenue_recognized` table which:
- Follows proper revenue recognition accounting
- Automatically excludes cancelled orders
- Nets out refunds ($332K in Q2)
- Uses recognition date, not order date
- Handles subscription revenue properly

### Is the Model Bad?
**No.** The model did exactly what you'd expect:
- ✅ Generated valid SQL
- ✅ Returned accurate data from the table it queried
- ✅ Formatted the answer clearly
- ❌ **But guessed the wrong table** (prompt didn't specify)

Even GPT-6 or Claude Opus would likely make the same mistake without explicit guidance. This is a **domain knowledge** issue that needs to be in the prompt.

---

## Preventing This in the Future

### Immediate
1. ✅ Update prompt with table usage rules
2. ✅ Test with known-good queries
3. ✅ Document which tables are "source of truth"

### Short Term
1. Create a test suite for common queries
2. Set up monthly validation (finbot vs finance reports)
3. Add schema documentation to the prompt

### Long Term
1. Consider query validation (block obvious errors)
2. Add logging to track which queries are run
3. Periodic audit of Slack responses

---

## Questions?

**Q: Do we need a better model?**  
A: No. The model is fine. We need a better prompt.

**Q: How did this get past testing?**  
A: The bot was built in a hackathon. Likely wasn't validated against official finance numbers.

**Q: Could this happen with other metrics?**  
A: Potentially. Should review prompt for other ambiguous cases.

**Q: How long has this been wrong?**  
A: Since March 2026 (6 months). Need to audit Slack history.

**Q: Is the warehouse data bad?**  
A: No. Both tables have correct data. FinBot just queried the wrong one.

---

## Contact

Investigation by: AI Assistant  
For questions about:
- The fix: Jonas (Data team)
- Finance impact: Marta (VP Finance)
- Board deck: Priya (Strategy)
- Overall decision: Daniel (CEO)

---

**Next Step:** Read `EXEC_SUMMARY.md` for the one-page version.
