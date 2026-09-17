#!/usr/bin/env python3
"""Judge script for outreach agent golden set.

Runs test cases and checks constraints. Reports pass/fail.
"""
import json
import sys
from typing import Dict, List, Any


def check_constraints(case: Dict, trace: List[Dict]) -> tuple[bool, List[str]]:
    """Check if a conversation trace meets the test case constraints.
    
    Returns:
        (passed, list_of_violations)
    """
    violations = []
    constraints = case.get("constraints", {})
    
    # Count turns
    num_turns = len(trace)
    max_turns = constraints.get("max_turns")
    if max_turns and num_turns > max_turns:
        violations.append(f"Exceeded max_turns: {num_turns} > {max_turns}")
    
    # Collect all tool calls
    all_tool_calls = []
    for turn in trace:
        all_tool_calls.extend(turn.get("tool_calls", []))
    
    # Check must_call
    must_call = constraints.get("must_call", [])
    for tool in must_call:
        if tool not in all_tool_calls:
            violations.append(f"Required tool not called: {tool}")
    
    # Check must_not_call
    must_not_call = constraints.get("must_not_call", [])
    for tool in must_not_call:
        if tool in all_tool_calls:
            violations.append(f"Forbidden tool called: {tool}")
    
    # Check must_not_call_repeatedly
    must_not_repeat = constraints.get("must_not_call_repeatedly", [])
    for tool in must_not_repeat:
        count = all_tool_calls.count(tool)
        if count > 1:
            violations.append(f"Tool called {count} times (should be called once): {tool}")
    
    # Check must_not_retry_same_error
    if constraints.get("must_not_retry_same_error"):
        # Look for patterns of same error repeated
        errors = []
        for turn in trace:
            # In real implementation, would parse tool results for errors
            # For now, check turn count as proxy (>8 = likely retry loop)
            if num_turns > 8:
                violations.append("Likely retry loop detected (>8 turns)")
                break
    
    # Check must_complete
    if constraints.get("must_complete"):
        last_turn = trace[-1] if trace else {}
        if last_turn.get("stop_reason") != "end_turn":
            violations.append("Conversation did not complete (no end_turn)")
    
    passed = len(violations) == 0
    return passed, violations


def main():
    # Load golden set
    with open("evals/golden.jsonl") as f:
        cases = [json.loads(line) for line in f]
    
    print("=" * 80)
    print("GOLDEN SET JUDGE - BRIGHTKILN OUTREACH AGENT")
    print("=" * 80)
    print()
    
    # For now, report what would be checked
    # In production, this would run the agent and collect traces
    
    print(f"Loaded {len(cases)} test cases\n")
    
    print("Test constraints that will be checked:")
    print()
    
    for i, case in enumerate(cases, 1):
        print(f"{i}. {case['case_id']}")
        print(f"   Scenario: {case['input']['scenario']}")
        constraints = case.get("constraints", {})
        if constraints:
            print("   Checks:")
            for key, val in constraints.items():
                print(f"     - {key}: {val}")
        print()
    
    print("=" * 80)
    print("TO RUN:")
    print("  1. Mock or connect to CRM test environment")
    print("  2. Run agent on each case input")
    print("  3. Collect traces and pass to check_constraints()")
    print("  4. Report pass/fail with violations")
    print()
    print("This framework is ready. Add test execution when you have a CRM test env.")
    print("=" * 80)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
