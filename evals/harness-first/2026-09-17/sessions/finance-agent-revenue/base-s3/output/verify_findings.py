#!/usr/bin/env python3
"""
Verification script for the Q2 revenue discrepancy analysis.
Run this to confirm all findings independently.

Usage: python3 verify_findings.py
"""

import sqlite3
import json

def main():
    print("=" * 80)
    print("Q2 REVENUE DISCREPANCY VERIFICATION")
    print("=" * 80)
    print()
    
    conn = sqlite3.connect('../warehouse.db')
    cursor = conn.cursor()
    
    # 1. What the bot calculated
    print("1. WHAT THE BOT CALCULATED")
    print("-" * 80)
    query_bot = """
        SELECT ROUND(SUM(amount), 2) AS revenue 
        FROM orders 
        WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30'
    """
    print(f"Query: {query_bot.strip()}")
    cursor.execute(query_bot)
    bot_result = cursor.fetchone()[0]
    print(f"Result: ${bot_result:,.2f}")
    print()
    
    # 2. What finance uses
    print("2. WHAT FINANCE CALCULATED (CORRECT)")
    print("-" * 80)
    query_finance = """
        SELECT ROUND(SUM(net_amount), 2)
        FROM revenue_recognized 
        WHERE period IN ('2026-04', '2026-05', '2026-06')
    """
    print(f"Query: {query_finance.strip()}")
    cursor.execute(query_finance)
    finance_result = cursor.fetchone()[0]
    print(f"Result: ${finance_result:,.2f}")
    print()
    
    # 3. The discrepancy
    print("3. THE DISCREPANCY")
    print("-" * 80)
    discrepancy = bot_result - finance_result
    print(f"Bot result:      ${bot_result:,.2f}")
    print(f"Finance result:  ${finance_result:,.2f}")
    print(f"Difference:      ${discrepancy:,.2f}")
    print()
    
    # 4. Why the bot was wrong - orders breakdown
    print("4. WHY THE BOT WAS WRONG - Orders by Status")
    print("-" * 80)
    cursor.execute("""
        SELECT 
            status,
            COUNT(*) as count,
            ROUND(SUM(amount), 2) as total
        FROM orders 
        WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30'
        GROUP BY status
        ORDER BY status
    """)
    
    total_all_orders = 0
    for row in cursor.fetchall():
        status, count, total = row
        marker = "✅" if status == "completed" else "❌"
        print(f"{marker} {status:20s}: {count:4d} orders = ${total:12,.2f}")
        total_all_orders += total
    print(f"   {'TOTAL (bot used)':20s}:           ${total_all_orders:12,.2f}")
    print()
    print("The bot counted ALL orders, including cancelled and refunded ones!")
    print()
    
    # 5. What finance uses - revenue recognized
    print("5. WHAT FINANCE USES - Revenue Recognized")
    print("-" * 80)
    cursor.execute("""
        SELECT 
            ROUND(SUM(gross_amount), 2) as gross,
            ROUND(SUM(refund_amount), 2) as refunds,
            ROUND(SUM(net_amount), 2) as net
        FROM revenue_recognized 
        WHERE period IN ('2026-04', '2026-05', '2026-06')
    """)
    gross, refunds, net = cursor.fetchone()
    print(f"Gross revenue:   ${gross:,.2f}")
    print(f"Refunds:        -${refunds:,.2f}")
    print(f"Net revenue:     ${net:,.2f}  ✅ CORRECT")
    print()
    
    # 6. Monthly breakdown
    print("6. MONTHLY BREAKDOWN (Q2 2026)")
    print("-" * 80)
    cursor.execute("""
        SELECT 
            period,
            ROUND(SUM(net_amount), 2) as revenue
        FROM revenue_recognized 
        WHERE period IN ('2026-04', '2026-05', '2026-06')
        GROUP BY period
        ORDER BY period
    """)
    months = {'04': 'April', '05': 'May', '06': 'June'}
    monthly_total = 0
    for period, revenue in cursor.fetchall():
        month_num = period.split('-')[1]
        month_name = months[month_num]
        print(f"{month_name:10s}: ${revenue:,.2f}")
        monthly_total += revenue
    print(f"{'Q2 Total':10s}: ${monthly_total:,.2f}  ✅")
    print()
    
    conn.close()
    
    # 7. Verification summary
    print("=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    
    checks = [
        ("Bot calculated $4.1M", abs(bot_result - 4138212.16) < 1),
        ("Finance calculated $3.6M", abs(finance_result - 3638335.79) < 1),
        ("Discrepancy is ~$500K", abs(discrepancy - 499876.37) < 1),
        ("Monthly totals match", abs(monthly_total - finance_result) < 1),
    ]
    
    all_passed = True
    for check_name, passed in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {check_name}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("✅ ALL CHECKS PASSED - Analysis confirmed!")
        print()
        print("CONCLUSION:")
        print("  • FinBot queried the orders table (wrong)")
        print("  • Finance uses revenue_recognized table (correct)")
        print("  • Bot included cancelled and refunded orders")
        print("  • This is NOT a hallucination or model quality issue")
        print("  • Fix: Update the prompt with business context")
    else:
        print("⚠️  SOME CHECKS FAILED - Review analysis")
    
    print("=" * 80)

if __name__ == "__main__":
    main()
