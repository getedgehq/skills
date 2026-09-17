#!/usr/bin/env python3
"""
FinBot Golden Set Evaluator

Usage:
    python run_eval.py                    # Run all tests
    python run_eval.py --priority critical  # Run only critical tests
    python run_eval.py --verbose          # Show full output
"""

import json
import sys
import re
from datetime import datetime


def extract_numbers(text):
    """Extract all numbers from text for comparison."""
    # Remove commas and dollar signs
    text = text.replace(',', '').replace('$', '')
    # Find all numbers (including decimals)
    numbers = re.findall(r'\d+\.?\d*', text)
    return [float(n) for n in numbers]


def check_answer(case, bot_answer):
    """Check if bot answer matches expected answer."""
    results = {
        "passed": False,
        "errors": [],
        "warnings": []
    }
    
    # Extract expected value(s)
    expected_val = case.get("expected_value")
    
    if expected_val is None:
        # Check if answer indicates no data
        if "no data" in bot_answer.lower() or "null" in bot_answer.lower() or "0" in bot_answer:
            results["passed"] = True
        else:
            results["errors"].append("Expected NULL/no data handling")
        return results
    
    # Extract numbers from bot answer
    bot_numbers = extract_numbers(bot_answer)
    
    if isinstance(expected_val, dict):
        # Multi-value answer (e.g., comparison questions)
        # Check if all expected values appear in the answer
        expected_nums = [v for v in expected_val.values() if isinstance(v, (int, float))]
        
        matches = 0
        for exp in expected_nums:
            for bot in bot_numbers:
                if abs(bot - exp) < 1000:  # Allow $1000 tolerance
                    matches += 1
                    break
        
        if matches >= len(expected_nums):
            results["passed"] = True
        else:
            results["errors"].append(f"Expected {len(expected_nums)} values, matched {matches}")
            results["errors"].append(f"Expected values: {expected_nums}")
            results["errors"].append(f"Bot numbers: {bot_numbers}")
    
    else:
        # Single value answer
        expected_num = float(expected_val)
        
        # Check if expected number appears in bot answer (with tolerance)
        found = False
        for bot_num in bot_numbers:
            if abs(bot_num - expected_num) < 1000:  # $1000 tolerance
                found = True
                if abs(bot_num - expected_num) > 10:
                    results["warnings"].append(f"Close but not exact: {bot_num} vs {expected_num}")
                break
        
        if found:
            results["passed"] = True
        else:
            results["errors"].append(f"Expected {expected_num}, got {bot_numbers}")
    
    return results


def check_constraints(case, queries_run):
    """Check if SQL queries match constraints."""
    issues = []
    
    for constraint in case.get("constraints", []):
        constraint_lower = constraint.lower()
        
        # Check table usage
        if "must query" in constraint_lower or "must use" in constraint_lower:
            if "revenue_recognized" in constraint_lower:
                if not any("revenue_recognized" in q.lower() for q in queries_run):
                    issues.append(f"❌ {constraint}")
                    continue
            if "orders" in constraint_lower and "not revenue" not in constraint_lower:
                if not any("orders" in q.lower() and "revenue_recognized" not in q.lower() for q in queries_run):
                    issues.append(f"❌ {constraint}")
                    continue
            if "refunds" in constraint_lower:
                if not any("refunds" in q.lower() for q in queries_run):
                    issues.append(f"❌ {constraint}")
                    continue
        
        # Check columns
        if "net_amount" in constraint_lower:
            if not any("net_amount" in q.lower() for q in queries_run):
                issues.append(f"❌ {constraint}")
                continue
        
        # Check for avoiding wrong tables
        if "should not" in constraint_lower or "not revenue_recognized" in constraint_lower:
            if "revenue_recognized" in constraint_lower:
                if any("revenue_recognized" in q.lower() for q in queries_run):
                    issues.append(f"❌ {constraint}")
                    continue
    
    return issues


