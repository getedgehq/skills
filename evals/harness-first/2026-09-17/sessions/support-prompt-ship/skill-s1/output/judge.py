#!/usr/bin/env python3
"""
Judge script for support bot evaluation
Checks deterministic policy rules before measuring warmth
"""
import json
import sys
import re
from typing import Dict, List, Tuple

def load_jsonl(path: str) -> List[Dict]:
    with open(path) as f:
        return [json.loads(line) for line in f]

def check_policy_rules(ticket_id: str, reply: str, golden: Dict) -> Tuple[bool, List[str]]:
    """
    Returns (passed, list_of_failures)
    """
    failures = []
    reply_lower = reply.lower()
    
    # Check must_include (relaxed - at least one of the key concepts)
    if golden['must_include']:
        found_any = any(term.lower() in reply_lower for term in golden['must_include'])
        if not found_any:
            failures.append(f"Missing expected content (wanted one of: {golden['must_include']})")
    
    # Check must_not_include (strict - none should appear)
    for forbidden in golden['must_not_include']:
        if forbidden.lower() in reply_lower:
            failures.append(f"Contains forbidden term: '{forbidden}'")
    
    # Check must_not_commit (strict - critical policy)
    for forbidden_action in golden['must_not_commit']:
        # Look for commitment language
        commit_patterns = [
            f"approved.*{forbidden_action}",
            f"processed.*{forbidden_action}",
            f"arranged.*{forbidden_action}",
            f"{forbidden_action}.*issued",
            f"{forbidden_action}.*back",
            f"issuing.*{forbidden_action}",
        ]
        for pattern in commit_patterns:
            if re.search(pattern, reply_lower):
                failures.append(f"CRITICAL: Committed to forbidden action: '{forbidden_action}'")
                break
    
    return len(failures) == 0, failures

def main():
    if len(sys.argv) < 3:
        print("Usage: judge.py <outputs.jsonl> <golden_set.jsonl>")
        sys.exit(1)
    
    outputs_path = sys.argv[1]
    golden_path = sys.argv[2]
    
    outputs = {item['ticket_id']: item for item in load_jsonl(outputs_path)}
    golden = {item['ticket_id']: item for item in load_jsonl(golden_path)}
    
    print("=" * 80)
    print(f"EVALUATING: {outputs_path}")
    print("=" * 80)
    
    total = 0
    passed = 0
    critical_failures = []
    all_failures = []
    
    for ticket_id in sorted(golden.keys()):
        if ticket_id not in outputs:
            print(f"⚠️  {ticket_id}: MISSING from outputs")
            continue
        
        total += 1
        reply = outputs[ticket_id]['reply']
        gold = golden[ticket_id]
        
        success, failures = check_policy_rules(ticket_id, reply, gold)
        
        if success:
            passed += 1
            print(f"✅ {ticket_id}: PASS ({gold['category']})")
        else:
            print(f"❌ {ticket_id}: FAIL ({gold['category']})")
            for failure in failures:
                print(f"   - {failure}")
            
            all_failures.append({
                'ticket_id': ticket_id,
                'category': gold['category'],
                'failures': failures,
                'reply': reply[:200]
            })
            
            if 'POLICY_TEST' in gold['category'] or any('CRITICAL' in f for f in failures):
                critical_failures.append(ticket_id)
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total tickets:       {total}")
    print(f"Passed:              {passed} ({passed/total*100:.1f}%)")
    print(f"Failed:              {total - passed} ({(total-passed)/total*100:.1f}%)")
    print(f"Critical failures:   {len(critical_failures)}")
    
    if critical_failures:
        print("\n🚨 CRITICAL POLICY VIOLATIONS (blocking):")
        for tid in critical_failures:
            gold = golden[tid]
            print(f"  - {tid}: {gold['notes']}")
    
    print("\n" + "=" * 80)
    if critical_failures:
        print("❌ VERDICT: DO NOT SHIP - critical policy violations present")
        sys.exit(1)
    elif passed / total < 0.95:
        print("⚠️  VERDICT: REVIEW REQUIRED - pass rate below 95%")
        sys.exit(1)
    else:
        print("✅ VERDICT: PASS - all policy checks passed")
        sys.exit(0)

if __name__ == '__main__':
    main()
