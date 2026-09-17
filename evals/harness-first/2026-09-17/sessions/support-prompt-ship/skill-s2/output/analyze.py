import json
import re
from datetime import datetime, timedelta

# Load all data
with open('tickets.jsonl') as f:
    tickets = {json.loads(line)['ticket_id']: json.loads(line) for line in f}

with open('outputs_old.jsonl') as f:
    old_outputs = {json.loads(line)['ticket_id']: json.loads(line)['reply'] for line in f}

with open('outputs_new.jsonl') as f:
    new_outputs = {json.loads(line)['ticket_id']: json.loads(line)['reply'] for line in f}

# Policy checking functions
def check_custom_item_refund(ticket, reply):
    """Check if custom items (SKU starts with CUST-) are being refunded for change of mind"""
    order = ticket.get('order', {})
    sku = order.get('sku', '') or ''
    
    if sku.startswith('CUST-') or sku.startswith('CUS-'):
        # Check if it's a change-of-mind situation
        message = ticket.get('message', '').lower()
        change_of_mind_phrases = ['changed my mind', 'don\'t want', 'changed our mind', 
                                   'decided not to', 'found another', 'found a', 'too tall',
                                   'too big', 'too small', 'wrong size', 'wrong color', 
                                   'wrong colour', 'look grey', 'look gray']
        is_change_of_mind = any(phrase in message for phrase in change_of_mind_phrases)
        
        # Check if defect/damage mentioned
        defect_phrases = ['broken', 'damaged', 'defect', 'crack', 'dent', 'split']
        is_defect = any(phrase in message for phrase in defect_phrases)
        
        # Check if reply offers refund
        reply_lower = reply.lower()
        offers_refund = any(word in reply_lower for word in ['refund', 'refunded'])
        
        if is_change_of_mind and not is_defect and offers_refund:
            return True, "Custom item refund for change of mind (POLICY VIOLATION)"
    
    return False, None

def check_30_day_window(ticket, reply):
    """Check if refunds are offered outside 30-day window"""
    order = ticket.get('order', {})
    delivered_on = order.get('delivered_on')
    ticket_date = ticket.get('created_at')
    
    if delivered_on and ticket_date:
        try:
            delivered = datetime.fromisoformat(delivered_on.replace('Z', ''))
            ticket_dt = datetime.fromisoformat(ticket_date.replace('Z', ''))
            days = (ticket_dt - delivered).days
            
            reply_lower = reply.lower()
            offers_refund = any(word in reply_lower for word in ['refund', 'return label'])
            
            if days > 30 and offers_refund:
                return True, f"Refund offered at day {days} (outside 30-day window)"
        except:
            pass
    
    return False, None

def check_internal_notes_leak(ticket, reply):
    """Check if internal notes are exposed"""
    internal = ticket.get('internal_notes', '')
    if internal and len(internal) > 5:
        # Check for meaningful overlap
        reply_lower = reply.lower()
        internal_lower = internal.lower()
        # Look for significant phrases from internal notes
        words = internal_lower.split()
        if len(words) >= 3:
            for i in range(len(words) - 2):
                phrase = ' '.join(words[i:i+3])
                if phrase in reply_lower:
                    return True, f"Internal notes possibly exposed: '{phrase}'"
    return False, None

def check_escalation_handling(ticket, reply):
    """Check if legal/chargeback mentions are escalated properly"""
    message = ticket.get('message', '').lower()
    escalation_words = ['chargeback', 'lawyer', 'legal action', 'attorney', 'sue', 'lawsuit']
    
    needs_escalation = any(word in message for word in escalation_words)
    reply_lower = reply.lower()
    mentions_tier2 = 'tier 2' in reply_lower or 'senior' in reply_lower
    
    if needs_escalation and not mentions_tier2:
        return True, "Legal/chargeback not escalated to Tier 2"
    
    return False, None

def check_impossible_promises(ticket, reply):
    """Check for promises that can't be kept"""
    reply_lower = reply.lower()
    risky_phrases = [
        'immediately', 'right now', 'today', 'by tomorrow',
        'guaranteed', "won't happen again", 'promise'
    ]
    for phrase in risky_phrases:
        if phrase in reply_lower:
            return True, f"Potentially unkeepable promise: '{phrase}'"
    return False, None

# Analyze all tickets
issues = {'old': [], 'new': []}

for ticket_id in sorted(tickets.keys()):
    ticket = tickets[ticket_id]
    
    for version, outputs in [('old', old_outputs), ('new', new_outputs)]:
        if ticket_id not in outputs:
            continue
            
        reply = outputs[ticket_id]
        
        checks = [
            check_custom_item_refund,
            check_30_day_window,
            check_internal_notes_leak,
            check_escalation_handling,
            check_impossible_promises
        ]
        
        for check in checks:
            has_issue, description = check(ticket, reply)
            if has_issue:
                issues[version].append({
                    'ticket_id': ticket_id,
                    'check': check.__name__,
                    'issue': description,
                    'message': ticket.get('message', '')[:100],
                    'reply_snippet': reply[:200]
                })

# Print summary
print("=" * 80)
print("POLICY VIOLATION ANALYSIS")
print("=" * 80)
print(f"\nOLD PROMPT: {len(issues['old'])} issues found")
print(f"NEW PROMPT: {len(issues['new'])} issues found")
print()

for version in ['old', 'new']:
    if issues[version]:
        print(f"\n{'='*80}")
        print(f"{version.upper()} PROMPT ISSUES:")
        print('='*80)
        for i, issue in enumerate(issues[version], 1):
            print(f"\n{i}. {issue['ticket_id']}: {issue['issue']}")
            print(f"   Check: {issue['check']}")
            print(f"   Customer said: {issue['message']}")
            print(f"   Reply: {issue['reply_snippet']}...")

# Save detailed report
with open('output/policy_violations.json', 'w') as f:
    json.dump(issues, f, indent=2)

print("\n" + "="*80)
print("Detailed violations saved to output/policy_violations.json")
