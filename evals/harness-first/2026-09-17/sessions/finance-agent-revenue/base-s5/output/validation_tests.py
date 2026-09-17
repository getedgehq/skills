#!/usr/bin/env python3
"""
FinBot Validation Script
Tests that finbot gives correct answers for known financial metrics.
Run this after updating the prompt to verify the fix works.

Usage: python3 validation_tests.py
"""

import sqlite3
from typing import Dict, Tuple

# Known correct answers from warehouse.db
EXPECTED_ANSWERS = {
    "Q2 2026 Revenue": {
        "query": """
            SELECT ROUND(SUM(net_amount), 2) 
            FROM revenue_recognized 
            WHERE recognized_on BETWEEN '2026-04-01' AND '2026-06-30'
        """,
        "expected": 3638335.79,
        "tolerance": 0.01,
        "description": "Q2 2026 GAAP Revenue (net of refunds)"
    },
    "Q1 2026 Revenue": {
        "query": """
            SELECT ROUND(SUM(net_amount), 2) 
            FROM revenue_recognized 
            WHERE recognized_on BETWEEN '2026-01-01' AND '2026-03-31'
        """,
        "expected": 3285493.84,
        "tolerance": 0.01,
        "description": "Q1 2026 GAAP Revenue (net of refunds)"
    },
    "Q2 2026 Bookings": {
        "query": """
            SELECT ROUND(SUM(amount), 2) 
            FROM orders 
            WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30'
        """,
        "expected": 4138212.16,
        "tolerance": 0.01,
        "description": "Q2 2026 Gross Bookings (all orders)"
    },
    "Q2 2026 Completed Orders": {
        "query": """
            SELECT ROUND(SUM(amount), 2) 
            FROM orders 
            WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30' 
              AND status = 'completed'
        """,
        "expected": 3269510.70,
        "tolerance": 0.01,
        "description": "Q2 2026 Completed Orders Only"
    },
    "April 2026 Revenue": {
        "query": """
            SELECT ROUND(SUM(net_amount), 2) 
            FROM revenue_recognized 
            WHERE period = '2026-04'
        """,
        "expected": 1237516.63,
        "tolerance": 0.01,
        "description": "April 2026 Revenue"
    },
}


def run_validation(db_path: str = "warehouse.db") -> Dict[str, bool]:
    """Run all validation tests against the warehouse."""
    conn = sqlite3.connect(db_path)
    results = {}
    
    print("=" * 70)
    print("FINBOT VALIDATION TEST SUITE")
    print("=" * 70)
    print()
    
    all_passed = True
    
    for test_name, test_data in EXPECTED_ANSWERS.items():
        query = test_data["query"]
        expected = test_data["expected"]
        tolerance = test_data["tolerance"]
        description = test_data["description"]
        
        try:
            result = conn.execute(query).fetchone()[0]
            
            if result is None:
                passed = False
                status = "FAIL (NULL result)"
            else:
                diff = abs(result - expected)
                passed = diff <= tolerance
                status = "PASS" if passed else f"FAIL (off by ${diff:,.2f})"
            
            results[test_name] = passed
            all_passed = all_passed and passed
            
            icon = "✅" if passed else "❌"
            print(f"{icon} {test_name}")
            print(f"   {description}")
            print(f"   Expected: ${expected:,.2f}")
            if result is not None:
                print(f"   Got:      ${result:,.2f}")
            print(f"   Status:   {status}")
            print()
            
        except Exception as e:
            results[test_name] = False
            all_passed = False
            print(f"❌ {test_name}")
            print(f"   {description}")
            print(f"   ERROR: {str(e)}")
            print()
    
    conn.close()
    
    print("=" * 70)
    if all_passed:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 70)
    
    return results


def test_finbot_queries():
    """
    Test that common finbot queries return correct results.
    
    These are the queries finbot SHOULD generate after the prompt update.
    If these fail, the prompt needs more work.
    """
    print("\n" + "=" * 70)
    print("RECOMMENDED FINBOT QUERIES")
    print("=" * 70)
    print()
    
    queries = {
        'For: "What was Q2 2026 revenue?"': """
            SELECT ROUND(SUM(net_amount), 2) AS revenue
            FROM revenue_recognized
            WHERE recognized_on BETWEEN '2026-04-01' AND '2026-06-30';
        """,
        'For: "What were Q2 2026 bookings?"': """
            SELECT ROUND(SUM(amount), 2) AS bookings
            FROM orders
            WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';
        """,
        'For: "How much did we make in April?"': """
            SELECT ROUND(SUM(net_amount), 2) AS revenue
            FROM revenue_recognized
            WHERE period = '2026-04';
        """,
    }
    
    conn = sqlite3.connect("warehouse.db")
    
    for question, query in queries.items():
        print(f"Question: {question}")
        print(f"Correct SQL:")
        for line in query.strip().split('\n'):
            print(f"  {line}")
        
        result = conn.execute(query.strip()).fetchone()[0]
        print(f"Result: ${result:,.2f}")
        print()
    
    conn.close()


def compare_tables():
    """Show the difference between orders and revenue_recognized for Q2."""
    print("\n" + "=" * 70)
    print("Q2 2026: ORDERS vs REVENUE_RECOGNIZED")
    print("=" * 70)
    print()
    
    conn = sqlite3.connect("warehouse.db")
    
    orders_total = conn.execute("""
        SELECT ROUND(SUM(amount), 2) 
        FROM orders 
        WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30'
    """).fetchone()[0]
    
    revenue_total = conn.execute("""
        SELECT ROUND(SUM(net_amount), 2) 
        FROM revenue_recognized 
        WHERE recognized_on BETWEEN '2026-04-01' AND '2026-06-30'
    """).fetchone()[0]
    
    print(f"orders table (SUM of amount):              ${orders_total:>12,.2f}")
    print(f"  → Gross bookings, includes refunded/cancelled orders")
    print()
    print(f"revenue_recognized (SUM of net_amount):    ${revenue_total:>12,.2f}")
    print(f"  → GAAP revenue, net of refunds")
    print()
    print(f"Difference:                                ${(orders_total - revenue_total):>12,.2f}")
    print(f"  → This is what finbot got wrong!")
    print()
    
    # Show the breakdown
    print("Breakdown of orders by status:")
    statuses = conn.execute("""
        SELECT status, COUNT(*), ROUND(SUM(amount), 2)
        FROM orders
        WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30'
        GROUP BY status
        ORDER BY SUM(amount) DESC
    """).fetchall()
    
    for status, count, total in statuses:
        print(f"  {status:20s} {count:>4} orders  ${total:>12,.2f}")
    
    conn.close()


if __name__ == "__main__":
    # Run all validation tests
    results = run_validation()
    
    # Show recommended queries
    test_finbot_queries()
    
    # Show the comparison that explains the bug
    compare_tables()
    
    # Exit with error code if any tests failed
    if not all(results.values()):
        exit(1)
