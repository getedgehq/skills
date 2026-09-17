# Quick Reference: What Actually Happened

## The Incident (One Sentence)
FinBot used the wrong database table for "revenue" because there was no data dictionary defining which table to use.

---

## The Numbers

| Source | Amount | Table Used | What It Measures |
|--------|--------|-----------|------------------|
| **FinBot** | $4,138,212 | `orders` | Gross bookings |
| **Finance** | $3,638,336 | `revenue_recognized` | Net recognized revenue |
| **Gap** | $499,876 | - | Refunds + timing |

---

## Why It Wasn't Hallucination

✓ FinBot queried real data from the database  
✓ Math was correct  
✓ SQL was valid  
✓ The number actually exists in `orders.amount`  

✗ It just used the wrong table

---

## What Was Missing

1. **Data dictionary** - No definition of "revenue"
2. **Test cases** - No way to catch this before board deck
3. **Eval process** - No regression testing
4. **Iteration limits** - Could have run forever
5. **Tracing** - Hard to debug issues

---

## What We Fixed

✅ Data dictionary with metric definitions  
✅ Updated prompt with clear table usage  
✅ Golden test set (20 cases)  
✅ Eval script  
✅ Max iterations = 10  
✅ Read-only database  
✅ Logging  

---

## The Right Answer

```sql
-- DON'T use this:
SELECT SUM(amount) FROM orders WHERE ...

-- DO use this:
SELECT SUM(net_amount) FROM revenue_recognized WHERE period IN (...)
```

**Rule:** For revenue questions, always use `revenue_recognized.net_amount` by `period`.

---

## Model Switch?

**No, not yet.**

The model did exactly what any model would do with ambiguous data definitions. Fix the data layer first, then test if you still want to compare models.

---

## Files to Read

1. **EXECUTIVE_SUMMARY.md** - Answer for Daniel (1 page)
2. **README.md** - Overview of everything
3. **VISUAL_COMPARISON.md** - See the two queries side-by-side
4. **data_dictionary.md** - Deploy this!
5. **IMPLEMENTATION_GUIDE.md** - How to fix and test

---

## One-Line Takeaway

**"The model didn't hallucinate - it had two revenue tables and no data dictionary telling it which to use."**
