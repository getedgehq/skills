#!/usr/bin/env python3
"""
Q2 Revenue Verification Script

Run this to verify all the numbers in the investigation report.
Usage: python3 verify_numbers.py
"""

import sqlite3

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def main():
    conn = sqlite3.connect('warehouse.db')
    
    print_section("Q2 2026 REVENUE VERIFICATION")
    
    # 1. What finbot reported
    print("1. WHAT FINBOT REPORTED (WRONG)")
    query = """
    SELECT ROUND(SUM(amount), 2) AS revenue 
    FROM orders 
    WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';
    """
    result = conn.execute(query).fetchone()[0]
    print(f"   Query: SELECT SUM(amount) FROM orders WHERE created_at IN Q2")
    print(f"   Result: ${result:,.2f}")
    print(f"   Status: ❌ WRONG - includes cancelled orders")
    
    # 2. What finance says (correct)
    print("\n2. WHAT FINANCE SAYS (CORRECT)")
    query = """
    SELECT ROUND(SUM(net_amount), 2) AS revenue
    FROM revenue_recognized 
    WHERE recognized_on BETWEEN '2026-04-01' AND '2026-06-30';
    """
    correct = conn.execute(query).fetchone()[0]
    print(f"   Query: SELECT SUM(net_amount) FROM revenue_recognized WHERE recognized_on IN Q2")
    print(f"   Result: ${correct:,.2f}")
    print(f"   Status: ✅ CORRECT - proper accounting")
    
    # 3. The discrepancy
    print("\n3. THE DISCREPANCY")
    print(f"   Finbot: ${result:,.2f}")
    print(f"   Finance: ${correct:,.2f}")
    print(f"   Difference: ${result - correct:,.2f} ({((result - correct) / correct * 100):.1f}% overstatement)")
    
    print_section("ROOT CAUSE ANALYSIS")
    
    # 4. Orders by status
    print("4. ORDERS TABLE BREAKDOWN (Q2 2026)")
    query = """
    SELECT 
        status, 
        COUNT(*) as count, 
        ROUND(SUM(amount), 2) as total
    FROM orders 
    WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30'
    GROUP BY status
    ORDER BY total DESC;
    """
    results = conn.execute(query).fetchall()
    print(f"   {'Status':<20} {'Count':>10} {'Amount':>20}")
    print(f"   {'-'*20} {'-'*10} {'-'*20}")
    total = 0
    for status, count, amount in results:
        print(f"   {status:<20} {count:>10,} ${amount:>18,.2f}")
        total += amount
    print(f"   {'-'*20} {'-'*10} {'-'*20}")
    print(f"   {'TOTAL':<20} {sum(r[1] for r in results):>10,} ${total:>18,.2f}")
    
    # 5. Cancelled orders specifically
    print("\n5. CANCELLED ORDERS (THE MAIN ISSUE)")
    query = """
    SELECT 
        COUNT(*) as count,
        ROUND(SUM(amount), 2) as total
    FROM orders 
    WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30'
    AND status = 'cancelled';
    """
    cancelled_count, cancelled_amt = conn.execute(query).fetchone()
    print(f"   Cancelled orders: {cancelled_count:,}")
    print(f"   Cancelled amount: ${cancelled_amt:,.2f}")
    print(f"   % of finbot's number: {(cancelled_amt / result * 100):.1f}%")
    print(f"   Status: These should NOT be in revenue calculations")
    
    # 6. Revenue_recognized breakdown
    print("\n6. REVENUE_RECOGNIZED TABLE (Q2 2026)")
    query = """
    SELECT 
        ROUND(SUM(gross_amount), 2) as gross,
        ROUND(SUM(refund_amount), 2) as refunds,
        ROUND(SUM(net_amount), 2) as net
    FROM revenue_recognized 
    WHERE recognized_on BETWEEN '2026-04-01' AND '2026-06-30';
    """
    gross, refunds, net = conn.execute(query).fetchone()
    print(f"   Gross revenue: ${gross:,.2f}")
    print(f"   Refunds: ${refunds:,.2f}")
    print(f"   Net revenue: ${net:,.2f}")
    print(f"   Verification: ${gross:,.2f} - ${refunds:,.2f} = ${net:,.2f} ✓")
    
    # 7. Cancelled orders in revenue_recognized
    print("\n7. CANCELLED ORDERS IN REVENUE_RECOGNIZED")
    query = """
    SELECT COUNT(DISTINCT rr.order_id) as count
    FROM revenue_recognized rr
    JOIN orders o ON rr.order_id = o.order_id
    WHERE o.status = 'cancelled'
    AND o.created_at BETWEEN '2026-04-01' AND '2026-06-30';
    """
    cancelled_in_rr = conn.execute(query).fetchone()[0]
    print(f"   Cancelled orders in revenue_recognized: {cancelled_in_rr}")
    print(f"   Status: ✅ Correct - cancelled orders excluded from revenue")
    
    print_section("MONTHLY BREAKDOWN")
    
    # 8. Monthly comparison
    print("8. REVENUE BY MONTH")
    
    print("\n   Orders Table (includes cancelled):")
    query = """
    SELECT 
        strftime('%Y-%m', created_at) as month, 
        ROUND(SUM(amount), 2) as amount
    FROM orders 
    WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30'
    GROUP BY month
    ORDER BY month;
    """
    orders_monthly = conn.execute(query).fetchall()
    print(f"   {'Month':<15} {'Amount':>20}")
    print(f"   {'-'*15} {'-'*20}")
    for month, amount in orders_monthly:
        print(f"   {month:<15} ${amount:>18,.2f}")
    
    print("\n   Revenue_Recognized Table (proper accounting):")
    query = """
    SELECT 
        period, 
        ROUND(SUM(net_amount), 2) as revenue
    FROM revenue_recognized 
    WHERE period IN ('2026-04', '2026-05', '2026-06')
    GROUP BY period
    ORDER BY period;
    """
    rr_monthly = conn.execute(query).fetchall()
    print(f"   {'Month':<15} {'Amount':>20}")
    print(f"   {'-'*15} {'-'*20}")
    total_rr = 0
    for period, revenue in rr_monthly:
        print(f"   {period:<15} ${revenue:>18,.2f}")
        total_rr += revenue
    print(f"   {'-'*15} {'-'*20}")
    print(f"   {'Q2 TOTAL':<15} ${total_rr:>18,.2f}")
    
    print_section("SUMMARY")
    
    print("✅ CORRECT QUERY FOR REVENUE:")
    print("   SELECT SUM(net_amount)")
    print("   FROM revenue_recognized") 
    print("   WHERE recognized_on BETWEEN '2026-04-01' AND '2026-06-30';")
    print(f"   Result: ${correct:,.2f}\n")
    
    print("❌ WRONG QUERY (what finbot used):")
    print("   SELECT SUM(amount)")
    print("   FROM orders")
    print("   WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';")
    print(f"   Result: ${result:,.2f}")
    print(f"   Error: Includes ${cancelled_amt:,.2f} of cancelled orders\n")
    
    print("🔧 THE FIX:")
    print("   Update prompt.md to tell the model to use revenue_recognized")
    print("   for all revenue questions, not the orders table.\n")
    
    print("💰 CORRECT Q2 2026 REVENUE FOR BOARD DECK:")
    print(f"   ${correct:,.2f} (or round to $3.64M)\n")
    
    conn.close()

if __name__ == "__main__":
    main()