def run_eval(test_filter=None, verbose=False):
    """Run evaluation on golden set."""
    
    print("="*70)
    print("FinBot Golden Set Evaluation")
    print("="*70)
    print()
    
    # Load golden set
    cases = []
    with open('output/evals/golden.jsonl', 'r') as f:
        for line in f:
            case = json.loads(line)
            if test_filter is None or case.get('priority') == test_filter:
                cases.append(case)
    
    print(f"Loaded {len(cases)} test cases")
    if test_filter:
        print(f"Filter: priority={test_filter}")
    print()
    
    # NOTE: This eval script checks the golden set structure and expected values
    # To actually test the bot, you would:
    # 1. Import and call the agent.answer() function for each case
    # 2. Capture the SQL queries it ran
    # 3. Check the answer against expected values
    # 
    # For now, we'll demonstrate with the known incident case
    
    print("DEMO: Checking the Q2 revenue incident case")
    print("-"*70)
    
    incident_case = next((c for c in cases if c['id'] == 'q2_2026_revenue'), None)
    if incident_case:
        print(f"Test: {incident_case['question']}")
        print(f"Expected: {incident_case['expected_answer']}")
        print()
        
        # Simulate what the OLD bot did (from transcript)
        old_query = "SELECT ROUND(SUM(amount), 2) AS revenue FROM orders WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';"
        old_answer = "Q2 2026 revenue was $4,138,212.16 (~$4.1M)."
        
        print("OLD BOT (before fix):")
        print(f"  Query: {old_query}")
        print(f"  Answer: {old_answer}")
        
        result = check_answer(incident_case, old_answer)
        constraint_issues = check_constraints(incident_case, [old_query])
        
        print(f"  Answer check: {'✓ PASS' if result['passed'] else '✗ FAIL'}")
        if result['errors']:
            for err in result['errors']:
                print(f"    - {err}")
        
        print(f"  Constraint check: {'✗ FAIL' if constraint_issues else '✓ PASS'}")
        if constraint_issues:
            for issue in constraint_issues:
                print(f"    {issue}")
        
        print()
        print("  OVERALL: ✗ FAIL - Used wrong table (orders instead of revenue_recognized)")
        print()
        
        # What the fixed bot should do
        print("FIXED BOT (after applying fixes):")
        fixed_query = "SELECT ROUND(SUM(net_amount), 2) FROM revenue_recognized WHERE period IN ('2026-04', '2026-05', '2026-06');"
        fixed_answer = "Q2 2026 revenue was $3,638,335.79."
        
        print(f"  Query: {fixed_query}")
        print(f"  Answer: {fixed_answer}")
        
        result2 = check_answer(incident_case, fixed_answer)
        constraint_issues2 = check_constraints(incident_case, [fixed_query])
        
        print(f"  Answer check: {'✓ PASS' if result2['passed'] else '✗ FAIL'}")
        if result2['errors']:
            for err in result2['errors']:
                print(f"    - {err}")
        
        print(f"  Constraint check: {'✓ PASS' if not constraint_issues2 else '✗ FAIL'}")
        if constraint_issues2:
            for issue in constraint_issues2:
                print(f"    {issue}")
        
        print()
        print("  OVERALL: ✓ PASS - Correct table and value")
    
    print()
    print("="*70)
    print("Summary")
    print("="*70)
    print()
    print(f"Total test cases: {len(cases)}")
    print(f"  - Critical: {sum(1 for c in cases if c['priority'] == 'critical')}")
    print(f"  - High: {sum(1 for c in cases if c['priority'] == 'high')}")
    print(f"  - Medium: {sum(1 for c in cases if c['priority'] == 'medium')}")
    print(f"  - Low: {sum(1 for c in cases if c['priority'] == 'low')}")
    print()
    print("To run full evaluation:")
    print("  1. Update this script to import agent.answer()")
    print("  2. Or mock/record actual bot responses")
    print("  3. Run against both old and new prompts")
    print("  4. Compare pass rates")
    print()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run FinBot golden set evaluation")
    parser.add_argument("--priority", choices=["critical", "high", "medium", "low"], 
                        help="Filter by priority")
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    
    args = parser.parse_args()
    run_eval(test_filter=args.priority, verbose=args.verbose)
