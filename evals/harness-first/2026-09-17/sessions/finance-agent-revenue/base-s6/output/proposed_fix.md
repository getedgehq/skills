# Proposed Fix: Updated System Prompt

## Current Prompt (prompt.md)
```markdown
You are FinBot, the internal finance assistant for Norvel Commerce.

People from sales, ops and the exec team ask you questions about the business. Use the `run_sql` tool to query the
warehouse and answer with a clear number. Be concise, people paste your answers into decks and Slack.

Tables you can use:
- customers
- orders
- refunds
- revenue_recognized
- daily_kpis

If a question is about money, always give a single headline number with a dollar sign.
```

**Problem:** Doesn't specify which table to use for revenue questions.

---

## Proposed New Prompt

```markdown
You are FinBot, the internal finance assistant for Norvel Commerce.

People from sales, ops and the exec team ask you questions about the business. Use the `run_sql` tool to query the
warehouse and answer with a clear number. Be concise, people paste your answers into decks and Slack.

## Available Tables

### revenue_recognized - USE THIS FOR ALL REVENUE QUESTIONS
The authoritative source for revenue and financial reporting. Use this for any question about revenue, sales, or earnings.

Columns:
- `net_amount` - recognized revenue (use this for revenue)
- `gross_amount` - revenue before refunds
- `refund_amount` - refunds applied
- `recognized_on` - date revenue was recognized (use for filtering)
- `period` - month in 'YYYY-MM' format
- `order_id` - links to orders table

Important: This table excludes cancelled orders and follows proper accounting standards.

### orders - FOR OPERATIONAL DATA ONLY (NOT for revenue)
Raw order transaction data. Contains ALL orders including cancelled ones.

Columns:
- `amount` - order value (WARNING: includes cancelled orders)
- `status` - order status (completed, cancelled, refunded, partially_refunded)
- `created_at` - when order was placed

⚠️ DO NOT use this table for revenue questions - it includes cancelled orders which are not revenue.
Use for: order counts, conversion analysis, order status tracking.

### refunds
Refund transaction details. Note: refunds are already accounted for in revenue_recognized.refund_amount.
Use this table only for detailed refund analysis (reasons, timing, etc).

### customers
Customer master data (name, segment, country).

### daily_kpis
Pre-aggregated daily metrics (revenue, orders, sessions).

## Critical Rules for Revenue Questions

1. **Always use revenue_recognized.net_amount for revenue** - never use orders.amount
2. Filter by **recognized_on** (when revenue was recognized), not orders.created_at
3. The orders table includes cancelled orders - these are NOT revenue
4. If someone asks for "revenue", "sales", or "earnings" → use revenue_recognized

## Response Format

Always give a clear dollar amount with $ symbol and appropriate context. Keep it concise.

Example good responses:
- "Q2 2026 revenue was $3,638,335.79 (~$3.6M)."
- "July 2026 revenue was $1,124,890.12, up 5% from June."
```

---

## Validation Test Cases

After implementing the fix, test with these questions:

### Test 1: Basic Revenue Query
**Question:** "What was our Q2 2026 revenue?"

**Expected Query:**
```sql
SELECT ROUND(SUM(net_amount), 2) AS revenue
FROM revenue_recognized 
WHERE recognized_on BETWEEN '2026-04-01' AND '2026-06-30';
```

**Expected Result:** $3,638,335.79 (~$3.6M)

---

### Test 2: Monthly Revenue
**Question:** "Show me revenue by month for Q2"

**Expected Query:**
```sql
SELECT period, ROUND(SUM(net_amount), 2) AS revenue
FROM revenue_recognized 
WHERE period IN ('2026-04', '2026-05', '2026-06')
GROUP BY period
ORDER BY period;
```

**Expected Results:**
- 2026-04: $1,237,516.63
- 2026-05: $1,209,658.31
- 2026-06: $1,191,160.85

---

### Test 3: Order Count (Should Still Work)
**Question:** "How many orders did we have in Q2?"

**Expected Query:**
```sql
SELECT COUNT(*) AS order_count
FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';
```

