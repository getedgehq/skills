-- SQL Verification: FinBot Q2 Revenue Discrepancy
-- Run this to reproduce the analysis

-- ============================================================
-- WHAT FINBOT QUERIED (WRONG)
-- ============================================================
SELECT 'FinBot Query (Wrong)' as source;
SELECT ROUND(SUM(amount), 2) AS revenue 
FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';
-- Result: $4,138,212.16

-- ============================================================
-- WHAT FINANCE USES (CORRECT)
-- ============================================================
SELECT 'Finance Query (Correct)' as source;
SELECT ROUND(SUM(net_amount), 2) as revenue
FROM revenue_recognized
WHERE period IN ('2026-04', '2026-05', '2026-06');
-- Result: $3,638,335.79

-- ============================================================
-- BREAKDOWN: What finbot included incorrectly
-- ============================================================
SELECT 'Q2 Orders by Status' as analysis;
SELECT 
    status,
    COUNT(*) as order_count,
    ROUND(SUM(amount), 2) as total_amount
FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30'
GROUP BY status
ORDER BY total_amount DESC;

-- Results:
-- completed: 1733 orders, $3,269,510.70
-- cancelled: 202 orders, $360,039.00    ← Should NOT be counted
-- partially_refunded: 174 orders, $318,719.01
-- refunded: 104 orders, $189,943.45     ← Should NOT be counted

-- ============================================================
-- REVENUE RECOGNIZED (The Source of Truth)
-- ============================================================
SELECT 'Q2 Revenue Recognized by Month' as analysis;
SELECT 
    period,
    ROUND(SUM(gross_amount), 2) as gross_revenue,
    ROUND(SUM(refund_amount), 2) as refunds,
    ROUND(SUM(net_amount), 2) as net_revenue
FROM revenue_recognized
WHERE period IN ('2026-04', '2026-05', '2026-06')
GROUP BY period
ORDER BY period;

-- Results:
-- 2026-04: $1,369,750.07 gross, $132,233.44 refunds, $1,237,516.63 net
-- 2026-05: $1,310,501.70 gross, $100,843.39 refunds, $1,209,658.31 net
-- 2026-06: $1,290,611.60 gross, $99,450.75 refunds, $1,191,160.85 net
-- TOTAL: $3,638,335.79 net

-- ============================================================
-- VERIFICATION: Cancelled orders should have net_amount = 0
-- ============================================================
SELECT 'Sample Cancelled Orders in revenue_recognized' as analysis;
SELECT 
    o.order_id,
    o.created_at,
    o.status,
    o.amount as order_amount,
    COALESCE(rr.net_amount, 0) as recognized_net
FROM orders o
LEFT JOIN revenue_recognized rr ON o.order_id = rr.order_id 
    AND rr.period IN ('2026-04', '2026-05', '2026-06')
WHERE o.created_at BETWEEN '2026-04-01' AND '2026-06-30'
    AND o.status IN ('cancelled', 'refunded')
LIMIT 10;

-- Shows that cancelled/refunded orders either have net_amount=0 or aren't in revenue_recognized at all
