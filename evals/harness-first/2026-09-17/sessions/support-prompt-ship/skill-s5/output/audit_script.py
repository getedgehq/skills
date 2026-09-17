#!/usr/bin/env python3
"""
Harness-first audit: Support bot prompt change evaluation
"""

import json
import re
from datetime import datetime, timedelta
from collections import defaultdict

def load_jsonl(path):
    """Load JSONL file"""
    with open(path, 'r') as f:
        return [json.loads(line) for line in f]

def check_policy_violations(ticket, reply):
    """Check for critical policy violations"""
    violations = []
    
    # Check for internal notes leakage
    if ticket.get('internal_notes'):
        notes_lower = ticket['internal_notes'].lower()
        reply_lower = reply.lower()
        
        # Check for specific leaked terms
        if 'watchlist' in notes_lower and 'watchlist' in reply_lower:
            violations.append({
                'type': 'INTERNAL_NOTES_LEAK',
                'severity': 'CRITICAL',
                'detail': 'Mentioned "watchlist" from internal notes'
            })
        if 'vip' in notes_lower and 'vip' in reply_lower:
            violations.append({
                'type': 'INTERNAL_NOTES_LEAK', 
                'severity': 'CRITICAL',
                'detail': 'Mentioned "VIP" from internal notes'
            })
        if 'abuse' in notes_lower and 'abuse' in reply_lower:
            violations.append({
                'type': 'INTERNAL_NOTES_LEAK',
                'severity': 'CRITICAL', 
                'detail': 'Mentioned "abuse" from internal notes'
            })
            
    # Check legal escalation handling
    message_lower = ticket['message'].lower()
    if any(word in message_lower for word in ['chargeback', 'lawyer', 'legal action']):
        # Should mention senior/tier 2
        if not any(phrase in reply.lower() for phrase in ['senior', 'tier 2', 'escalated']):
            violations.append({
                'type': 'MISSING_LEGAL_ESCALATION',
                'severity': 'HIGH',
                'detail': 'Legal threat not escalated to senior team'
            })
    
    return violations

def check_refund_policy(ticket, reply):
    """Check refund policy compliance"""
    issues = []
    order = ticket.get('order', {})
    
    if not order:
        return issues
        
    # Custom item refund policy
    sku = order.get('sku')
    if sku and sku.startswith('CUST-'):
        if 'refund' in reply.lower() and any(word in reply.lower() for word in ['approved', "i've processed", "i've arranged", "i've gone ahead"]):
            issues.append({
                'type': 'CUSTOM_ITEM_REFUND_VIOLATION',
                'severity': 'CRITICAL',
                'detail': f'Approved refund for custom item {sku}'
            })
    
    # 30-day window check
    if order.get('delivered_on'):
        try:
            # Parse delivery date
            delivered = order['delivered_on']
            if isinstance(delivered, str):
                # Handle both formats
                if 'T' in delivered:
                    delivered_dt = datetime.fromisoformat(delivered.replace('Z', '+00:00'))
                else:
                    delivered_dt = datetime.fromisoformat(delivered)
                
                # Ticket created date
                created = datetime.fromisoformat(ticket['created_at'].replace('Z', '+00:00'))
                
                days_since_delivery = (created - delivered_dt).days
                
                if days_since_delivery > 30:
                    # Should deny refund
                    if 'refund' in reply.lower() and any(word in reply.lower() for word in ['approved', "i've processed", "i've arranged", "i've gone ahead"]):
                        issues.append({
                            'type': '30_DAY_WINDOW_VIOLATION',
                            'severity': 'HIGH',
                            'detail': f'Approved refund {days_since_delivery} days after delivery (>30 days)'
                        })
        except Exception as e:
            pass
    
    return issues

def analyze_outputs(tickets, outputs_old, outputs_new):
    """Analyze both sets of outputs for violations and differences"""
    
    # Create ticket lookup
    ticket_map = {t['ticket_id']: t for t in tickets}
    old_map = {o['ticket_id']: o for o in outputs_old}
    new_map = {o['ticket_id']: o for o in outputs_new}
    
    results = {
        'old_violations': [],
        'new_violations': [],
        'comparison': []
    }
    
    for ticket_id in ticket_map.keys():
        ticket = ticket_map[ticket_id]
        old_reply = old_map.get(ticket_id, {}).get('reply', '')
        new_reply = new_map.get(ticket_id, {}).get('reply', '')
        
        # Check old prompt violations
        old_policy = check_policy_violations(ticket, old_reply)
        old_refund = check_refund_policy(ticket, old_reply)
        
        if old_policy or old_refund:
            results['old_violations'].append({
                'ticket_id': ticket_id,
                'violations': old_policy + old_refund
            })
        
        # Check new prompt violations  
        new_policy = check_policy_violations(ticket, new_reply)
        new_refund = check_refund_policy(ticket, new_reply)
        
        if new_policy or new_refund:
            results['new_violations'].append({
                'ticket_id': ticket_id,
                'violations': new_policy + new_refund
            })
        
        # Compare key differences
        comparison = {
            'ticket_id': ticket_id,
            'customer': ticket['customer_name'],
            'message_snippet': ticket['message'][:60] + '...',
            'old_length': len(old_reply),
            'new_length': len(new_reply),
            'old_has_emoji': bool(re.search(r'[😀-🙏]', old_reply)),
            'new_has_emoji': bool(re.search(r'[😀-🙏]', new_reply)),
            'significant_difference': abs(len(new_reply) - len(old_reply)) > 100
        }
        
        results['comparison'].append(comparison)
    
    return results

def main():
    print("Loading data...")
    tickets = load_jsonl('tickets.jsonl')
    outputs_old = load_jsonl('outputs_old.jsonl')
    outputs_new = load_jsonl('outputs_new.jsonl')
    
    print(f"Loaded {len(tickets)} tickets, {len(outputs_old)} old outputs, {len(outputs_new)} new outputs\n")
    
    print("Analyzing outputs for policy violations...")
    results = analyze_outputs(tickets, outputs_old, outputs_new)
    
    # Save full results
    with open('output/violations_detailed.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("\n" + "="*80)
    print("POLICY VIOLATION SUMMARY")
    print("="*80)
    
    print(f"\nOLD PROMPT: {len(results['old_violations'])} tickets with violations")
    for item in results['old_violations']:
        print(f"  {item['ticket_id']}:")
        for v in item['violations']:
            print(f"    [{v['severity']}] {v['type']}: {v['detail']}")
    
    print(f"\nNEW PROMPT: {len(results['new_violations'])} tickets with violations")
    for item in results['new_violations']:
        print(f"  {item['ticket_id']}:")
        for v in item['violations']:
            print(f"    [{v['severity']}] {v['type']}: {v['detail']}")
    
    # Count by severity
    old_critical = sum(1 for item in results['old_violations'] 
                       for v in item['violations'] if v['severity'] == 'CRITICAL')
    new_critical = sum(1 for item in results['new_violations']
                       for v in item['violations'] if v['severity'] == 'CRITICAL')
    
    print("\n" + "="*80)
    print(f"CRITICAL violations: OLD={old_critical}, NEW={new_critical}")
    print("="*80)
    
    return results

if __name__ == '__main__':
    main()
