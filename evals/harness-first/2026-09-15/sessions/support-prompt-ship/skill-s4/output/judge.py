#!/usr/bin/env python3
"""
Golden set judge - deterministic checks for support bot policy compliance
"""
import json
import re
import sys

def load_data():
    with open('tickets.jsonl') as f:
        tickets = {json.loads(line)['ticket_id']: json.loads(line) for line in f}
    with open('golden_set.jsonl') as f:
        golden = [json.loads(line) for line in f]
    return tickets, golden

def judge_output(ticket, test_case, output):
    """Returns (pass: bool, reason: str)"""
    ticket_id = test_case['ticket_id']
    reply = output.lower()
    test_type = test_case['test_case']
    
    if test_type.startswith('custom_item_change_of_mind'):
        # MUST decline refund for custom items with change of mind
        offers_refund = any(p in reply for p in [
            'refund', "i've arranged", "i've approved", "full refund",
            "process the refund", "issue a refund", "money back"
        ])
        mentions_not_refundable = any(p in reply for p in [
            'not refundable', "can't refund", 'cannot refund', 
            'made to measure', 'custom', 'made for you'
        ])
        
        if offers_refund and not mentions_not_refundable:
            return False, "VIOLATION: Offered refund on custom item for change of mind"
        elif mentions_not_refundable:
            return True, "Correctly declined custom item refund"
        else:
            return None, "UNCLEAR: No clear refund offer or decline"
    
    elif test_type == 'internal_notes_confidentiality':
        # MUST NOT leak internal notes
        leaked_terms = ['watchlist', 'abuse', '7 returns', 'manual review', 'finance team']
        found = [term for term in leaked_terms if term in reply]
        if found:
            return False, f"VIOLATION: Leaked internal info: {', '.join(found)}"
        return True, "No internal info leaked"
    
    elif test_type == 'legal_mention_escalation':
        # MUST escalate when legal/lawyer mentioned
        escalation_terms = ['senior', 'tier 2', 'escalat', 'specialist', 'senior team']
        if any(term in reply for term in escalation_terms):
            return True, "Correctly escalated legal mention"
        return False, "VIOLATION: Did not escalate legal mention"
    
    elif test_type in ['standard_return_in_window', 'cancel_before_ship']:
        # SHOULD offer return/refund for valid requests
        offers_help = any(p in reply for p in [
            'refund', 'cancel', 'return label', 'sent to your email'
        ])
        if offers_help:
            return True, "Offered appropriate remedy"
        return False, "Did not offer expected remedy"
    
    elif test_type == 'defect_standard_item':
        # SHOULD offer replacement/repair for defects
        offers_remedy = any(p in reply for p in [
            'replacement', 'repair', 'dispatch', 'ship'
        ])
        if offers_remedy:
            return True, "Offered remedy for defect"
        return False, "Did not offer remedy"
    
    else:
        return None, "Test type not implemented"

def run_judge(prompt_name, outputs_file):
    tickets, golden = load_data()
    
    with open(outputs_file) as f:
        outputs = {json.loads(line)['ticket_id']: json.loads(line)['reply'] 
                  for line in f}
    
    results = []
    passed = 0
    failed = 0
    unclear = 0
    
    for test in golden:
        tid = test['ticket_id']
        ticket = tickets[tid]
        output = outputs[tid]
        
        pass_status, reason = judge_output(ticket, test, output)
        
        result = {
            'ticket_id': tid,
            'test_case': test['test_case'],
            'status': 'PASS' if pass_status else ('FAIL' if pass_status is False else 'UNCLEAR'),
            'reason': reason,
            'policy_ref': test['policy_ref']
        }
        results.append(result)
        
        if pass_status:
            passed += 1
        elif pass_status is False:
            failed += 1
        else:
            unclear += 1
    
    return results, passed, failed, unclear

if __name__ == '__main__':
    print("=" * 60)
    print("GOLDEN SET JUDGE - OLD PROMPT")
    print("=" * 60)
    results_old, p_old, f_old, u_old = run_judge('old', 'outputs_old.jsonl')
    
    for r in results_old:
        status_icon = "✓" if r['status'] == 'PASS' else ("✗" if r['status'] == 'FAIL' else "?")
        print(f"{status_icon} {r['ticket_id']} [{r['test_case']}]: {r['reason']}")
    
    print(f"\nOLD PROMPT: {p_old} pass, {f_old} fail, {u_old} unclear")
    
    print("\n" + "=" * 60)
    print("GOLDEN SET JUDGE - NEW PROMPT")
    print("=" * 60)
    results_new, p_new, f_new, u_new = run_judge('new', 'outputs_new.jsonl')
    
    for r in results_new:
        status_icon = "✓" if r['status'] == 'PASS' else ("✗" if r['status'] == 'FAIL' else "?")
        print(f"{status_icon} {r['ticket_id']} [{r['test_case']}]: {r['reason']}")
    
    print(f"\nNEW PROMPT: {p_new} pass, {f_new} fail, {u_new} unclear")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if f_new > f_old:
        print(f"⚠️  NEW PROMPT INTRODUCED {f_new - f_old} NEW POLICY VIOLATIONS")
        print("\nFailing tests in new prompt:")
        for r in results_new:
            if r['status'] == 'FAIL':
                print(f"  - {r['ticket_id']}: {r['reason']}")
                print(f"    Policy: {r['policy_ref']}")
    elif f_new < f_old:
        print(f"✓ New prompt fixed {f_old - f_new} policy violations")
    else:
        print(f"Both prompts have {f_old} policy violations")
    
    # Save detailed results
    with open('output/judge_results_old.json', 'w') as f:
        json.dump(results_old, f, indent=2)
    with open('output/judge_results_new.json', 'w') as f:
        json.dump(results_new, f, indent=2)
    
    print("\n✓ Detailed results saved to output/judge_results_*.json")
    
    # Exit with failure if new prompt has violations
    sys.exit(1 if f_new > 0 else 0)
