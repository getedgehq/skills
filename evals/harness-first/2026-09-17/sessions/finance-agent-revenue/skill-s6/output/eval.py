#!/usr/bin/env python3
"""
FinBot Evaluation Script

Runs the golden set test cases against FinBot and reports pass/fail.

Usage:
    python eval.py [--golden golden_set.jsonl] [--verbose]
"""

import argparse
import json
import sys
import re
from pathlib import Path

# Add current dir to path to import agent
sys.path.insert(0, str(Path(__file__).parent.parent))

def load_golden_set(path):
    """Load test cases from JSONL file."""
    cases = []
    with open(path, 'r') as f:
        for line in f:
            cases.append(json.loads(line))
    return cases

def extract_number(text):
    """Extract first number from text (handles $1,234.56 format)."""
    # Remove currency symbols and commas
    cleaned = re.sub(r'[$,]', '', text)
    # Find first number (int or float)
    match = re.search(r'-?\d+\.?\d*', cleaned)
    if match:
        return float(match.group())
    return None

def check_numeric_answer(expected, actual, tolerance_pct=0.1):
    """Check if actual is within tolerance of expected."""
    if expected == 0:
        return actual == 0
    
    diff_pct = abs((actual - expected) / expected) * 100
    return diff_pct <= tolerance_pct

def check_sql_constraints(sql_log, constraints):
    """Check if SQL queries meet the constraints."""
    failures = []
    
    if constraints.get('must_use_revenue_recognized'):
        if 'revenue_recognized' not in sql_log.lower():
            failures.append("Should use revenue_recognized table")
    
    if constraints.get('must_not_use_orders_table'):
        if 'from orders' in sql_log.lower():
            failures.append("Should NOT use orders table for revenue")
    
    return failures

def run_test_case(case, agent_fn, verbose=False):
    """Run a single test case and return pass/fail with details."""
    question = case['question']
    expected_numeric = case.get('expected_answer_numeric')
    tolerance = case.get('tolerance_pct', 0.1)
    constraints = case.get('constraints', {})
    
    if verbose:
        print(f"\n--- Test: {case['id']} ---")
        print(f"Question: {question}")
        print(f"Expected: {case['expected_answer']}")
    
    try:
        # Run the agent (this would need SQL logging enabled)
        answer = agent_fn(question)
        
        if verbose:
            print(f"Got: {answer[:200]}")
        
        # Extract numeric value from answer
        actual_numeric = extract_number(answer)
        
        if actual_numeric is None and expected_numeric is not None:
            return {
                'id': case['id'],
                'pass': False,
                'reason': 'No numeric answer found',
                'expected': case['expected_answer'],
                'actual': answer[:100]
            }
        
        # Check numeric match
        if expected_numeric is not None:
            if check_numeric_answer(expected_numeric, actual_numeric, tolerance):
                result = {'id': case['id'], 'pass': True}
                if verbose:
                    print("✓ PASS")
                return result
            else:
                diff_pct = abs((actual_numeric - expected_numeric) / expected_numeric) * 100
                return {
                    'id': case['id'],
                    'pass': False,
                    'reason': f'Wrong number: {diff_pct:.1f}% off',
                    'expected': expected_numeric,
                    'actual': actual_numeric
                }
        
        # For non-numeric cases, just check we got an answer
        if answer and len(answer) > 0:
            return {'id': case['id'], 'pass': True}
        else:
            return {
                'id': case['id'],
                'pass': False,
                'reason': 'Empty answer'
            }
    
    except Exception as e:
        return {
            'id': case['id'],
            'pass': False,
            'reason': f'Exception: {str(e)[:100]}',
            'error': str(e)
        }

def main():
    parser = argparse.ArgumentParser(description='Evaluate FinBot against golden set')
    parser.add_argument('--golden', default='golden_set.jsonl', help='Path to golden set JSONL')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--no-run', action='store_true', help='Just validate golden set format')
    args = parser.parse_args()
    
    # Load golden set
    golden_path = Path(args.golden)
    if not golden_path.exists():
        print(f"Error: Golden set not found: {golden_path}")
        sys.exit(1)
    
    cases = load_golden_set(golden_path)
    print(f"Loaded {len(cases)} test cases from {golden_path}")
    
    if args.no_run:
        print("\n✓ Golden set format valid")
        for case in cases:
            print(f"  [{case['id']}] {case['question']}")
        sys.exit(0)
    
    # Import agent
    try:
        from agent import answer as agent_answer
    except ImportError:
        print("Error: Could not import agent.py")
        print("Make sure you run this from the output/ directory or set PYTHONPATH")
        sys.exit(1)
    
    # Run all test cases
    print("\n" + "="*80)
    print("Running evaluation...")
    print("="*80)
    
    results = []
    for case in cases:
        result = run_test_case(case, agent_answer, verbose=args.verbose)
        results.append(result)
        
        if not args.verbose:
            status = "✓ PASS" if result['pass'] else "✗ FAIL"
            print(f"{status:8} [{result['id']}]")
            if not result['pass']:
                print(f"         Reason: {result.get('reason', 'Unknown')}")
    
    # Summary
    passed = sum(1 for r in results if r['pass'])
    total = len(results)
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    print("\n" + "="*80)
    print(f"RESULTS: {passed}/{total} passed ({pass_rate:.1f}%)")
    print("="*80)
    
    # Show failures
    failures = [r for r in results if not r['pass']]
    if failures:
        print(f"\nFailed cases ({len(failures)}):")
        for r in failures:
            print(f"  ✗ {r['id']}")
            print(f"    Reason: {r.get('reason', 'Unknown')}")
            if 'expected' in r:
                print(f"    Expected: {r['expected']}")
            if 'actual' in r:
                print(f"    Actual: {r['actual']}")
    
    # Exit code
    sys.exit(0 if passed == total else 1)

if __name__ == '__main__':
    main()
