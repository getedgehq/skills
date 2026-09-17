#!/usr/bin/env python3
"""
Judge for outreach agent golden set.

Checks deterministic constraints first (tool call counts, max turns, policy rules),
then uses LLM grading only for subjective quality.
"""
import json
import sys
from pathlib import Path

# Load golden set
golden_path = Path(__file__).parent / "golden.jsonl"
cases = []
with open(golden_path) as f:
    for line in f:
        cases.append(json.loads(line))

print(f"Loaded {len(cases)} golden set cases from {golden_path}")
print()

# Placeholder: actual eval would run agent and collect traces
# For now, just document the checks

results = []
for case in cases:
    case_id = case["case_id"]
    checks = []
    
    # Deterministic checks based on case type
    if "constraint" in case:
        if "must not call crm_get_account more than" in case["constraint"]:
            max_val = case["constraint"].split("more than")[1].strip().split()[0]
            checks.append({
                "type": "tool_count",
                "tool": "crm_get_account",
                "max": int(max_val),
                "description": case["constraint"]
            })
        elif "must call crm_get_account exactly 1 time" in case["constraint"]:
            checks.append({
                "type": "tool_count_exact",
                "tool": "crm_get_account",
                "expected": 1,
                "description": case["constraint"]
            })
        elif "must not call crm_update_contact more than" in case["constraint"]:
            max_val = case["constraint"].split("more than")[1].strip().split()[0]
            checks.append({
                "type": "tool_count",
                "tool": "crm_update_contact",
                "max": int(max_val),
                "description": case["constraint"]
            })
    
    if "max_turns" in case:
        checks.append({
            "type": "max_turns",
            "max": case["max_turns"],
            "description": f"Must complete in {case['max_turns']} turns or less"
        })
    
    if "expected_email_sent" in case:
        checks.append({
            "type": "policy_email",
            "expected": case["expected_email_sent"],
            "description": f"Email sent: {case['expected_email_sent']}"
        })
    
    if "expected_score_range" in case:
        checks.append({
            "type": "score_range",
            "min": case["expected_score_range"][0],
            "max": case["expected_score_range"][1],
            "description": f"Score in range {case['expected_score_range']}"
        })
    
    results.append({
        "case_id": case_id,
        "source": case.get("source", ""),
        "checks": checks,
        "status": "NOT_RUN"
    })

print("Deterministic checks defined for each case:")
print("-" * 80)
for result in results:
    print(f"\n{result['case_id']} (source: {result['source']})")
    if result['checks']:
        for check in result['checks']:
            print(f"  ✓ {check['description']}")
    else:
        print("  (behavior check only, see expected_behavior in golden.jsonl)")

print("\n" + "=" * 80)
print("TO RUN THIS EVAL:")
print("1. Implement agent runner that collects tool call traces")
print("2. Run agent on each case, log: turns, tool calls, final output")
print("3. Compare actual vs expected for each deterministic check")
print("4. For subjective checks (email quality), use LLM-as-judge with rubric")
print("5. Report pass/fail per case and aggregate stats")
print()
print("USAGE: python evals/judge.py [--run] [--model MODEL]")
print("  --run: actually execute agent (requires mock CRM or test env)")
print("  --model: override model for testing (default: from config.json)")
