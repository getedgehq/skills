#!/usr/bin/env python3
"""Judge script for finbot golden set. Runs test cases and checks output."""
import json
import re
import sys
import os
import sqlite3

# Add parent directory to path to import agent
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent import answer

def extract_number(text):
    """Extract first dollar amount or number from text."""
    # Try to find dollar amounts first
    dollar_match = re.search(r'\$?([\d,]+\.?\d*)[MmKk]?', text)
    if dollar_match:
        num_str = dollar_match.group(1).replace(',', '')
        num = float(num_str)
        # Handle M and K suffixes
        if 'M' in text[dollar_match.start():dollar_match.end()+1].upper():
            num *= 1_000_000
        elif 'K' in text[dollar_match.start():dollar_match.end()+1].upper():
            num *= 1_000
        return num
    return None

def check_table_used(conn, case_id):
    """Check if the correct table was queried by looking at test run."""
    # This is a simplified check - in production would parse SQL logs
    return None

def judge_case(case, conn):
    """Run a single test case and return pass/fail."""
    case_id = case['id']
    question = case['input']
    expected = case['expected_value']
    expected_table = case.get('expected_table')
    
    print(f"\n{'='*60}")
    print(f"Case: {case_id}")
    print(f"Question: {question}")
    print(f"Expected: {expected:,.2f}" if isinstance(expected, float) else f"Expected: {expected}")
    
    try:
        result = answer(question)
        print(f"Got: {result[:200]}")
        
        # Extract number from result
        actual = extract_number(result)
        
        if actual is None:
            print("❌ FAIL: Could not extract number from response")
            return False
        
        # Check if values match (within 1% tolerance for floats)
        if isinstance(expected, float):
            tolerance = abs(expected * 0.01)
            match = abs(actual - expected) <= tolerance
            print(f"Extracted: {actual:,.2f}")
            print(f"Expected: {expected:,.2f}")
            print(f"Diff: {abs(actual - expected):,.2f}")
        else:
            match = int(actual) == expected
            print(f"Extracted: {int(actual)}")
        
        if match:
            print("✓ PASS")
            return True
        else:
            print("❌ FAIL: Number mismatch")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    golden_path = os.path.join(os.path.dirname(__file__), 'golden.jsonl')
    
    # Load golden set
    cases = []
    with open(golden_path) as f:
        for line in f:
            cases.append(json.loads(line))
    
    print(f"Running {len(cases)} test cases from {golden_path}")
    
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'warehouse.db')
    conn = sqlite3.connect(db_path)
    
    results = []
    for case in cases:
        passed = judge_case(case, conn)
        results.append({
            'case_id': case['id'],
            'passed': passed
        })
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    passed = sum(1 for r in results if r['passed'])
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    
    for r in results:
        status = "✓" if r['passed'] else "❌"
        print(f"  {status} {r['case_id']}")
    
    return 0 if passed == total else 1

if __name__ == '__main__':
    sys.exit(main())
