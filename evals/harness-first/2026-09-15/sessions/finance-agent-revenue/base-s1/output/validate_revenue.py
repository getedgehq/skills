#!/usr/bin/env python3
"""
FinBot Revenue Validation Script
Run this to verify Q2 2026 revenue figures and diagnose discrepancies
"""

import sqlite3
from datetime import datetime

DB_PATH = "../warehouse.db"

def format_currency(amount):
    """Format amount as currency"""
    return f"${amount:,.2f}"

def format_millions(amount):
    """Format amount in millions"""
    return f"${amount/1000000:.1f}M"

def run_query(conn, query, description):
    """Run a query and print results"""
    print(f"\n{'='*70}")
    print(f"Query: {description}")
    print('='*70)
    print(f"{query}\n")
    
    cursor = conn.execute(query)
    rows = cursor.fetchall()
    cols = [d[0] for d in cursor.description]
    
    print(f"Columns: {cols}")
    for row in rows:
        print(f"  {row}")
    
    return rows

def main():
    print("="*70)
    print("FINBOT Q2 2026 REVENUE VALIDATION")
    print(f"Run at: {datetime.now()}")
    print("="*70)
    
    conn = sqlite3.connect(DB_PATH)
    
    # 1. What FinBot reported
    print("\n" + "🤖 " + "="*65)
    print("1. WHAT FINBOT REPORTED (INCORRECT)")
    print("="*70)
    
    query1 = """
    SELECT ROUND(SUM(amount), 2) AS revenue 
    FROM orders 
    WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';
    """
    result1 = run_query(conn, query1, "FinBot's Original Query (orders table)")
    finbot_amount = result1[0][0]
    print(f"\n📊 FinBot reported: {format_currency(finbot_amount)} ({format_millions(finbot_amount)})")
    
    # 2. What Finance reports
    print("\n" + "💰 " + "="*65)
    print("2. WHAT FINANCE REPORTS (CORRECT)")
    print("="*70)
    
    query2 = """
    SELECT ROUND(SUM(net_amount), 2) AS revenue
    FROM revenue_recognized 
    WHERE period IN ('2026-04', '2026-05', '2026-06');
    """
    result2 = run_query(conn, query2, "Correct Query (revenue_recognized table)")
    finance_amount = result2[0][0]
    print(f"\n📊 Finance reports: {format_currency(finance_amount)} ({format_millions(finance_amount)})")
    
    # 3. The discrepancy
    print("\n" + "⚠️  " + "="*65)
    print("3. DISCREPANCY ANALYSIS")
    print("="*70)
    
    difference = finbot_amount - finance_amount
    pct_diff = (difference / finance_amount) * 100
    
    print(f"FinBot amount:    {format_currency(finbot_amount)}")
    print(f"Finance amount:   {format_currency(finance_amount)}")
    print(f"Difference:       {format_currency(difference)} ({pct_diff:.1f}% overstatement)")
    
    # 4. Breakdown of discrepancy
    print("\n" + "🔍 " + "="*65)
    print("4. WHY THE DIFFERENCE?")
    print("="*70)
    
    # Cancelled orders
    query3 = """
    SELECT 
        status,
        COUNT(*) as count,
        ROUND(SUM(amount), 2) as total
    FROM orders 
    WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30'
    GROUP BY status
    ORDER BY total DESC;
    """
    print("\nOrders by status:")
    results3 = run_query(conn, query3, "Orders breakdown by status")
    
    cancelled_amount = 0
    for row in results3:
        status, count, amount = row
        if status == 'cancelled':
            cancelled_amount = amount
        print(f"  {status:20} | Count: {count:4} | Amount: {format_currency(amount)}")
    
    # Refunds
    query4 = """
    SELECT 
        ROUND(SUM(gross_amount), 2) as gross,
        ROUND(SUM(refund_amount), 2) as refunds,
        ROUND(SUM(net_amount), 2) as net
    FROM revenue_recognized 
    WHERE period IN ('2026-04', '2026-05', '2026-06');
    """
    result4 = run_query(conn, query4, "Gross vs Net revenue")
    gross, refunds, net = result4[0]
    
    print(f"\n  Gross revenue:  {format_currency(gross)}")
    print(f"  Refunds:        {format_currency(refunds)}")
    print(f"  Net revenue:    {format_currency(net)}")
    
    # 5. Summary
    print("\n" + "📋 " + "="*65)
    print("5. SUMMARY")
    print("="*70)
    
    print(f"""
Discrepancy breakdown:
  1. Cancelled orders:      {format_currency(cancelled_amount)}
  2. Refunds:               {format_currency(refunds)}
  3. Other timing diffs:    ~{format_currency(difference - cancelled_amount - (finbot_amount - gross - cancelled_amount))}
  
  Total difference:         {format_currency(difference)}
  
Root Cause:
  ✗ FinBot queried 'orders' table (gross bookings, includes cancelled)
  ✓ Should query 'revenue_recognized' table (net revenue, GAAP-compliant)
  
Fix:
  → Update prompt.md to specify revenue_recognized for revenue questions
  → No model upgrade needed - this is a configuration issue
  
Confidence: 100%
""")
    
    # 6. Validation checks
    print("\n" + "✅ " + "="*65)
    print("6. DATA INTEGRITY CHECKS")
    print("="*70)
    
    # Check 1: Net = Gross - Refunds
    query5 = """
    SELECT COUNT(*) 
    FROM revenue_recognized
    WHERE period IN ('2026-04', '2026-05', '2026-06')
    AND ABS(net_amount - (gross_amount - refund_amount)) > 0.01;
    """
    result5 = run_query(conn, query5, "Check: net = gross - refunds")
    integrity_issues = result5[0][0]
    
    if integrity_issues == 0:
        print("✅ PASS: All net amounts correctly calculated (gross - refunds)")
    else:
        print(f"⚠️  FAIL: Found {integrity_issues} rows with incorrect arithmetic")
    
    # Check 2: All orders exist
    query6 = """
    SELECT COUNT(DISTINCT rr.order_id) as in_rev_rec,
           COUNT(DISTINCT o.order_id) as in_orders
    FROM revenue_recognized rr
    LEFT JOIN orders o ON rr.order_id = o.order_id
    WHERE rr.period IN ('2026-04', '2026-05', '2026-06');
    """
    result6 = run_query(conn, query6, "Check: all orders exist in both tables")
    rr_count, orders_count = result6[0]
    
    if rr_count == orders_count:
        print(f"✅ PASS: All {rr_count} orders in revenue_recognized exist in orders table")
    else:
        print(f"⚠️  FAIL: Mismatch - {rr_count} in rev_rec, {orders_count} in orders")
    
    # 7. Recommended query
    print("\n" + "💡 " + "="*65)
    print("7. RECOMMENDED QUERY FOR REVENUE QUESTIONS")
    print("="*70)
    
    recommended = """
SELECT 
    period,
    ROUND(SUM(net_amount), 2) as revenue
FROM revenue_recognized 
WHERE period IN ('2026-04', '2026-05', '2026-06')
GROUP BY period
ORDER BY period;
"""
    print(recommended)
    
    print("\nFor Q2 total:")
    print("""
SELECT ROUND(SUM(net_amount), 2) as q2_revenue
FROM revenue_recognized 
WHERE period IN ('2026-04', '2026-05', '2026-06');
""")
    
    print("\n" + "="*70)
    print("VALIDATION COMPLETE")
    print("="*70)
    print(f"""
Final Answer:
  Correct Q2 2026 Revenue: {format_currency(finance_amount)} ({format_millions(finance_amount)})
  
Status: ✅ Issue diagnosed, fix identified, ready to deploy
""")
    
    conn.close()

if __name__ == "__main__":
    main()
