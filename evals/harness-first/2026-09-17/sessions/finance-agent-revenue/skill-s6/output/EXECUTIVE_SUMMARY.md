# Executive Summary for Daniel

**One-line answer:** Don't upgrade the model. FinBot used the wrong table—it counted cancelled and refunded orders ($500k) that finance correctly excluded. This is a data layer problem, not a model problem.

## The Discrepancy

- **FinBot said:** $4.1M Q2 revenue (went into board deck)
- **Finance says:** $3.6M Q2 revenue (GAAP close)
- **Difference:** $499,876 (13.9% error)

## Root Cause

**FinBot queried the ORDERS table, which includes cancelled and refunded orders. Finance uses the REVENUE_RECOGNIZED table (GAAP accounting).**

### What FinBot counted (orders table):
```
Completed orders:          $3,269,510.70
Cancelled orders:          $  360,039.00  ⚠️
Refunded orders:           $  189,943.45  ⚠️
Partially refunded orders: $  318,719.01  ⚠️
─────────────────────────────────────────
Total:                     $4,138,212.16  ← FinBot's answer
```

### What Finance uses (revenue_recognized table):
```
April:   $1,237,516.63
May:     $1,209,658.31
June:    $1,191,160.85
─────────────────────
Total:   $3,638,335.79  ← Finance's close
```

## Evidence

- **File:** `transcripts/2026-09-11_board-deck.md` line 6-8
- **SQL executed:** `SELECT SUM(amount) FROM orders WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30'`
- **Model behavior:** The model faithfully executed the query—no hallucination, no math error
- **Warehouse proof:** Recomputed both numbers from `warehouse.db`—both are correct for their respective tables

## Why This Happened

1. **No data dictionary**: The prompt says "use orders table" without defining when to use `orders` vs `revenue_recognized`
2. **Ambiguous metric**: "Revenue" can mean gross bookings, recognized revenue, or cash collected—different tables give different numbers
3. **No validation**: No golden set of past questions with expected answers to catch this

## What This Is NOT

- ❌ Not a hallucination (model didn't make up numbers)
- ❌ Not a model capability problem (any model would pick the wrong table given the prompt)
- ❌ Not a reasoning failure (the SQL is correct for what was asked)

**This is a harness problem.** The system has no definition of "revenue", no test cases, and the prompt lists multiple tables without guidance on when to use each.

---

**Recommendation:** Fix the data layer first (define metrics, add golden set). Do NOT upgrade the model until you have evidence it would help.

**Timeline for tomorrow's meeting:**
- Board deck needs correction: Q2 revenue is $3.6M, not $4.1M
- Source of error: internal bot queried wrong table (operational data, not GAAP close)
- Fix in progress: data definitions + validation suite
