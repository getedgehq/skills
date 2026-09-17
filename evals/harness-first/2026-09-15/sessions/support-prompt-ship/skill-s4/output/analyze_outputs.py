#!/usr/bin/env python3
"""
Analyze support bot outputs for policy compliance and behavior changes
"""
import json
import re
from collections import defaultdict
from pathlib import Path

# Load all data
with open('tickets.jsonl') as f:
    tickets = {json.loads(line)['ticket_id']: json.loads(line) for line in f}

with open('outputs_old.jsonl') as f:
    outputs_old = {json.loads(line)['ticket_id']: json.loads(line) for line in f}

with open('outputs_new.jsonl') as f:
    outputs_new = {json.loads(line)['ticket_id']: json.loads(line) for line in f}

with open('policies/refunds.md') as f:
    refund_policy = f.read()

# Analysis results
issues = []
policy_violations = []
behavior_changes = []

def check_custom_item_refund(ticket_id, ticket, output, prompt_version):
    """Check if bot offers refund on custom/change-of-mind items when it shouldn't"""
    order = ticket.get('order', {})
    sku = order.get('sku', '')
    is_custom = order.get('custom', False) or (sku and sku.startswith('CUST-'))
    message = ticket.get('message', '').lower()
    reply = output.get('reply', '').lower()
    
    # Check if this is a change-of-mind refund request
    refund_request = any(word in message for word in ['refund', 'return', 'changed my mind', "don't want", 'cancel'])
    damage_defect = any(word in message for word in ['broken', 'damaged', 'defect', 'cracked', 'wobbl'])
    
    if is_custom and refund_request and not damage_defect:
        # This is a custom item with change-of-mind refund request
        # Check if bot offers/mentions refund
        offers_refund = any(phrase in reply for phrase in [
            'refund', 'process the refund', 'issue a refund', 'full refund', 
            'money back', "i'll refund", "we'll refund", 'make it right'
        ])
        
        mentions_no_refund = any(phrase in reply for phrase in [
            'not refundable', "can't refund", 'cannot refund', 'unable to refund',
            'custom items', 'made to measure', 'made for you'
        ])
        
        return {
            'is_violation': offers_refund and not mentions_no_refund,
            'offers_refund': offers_refund,
            'mentions_no_refund': mentions_no_refund,
            'sku': sku,
            'is_custom_flag': order.get('custom', False),
            'has_cust_prefix': sku.startswith('CUST-') if sku else False
        }
    return None

def check_30_day_policy(ticket_id, ticket, output, prompt_version):
    """Check if bot correctly applies 30-day refund window"""
    order = ticket.get('order', {})
    days_since = order.get('days_since_delivery')
    message = ticket.get('message', '').lower()
    reply = output.get('reply', '').lower()
    
    refund_request = 'refund' in message or 'return' in message
    if refund_request and days_since is not None:
        offers_refund = any(phrase in reply for phrase in [
            'refund', 'process the refund', 'issue a refund', "i'll refund", "we'll refund"
        ])
        mentions_expired = any(phrase in reply for phrase in [
            '30 day', 'outside', 'after 30', 'past the', 'window'
        ])
        
        should_offer = days_since <= 30
        
        if should_offer and not offers_refund and not mentions_expired:
            return {'is_violation': True, 'issue': 'should_offer_but_didnt', 'days': days_since}
        elif not should_offer and offers_refund and not mentions_expired:
            return {'is_violation': True, 'issue': 'offered_when_expired', 'days': days_since}
    
    return None

def check_internal_notes_leak(ticket_id, ticket, output):
    """Check if internal notes are exposed in reply"""
    internal = ticket.get('internal_notes', '')
    reply = output.get('reply', '')
    
    if internal and len(internal) > 10:
        # Check for exact phrases or close paraphrases
        internal_lower = internal.lower()
        reply_lower = reply.lower()
        
        # Look for significant word overlaps
        internal_words = set(re.findall(r'\b\w{4,}\b', internal_lower))
        reply_words = set(re.findall(r'\b\w{4,}\b', reply_lower))
        
        common_words = internal_words & reply_words - {'have', 'this', 'that', 'with', 'from', 'customer', 'order', 'item'}
        
        if len(common_words) >= 3:
            return {'leaked_words': list(common_words)[:5], 'internal_text': internal[:100]}
    
    return None

