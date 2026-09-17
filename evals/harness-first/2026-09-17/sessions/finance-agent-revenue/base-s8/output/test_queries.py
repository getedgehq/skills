#!/usr/bin/env python3
"""
Test script to verify the prompt fix works correctly.
Compares old vs new prompt behavior on critical revenue questions.
"""

import sys
import os

# Add parent directory to path to import agent
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3

def test_queries_direct():
    """
    Test queries directly against the database to show what the correct answers should be.
    """
    conn = sqlite3.connect('warehouse.db')
    
    print("="*70)
    print("EXPECTED CORRECT ANSWERS (Direct Database Queries)")
    print("="*70)
    print()
    
    # Q2 2026 Revenue
    print("1. Q2 2026 Revenue")
    print("-" * 50)
    cur = conn.execute("""
        SELECT ROUND(SUM(net_amount), 2) AS revenue
        FROM revenue_recognized 
        WHERE period IN ('2026-04', '2026-05', '2026-06')
    """)
    q2_revenue = cur.fetchone()[0]
    print(f"   Correct answer: ${q2_revenue:,.2f} (~$3.6M)")
    
    # Compare to wrong method
    cur = conn.execute("""
        SELECT ROUND(SUM(amount), 2) AS revenue
        FROM orders 
        WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30'
    """)
    q2_wrong = cur.fetchone()[0]
    print(f"   Wrong (orders table): ${q2_wrong:,.2f} (~$4.1M)")
    print(f"   Error if using orders: ${q2_wrong - q2_revenue:,.2f} overstated")
    print()
    
    # Q1 2026 Revenue
    print("2. Q1 2026 Revenue")
    print("-" * 50)
    cur = conn.execute("""
        SELECT ROUND(SUM(net_amount), 2) AS revenue
        FROM revenue_recognized 
        WHERE period IN ('2026-01', '2026-02', '2026-03')
    """)
    q1_revenue = cur.fetchone()[0]
    print(f"   Correct answer: ${q1_revenue:,.2f} (~$3.3M)")
    print()
    
    # August 2026 Revenue (single month)
    print("3. August 2026 Revenue")
    print("-" * 50)
    cur = conn.execute("""
        SELECT ROUND(SUM(net_amount), 2) AS revenue
        FROM revenue_recognized 
        WHERE period = '2026-08'
    """)
    aug_revenue = cur.fetchone()[0]
    print(f"   Correct answer: ${aug_revenue:,.2f} (~$1.2M)")
    print()
    
    # Q2 Order Count (orders table is OK for this)
    print("4. Q2 2026 Order Count")
    print("-" * 50)
    cur = conn.execute("""
        SELECT COUNT(*) AS order_count
        FROM orders 
        WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30'
        AND status IN ('completed', 'partially_refunded')
    """)
    q2_orders = cur.fetchone()[0]
    print(f"   Correct answer: {q2_orders:,} orders (completed + partially_refunded)")
    print()
    
    conn.close()
    
    print("="*70)
    print("TO TEST WITH FINBOT:")
    print("="*70)
    print()
    print("After deploying the fixed prompt, run these commands:")
    print()
    print('1. python agent.py "what was our Q2 2026 revenue?"')
    print(f'   Expected: ~$3.6M (${q2_revenue:,.2f})')
    print()
    print('2. python agent.py "what was our Q1 2026 revenue?"')
    print(f'   Expected: ~$3.3M (${q1_revenue:,.2f})')
    print()
    print('3. python agent.py "what was our August 2026 revenue?"')
    print(f'   Expected: ~$1.2M (${aug_revenue:,.2f})')
    print()
    print('4. python agent.py "how many orders did we have in Q2 2026?"')
    print(f'   Expected: ~{q2_orders:,} orders')
    print()
    print("="*70)

def show_table_comparison():
    """Show the difference between tables for debugging"""
    conn = sqlite3.connect('warehouse.db')
    
    print()
    print("="*70)
    print("TABLE COMPARISON FOR Q2 2026")
    print("="*70)
    print()
    
    print("Option A: orders table (WRONG for revenue)")
    cur = conn.execute("""
        SELECT 
            status,
            COUNT(*) as count,
            ROUND(SUM(amount), 2) as total
        FROM orders 
        WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30'
        GROUP BY status
    """)
    total_orders = 0
    for row in cur:
        print(f"  {row[0]:20s}: {row[1]:4d} orders, ${row[2]:12,.2f}")
        total_orders += row[2]
    print(f"  {'TOTAL':20s}:           ${total_orders:12,.2f}  ❌ Includes cancelled/refunded")
    print()
    
    print("Option B: revenue_recognized table (CORRECT)")
    cur = conn.execute("""
        SELECT 
            period,
            ROUND(SUM(gross_amount), 2) as gross,
            ROUND(SUM(refund_amount), 2) as refunds,
            ROUND(SUM(net_amount), 2) as net
        FROM revenue_recognized 
        WHERE period IN ('2026-04', '2026-05', '2026-06')
        GROUP BY period
    """)
    total_net = 0
    for row in cur:
        print(f"  {row[0]}: Gross ${row[1]:10,.2f} - Refunds ${row[2]:10,.2f} = Net ${row[3]:10,.2f}")
        total_net += row[3]
    print(f"  TOTAL:                                            Net ${total_net:10,.2f}  ✓ Official number")
    print()
    
    print(f"Difference: ${total_orders - total_net:,.2f} ({((total_orders/total_net - 1)*100):.1f}% overstatement)")
    print()
    
    conn.close()

if __name__ == "__main__":
    test_queries_direct()
    show_table_comparison()
    
    print()
    print("="*70)
    print("DEPLOYMENT STEPS:")
    print("="*70)
    print()
    print("1. Back up current prompt:")
    print("   cp prompt.md prompt.md.backup")
    print()
    print("2. Deploy fixed prompt:")
    print("   cp output/fixed_prompt.md prompt.md")
    print()
    print("3. Test the fix:")
    print('   python agent.py "what was our Q2 2026 revenue?"')
    print()
    print("4. Verify it returns ~$3.6M (not $4.1M)")
    print()
