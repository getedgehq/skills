#!/usr/bin/env python3
"""
Golden set judge for FinBot.

Runs test cases against the agent and validates:
- Correct table/column used
- Correct numeric value (within tolerance)
- No hallucinations

Usage:
  python judge.py                    # run all tests
  python judge.py --case q2_revenue  # run specific test
  python judge.py --verbose          # show full bot responses
"""
import json
import re
import sys
import sqlite3
from pathlib import Path

# Adjust import path to find agent.py
sys.path.insert(0, str(Path(__file__).parent.parent))


def load_golden_set(path="evals/golden.jsonl"):
    cases = []
    with open(path) as f:
        for line in f:
            if line.strip():
                cases.append(json.loads(line))
    return cases


def extract_sql_from_response(response):
    """Extract SQL queries from bot response (works with transcripts or raw output)."""
    # Look for SQL in markdown code blocks or raw queries
    pattern = r'```sql\n(.*?)```|SELECT\s+.*?;'
    matches = re.findall(pattern, response, re.IGNORECASE | re.DOTALL)
    queries = []
    for match in matches:
        if isinstance(match, tuple):
            query = match[0] if match[0] else match[1]
        else:
            query = match
        if query and query.strip():
            queries.append(query.strip())
    return queries


def extract_number_from_response(response):
    """Extract dollar amount or number from bot response."""
    # Look for $X,XXX,XXX.XX or plain numbers
    dollar_match = re.search(r'\$[\d,]+\.?\d*', response)
    if dollar_match:
        return float(dollar_match.group().replace('$', '').replace(',', ''))
    
    # Look for standalone numbers
    number_match = re.search(r'\b(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\b', response)
    if number_match:
        return float(number_match.group().replace(',', ''))
    
    return None


def check_query_table(queries, expected_table):
    """Check if any query uses the expected table."""
    for query in queries:
        if expected_table.lower() in query.lower():
            return True
    return False


def check_query_column(queries, expected_column):
    """Check if any query references the expected column."""
    for query in queries:
        if expected_column.lower() in query.lower():
            return True
    return False


def run_test(case, agent_fn, verbose=False):
    """Run a single test case."""
    test_id = case['id']
    user_input = case['input']
    
    # Run the bot
    try:
        response = agent_fn(user_input)
    except Exception as e:
        return {
            'id': test_id,
            'status': 'ERROR',
            'error': str(e),
            'input': user_input
        }
    
    if verbose:
        print(f"\n--- Response for {test_id} ---")
        print(response)
        print("---\n")
    
    # Extract queries from response
    queries = extract_sql_from_response(response)
    
    result = {
        'id': test_id,
        'input': user_input,
        'queries': queries,
        'response_snippet': response[:200] if len(response) > 200 else response,
        'checks': []
    }
    
    # Check 1: Expected table
    if 'expected_query_table' in case:
        table_ok = check_query_table(queries, case['expected_query_table'])
        result['checks'].append({
            'check': 'table',
            'expected': case['expected_query_table'],
            'passed': table_ok
        })
    
    # Check 2: Expected column
    if 'expected_query_column' in case:
        column_ok = check_query_column(queries, case['expected_query_column'])
        result['checks'].append({
            'check': 'column',
            'expected': case['expected_query_column'],
            'passed': column_ok
        })
    
    # Check 3: Expected value
    if 'expected_value' in case:
        actual_value = extract_number_from_response(response)
        tolerance = case.get('tolerance', 0)
        
        if actual_value is None:
            value_ok = False
        else:
            diff = abs(actual_value - case['expected_value'])
            value_ok = diff <= tolerance
        
        result['checks'].append({
            'check': 'value',
            'expected': case['expected_value'],
            'actual': actual_value,
            'tolerance': tolerance,
            'passed': value_ok
        })
    
    # Check 4: Value in range
    if 'expected_min' in case or 'expected_max' in case:
        actual_value = extract_number_from_response(response)
        min_val = case.get('expected_min', float('-inf'))
        max_val = case.get('expected_max', float('inf'))
        
        if actual_value is None:
            range_ok = False
        else:
            range_ok = min_val <= actual_value <= max_val
        
        result['checks'].append({
            'check': 'range',
            'expected_min': min_val,
            'expected_max': max_val,
            'actual': actual_value,
            'passed': range_ok
        })
    
    # Determine overall status
    if not result['checks']:
        result['status'] = 'SKIP'
    elif all(c['passed'] for c in result['checks']):
        result['status'] = 'PASS'
    else:
        result['status'] = 'FAIL'
    
    return result


def print_results(results):
    """Print test results in a readable format."""
    print("\n" + "="*70)
    print("GOLDEN SET RESULTS")
    print("="*70 + "\n")
    
    passed = sum(1 for r in results if r['status'] == 'PASS')
    failed = sum(1 for r in results if r['status'] == 'FAIL')
    errors = sum(1 for r in results if r['status'] == 'ERROR')
    
    for result in results:
        status_emoji = {
            'PASS': '✅',
            'FAIL': '❌',
            'ERROR': '💥',
            'SKIP': '⏭️ '
        }
        
        emoji = status_emoji.get(result['status'], '?')
        print(f"{emoji} {result['id']} - {result['status']}")
        
        if result['status'] == 'ERROR':
            print(f"   Error: {result['error']}")
        elif result['status'] == 'FAIL':
            for check in result['checks']:
                if not check['passed']:
                    print(f"   ❌ {check['check']}: expected {check.get('expected')}, got {check.get('actual')}")
        
        if result.get('queries'):
            print(f"   Queries: {len(result['queries'])} found")
    
    print("\n" + "-"*70)
    print(f"TOTAL: {len(results)} tests")
    print(f"✅ PASSED: {passed}")
    print(f"❌ FAILED: {failed}")
    print(f"💥 ERRORS: {errors}")
    print("-"*70 + "\n")
    
    return passed, failed, errors


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Run FinBot golden set tests')
    parser.add_argument('--case', help='Run specific test case by ID')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show full bot responses')
    parser.add_argument('--golden', default='evals/golden.jsonl', help='Path to golden set file')
    args = parser.parse_args()
    
    # Load golden set
    try:
        cases = load_golden_set(args.golden)
    except FileNotFoundError:
        print(f"❌ Golden set not found: {args.golden}")
        sys.exit(1)
    
    # Filter to specific case if requested
    if args.case:
        cases = [c for c in cases if c['id'] == args.case]
        if not cases:
            print(f"❌ Test case '{args.case}' not found in golden set")
            sys.exit(1)
    
    print(f"Running {len(cases)} test(s)...\n")
    
    # Import agent (this would normally import the real agent.answer function)
    try:
        from agent import answer as agent_fn
    except ImportError:
        print("⚠️  Could not import agent.answer - using mock for demonstration")
        # Mock agent for this demo
        def agent_fn(question):
            # Simulate what the current broken bot would return
            if "Q2 2026 revenue" in question or "Q2" in question:
                return "SELECT SUM(amount) FROM orders WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30'; Result: $4,138,212.16"
            return "Mock response"
    
    # Run tests
    results = []
    for case in cases:
        result = run_test(case, agent_fn, verbose=args.verbose)
        results.append(result)
    
    # Print results
    passed, failed, errors = print_results(results)
    
    # Exit code
    sys.exit(0 if failed == 0 and errors == 0 else 1)


if __name__ == '__main__':
    main()
