#!/usr/bin/env python3
"""
Reusable prompt testing script for support bot
Run this every time you update the prompt to check for policy violations.

Usage:
    python test_prompt.py <tickets_file> <outputs_file> <prompt_name>

Example:
    python test_prompt.py tickets.jsonl outputs_new.jsonl "new_prompt_v4"
"""
import sys
import json
import re
from datetime import datetime
from collections import defaultdict

# Policy constants
REFUND_WINDOW_DAYS = 30

def parse_date(date_str):
    """Parse ISO date or datetime string, removing timezone info"""
    if not date_str:
        return None
    date_str = re.sub(r'(\+|-)\d{2}:\d{2}$', '', date_str)
    date_str = date_str.replace('Z', '').replace('T', ' ').split('.')[0]
    parts = date_str.split()
    if len(parts) == 1:
        return datetime.fromisoformat(date_str + ' 00:00:00')
    return datetime.fromisoformat(date_str)

def days_since_delivery(ticket):
    """Calculate days since delivery"""
    order = ticket.get('order', {})
    if not order.get('delivered_on'):
        return None
    delivered = parse_date(order['delivered_on'])
    ticket_date = parse_date(ticket['created_at'])
    return (ticket_date - delivered).days

def is_within_refund_window(ticket):
    """Check if ticket is within 30-day refund window"""
    days = days_since_delivery(ticket)
    if days is None:
        return None
    return days <= REFUND_WINDOW_DAYS

def is_custom_item(ticket):
    """Check if item is custom/made-to-measure"""
    sku = ticket.get('order', {}).get('sku')
    if not sku:
        return False
    return sku.startswith('CUST-')

def mentions_legal_escalation(message):
    """Check if message mentions legal/chargeback keywords"""
    if not message:
        return False
    keywords = ['chargeback', 'lawyer', 'legal action', 'attorney', 'solicitor']
    msg_lower = message.lower()
    return any(kw in msg_lower for kw in keywords)

def check_refund_offered(reply):
    """Check if a refund was approved/offered in the reply"""
    reply_lower = reply.lower()
    refund_signals = [
        "i've arranged a full refund",
        "i've processed a full refund", 
        "i've approved a full refund",
        "i've gone ahead and approved a full refund",
        "we'll refund you",
        "your refund will",
        "approved a full refund",
        "processed a full refund",
        "refund for you",
        "refund on its way"
    ]
    return any(signal in reply_lower for signal in refund_signals)

def check_policy_violations(ticket, reply):
    """Check for policy violations"""
    violations = []
    message = ticket.get('message', '')
    order = ticket.get('order', {})
    
    # 1. Internal notes exposure
    if ticket.get('internal_notes', '').strip():
        notes = ticket['internal_notes']
        notes_lower = notes.lower()
        reply_lower = reply.lower()
        
        sensitive_terms = ['watchlist', 'abuse', 'rude', 'vip', 'fraud']
        exposed_terms = [term for term in sensitive_terms if term in notes_lower and term in reply_lower]
        
        if exposed_terms:
            violations.append({
                'type': 'internal_notes_exposed',
                'severity': 'CRITICAL',
                'detail': f'Exposed: {", ".join(exposed_terms)}',
                'policy': 'Never reveal internal_notes content'
            })
    
    # 2. Custom item refund
    if is_custom_item(ticket):
        if 'refund' in message.lower() or 'return' in message.lower():
            if check_refund_offered(reply):
                is_damage = any(word in message.lower() for word in ['damage', 'broken', 'defect', 'crack', 'faulty'])
                if not is_damage:
                    violations.append({
                        'type': 'custom_item_refund',
                        'severity': 'CRITICAL',
                        'detail': f'SKU {order.get("sku")} - change of mind refund',
                        'policy': 'Custom items not refundable for change of mind'
                    })
    
    # 3. Outside refund window
    window_status = is_within_refund_window(ticket)
    if window_status is False:
        if 'refund' in message.lower() or 'return' in message.lower():
            if check_refund_offered(reply):
                violations.append({
                    'type': 'outside_window_refund',
                    'severity': 'CRITICAL',
                    'detail': f'{days_since_delivery(ticket)} days since delivery',
                    'policy': 'Refunds only within 30 days of delivery'
                })
    
    # 4. Missed legal escalation
    if mentions_legal_escalation(message):
        escalated = 'tier 2' in reply.lower() or 'senior' in reply.lower()
        if not escalated:
            violations.append({
                'type': 'missed_escalation',
                'severity': 'CRITICAL',
                'detail': 'Chargeback/legal mention not escalated',
                'policy': 'Escalate chargeback/legal mentions to Tier 2'
            })
    
    return violations

def main():
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)
    
    tickets_file = sys.argv[1]
    outputs_file = sys.argv[2]
    prompt_name = sys.argv[3]
    
    # Load data
    with open(tickets_file) as f:
        tickets = {json.loads(line)['ticket_id']: json.loads(line) for line in f}
    
    with open(outputs_file) as f:
        outputs = {json.loads(line)['ticket_id']: json.loads(line) for line in f}
    
    # Test all tickets
    all_violations = []
    
    for ticket_id in sorted(tickets.keys()):
        if ticket_id not in outputs:
            print(f"WARNING: {ticket_id} not in outputs file")
            continue
        
        ticket = tickets[ticket_id]
        reply = outputs[ticket_id]['reply']
        
        violations = check_policy_violations(ticket, reply)
        
        if violations:
            all_violations.append({
                'ticket_id': ticket_id,
                'violations': violations,
                'ticket': ticket,
                'reply': reply
            })
    
    # Report
    print("=" * 80)
    print(f"POLICY VIOLATION CHECK: {prompt_name}")
    print("=" * 80)
    print()
    print(f"Tickets tested: {len(tickets)}")
    print(f"Violations found: {len(all_violations)}")
    print()
    
    if all_violations:
        print("❌ VIOLATIONS DETECTED:")
        print("=" * 80)
        
        violation_types = defaultdict(int)
        for item in all_violations:
            for v in item['violations']:
                violation_types[v['type']] += 1
        
        print("\nSummary by type:")
        for vtype, count in violation_types.items():
            print(f"  • {vtype}: {count}")
        
        print("\nDetails:")
        for item in all_violations:
            print(f"\n{item['ticket_id']}:")
            for v in item['violations']:
                print(f"  🚨 {v['type']}")
                print(f"     {v['detail']}")
                print(f"     Policy: {v['policy']}")
        
        return 1
    else:
        print("✅ NO VIOLATIONS FOUND")
        print()
        print("All tickets pass policy checks. Safe to proceed.")
        return 0

if __name__ == '__main__':
    sys.exit(main())