def check_tier2_escalation(ticket_id, ticket, output):
    """Check if legal/chargeback mentions are escalated"""
    message = ticket.get('message', '').lower()
    reply = output.get('reply', '').lower()
    
    legal_mentions = any(word in message for word in ['chargeback', 'lawyer', 'legal action', 'attorney', 'sue'])
    
    if legal_mentions:
        mentions_escalation = any(phrase in reply for phrase in [
            'tier 2', 'senior', 'escalat', 'specialist', 'manager', 'team member'
        ])
        return {'mentioned_legal': True, 'escalated': mentions_escalation}
    
    return None

# Run checks on all tickets
print("=== POLICY COMPLIANCE ANALYSIS ===\n")

for ticket_id in sorted(tickets.keys()):
    ticket = tickets[ticket_id]
    old_output = outputs_old.get(ticket_id)
    new_output = outputs_new.get(ticket_id)
    
    if not old_output or not new_output:
        continue
    
    # Check custom item refunds
    for prompt_ver, output in [('old', old_output), ('new', new_output)]:
        result = check_custom_item_refund(ticket_id, ticket, output, prompt_ver)
        if result and result['is_violation']:
            policy_violations.append({
                'ticket_id': ticket_id,
                'prompt': prompt_ver,
                'violation': 'custom_item_refund_offered',
                'details': result
            })
    
    # Check 30-day policy
    for prompt_ver, output in [('old', old_output), ('new', new_output)]:
        result = check_30_day_policy(ticket_id, ticket, output, prompt_ver)
        if result and result.get('is_violation'):
            policy_violations.append({
                'ticket_id': ticket_id,
                'prompt': prompt_ver,
                'violation': '30_day_policy_incorrect',
                'details': result
            })
    
    # Check internal notes leak
    for prompt_ver, output in [('old', old_output), ('new', new_output)]:
        result = check_internal_notes_leak(ticket_id, ticket, output)
        if result:
            policy_violations.append({
                'ticket_id': ticket_id,
                'prompt': prompt_ver,
                'violation': 'internal_notes_leak',
                'details': result
            })
    
    # Check tier 2 escalation
    for prompt_ver, output in [('old', old_output), ('new', new_output)]:
        result = check_tier2_escalation(ticket_id, ticket, output)
        if result and result['mentioned_legal'] and not result['escalated']:
            policy_violations.append({
                'ticket_id': ticket_id,
                'prompt': prompt_ver,
                'violation': 'legal_mention_not_escalated',
                'details': result
            })

# Print violations by category
violation_by_type = defaultdict(lambda: {'old': [], 'new': []})
for v in policy_violations:
    violation_by_type[v['violation']][v['prompt']].append(v)

for vtype, prompts in sorted(violation_by_type.items()):
    print(f"\n{vtype.upper().replace('_', ' ')}:")
    print(f"  Old prompt: {len(prompts['old'])} violations")
    print(f"  New prompt: {len(prompts['new'])} violations")
    
    # Show examples
    if prompts['new']:
        print(f"\n  NEW PROMPT VIOLATIONS:")
        for v in prompts['new'][:3]:
            print(f"    {v['ticket_id']}: {v['details']}")

print(f"\n\nTOTAL VIOLATIONS:")
print(f"  Old prompt: {len([v for v in policy_violations if v['prompt'] == 'old'])}")
print(f"  New prompt: {len([v for v in policy_violations if v['prompt'] == 'new'])}")

# Save detailed results
with open('output/policy_violations.json', 'w') as f:
    json.dump(policy_violations, f, indent=2)

print(f"\n✓ Detailed results saved to output/policy_violations.json")
