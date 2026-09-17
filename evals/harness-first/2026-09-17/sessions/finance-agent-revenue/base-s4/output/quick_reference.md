# Quick Reference: FinBot Revenue Issue

## The Problem in One Sentence
FinBot reported Q2 revenue as $4.1M by summing orders (bookings), but finance's GAAP revenue is $3.6M.

## Why It Happened
The bot doesn't know that "revenue" means GAAP-recognized revenue, not order bookings.

## The Fix
Tell it in the prompt: "For revenue questions, use `revenue_recognized` table, not `orders` table."

## Why Not Upgrade the Model?
No LLM knows your company's tables without being told. This is a documentation fix, not a capability issue.

---

## Numbers Breakdown

| Source | Amount | What It Measures |
|--------|--------|------------------|
| FinBot (orders table) | $4,138,212 | Bookings: all orders placed in Q2 |
| Finance (revenue_recognized) | $3,638,336 | GAAP revenue: recognized in Q2 |
| **Difference** | **$499,876** | See breakdown below ⬇️ |

## Where the $500K Difference Comes From

1. **Cancelled orders:** $360K orders that never became revenue ✅ in orders ❌ in revenue_recognized
2. **Q2 orders recognized in Q3:** $120K late-quarter orders ✅ in orders ❌ in Q2 revenue
3. **Q1 orders recognized in Q2:** $265K early fulfillment ❌ in orders ✅ in Q2 revenue
4. **Refund adjustments:** $143K net difference in refund accounting

---

## Key Tables Explained

### orders
- **What:** When customers placed orders
- **Amount:** Original order amount
- **Includes:** Cancelled, refunded, all statuses
- **Use for:** Bookings, order counts, pipeline metrics
- **Date field:** `created_at`

### revenue_recognized
- **What:** When revenue was earned (GAAP)
- **Amount:** Net amount after refunds
- **Excludes:** Cancelled orders that never became revenue
- **Use for:** Financial reporting, board metrics, revenue
- **Date field:** `recognized_on`

---

## Example Queries

### ✅ CORRECT - Revenue Question
```sql
-- "What was Q2 revenue?"
SELECT SUM(net_amount) 
FROM revenue_recognized 
WHERE recognized_on BETWEEN '2026-04-01' AND '2026-06-30';
-- Result: $3,638,335.79 ✅
```

### ❌ INCORRECT - What FinBot Did
```sql
-- "What was Q2 revenue?"
SELECT SUM(amount) 
FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';
-- Result: $4,138,212.16 ❌ (This is bookings, not revenue!)
```

### ✅ CORRECT - Order Count Question
```sql
-- "How many orders in Q2?"
SELECT COUNT(*) 
FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';
-- Using orders table is correct here!
```

---

## Deploy Checklist

- [ ] Review updated prompt in `output/prompt_fix.md`
- [ ] Replace `prompt.md` with updated version
- [ ] Test: `python agent.py "what was Q2 2026 revenue?"`
- [ ] Verify result is $3,638,335.79 (~$3.6M)
- [ ] Test: `python agent.py "how many orders in Q2 2026?"`
- [ ] Verify it still uses orders table correctly
- [ ] Update board pre-read to $3.6M
- [ ] Monitor #ask-finance for next few days

---

## Cost-Benefit Analysis

| Solution | Cost | Time | Effectiveness |
|----------|------|------|---------------|
| **Update prompt** | $0 | 30 min | ✅ Fixes root cause |
| Upgrade to GPT-6/Opus | $50K+/year | 1 week | ❌ Won't fix this |
| Add validation logic | Eng time | 2 hours | ✅ Extra safety net |
| Create simplified views | ETL time | 3 hours | ✅ Makes it foolproof |

**Recommended:** Start with prompt update (free, fast, effective), add validation as time permits.

---

## Files Delivered

1. **executive_summary.md** ← Start here (for Daniel)
2. **incident_report.md** ← Full analysis and recommendations
3. **technical_analysis.md** ← Deep dive for eng team
4. **prompt_fix.md** ← Ready-to-deploy prompt
5. **quick_reference.md** ← This file (cheat sheet)

---

## Key Takeaway

**This is not a "the model isn't smart enough" problem.**

It's a "we didn't tell the model which table to use" problem.

Fix: Better instructions. Cost: $0. Time: 30 minutes.

No model upgrade needed.
