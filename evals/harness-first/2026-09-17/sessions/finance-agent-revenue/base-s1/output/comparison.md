# Side-by-Side Comparison: What FinBot Did vs What It Should Do

## The Question
**Priya asked (Sept 11, 10:02 AM):** "what was our Q2 2026 revenue?"

---

## What FinBot Actually Did (WRONG)

### Query Run:
```sql
SELECT ROUND(SUM(amount), 2) AS revenue 
FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';
```

### Result:
```
$4,138,212.16
```

### FinBot's Response:
> Q2 2026 revenue was **$4,138,212.16** (~$4.1M).

### What This Actually Represents:
- ✅ All orders with created_at in Q2
- ❌ Includes 202 cancelled orders ($360k)
- ❌ Includes orders that were later refunded
- ❌ Gross amounts (before refund processing)
- ❌ NOT the same as revenue recognized

---

## What FinBot Should Have Done (CORRECT)

### Query That Should Run:
```sql
SELECT ROUND(SUM(net_amount), 2) AS revenue
FROM revenue_recognized 
WHERE period IN ('2026-04', '2026-05', '2026-06');
```

### Result:
```
$3,638,335.79
```

### Correct Response:
> Q2 2026 revenue was **$3,638,335.79** (~$3.6M).

### What This Represents:
- ✅ GAAP-compliant recognized revenue
- ✅ Net of refunds
- ✅ Excludes cancelled orders
- ✅ Matches Finance's books
- ✅ What should go in board deck

---

## Detailed Breakdown

### Orders Table (What FinBot Used)
| Status | Count | Total Amount | Should Count as Revenue? |
|--------|-------|--------------|--------------------------|
| completed | 1,733 | $3,269,510.70 | Partial (need to subtract refunds) |
| cancelled | 202 | $360,039.00 | ❌ NO |
| partially_refunded | 174 | $318,719.01 | Partial (need to subtract refund portion) |
| refunded | 104 | $189,943.45 | ❌ NO |
| **TOTAL** | **2,213** | **$4,138,212.16** | This is what FinBot returned |

### Revenue_Recognized Table (What Finance Uses)
| Month | Net Revenue | Notes |
|-------|-------------|-------|
| 2026-04 | $1,237,516.63 | April recognized revenue |
| 2026-05 | $1,209,658.31 | May recognized revenue |
| 2026-06 | $1,191,160.85 | June recognized revenue |
| **Q2 Total** | **$3,638,335.79** | Finance's $3.6M (rounded) |

### The Math
```
Orders table total:           $4,138,212.16
  - Cancelled orders:         -$  360,039.00
  - Refunds:                  -$  332,528.00
  - Timing adjustments:       -/+ various
  ___________________________________________
Revenue_recognized net:       $3,638,335.79
Rounded (Finance reports):    $3,600,000.00
```

---

## Why This Matters

### From Product/Strategy Perspective:
- **Bookings** (orders table): $4.1M ← tells you how much customers ordered
- **Revenue** (revenue_recognized): $3.6M ← tells you how much money you actually made

### From Finance/Accounting Perspective:
- Only recognized revenue counts for:
  - Board reporting
  - GAAP compliance
  - Financial statements
  - Investor updates
  - SEC filings (if applicable)

### From Board/Investor Perspective:
- Sending $4.1M when actual revenue is $3.6M = 14% overstatement
- Looks like either incompetence or intentional inflation
- Erodes trust in company's numbers

---

## Test Cases

### After deploying the fix, these should work correctly:

#### Test 1: Simple Q2 Query
```
User: "what was our Q2 2026 revenue?"

CORRECT Response:
"Q2 2026 revenue was $3,638,335.79 (~$3.6M)."

SQL Used:
SELECT SUM(net_amount) FROM revenue_recognized 
WHERE period IN ('2026-04', '2026-05', '2026-06');
```

