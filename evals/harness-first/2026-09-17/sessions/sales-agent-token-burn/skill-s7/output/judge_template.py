#!/usr/bin/env python3
"""
Template for golden set evaluation judge.

Usage:
  1. Fill in the TODO sections
  2. Run: python judge_template.py golden_set.jsonl results.jsonl
  3. Review pass/fail output
"""
import json
import sys


def load_jsonl(path):
    """Load JSONL file into list of dicts."""
    with open(path) as f:
        return [json.loads(line) for line in f]


def judge_case(expected, actual):
    """
    Compare expected vs actual outcomes.
    
    Args:
        expected: dict with id, expected_score_min, expected_score_max, should_send_email
        actual: dict with lead_id, score, email_sent, email_body (from agent run)
    
    Returns:
        dict with pass/fail and reasons
    """
    failures = []
    
    # TODO: Extract actual score from agent output
    # This depends on how you structure the agent results
    actual_score = actual.get("score")
    if actual_score is None:
        failures.append("No score found in output")
    elif not (expected["expected_score_min"] <= actual_score <= expected["expected_score_max"]):
        failures.append(
            f"Score {actual_score} outside expected range "
            f"[{expected['expected_score_min']}, {expected['expected_score_max']}]"
        )
    
    # Check email sent/not sent
    actual_sent = actual.get("email_sent", False)
    if actual_sent != expected["should_send_email"]:
        failures.append(
            f"Email sent={actual_sent}, expected={expected['should_send_email']}"
        )
    
    # TODO: Check email quality if one was sent
    if actual_sent and expected["should_send_email"]:
        email_body = actual.get("email_body", "")
        word_count = len(email_body.split())
        
        if word_count > 120:
            failures.append(f"Email too long: {word_count} words (max 120)")
        
        if word_count < 30:
            failures.append(f"Email too short: {word_count} words (min ~30)")
        
        # TODO: Add more email quality checks
        # - Contains greeting?
        # - Mentions product/value prop?
        # - Has signature?
        # - Professional tone? (could use LLM judge here)
    
    return {
        "id": expected["id"],
        "passed": len(failures) == 0,
        "failures": failures,
    }


def main():
    if len(sys.argv) < 3:
        print("Usage: python judge_template.py golden_set.jsonl actual_results.jsonl")
        sys.exit(1)
    
    expected_cases = load_jsonl(sys.argv[1])
    actual_results = load_jsonl(sys.argv[2])
    
    # TODO: Match expected to actual by lead_id or eval id
    # This is a simplified version - you'll need to handle this based on your data
    results_by_id = {r["id"]: r for r in actual_results}
    
    passed = 0
    failed = 0
    
    print("=" * 70)
    print("GOLDEN SET EVALUATION RESULTS")
    print("=" * 70)
    
    for exp in expected_cases:
        act = results_by_id.get(exp["id"])
        if act is None:
            print(f"\n❌ {exp['id']}: NOT RUN")
            failed += 1
            continue
        
        result = judge_case(exp, act)
        
        if result["passed"]:
            print(f"\n✅ {exp['id']}: PASS")
            passed += 1
        else:
            print(f"\n❌ {exp['id']}: FAIL")
            for failure in result["failures"]:
                print(f"   - {failure}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"SUMMARY: {passed} passed, {failed} failed")
    print("=" * 70)


if __name__ == "__main__":
    main()