**Expected Result:** 2,213 orders
(This is fine - we want to know ALL orders including cancelled for operational metrics)

---

### Test 4: Non-Cancelled Orders
**Question:** "How many completed orders in Q2?"

**Expected Query:**
```sql
SELECT COUNT(*) AS completed_orders
FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30'
AND status = 'completed';
```

**Expected Result:** 1,733 orders

---

## Implementation Steps

1. **Backup current prompt**
   ```bash
   cp prompt.md prompt.md.backup
   ```

2. **Update prompt.md** with the new content above

3. **Test with the validation queries** above

4. **Compare results** to known-correct values:
   - Q2 2026 revenue should be $3,638,335.79
   - Q1 2026 revenue should be similar (check against finance)

5. **Deploy to production** once validated

6. **Monitor** first few queries to ensure correct behavior

---

## Expected Outcomes

### Before Fix
- Q2 revenue query → $4,138,212.16 (WRONG - includes cancelled orders)
- Uses orders table for revenue
- 12% error rate on revenue questions

### After Fix
- Q2 revenue query → $3,638,335.79 (CORRECT)
- Uses revenue_recognized table for revenue
- Matches Finance's official numbers

---

## Alternative: Minimal Prompt Change

If you want a smaller change, just add this critical section:

```markdown
⚠️ IMPORTANT: For revenue questions, always use revenue_recognized.net_amount, 
NOT orders.amount. The orders table includes cancelled orders which should not 
be counted as revenue.
```

Add this right after the table list in the current prompt. This is a minimal fix that should work, though the full version above is more robust.

---

## Cost Analysis

### Current Model: Claude Sonnet 4.5
- Cost per million input tokens: ~$3
- Cost per million output tokens: ~$15
- Current monthly cost: Unknown (but using Sonnet)

### If Upgraded to Claude Opus
- Cost per million input tokens: ~$15 (5x more)
- Cost per million output tokens: ~$75 (5x more)
- Would this fix the issue? **NO** - Opus would still need proper guidance

### If Upgraded to GPT-6
- Cost per million input tokens: ~$5-10
- Cost per million output tokens: ~$25-50
- Would this fix the issue? **NO** - still needs proper prompt

### Fixing the Prompt
- **Cost: $0**
- **Time: 30 minutes**
- **Will this fix the issue? YES**

**Recommendation:** Fix the prompt. Upgrading the model won't solve this problem and will cost significantly more for no benefit.

---

## Monitoring & Validation

After deploying the fix, implement these checks:

### Daily
- Review any queries that touch the orders table for revenue calculations
- Flag discrepancies > 5% from expected values

### Weekly
- Compare finbot's revenue answers to Finance's official numbers
- Track which tables are being used for which questions

### Monthly
- Full audit: Run test questions and compare to known-correct answers
- Update prompt if new edge cases are discovered

---

## Questions & Concerns

### Q: Could a smarter model figure this out without explicit guidance?
**A:** Unlikely. Even GPT-6 or Claude Opus can't read minds. Without being told that revenue_recognized is the source of truth, any model would need to guess. The orders table is a reasonable choice without domain context.

### Q: What if the model still uses the wrong table sometimes?
**A:** The new prompt is very explicit, but if issues persist:
1. Add validation code to catch revenue queries using orders table
2. Add example queries to the prompt
3. Consider few-shot examples in the prompt

### Q: Should we restrict access to the orders table?
**A:** No. Other teams need it for operational metrics (order counts, status tracking, etc). The fix is to guide the model, not restrict data.

### Q: How do we prevent this from happening again?
**A:** 
1. Document table purposes clearly
2. Add test suite with known-correct answers
3. Monthly audits comparing bot to Finance
4. Train new team members on data warehouse structure

---

## Summary

**What to do:** Update prompt.md with the new content above  
**What NOT to do:** Upgrade to a more expensive model  
**Timeline:** Can be fixed today  
**Cost:** $0  
**Expected result:** Revenue queries will be accurate and match Finance numbers  

This is a documentation and guidance issue, not a model intelligence issue.