#### Test 2: Quarterly Comparison
```
User: "compare Q1 vs Q2 revenue"

CORRECT Response:
"Q1 2026: $3,285,493.84 (~$3.3M)
Q2 2026: $3,638,335.79 (~$3.6M)
Growth: +10.7% QoQ"

SQL Used:
SELECT 
  CASE 
    WHEN period IN ('2026-01','2026-02','2026-03') THEN 'Q1'
    WHEN period IN ('2026-04','2026-05','2026-06') THEN 'Q2'
  END as quarter,
  SUM(net_amount) as revenue
FROM revenue_recognized
WHERE period LIKE '2026-%'
GROUP BY quarter;
```

#### Test 3: Monthly Trend
```
User: "show me monthly revenue for Q2"

CORRECT Response:
"Q2 2026 Monthly Revenue:
- April: $1,237,516.63
- May: $1,209,658.31
- June: $1,191,160.85
Trend: -3.7% from April to June"

SQL Used:
SELECT period, SUM(net_amount) as revenue
FROM revenue_recognized 
WHERE period IN ('2026-04', '2026-05', '2026-06')
GROUP BY period;
```

#### Test 4: Bookings Question (Should Still Use Orders)
```
User: "what were our bookings in Q2?"

CORRECT Response:
"Q2 2026 bookings were $4,138,212.16 (~$4.1M) across 2,213 orders."

SQL Used:
SELECT SUM(amount), COUNT(*) FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';

NOTE: This is CORRECT for bookings! Different metric than revenue.
```

---

## Common Confusion: Revenue vs Bookings

| Term | Definition | Table to Use | Use Cases |
|------|------------|--------------|-----------|
| **Revenue** | Money recognized per GAAP, net of refunds | `revenue_recognized` | Board decks, financial reports, investor updates |
| **Bookings** | Orders placed, gross amounts | `orders` | Sales pipeline, demand trends, capacity planning |
| **Billings** | Invoices sent | (not in this DB) | Cash flow forecasting |
| **Collections** | Cash received | (not in this DB) | Cash management |

**Key insight:** These are all different! Revenue ≠ Bookings ≠ Cash

---

## Verification Steps

### 1. Check Against Finance's Books
```sql
-- Run this and compare to Finance's Q2 close
SELECT ROUND(SUM(net_amount)/1000000, 1) as revenue_millions
FROM revenue_recognized 
WHERE period IN ('2026-04', '2026-05', '2026-06');
-- Should return: 3.6
```

### 2. Check YTD Revenue
```sql
-- First half of 2026
SELECT ROUND(SUM(net_amount)/1000000, 1) as h1_revenue_millions
FROM revenue_recognized 
WHERE period IN ('2026-01','2026-02','2026-03','2026-04','2026-05','2026-06');
-- Should return: 6.9 (Q1: 3.3 + Q2: 3.6)
```

### 3. Validate Data Integrity
```sql
-- Net amount should equal gross minus refunds
SELECT COUNT(*) 
FROM revenue_recognized
WHERE ABS(net_amount - (gross_amount - refund_amount)) > 0.01;
-- Should return: 0
```

---

## Before & After Screenshot (Text)

### BEFORE (Slack, Sept 11):
```
Priya: @finbot what was our Q2 2026 revenue?

finbot: Q2 2026 revenue was $4,138,212.16 (~$4.1M).     ❌ WRONG

Priya: perfect ty 🙏
```

### AFTER (Expected):
```
Priya: @finbot what was our Q2 2026 revenue?

finbot: Q2 2026 revenue was $3,638,335.79 (~$3.6M).     ✅ CORRECT

Priya: and how does that compare to Q1?

finbot: Q1 was $3,285,493.84 (~$3.3M). Q2 grew +10.7% QoQ.
```

---

## Key Takeaway

**The model CAN do the math.** It just needs to know:
1. Which table to use (revenue_recognized, not orders)
2. Which column to sum (net_amount, not amount)
3. How to filter (by period, not created_at)

**This is a configuration fix, not an intelligence problem.**

Model is like an analyst who:
- ✅ Knows SQL
- ✅ Can read a database
- ✅ Can calculate sums
- ❌ Doesn't know company's revenue recognition policy

**The fix:** Tell it the policy (via prompt).
