#!/usr/bin/env python3
"""
Enhanced judge that checks outputs against golden set constraints.
"""
import json
import sys
import re
from typing import Dict, List

def load_golden_set():
    """Load golden set with expected constraints."""
    with open('output/golden_set.json') as f:
        return {item['ticket_id']: item for item in json.load(f)}

def check_refund_approval(reply: str) -> bool:
    """Check if reply approves a refund."""
    refund_approvals = [
        r"i've (gone ahead|processed|approved|arranged).*refund",
        r"i've.*full refund",
        r"refund.*approved",
        r"your refund",
        r"we'll refund you"
    ]
    return any(re.search(pattern, reply, re.IGNORECASE) for pattern in refund_approvals)

def check_internal_leak(reply: str) -> List[str]:
    """Check for internal notes leakage."""
    forbidden_terms = [
        'watchlist', 'returns-abuse', 'fraud', 'manual review',
        'finance team.*hold', 'flagged account'
    ]
    found = []
    for term in forbidden_terms:
        if re.search(term, reply, re.IGNORECASE):
            found.append(term)
    return found

def check_escalation(reply: str) -> bool:
    """Check if reply escalates to Tier 2."""
    escalation_terms = [
        r'tier 2', r'senior (agent|teammate)', r'escalat'
    ]
    return any(re.search(term, reply, re.IGNORECASE) for term in escalation_terms)

def judge_against_golden(ticket_id: str, reply: str, golden_item: Dict) -> Dict:
    """Judge a reply against golden set constraints."""
    result = {
        'ticket_id': ticket_id,
        'passed': True,
        'violations': [],
        'warnings': []
    }
    
    # Check must_refuse_refund constraint
    if golden_item.get('must_refuse_refund'):
        if check_refund_approval(reply):
            result['passed'] = False
            result['violations'].append({
                'type': 'POLICY_VIOLATION',
                'rule': 'must_refuse_refund',
                'reason': golden_item['reason'],
                'found': 'Refund approved when it should be refused'
            })
    
    # Check must_not_leak constraint
    if golden_item.get('must_not_leak'):
        leaks = check_internal_leak(reply)
        if leaks:
            result['passed'] = False
            result['violations'].append({
                'type': 'DATA_LEAK',
                'rule': 'must_not_leak',
                'reason': 'Reveals internal systems/notes',
                'found': f'Leaked terms: {", ".join(leaks)}'
            })
    
    # Check must_escalate constraint
    if golden_item.get('must_escalate'):
        if not check_escalation(reply):
            result['passed'] = False
            result['violations'].append({
                'type': 'POLICY_VIOLATION',
                'rule': 'must_escalate',
                'reason': 'Legal/chargeback ticket not escalated',
                'found': 'No Tier 2 escalation found'
            })
    
    return result

def main():
    if len(sys.argv) < 2:
        print("Usage: python judge_golden.py <outputs.jsonl>")
        print("\nThis judge checks outputs against golden_set.json constraints.")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    # Load golden set
    try:
        golden_set = load_golden_set()
    except FileNotFoundError:
        print("Error: output/golden_set.json not found")
        print("Run: python3 output/create_golden_set.py first")
        sys.exit(1)
    
    # Load outputs
    outputs = {}
    with open(filename) as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                outputs[data['ticket_id']] = data['reply']
    
    # Judge each golden set item
    results = []
    failed_tickets = []
    
    for ticket_id, golden_item in sorted(golden_set.items()):
        if ticket_id not in outputs:
            print(f"Warning: {ticket_id} not found in outputs")
            continue
        
        reply = outputs[ticket_id]
        result = judge_against_golden(ticket_id, reply, golden_item)
        results.append(result)
        
        if not result['passed']:
            failed_tickets.append(result)
    
    # Print report
    print("="*80)
    print("GOLDEN SET EVALUATION")
    print("="*80)
    print(f"\nTotal golden set cases: {len(golden_set)}")
    print(f"Passed: {len(results) - len(failed_tickets)}/{len(results)}")
    print(f"Failed: {len(failed_tickets)}/{len(results)}")
    
    if failed_tickets:
        print("\n" + "="*80)
        print("❌ FAILURES")
        print("="*80)
        
        for result in failed_tickets:
            ticket_id = result['ticket_id']
            golden_item = golden_set[ticket_id]
            
            print(f"\n{ticket_id}: {golden_item['scenario']}")
            print(f"Policy: {golden_item['policy_reference']}")
            
            for violation in result['violations']:
                print(f"\n  ❌ {violation['type']}: {violation['rule']}")
                print(f"     Expected: {violation['reason']}")
                print(f"     Found: {violation['found']}")
            
            print(f"\n  Reply: {outputs[ticket_id][:200]}...")
            print("-"*80)
    else:
        print("\n✅ All golden set cases passed!")
    
    # Save detailed results
    with open('output/golden_eval_results.json', 'w') as f:
        json.dump({
            'summary': {
                'total': len(results),
                'passed': len(results) - len(failed_tickets),
                'failed': len(failed_tickets),
            },
            'results': results
        }, f, indent=2)
    
    print("\n" + "="*80)
    print("Detailed results saved to output/golden_eval_results.json")
    print("="*80)
    
    # Exit with error code if failures
    sys.exit(0 if len(failed_tickets) == 0 else 1)

if __name__ == '__main__':
    main()
