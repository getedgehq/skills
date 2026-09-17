# Numbers Verification Report

All numbers independently verified by running queries against `warehouse.db`.

---

## Q2 2026 Revenue (The Incident)

### What FinBot Did (Wrong Query)
```sql
SELECT ROUND(SUM(amount), 2) AS revenue 
FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';
```
**Result:** $4,138,212.16 ✓ (verified)

### What Finance Does (Correct Query)
```sql
SELECT ROUND(SUM(net_amount), 2) AS revenue 
FROM revenue_recognized 
WHERE period IN ('2026-04', '2026-05', '2026-06');
```
**Result:** $3,638,335.79 ✓ (verified)

### The Gap Analysis
```sql
-- Q2 refunds from revenue_recognized
SELECT ROUND(SUM(refund_amount), 2)
FROM revenue_recognized 
WHERE period IN ('2026-04', '2026-05', '2026-06');
```
**Refunds:** $332,527.58 ✓

```sql
-- Q2 gross from revenue_recognized
SELECT ROUND(SUM(gross_amount), 2)
FROM revenue_recognized 
WHERE period IN ('2026-04', '2026-05', '2026-06');
```
**Gross (recognized):** $3,970,863.37 ✓

**Calculation:**
- Orders table (gross by creation date): $4,138,212.16
- Revenue_recognized gross (by period): $3,970,863.37
- Timing difference: $167,348.79 (orders created in Q2 but recognized later, or vice versa)
- Refunds: $332,527.58
- Net revenue: $3,638,335.79 ✓

**Total gap:** $4,138,212.16 - $3,638,335.79 = $499,876.37 ✓

---

## Q1 2026 Revenue (From Transcript)

### What FinBot Did
```sql
SELECT ROUND(SUM(amount), 2) AS revenue 
FROM orders 
WHERE created_at BETWEEN '2026-01-01' AND '2026-03-31';
```
**Result:** $4,141,985.86 ✓ (matches transcript)

### Correct Calculation
```sql
SELECT ROUND(SUM(net_amount), 2) 
FROM revenue_recognized 
WHERE period IN ('2026-01', '2026-02', '2026-03');
```
**Result:** $3,948,091.29 ✓

**Gap:** $193,894.57 (similar pattern - timing + refunds)

---

## Database Statistics

### Orders Table
```sql
SELECT 
    COUNT(*) as total_orders,
    COUNT(CASE WHEN created_at BETWEEN '2026-04-01' AND '2026-06-30' THEN 1 END) as q2_orders,
    ROUND(SUM(amount), 2) as total_amount
FROM orders;
```
**Results:**
- Total orders: 6,136 ✓
- Q2 orders: 1,563 ✓
- Total amount: $14,846,583.66 ✓

### Refunds Table
```sql
SELECT 
    COUNT(*) as total_refunds,
    COUNT(CASE WHEN refunded_at BETWEEN '2026-04-01' AND '2026-06-30' THEN 1 END) as q2_refunds,
    ROUND(SUM(amount), 2) as total_refunded
FROM refunds;
```
**Results:**
- Total refunds: 805 ✓
- Q2 refunds: 203 ✓
- Total refunded: $1,120,757.56 ✓

### Revenue_recognized Table
```sql
SELECT 
    COUNT(*) as total_records,
    COUNT(DISTINCT period) as periods,
    ROUND(SUM(net_amount), 2) as total_revenue
FROM revenue_recognized;
```
**Results:**
- Total records: 5,598 ✓
- Unique periods: 6 (2026-01 through 2026-06) ✓
- Total net revenue: $13,218,869.82 ✓

---

## Verification Method

1. Connected to `warehouse.db` using Python sqlite3
2. Ran all queries independently
3. Calculated differences manually
4. Cross-checked against transcript numbers
5. Verified refund amounts from both tables
6. Confirmed timing differences exist

**Conclusion:** All numbers are real and mathematically correct from their source tables. The incident was caused by querying the wrong table, not by hallucination or incorrect calculation.

---

## Evidence Files

All queries can be re-run:
```bash
python3 << 'VERIFY'
import sqlite3
conn = sqlite3.connect('warehouse.db')

print("FinBot's query:")
print(conn.execute("""
    SELECT ROUND(SUM(amount), 2) 
    FROM orders 
    WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30'
""").fetchone()[0])

print("\nFinance's query:")
print(conn.execute("""
    SELECT ROUND(SUM(net_amount), 2) 
    FROM revenue_recognized 
    WHERE period IN ('2026-04', '2026-05', '2026-06')
""").fetchone()[0])

conn.close()
VERIFY
```

Expected output:
```
FinBot's query:
4138212.16

Finance's query:
3638335.79
```

---

## Sign-off

✅ All numbers verified against source database  
✅ Math checked independently  
✅ Both queries produce consistent results  
✅ Gap fully explained (refunds + timing)  
✅ No hallucination detected  

Investigation date: 2026-09-16  
Database: warehouse.db (provided)
