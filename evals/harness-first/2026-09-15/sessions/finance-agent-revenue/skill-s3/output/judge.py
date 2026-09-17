#!/usr/bin/env python3
"""
Judge: Automated test scorer for FinBot.
Usage: python judge.py [--agent agent.py] [--golden golden-set.jsonl]
"""
import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path


def extract_number(text):
    """Extract the first dollar amount or number from text."""
    # Try to find dollar amounts first
    dollar_match = re.search(r'\$\s*([\d,]+(?:\.\d{2})?)', text)
    if dollar_match:
        return float(dollar_match.group(1).replace(',', ''))
    
    # Try to find any number
    number_match = re.search(r'([\d,]+(?:\.\d+)?)', text)
    if number_match:
        return float(number_match.group(1).replace(',', ''))
    
    return None


def check_case(case, answer, verbose=False):
    """Check if an answer passes a test case."""
    case_id = case['id']
    
    # Check for expected value (numeric comparison)
    if 'expected_value' in case:
        expected = case['expected_value']
        tolerance = case.get('tolerance', 0.01)
        
        actual = extract_number(answer)
        if actual is None:
            return False, f"Could not extract number from answer"
        
        diff = abs(actual - expected)
        if diff <= tolerance:
            return True, f"✓ {actual} matches {expected} (within {tolerance})"
        else:
            return False, f"✗ {actual} != {expected} (diff: {diff})"
    
    # Check for expected strings in answer
    if 'expected_answer_contains' in case:
        missing = []
        for expected_str in case['expected_answer_contains']:
            if str(expected_str) not in answer:
                missing.append(expected_str)
        
        if not missing:
            return True, f"✓ Answer contains all expected strings"
        else:
            return False, f"✗ Missing: {missing}"
    
    return None, "No assertions defined for this case"


def run_reference_query(case):
    """Run the reference SQL query to get the expected answer."""
    if 'reference_sql' not in case:
        return None
    
    try:
        conn = sqlite3.connect('warehouse.db')
        result = conn.execute(case['reference_sql']).fetchone()
        conn.close()
        return result[0] if result else None
    except Exception as e:
        return f"Error: {e}"


def main():
    parser = argparse.ArgumentParser(description='Run golden set tests against FinBot')
    parser.add_argument('--agent', default='agent.py', help='Agent script to test')
    parser.add_argument('--golden', default='output/golden-set.jsonl', help='Golden set file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--dry-run', action='store_true', help='Just validate golden set without running agent')
    args = parser.parse_args()
    
    # Load golden set
    golden_path = Path(args.golden)
    if not golden_path.exists():
        print(f"Error: Golden set not found at {golden_path}")
        return 1
    
    cases = []
    with open(golden_path) as f:
        for line in f:
            if line.strip():
                cases.append(json.loads(line))
    
    print(f"Loaded {len(cases)} test cases from {golden_path}")
    
    if args.dry_run:
        print("\n=== DRY RUN: Validating golden set ===")
        for i, case in enumerate(cases, 1):
            print(f"\n{i}. [{case['id']}]")
            print(f"   Input: {case['input']}")
            if 'expected_value' in case:
                print(f"   Expected: {case['expected_value']} {case.get('expected_unit', '')}")
            if 'expected_answer_contains' in case:
                print(f"   Must contain: {case['expected_answer_contains']}")
            if 'reference_sql' in case:
                result = run_reference_query(case)
                print(f"   Reference query result: {result}")
        return 0
    
    # Check if agent exists
    agent_path = Path(args.agent)
    if not agent_path.exists():
        print(f"Error: Agent not found at {agent_path}")
        return 1
    
    # Run tests
    print(f"\n=== Running tests against {agent_path} ===\n")
    
    results = []
    passed = 0
    failed = 0
    errors = 0
    
    for i, case in enumerate(cases, 1):
        case_id = case['id']
        question = case['input']
        
        print(f"{i}/{len(cases)} [{case_id}]", end=' ')
        sys.stdout.flush()
        
        # Run the agent
        try:
            import subprocess
            result = subprocess.run(
                ['python3', str(agent_path), question],
                capture_output=True,
                text=True,
                timeout=30
            )
            answer = result.stdout.strip()
            
            if result.returncode != 0:
                print(f"ERROR (exit {result.returncode})")
                if args.verbose:
                    print(f"   stderr: {result.stderr}")
                errors += 1
                results.append({
                    'case_id': case_id,
                    'status': 'error',
                    'error': result.stderr
                })
                continue
            
            # Check the answer
            success, message = check_case(case, answer, args.verbose)
            
            if success:
                print(f"PASS")
                passed += 1
                results.append({
                    'case_id': case_id,
                    'status': 'pass',
                    'answer': answer
                })
            else:
                print(f"FAIL - {message}")
                if args.verbose:
                    print(f"   Question: {question}")
                    print(f"   Answer: {answer}")
                failed += 1
                results.append({
                    'case_id': case_id,
                    'status': 'fail',
                    'reason': message,
                    'answer': answer
                })
        
        except subprocess.TimeoutExpired:
            print("TIMEOUT")
            errors += 1
            results.append({
                'case_id': case_id,
                'status': 'timeout'
            })
        except Exception as e:
            print(f"ERROR - {e}")
            errors += 1
            results.append({
                'case_id': case_id,
                'status': 'error',
                'error': str(e)
            })
    
    # Summary
    total = len(cases)
    print(f"\n{'='*60}")
    print(f"RESULTS: {passed}/{total} passed, {failed} failed, {errors} errors")
    print(f"Pass rate: {100*passed/total:.1f}%")
    print(f"{'='*60}")
    
    # Failed cases detail
    if failed > 0:
        print(f"\nFailed cases:")
        for r in results:
            if r['status'] == 'fail':
                print(f"  - {r['case_id']}: {r.get('reason', 'unknown')}")
    
    # Save results
    results_path = Path('output/judge-results.json')
    with open(results_path, 'w') as f:
        json.dump({
            'summary': {
                'total': total,
                'passed': passed,
                'failed': failed,
                'errors': errors,
                'pass_rate': passed / total if total > 0 else 0
            },
            'results': results
        }, f, indent=2)
    
    print(f"\nDetailed results saved to {results_path}")
    
    return 0 if failed == 0 and errors == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
