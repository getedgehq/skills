#!/usr/bin/env python3
"""Golden set evaluator for finbot.

Usage: python eval_judge.py [--run-agent]

By default, checks pre-recorded answers. Use --run-agent to test live.
"""
import json
import re
import sys
import sqlite3


def extract_number(text):
    """Extract the first dollar amount or number from text."""
    # Try to find $X,XXX.XX format
    match = re.search(r'\$([0-9,]+(?:\.[0-9]{2})?)', text)
    if match:
        return float(match.group(1).replace(',', ''))
    
    # Try to find plain number
    match = re.search(r'\b([0-9,]+(?:\.[0-9]+)?)\b', text)
    if match:
        return float(match.group(1).replace(',', ''))
    
    return None


def check_sql_query(query, constraints):
    """Check if SQL query meets the constraints."""
    query_lower = query.lower()
    issues = []
    
    for constraint in constraints:
        if "must use revenue_recognized" in constraint.lower():
            if "revenue_recognized" not in query_lower:
                issues.append(f"❌ {constraint}")
            else:
                issues.append(f"✓ {constraint}")
        
        elif "must sum net_amount" in constraint.lower():
            if "sum(net_amount)" not in query_lower:
                issues.append(f"❌ {constraint}")
            else:
                issues.append(f"✓ {constraint}")
        
        elif "must not use orders table" in constraint.lower():
            if "from orders" in query_lower:
                issues.append(f"❌ {constraint}")
            else:
                issues.append(f"✓ {constraint}")
        
        elif "must use orders table" in constraint.lower():
            if "from orders" not in query_lower:
                issues.append(f"❌ {constraint}")
            else:
                issues.append(f"✓ {constraint}")
    
    return issues


def judge_case(case_id, input_text, actual_answer, actual_sql, expected):
    """Judge a single test case."""
    print(f"\n{'='*70}")
    print(f"Case: {case_id}")
    print(f"Input: {input_text}")
    print(f"{'='*70}")
    
    passed = True
    
    # Check the number
    actual_num = extract_number(actual_answer)
    expected_num = expected.get('expected_number')
    
    if actual_num is not None and expected_num is not None:
        diff = abs(actual_num - expected_num)
        tolerance = 1000  # $1000 tolerance
        
        if diff <= tolerance:
            print(f"✓ Number check: ${actual_num:,.2f} (expected ${expected_num:,.2f}, diff ${diff:.2f})")
        else:
            print(f"❌ Number check: ${actual_num:,.2f} (expected ${expected_num:,.2f}, diff ${diff:,.2f})")
            passed = False
    else:
        print(f"⚠ Could not extract number from answer")
        print(f"  Actual: {actual_answer}")
        passed = False
    
    # Check SQL constraints
    if actual_sql and 'constraints' in expected:
        print(f"\nSQL constraints:")
        issues = check_sql_query(actual_sql, expected['constraints'])
        for issue in issues:
            print(f"  {issue}")
            if issue.startswith('❌'):
                passed = False
    
    # Show the SQL
    if actual_sql:
        print(f"\nActual SQL:\n  {actual_sql}")
    
    if 'correct_sql' in expected:
        print(f"\nExpected SQL:\n  {expected['correct_sql']}")
    
    print(f"\nResult: {'PASS ✓' if passed else 'FAIL ❌'}")
    return passed


def run_eval(use_live_agent=False):
    """Run the golden set evaluation."""
    
    # Load golden set
    with open('golden_set.jsonl', 'r') as f:
        cases = [json.loads(line) for line in f]
    
    print(f"Loaded {len(cases)} test cases")
    
    # For now, we'll test with the known bad answer from the transcript
    # In a real setup with --run-agent, we'd call agent.answer() here
    
    results = []
    
    if not use_live_agent:
        print("\n" + "="*70)
        print("TESTING WITH INCIDENT DATA (the bad answer that went to the board)")
        print("="*70)
        
        # Test the Q2 2026 case with the actual bad answer from transcript
        case = cases[0]  # q2-2026-revenue
        
        actual_answer = "Q2 2026 revenue was **$4,138,212.16** (~$4.1M)."
        actual_sql = "SELECT ROUND(SUM(amount), 2) AS revenue FROM orders WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';"
        
        passed = judge_case(
            case['id'],
            case['input'],
            actual_answer,
            actual_sql,
            case
        )
        
        results.append({
            'case_id': case['id'],
            'passed': passed
        })
    
    else:
        # Would run live agent here
        print("\nLive agent testing not implemented yet - need FINBOT_GATEWAY_TOKEN")
        print("To test manually: python agent.py 'what was our Q2 2026 revenue?'")
    
    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    
    passed_count = sum(1 for r in results if r['passed'])
    total_count = len(results)
    
    print(f"Passed: {passed_count}/{total_count}")
    
    if passed_count < total_count:
        print("\n⚠ FAILURES DETECTED - DO NOT DEPLOY")
        return 1
    else:
        print("\n✓ All tests passed")
        return 0


if __name__ == '__main__':
    use_live = '--run-agent' in sys.argv
    sys.exit(run_eval(use_live))
