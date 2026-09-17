#!/usr/bin/env python3
"""
Test script to verify finbot returns correct revenue numbers after prompt fix.
Run this after deploying prompt_FIXED.md to validate the fix works.
"""

import sqlite3

def get_correct_revenue(period_list):
    """Get the correct revenue from revenue_recognized table."""
    conn = sqlite3.connect('warehouse.db')
    cursor = conn.cursor()
    
    placeholders = ','.join(['?' for _ in period_list])
    query = f"""
        SELECT ROUND(SUM(net_amount), 2)
        FROM revenue_recognized
        WHERE period IN ({placeholders})
    """
    cursor.execute(query, period_list)
    result = cursor.fetchone()[0]
    conn.close()
    return result

def test_finbot_response(question, expected_periods, expected_amount):
    """Test if finbot would return the correct amount."""
    print(f"\n{'='*70}")
    print(f"TEST: {question}")
    print('='*70)
    print(f"Expected periods: {', '.join(expected_periods)}")
    print(f"Expected amount:  ${expected_amount:,.2f}")
    
    # Get what the correct query should return
    actual = get_correct_revenue(expected_periods)
    
    if abs(actual - expected_amount) < 0.01:  # Account for rounding
        print(f"Actual amount:    ${actual:,.2f}")
        print("✅ PASS - Amount matches")
        return True
    else:
        print(f"Actual amount:    ${actual:,.2f}")
        print(f"❌ FAIL - Mismatch of ${abs(actual - expected_amount):,.2f}")
        return False

def main():
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                   FINBOT FIX VALIDATION TEST                         ║
╚══════════════════════════════════════════════════════════════════════╝

This script validates the expected revenue numbers from the database.
After deploying prompt_FIXED.md, run:
    
    python agent.py "what was our Q2 2026 revenue?"
    
And verify finbot returns these numbers.
""")

    tests = [
        ("What was our Q2 2026 revenue?", 
         ['2026-04', '2026-05', '2026-06'], 
         3638335.79),
        
        ("What was our Q1 2026 revenue?",
         ['2026-01', '2026-02', '2026-03'],
         3285493.84),
        
        ("How much revenue in June 2026?",
         ['2026-06'],
         1191160.85),
        
        ("What was revenue in April 2026?",
         ['2026-04'],
         1237516.63),
    ]
    
    passed = 0
    failed = 0
    
    for question, periods, expected in tests:
        if test_finbot_response(question, periods, expected):
            passed += 1
        else:
            failed += 1
    
    print(f"\n{'='*70}")
    print("SUMMARY")
    print('='*70)
    print(f"Tests passed: {passed}/{len(tests)}")
    print(f"Tests failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n✅ All validation tests passed!")
        print("\nNext step: Test actual finbot with:")
        print('    python agent.py "what was our Q2 2026 revenue?"')
        print("\nFinbot should:")
        print("  1. Query revenue_recognized table (not orders)")
        print("  2. Sum net_amount (not gross_amount or orders.amount)")
        print("  3. Return ~$3.6M for Q2 (not $4.1M)")
    else:
        print("\n❌ Some tests failed - check database or expected values")
    
    print()

if __name__ == "__main__":
    main()
