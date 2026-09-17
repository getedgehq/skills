#!/usr/bin/env python3
"""Golden set evaluator for the outreach agent.

Usage:
    python evals/run_evals.py                    # run on current model
    python evals/run_evals.py --model claude-haiku-4-5  # run on specific model
    python evals/run_evals.py --case normal_high_score   # run single case
"""
import argparse
import json
import os
import sys
from datetime import datetime
from collections import Counter

# Add parent dir to path so we can import agent
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.loop import run_conversation, TurnLimitExceeded, CostLimitExceeded
from agent import llm as llm_mod
from agent import tools as tools_mod


class MockToolbox(tools_mod.Toolbox):
    """Mock toolbox that simulates CRM/email without real calls."""
    
    def __init__(self):
        super().__init__()
        self.call_log = []
    
    def execute(self, name, arguments):
        self.call_log.append({"tool": name, "args": arguments})
        
        # Simulate different scenarios based on account_id
        if name == "crm_get_account":
            account_id = arguments["account_id"]
            
            if "merged" in account_id:
                raise tools_mod.ToolError("Account was merged. Use the parent account ID instead.", status=404)
            
            if "broken" in account_id:
                # Return minimal data to trigger lots of turns
                return {"contacts": [{"id": "ct_001", "email": "test@example.com"}], "activities": []}
            
            # Return realistic mock data based on ID
            size = "large" if "large" in account_id else "medium"
            contact_count = 5 if "multi" in account_id else 1
            
            return {
                "account_id": account_id,
                "company": f"Test Company {account_id}",
                "size": size,
                "contacts": [
                    {"id": f"ct_{i:03d}", "email": f"contact{i}@test.com", "name": f"Contact {i}"}
                    for i in range(1, contact_count + 1)
                ],
                "activities": [] if "no_activity" in account_id else [
                    {"type": "page_view", "timestamp": "2026-09-01T10:00:00Z"}
                ],
                "notes": "spam detected" if "spam" in account_id else "normal account",
            }
        
        elif name == "crm_update_contact":
            contact_id = arguments["contact_id"]
            fields = arguments["fields"]
            
            # Simulate 422 on lead_score_v2 for test case 8
            if "lead_score_v2" in fields and contact_id == "ct_001":
                # First call fails with 422
                if self.call_log.count({"tool": "crm_update_contact", "args": arguments}) <= 1:
                    raise tools_mod.ToolError(
                        "Field 'lead_score_v2' does not exist in CRM schema. Check docs/crm_fields.md for valid fields.",
                        status=422
                    )
            
            return {"updated": True, "contact_id": contact_id}
        
        elif name == "send_email":
            return {"sent": True, "message_id": f"<test-{len(self.call_log)}@test.com>"}
        
        return super().execute(name, arguments)


def check_case(case, result):
    """Check if result matches expected criteria. Returns (pass, failures list)."""
    expected = case["expected"]
    failures = []
    
    # Check tools used
    if "tools" in expected:
        expected_tools = set(expected["tools"])
        actual_tools = set(c["tool"] for c in result.get("call_log", []))
        if not expected_tools.issubset(actual_tools):
            missing = expected_tools - actual_tools
            failures.append(f"missing tools: {missing}")
    
    # Check score range
    if "score_range" in expected:
        score = result.get("score")
        if score is None:
            failures.append("no score extracted")
        elif not (expected["score_range"][0] <= score <= expected["score_range"][1]):
            failures.append(f"score {score} not in range {expected['score_range']}")
    
    # Check email sent
    if "email_sent" in expected:
        email_sent = any(c["tool"] == "send_email" for c in result.get("call_log", []))
        if email_sent != expected["email_sent"]:
            failures.append(f"email_sent={email_sent}, expected {expected['email_sent']}")
    
    # Check score field used
    if "score_field" in expected:
        update_calls = [c for c in result.get("call_log", []) if c["tool"] == "crm_update_contact"]
        if not update_calls:
            failures.append("no crm_update_contact calls")
        else:
            fields = update_calls[-1]["args"]["fields"]  # check last update
            if expected["score_field"] not in fields:
                failures.append(f"field {expected['score_field']} not in {list(fields.keys())}")
    
    # Check max turns
    if "max_turns" in expected:
        turns = result.get("turns", 0)
        if turns > expected["max_turns"]:
            failures.append(f"turns={turns}, expected <={expected['max_turns']}")
    
    # Check max cost
    if "max_cost" in expected:
        cost = result.get("cost", 0)
        if cost > expected["max_cost"]:
            failures.append(f"cost=${cost:.4f}, expected <=${expected['max_cost']}")
    
    # Check single CRM fetch
    if "crm_get_account_count" in expected:
        actual = sum(1 for c in result.get("call_log", []) if c["tool"] == "crm_get_account")
        if actual != expected["crm_get_account_count"]:
            failures.append(f"crm_get_account called {actual} times, expected {expected['crm_get_account_count']}")
    
    # Check error raised
    if expected.get("cost_error_raised"):
        if result.get("error_type") != "CostLimitExceeded":
            failures.append(f"expected CostLimitExceeded, got {result.get('error_type', 'none')}")
    
    if expected.get("turn_error_raised"):
        if result.get("error_type") != "TurnLimitExceeded":
            failures.append(f"expected TurnLimitExceeded, got {result.get('error_type', 'none')}")
    
    return len(failures) == 0, failures


