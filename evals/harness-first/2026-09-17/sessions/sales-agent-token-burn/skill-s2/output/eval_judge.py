#!/usr/bin/env python3
"""
Eval judge for outreach agent.

Runs golden set and checks:
- Did it complete successfully?
- Was CRM update successful?
- Was email sent when appropriate?
- Did it stay within cost/turn limits?
- Was the correct score field used?

Usage:
    python eval_judge.py --golden-set evals/golden.jsonl --output results.jsonl
"""
import argparse
import json
import sys
from pathlib import Path

# Add agent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.loop import run_conversation
from agent import llm, tools


def check_case(case, result):
    """Check one test case against expected outcomes."""
    failures = []
    
    # Check max turns
    if "max_turns" in case["expected"]:
        if result["turns"] > case["expected"]["max_turns"]:
            failures.append(f"Exceeded max turns: {result['turns']} > {case['expected']['max_turns']}")
    
    # Check max cost
    if "max_cost_usd" in case["expected"]:
        if result["total_cost"] > case["expected"]["max_cost_usd"]:
            failures.append(f"Exceeded max cost: ${result['total_cost']:.4f} > ${case['expected']['max_cost_usd']}")
    
    # Check CRM update succeeded
    if case["expected"].get("crm_update_succeeded"):
        if not result.get("crm_update_success"):
            failures.append("CRM update failed or not attempted")
    
    # Check score field
    if "score_field" in case["expected"]:
        if result.get("score_field_used") != case["expected"]["score_field"]:
            failures.append(f"Wrong score field: {result.get('score_field_used')} != {case['expected']['score_field']}")
    
    # Check email sent
    if case["expected"].get("email_sent"):
        if not result.get("email_sent"):
            failures.append("Expected email to be sent but it wasn't")
    
    # Check email conditional
    if "email_sent_if_score_gte_50" in case["expected"]:
        score = result.get("score", 0)
        email_sent = result.get("email_sent", False)
        if score >= 50 and not email_sent:
            failures.append(f"Score {score} >= 50 but no email sent")
        elif score < 50 and email_sent:
            failures.append(f"Score {score} < 50 but email was sent")
    
    return {
        "passed": len(failures) == 0,
        "failures": failures,
        "result": result,
    }


def run_eval(golden_set_path, output_path):
    """Run all cases in golden set and write results."""
    cases = []
    with open(golden_set_path) as f:
        for line in f:
            cases.append(json.loads(line))
    
    results = []
    for i, case in enumerate(cases):
        print(f"Running case {i+1}/{len(cases)}: {case['lead_id']}...", end=" ")
        
        # Mock the agent run
        # In real implementation, this would:
        # 1. Run run_conversation() with the lead
        # 2. Parse logs/traces to extract: turns, cost, CRM updates, emails
        # 3. Return structured result
        
        # For now, stub it:
        result = {
            "lead_id": case["lead_id"],
            "turns": 4,
            "total_cost": 0.15,
            "crm_update_success": True,
            "email_sent": True,
            "score": 65,
            "score_field_used": "lead_score",
        }
        
        check_result = check_case(case, result)
        
        if check_result["passed"]:
            print("✅ PASS")
        else:
            print(f"❌ FAIL: {', '.join(check_result['failures'])}")
        
        results.append({
            "case": case,
            "check": check_result,
        })
    
    # Write results
    with open(output_path, "w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")
    
    # Summary
    passed = sum(1 for r in results if r["check"]["passed"])
    total = len(results)
    print()
    print(f"Results: {passed}/{total} passed ({passed/total*100:.1f}%)")
    print(f"Written to: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run golden set evals")
    parser.add_argument("--golden-set", required=True, help="Path to golden set JSONL")
    parser.add_argument("--output", required=True, help="Path to write results JSONL")
    args = parser.parse_args()
    
    run_eval(args.golden_set, args.output)
