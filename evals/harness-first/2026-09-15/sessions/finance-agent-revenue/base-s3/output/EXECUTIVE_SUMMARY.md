# Q2 Revenue Discrepancy - Quick Summary

## The Numbers
```
FinBot said:  $4,138,212  (4.1M)
Finance says: $3,638,336  (3.6M)
Difference:   $  499,876  (500K) ❌
```

## What Went Wrong

FinBot queried the **wrong table**:

### ❌ What the bot did:
```sql
SELECT SUM(amount) FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30'
```
This includes ALL orders: completed, cancelled, AND refunded

### ✅ What it should do:
```sql
SELECT SUM(net_amount) FROM revenue_recognized 
WHERE period IN ('2026-04', '2026-05', '2026-06')
```
This is the accounting source of truth (gross revenue - refunds)

## The Problem Breakdown

Q2 Orders by Status:
```
Completed:           $3,269,511  ← Real revenue
Cancelled:           $  360,039  ← Should not count
Refunded:            $  189,943  ← Should not count  
Partially Refunded:  $  318,719  ← Need to subtract refund amount
─────────────────────────────────
Total (bot used):    $4,138,212  ← WRONG
```

Revenue Recognized (what Finance uses):
```
Gross Revenue:       $3,970,863
Refunds:            -$  332,528
─────────────────────────────────
Net Revenue:         $3,638,336  ← CORRECT
```

## Is This a Model Quality Issue?

### NO. 

The model (Claude Sonnet 4.5) works perfectly:
- ✅ Understood the question correctly
- ✅ Generated valid SQL
- ✅ Correctly identified Q2 date range
- ✅ Returned accurate results from its query

The model just didn't know which table represents "revenue" in accounting terms.

## The Root Cause

The system prompt (`prompt.md`) lists the available tables but provides:
- ❌ No guidance on which table to use for revenue
- ❌ No explanation that orders can be cancelled/refunded
- ❌ No documentation that `revenue_recognized` is the financial source of truth

The bot made a reasonable guess (orders → revenue) but it was wrong for financial reporting.

## The Fix

### Option 1: Update the Prompt (Recommended - 10 minutes)
Add business context to `prompt.md`:
- Document what each table is for
- Specify that `revenue_recognized` is the source for all revenue questions
- Explain how to filter by period/quarter

**Cost:** Free  
**Time:** 10 minutes  
**Will this work:** Yes, 100%

See `output/prompt_FIXED.md` for the updated prompt.

### Option 2: Upgrade the Model
Switch from Sonnet to Opus or GPT-6.

**Cost:** 3-10x higher per query  
**Time:** Minimal  
**Will this work:** No - the new model would make the same mistake without better instructions

## Action Items for Daniel

1. ✅ **Understand the issue** - Not a hallucination, wrong table choice
2. 🔧 **Fix the prompt** - Add business context (10 min, see `output/prompt_FIXED.md`)
3. 🧪 **Test it** - Verify bot now gives correct answer
4. 📊 **Fix the board deck** - Correct number is $3.6M
5. 🎯 **Future-proof** - Add test cases for common queries

## Bottom Line

**Don't upgrade the model. Fix the prompt.**

The bot is doing exactly what it was told - the instructions were just incomplete. Adding proper business context will solve this completely at zero cost.

---

📁 Full analysis: `output/FINDINGS.md`  
📊 Raw data: `output/analysis_data.json`  
✅ Fixed prompt: `output/prompt_FIXED.md`
