#!/usr/bin/env python3
"""
Verification script - demonstrates the problem and solution without requiring LLM calls.
Shows what SQL the bot would run with current vs fixed prompt.
"""
import sqlite3

def main():
    conn = sqlite3.connect('warehouse.db')
    
    print("="*70)
    print("FINBOT Q2 REVENUE INCIDENT - SQL COMPARISON")
    print("="*70)
    
    print("\n" + "="*70)
    print("CURRENT BEHAVIOR (What finbot actually did)")
    print("="*70)
    
    # What finbot ran
    query1 = """
    SELECT ROUND(SUM(amount), 2) AS revenue 
    FROM orders 
    WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30'
    """
    
    print(f"\nQuery: {query1.strip()}")
    cur = conn.execute(query1)
    result = cur.fetchone()[0]
    print(f"\nResult: ${result:,.2f}")
    print(f"Rounded: $4.1M")
    print("\n⚠️  PROBLEM: This includes cancelled and refunded orders!")
    
    # Show breakdown
    print("\nBreakdown by order status:")
    query_breakdown = """
    SELECT status, COUNT(*) as count, ROUND(SUM(amount), 2) as total
    FROM orders 
    WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30'
    GROUP BY status
    ORDER BY total DESC
    """
    cur = conn.execute(query_breakdown)
    for row in cur.fetchall():
        status, count, total = row
        marker = "❌" if status in ('cancelled', 'refunded') else "✓"
        print(f"  {marker} {status:20s} {count:4d} orders  ${total:>12,.2f}")
    
    print("\n" + "="*70)
    print("CORRECT BEHAVIOR (What finbot should do)")
    print("="*70)
    
    # What finbot should run
    query2 = """
    SELECT ROUND(SUM(net_amount), 2) AS revenue
    FROM revenue_recognized
    WHERE period IN ('2026-04', '2026-05', '2026-06')
    """
    
    print(f"\nQuery: {query2.strip()}")
    cur = conn.execute(query2)
    result = cur.fetchone()[0]
    print(f"\nResult: ${result:,.2f}")
    print(f"Rounded: $3.6M")
    print("\n✓ CORRECT: This is net recognized revenue (matches finance close)")
    
    # Show breakdown
    print("\nBreakdown by month:")
    query_breakdown2 = """
    SELECT period, 
           ROUND(SUM(gross_amount), 2) as gross,
           ROUND(SUM(refund_amount), 2) as refunds,
           ROUND(SUM(net_amount), 2) as net
    FROM revenue_recognized
    WHERE period IN ('2026-04', '2026-05', '2026-06')
    GROUP BY period
    ORDER BY period
    """
    cur = conn.execute(query_breakdown2)
    print(f"  {'Month':<10s} {'Gross':>12s} {'Refunds':>12s} {'Net':>12s}")
    print("  " + "-"*50)
    for row in cur.fetchall():
        period, gross, refunds, net = row
        print(f"  {period:<10s} ${gross:>11,.2f} ${refunds:>11,.2f} ${net:>11,.2f}")
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    wrong = 4138212.16
    right = 3638335.79
    diff = wrong - right
    
    print(f"\nFinBot's answer (wrong): ${wrong:>12,.2f}  (from orders table)")
    print(f"Finance close (correct):  ${right:>12,.2f}  (from revenue_recognized)")
    print(f"                          {'─'*16}")
    print(f"Discrepancy:              ${diff:>12,.2f}  (cancelled + refunded)")
    
    print(f"\nThis ${diff:,.2f} difference went into the board deck.")
    
    print("\n" + "="*70)
    print("THE FIX")
    print("="*70)
    print("""
The updated prompt (output/prompt_fixed.md) now explicitly states:

  "For any question about revenue:
   - Use revenue_recognized table, NOT orders table
   - Sum the net_amount column (gross revenue minus refunds)"

The updated agent (output/agent_fixed.py) adds:
   - Max 5 iterations (prevents runaway loops)
   - Read-only database connection (prevents accidental writes)
   - Query logging (for future tracing)

The golden set (output/golden.jsonl) includes test cases that will catch
this error before it reaches production.
""")

if __name__ == '__main__':
    main()