def run_case(case, llm):
    """Run a single test case. Returns result dict."""
    try:
        toolbox = MockToolbox()
        conv_id = f"test_{case['id']}"
        
        output = run_conversation(
            lead_id=case["lead_id"],
            llm=llm,
            tools=toolbox,
            conversation_id=conv_id,
            max_turns=case["expected"].get("max_turns", 10),
            max_cost_usd=case["expected"].get("max_cost", 2.0),
        )
        
        # Extract score from output (look for numbers)
        score = None
        import re
        matches = re.findall(r'\b(\d{1,3})\b', output)
        if matches:
            score = int(matches[0])
        
        return {
            "output": output,
            "call_log": toolbox.call_log,
            "turns": len([c for c in toolbox.call_log]),
            "cost": 0.0,  # would need to track from llm calls
            "score": score,
            "error": None,
            "error_type": None,
        }
    
    except (TurnLimitExceeded, CostLimitExceeded) as e:
        return {
            "output": None,
            "call_log": toolbox.call_log if 'toolbox' in locals() else [],
            "turns": len(toolbox.call_log) if 'toolbox' in locals() else 0,
            "cost": 0.0,
            "score": None,
            "error": str(e),
            "error_type": type(e).__name__,
        }
    
    except Exception as e:
        return {
            "output": None,
            "call_log": toolbox.call_log if 'toolbox' in locals() else [],
            "turns": 0,
            "cost": 0.0,
            "score": None,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def main():
    parser = argparse.ArgumentParser(description="Run golden set evals")
    parser.add_argument("--model", help="Model to test (default: from config)")
    parser.add_argument("--case", help="Run single case by ID")
    parser.add_argument("--output", help="Output file (default: evals/results_TIMESTAMP.jsonl)")
    args = parser.parse_args()
    
    # Load golden set
    with open("evals/golden.jsonl") as f:
        cases = [json.loads(line) for line in f]
    
    if args.case:
        cases = [c for c in cases if c["id"] == args.case]
        if not cases:
            print(f"Case {args.case} not found")
            return 1
    
    # Set up LLM (mock for now - would need to adapt llm.py)
    if args.model:
        print(f"Note: Model override not yet implemented, using config model")
    
    llm = llm_mod.Client.from_config()
    
    # Run cases
    results = []
    passed = 0
    failed = 0
    
    print(f"Running {len(cases)} test cases...")
    print()
    
    for case in cases:
        print(f"  {case['id']:<30}", end=" ")
        result = run_case(case, llm)
        is_pass, failures = check_case(case, result)
        
        if is_pass:
            print("✓ PASS")
            passed += 1
        else:
            print(f"✗ FAIL: {', '.join(failures)}")
            failed += 1
        
        results.append({
            "case_id": case["id"],
            "pass": is_pass,
            "failures": failures,
            "result": result,
        })
    
    # Summary
    print()
    print("=" * 60)
    print(f"PASSED: {passed}/{len(cases)}")
    print(f"FAILED: {failed}/{len(cases)}")
    print("=" * 60)
    
    # Save results
    output_path = args.output or f"evals/results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
    with open(output_path, "w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")
    print(f"Results saved to {output_path}")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
