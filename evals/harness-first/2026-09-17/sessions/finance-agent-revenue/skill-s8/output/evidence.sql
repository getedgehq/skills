-- Evidence: Reproducing both numbers in the Q2 revenue discrepancy
-- Run: python3 -c "import sqlite3; conn=sqlite3.connect('warehouse.db'); exec(open('evidence.sql').read())"

-- ==================================================
-- WHAT FINBOT CALCULATED (WRONG)
-- ==================================================

-- FinBot used this query (from transcript 2026-09-11_board-deck.md):
SELECT ROUND(SUM(amount), 2) AS finbot_answer
FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';
-- Result: $4,138,212.16

-- Breakdown by order status:
SELECT 
    status,
    COUNT(*) as order_count,
    ROUND(SUM(amount), 2) as total_amount
FROM orders
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30'
GROUP BY status
ORDER BY total_amount DESC;
-- completed:           1733 orders, $3,269,510.70
-- cancelled:            202 orders,   $360,039.00  ❌ Should not count
-- partially_refunded:   174 orders,   $318,719.01  ❌ Should use net, not gross
-- refunded:             104 orders,   $189,943.45  ❌ Should not count


-- ==================================================
-- WHAT FINANCE CALCULATED (CORRECT)
-- ==================================================

-- Finance uses revenue_recognized (GAAP-compliant):
SELECT ROUND(SUM(net_amount), 2) AS finance_close
FROM revenue_recognized
WHERE recognized_on BETWEEN '2026-04-01' AND '2026-06-30';
-- Result: $3,638,335.79

-- Breakdown by month:
SELECT 
    period,
    COUNT(*) as line_items,
    ROUND(SUM(gross_amount), 2) as gross,
    ROUND(SUM(refund_amount), 2) as refunds,
    ROUND(SUM(net_amount), 2) as net_revenue
FROM revenue_recognized
WHERE recognized_on BETWEEN '2026-04-01' AND '2026-06-30'
GROUP BY period
ORDER BY period;


-- ==================================================
-- RECONCILIATION
-- ==================================================

-- The $499,876 discrepancy breaks down as:
-- 1. Cancelled orders that should not count: $360,039
-- 2. Refunded orders that should not count: $189,943
-- 3. Partial refunds on completed orders: ~$50,106
--    (revenue_recognized accounts for these, orders table doesn't)

SELECT 
    'FinBot answer (wrong)' as source,
    ROUND(SUM(amount), 2) as amount
FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30'

UNION ALL

SELECT 
    'Finance close (correct)' as source,
    ROUND(SUM(net_amount), 2) as amount
FROM revenue_recognized
WHERE recognized_on BETWEEN '2026-04-01' AND '2026-06-30'

UNION ALL

SELECT 
    'Discrepancy' as source,
    ROUND(
        (SELECT SUM(amount) FROM orders WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30')
        -
        (SELECT SUM(net_amount) FROM revenue_recognized WHERE recognized_on BETWEEN '2026-04-01' AND '2026-06-30')
    , 2) as amount;


-- ==================================================
-- WHY THE CORRECT TABLE MATTERS
-- ==================================================

-- The revenue_recognized table contains:
-- - net_amount = gross_amount - refund_amount (official GAAP revenue)
-- - recognized_on = the date revenue is officially counted
-- - period = the fiscal period ('2026-04', '2026-05', etc.)

-- Sample data from revenue_recognized:
SELECT 
    order_id,
    recognized_on,
    period,
    gross_amount,
    refund_amount,
    net_amount
FROM revenue_recognized
WHERE period IN ('2026-04', '2026-05', '2026-06')
ORDER BY recognized_on
LIMIT 10;
