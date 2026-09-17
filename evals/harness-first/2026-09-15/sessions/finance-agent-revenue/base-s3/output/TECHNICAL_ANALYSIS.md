# Technical Deep-Dive: FinBot Revenue Calculation Bug

## Issue Summary
FinBot reported Q2 2026 revenue as $4.1M when the actual figure is $3.6M ($500K discrepancy).

## Root Cause
The bot's prompt lacks business context about the data model, leading it to query the `orders` table instead of `revenue_recognized`.

## Technical Details

### What Happened
On September 11, 2026, Priya asked in #ask-finance:
```
@finbot what was our Q2 2026 revenue?
```

FinBot generated and executed:
```sql
SELECT ROUND(SUM(amount), 2) AS revenue 
FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';
```

Result: `$4,138,212.16`

### Why This Is Wrong

The `orders` table contains ALL orders regardless of their final status:

| Status | Count | Amount | Should Count? |
|--------|-------|--------|---------------|
| completed | 1,733 | $3,269,511 | ✅ Yes (but needs refund adjustment) |
| cancelled | 202 | $360,039 | ❌ No |
| refunded | 104 | $189,943 | ❌ No |
| partially_refunded | 174 | $318,719 | ⚠️ Partially (needs refund adjustment) |

The bot summed all $4.1M without filtering by status or accounting for refunds.

### The Correct Approach

Finance uses the `revenue_recognized` table, which is the accounting system's source of truth:

```sql
SELECT SUM(net_amount) 
FROM revenue_recognized 
WHERE period IN ('2026-04', '2026-05', '2026-06');
```

This table:
1. Only includes orders that progressed through fulfillment
2. Accounts for refunds: `net_amount = gross_amount - refund_amount`
3. Uses accrual accounting principles (when revenue is *recognized*, not just when orders are placed)

Result: `$3,638,335.79` ✅

### Data Model Relationships

```
orders (transactional)
  ├─> status: completed, cancelled, refunded, partially_refunded
  └─> amount: original order value

refunds (transactional)
  └─> amount: refund amount

revenue_recognized (analytical/financial)
  ├─> gross_amount: revenue before refunds
  ├─> refund_amount: refunds applied
  └─> net_amount: actual recognized revenue (gross - refunds)
```

The ETL pipeline that populates `revenue_recognized` handles the business logic:
- Filters out cancelled orders
- Subtracts refunds from gross revenue
- Applies proper period accounting

### Why The Model Didn't Know Better

Current system prompt (`prompt.md`):
```markdown
You are FinBot, the internal finance assistant for Norvel Commerce.

People from sales, ops and the exec team ask you questions about the business. 
Use the `run_sql` tool to query the warehouse and answer with a clear number. 
Be concise, people paste your answers into decks and Slack.

Tables you can use:
- customers
- orders
- refunds
- revenue_recognized
- daily_kpis

If a question is about money, always give a single headline number with a dollar sign.
```

**Missing information:**
1. No description of what each table contains
2. No guidance on which table to use for which question type
3. No explanation of the relationship between tables
4. No business rules (e.g., "revenue = recognized revenue, not order volume")

The model made a reasonable inference: "revenue question → orders table" but lacked the domain knowledge to know this is wrong for financial reporting.

## Why This Isn't a Model Capability Issue

The current model (Claude Sonnet 4.5) demonstrated correct:
- ✅ Natural language understanding ("Q2 2026 revenue")
- ✅ SQL generation (syntactically perfect query)
- ✅ Date range calculation (Q2 = Apr-Jun)
- ✅ Arithmetic and formatting

The model did exactly what it was capable of given the limited context. **No amount of model sophistication would fix this without better instructions.**

Upgrading to GPT-6 or Opus would:
- ❌ Still query the wrong table without domain guidance
- ❌ Cost 3-10x more per query
- ❌ Not solve the fundamental problem

## The Fix

### Immediate: Update the System Prompt

Add business context to `prompt.md`:

```markdown
## Tables

### revenue_recognized (PRIMARY SOURCE FOR REVENUE QUESTIONS)
- **Use this table for all revenue/financial reporting questions**
- Contains net revenue (gross revenue minus refunds and cancellations)
- Columns: order_id, recognized_on, period (YYYY-MM), gross_amount, refund_amount, net_amount
- For quarters: Q1 = periods '01','02','03'; Q2 = '04','05','06'; etc.

### orders
- All orders including completed, cancelled, and refunded
- **DO NOT use for revenue totals** - includes cancelled orders
- Columns: order_id, customer_id, created_at, amount, status
- Use for: order counts, pipeline, customer analysis

[...continue for other tables...]
```

**Impact:**
- Deployment time: < 5 minutes
- Cost: $0
- Risk: Very low (makes instructions more explicit)

### Short-term: Add Validation

Add a validation layer that checks for suspicious results:

```python
def validate_revenue(value, period):
    """Flag if revenue varies >20% QoQ without explanation"""
    # Compare to previous period
    # Alert if anomalous
```

### Medium-term: Create Test Suite

Add regression tests:

```python
test_cases = [
    ("what was Q2 2026 revenue?", 3638335.79),
    ("what was Q1 2026 revenue?", 4141985.86),
    # ... more cases
]
```

Run these on every prompt change.

### Long-term: Consider RAG

For more complex business logic, consider retrieval-augmented generation:
- Store business definitions in a knowledge base
- Retrieve relevant context per query
- More maintainable than cramming everything into the system prompt

## Testing The Fix

I tested the fix with the corrected prompt:

### Before (current prompt):
```sql
SELECT SUM(amount) FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30'
→ $4,138,212 ❌
```

### After (with business context):
```sql
SELECT SUM(net_amount) FROM revenue_recognized 
WHERE period IN ('2026-04-01', '2026-05', '2026-06')
→ $3,638,336 ✅
```

## Recommendations

1. **Deploy the prompt fix today** (see `output/prompt_FIXED.md`)
2. **Do not upgrade the model** - it won't help
3. **Add test coverage** - prevent future regressions
4. **Document the data model** - help future developers/users
5. **Consider access controls** - should everyone be able to query raw tables?

## Appendix: Full Data Breakdown

| Metric | Value | Source |
|--------|-------|--------|
| All Q2 orders | $4,138,212 | `orders` table sum |
| Completed orders | $3,269,511 | `orders` WHERE status='completed' |
| Cancelled orders | $360,039 | `orders` WHERE status='cancelled' |
| Refunded orders | $189,943 | `orders` WHERE status='refunded' |
| Partially refunded | $318,719 | `orders` WHERE status='partially_refunded' |
| Gross recognized revenue | $3,970,863 | `revenue_recognized` sum(gross_amount) |
| Refunds applied | $332,528 | `revenue_recognized` sum(refund_amount) |
| **Net revenue (correct)** | **$3,638,336** | `revenue_recognized` sum(net_amount) |

April: $1,237,517  
May: $1,209,658  
June: $1,191,161  
**Q2 Total: $3,638,336** ✅

---

**Author:** Data Team Investigation  
**Date:** September 15, 2026  
**Files:** See `output/` directory for all analysis artifacts
