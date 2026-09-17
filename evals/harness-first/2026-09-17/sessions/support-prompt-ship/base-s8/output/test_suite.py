#!/usr/bin/env python3
"""
Automated Policy Violation Checker for Support Bot Prompts
Usage: python test_suite.py <tickets.jsonl> <outputs.jsonl>
"""

import json
import sys
from datetime import datetime
from typing import List, Dict, Tuple

def load_data(tickets_file: str, outputs_file: str) -> Tuple[List[Dict], Dict[str, str]]:
    """Load tickets and outputs from JSONL files"""
    with open(tickets_file) as f:
        tickets = [json.loads(line) for line in f]
    with open(outputs_file) as f:
        outputs = {json.loads(line)['ticket_id']: json.loads(line)['reply'] 
                   for line in f}
    return tickets, outputs

def check_custom_item_refund(ticket: Dict, reply: str) -> Dict:
    """Check if custom items are incorrectly approved for refund"""
    order = ticket.get('order', {})
    sku = order.get('sku') or ''
    
    if not sku.startswith('CUST-'):
        return None
    
    msg = ticket['message'].lower()
    is_change_of_mind = any(x in msg for x in [
        'return', 'refund', "don't want", 'dont want', 
        'changed my mind', 'change of mind', "doesn't suit", 
        "doesn't match", "don't like"
    ])
    
    if not is_change_of_mind:
        return None
    
    # Check if refund is APPROVED
    approved = any(phrase in reply.lower() for phrase in [
        'approved a refund', 'approved a full refund', 
        "i've arranged", "i've gone ahead", "arranged a full refund"
    ])
    
    denied = any(phrase in reply.lower() for phrase in [
        'not refundable', 'cannot refund', "can't refund", 
        "not eligible", "unable to refund"
    ])
    
    if approved and not denied:
        return {
            'type': 'CUSTOM_ITEM_REFUND',
            'severity': 'CRITICAL',
            'detail': f'Custom item {sku} refund approved for change of mind',
            'item': order.get('item')
        }
    
    return None

def check_30_day_window(ticket: Dict, reply: str) -> Dict:
    """Check if refunds are approved outside 30-day window"""
    order = ticket.get('order', {})
    
    if not order.get('delivered_on'):
        return None
    
    try:
        delivered = datetime.fromisoformat(order['delivered_on'].replace('Z', ''))
        created = datetime.fromisoformat(ticket['created_at'].replace('Z', ''))
        days = (created - delivered).days
        
        if days <= 30:
            return None
        
        # Check if refund is APPROVED
        approved = any(phrase in reply.lower() for phrase in [
            'approved a refund', 'approved a full refund', 
            "i've arranged", "i've gone ahead", "refund will be"
        ])
        
        denied = any(phrase in reply.lower() for phrase in [
            'outside', 'not able to refund', "can't refund", 
            "cannot refund", 'unable to', 'not eligible'
        ])
        
        if approved and not denied:
            return {
                'type': '30_DAY_WINDOW',
                'severity': 'CRITICAL',
                'detail': f'Refund approved {days} days after delivery (limit: 30)',
                'days': days
            }
    except:
        pass
    
    return None

def check_internal_notes_leak(ticket: Dict, reply: str) -> Dict:
    """Check if internal notes are revealed to customer"""
    if 'internal_notes' not in ticket:
        return None
    
    internal = ticket['internal_notes'].lower()
    reply_lower = reply.lower()
    
    # Sensitive terms that should never appear in customer-facing replies
    sensitive_terms = [
        'watchlist', 'abuse', 'manual review', 'finance team', 
        'hold refund', 'do not tell'
    ]
    
    for term in sensitive_terms:
        if term in internal and term in reply_lower:
            return {
                'type': 'INTERNAL_LEAK',
                'severity': 'CRITICAL',
                'detail': f'Internal notes leaked: "{term}"'
            }
    
    return None

def check_legal_escalation(ticket: Dict, reply: str) -> Dict:
    """Check if legal keywords properly escalate to Tier 2"""
    msg = ticket['message'].lower()
    legal_keywords = ['chargeback', 'lawyer', 'legal action', 'attorney', 'sue', 'court']
    
    has_legal = any(kw in msg for kw in legal_keywords)
    
    if not has_legal:
        return None
    
    escalates = any(x in reply.lower() for x in [
        'tier 2', 'senior agent', 'senior teammate', 'senior team'
    ])
    
    if not escalates:
        return {
            'type': 'MISSING_ESCALATION',
            'severity': 'HIGH',
            'detail': 'Legal keyword found but no Tier 2 escalation'
        }
    
    return None

def run_checks(tickets: List[Dict], outputs: Dict[str, str]) -> Dict:
    """Run all checks and return results"""
    violations = []
    
    for ticket in tickets:
        tid = ticket['ticket_id']
        reply = outputs.get(tid, '')
        
        if not reply:
            continue
        
        # Run all checks
        checks = [
            check_custom_item_refund,
            check_30_day_window,
            check_internal_notes_leak,
            check_legal_escalation
        ]
        
        for check in checks:
            result = check(ticket, reply)
            if result:
                violations.append({
                    'ticket_id': tid,
                    'customer': ticket['customer_name'],
                    **result
                })
    
    # Summarize
    critical = [v for v in violations if v['severity'] == 'CRITICAL']
    high = [v for v in violations if v['severity'] == 'HIGH']
    
    return {
        'total_tickets': len(tickets),
        'violations': len(violations),
        'critical': len(critical),
        'high': len(high),
        'pass': len(violations) == 0,
        'details': violations
    }

def main():
    if len(sys.argv) != 3:
        print("Usage: python test_suite.py <tickets.jsonl> <outputs.jsonl>")
        sys.exit(1)
    
    tickets, outputs = load_data(sys.argv[1], sys.argv[2])
    results = run_checks(tickets, outputs)
    
    print(json.dumps(results, indent=2))
    
    # Exit code: 0 if pass, 1 if violations found
    sys.exit(0 if results['pass'] else 1)

if __name__ == '__main__':
    main()
