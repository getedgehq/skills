# Before & After: Prompt Fix Demonstration

## Test Question: "What was our Q2 2026 revenue?"

---

### BEFORE (Current Prompt - INCORRECT)

**System Prompt:**
```
You are FinBot, the internal finance assistant for Norvel Commerce.

Tables you can use:
- customers
- orders
- refunds
- revenue_recognized
- daily_kpis

If a question is about money, always give a single headline number with a dollar sign.
```

**FinBot's Reasoning:**
1. User asks for "revenue"
2. I see an `orders` table with an `amount` column
3. I'll sum the amounts for Q2 dates
4. This seems reasonable

**SQL Generated:**
```sql
SELECT ROUND(SUM(amount), 2) AS revenue 
FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';
```

**Result:**
```
Q2 2026 revenue was $4,138,212.16 (~$4.1M).
```

**What's Wrong:**
- ❌ Includes $360K of cancelled orders
- ❌ Includes $190K of fully refunded orders  
- ❌ Doesn't account for partial refunds
- ❌ Overstates revenue by $500K (13.7%)
- ❌ Doesn't match Finance's books

---

### AFTER (Fixed Prompt - CORRECT)

**System Prompt:**
```
You are FinBot, the internal finance assistant for Norvel Commerce.

## CRITICAL: Table Usage Rules

**For REVENUE questions, ALWAYS use `revenue_recognized` table:**
- Query `revenue_recognized.net_amount` (this is the official GAAP revenue number)
- NEVER use `orders.amount` for revenue questions (includes cancelled orders and ignores refunds)
- Filter by `period` column for month/quarter queries (format: 'YYYY-MM')
  - Example Q1: WHERE period IN ('2026-01', '2026-02', '2026-03')
  - Example Q2: WHERE period IN ('2026-04', '2026-05', '2026-06')

**Other tables:**
- `orders` - Raw transaction data (use for order counts, but NOT revenue totals)
- `refunds` - Individual refund records (already netted out in revenue_recognized)
- `customers` - Customer master data
- `daily_kpis` - Operational metrics (may be incomplete)
```

**FinBot's Reasoning:**
1. User asks for "revenue"
2. My instructions say to ALWAYS use `revenue_recognized.net_amount` for revenue
3. For Q2, I need periods '2026-04', '2026-05', '2026-06'
4. This is the official GAAP number

**SQL Generated:**
```sql
SELECT ROUND(SUM(net_amount), 2) AS revenue
FROM revenue_recognized
WHERE period IN ('2026-04', '2026-05', '2026-06');
```

**Result:**
```
Q2 2026 revenue was $3,638,335.79 (~$3.6M).

Breakdown by month:
- April: $1,237,516.63
- May: $1,209,658.31
- June: $1,191,160.85
```

**What's Right:**
- ✅ Uses official revenue recognition table
- ✅ Net amount already excludes cancelled orders
- ✅ Refunds already netted out
- ✅ Matches Finance's $3.6M close exactly
- ✅ Uses period column for accurate month mapping

---

## Side-by-Side Comparison

| Aspect | BEFORE (Wrong) | AFTER (Correct) |
|--------|----------------|-----------------|
| **Table Used** | orders | revenue_recognized |
| **Column Used** | amount | net_amount |
| **Result** | $4,138,212.16 | $3,638,335.79 |
| **Matches Finance** | ❌ No (off by $500K) | ✅ Yes (exact match) |
| **Handles Refunds** | ❌ No | ✅ Yes (netted) |
| **Excludes Cancelled** | ❌ No | ✅ Yes (excluded) |
| **Board-Ready** | ❌ No | ✅ Yes |

---

## What Changed?

**Code changes:** 0 lines  
**Model changes:** None (still Claude Sonnet 4.5)  
**Cost changes:** $0  

**Prompt changes:** Added explicit guidance on which table to use for revenue questions

**Time to fix:** 5 minutes  
**Time to deploy:** 1 minute  

---

## Additional Test Cases

### Test 2: "What was Q1 2026 revenue?"

**BEFORE:** Would query orders table → $4,141,985.86 (WRONG)  
**AFTER:** Queries revenue_recognized → $3,285,493.84 (CORRECT)

### Test 3: "How many orders in Q2?"

**BEFORE:** Counts all orders including cancelled → 2,213 (MISLEADING)  
**AFTER:** Still uses orders table but now prompt clarifies this is OK for counts → Can add status filter

### Test 4: "What's our August revenue?"

**BEFORE:** Might use orders or daily_kpis (inconsistent)  
**AFTER:** Uses revenue_recognized with period='2026-08' → $1,162,073.21 (CONSISTENT)

---

## Why This Fix Works

The model wasn't broken—it was **under-specified**.

**Before:** "Here are 5 tables, figure out which one has revenue"  
**After:** "For revenue, always use table X, column Y"

It's the difference between:
- ❌ "The answer is somewhere in these 5 books"
- ✅ "The answer is in Book 3, Chapter 2, under 'Net Revenue'"

---

## Deployment Verification

After deploying `output/fixed_prompt.md`, run:

```bash
python agent.py "what was our Q2 2026 revenue?"
```

**Expected output:**
```
Q2 2026 revenue was $3,638,335.79 (~$3.6M).
```

**If you see $4.1M, the fix wasn't deployed correctly.**

---

## Key Takeaway

Same model + better instructions = correct answers.

No need for Opus, GPT-6, or any model upgrade.  
Just need to tell the bot where to find "revenue" in your warehouse.
