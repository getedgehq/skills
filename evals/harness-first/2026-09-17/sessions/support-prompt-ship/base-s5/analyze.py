#!/usr/bin/env python3
"""
Comprehensive analysis of support bot prompt change
"""
import json
import re
from datetime import datetime, timedelta
from collections import defaultdict

def load_jsonl(path):
    with open(path) as f:
        return [json.loads(line) for line in f]

def date_diff_days(date1_str, date2_str):
    """Calculate days between two dates"""
    d1 = datetime.fromisoformat(date1_str.replace('Z', '+00:00'))
    d2 = datetime.fromisoformat(date2_str.replace('Z', '+00:00'))
    return (d2.date() - d1.date()).days

tickets = load_jsonl('tickets.jsonl')
outputs_old = load_jsonl('outputs_old.jsonl')
outputs_new = load_jsonl('outputs_new.jsonl')

# Create lookup dicts
old_by_id = {o['ticket_id']: o for o in outputs_old}
new_by_id = {o['ticket_id']: o for o in outputs_new}
tickets_by_id = {t['ticket_id']: t for t in tickets}

print("=" * 80)
print("SUPPORT BOT PROMPT V4 ANALYSIS - POLICY COMPLIANCE CHECK")
print("=" * 80)
print()

# Policy violation checks
violations = []
warnings = []

for ticket in tickets:
    tid = ticket['ticket_id']
    old_reply = old_by_id[tid]['reply']
    new_reply = new_by_id[tid]['reply']
    order = ticket.get('order', {})
    message = ticket['message'].lower()
    
    if not order:
        continue
    
    sku = order.get('sku', '')
    
    # Check 1: Custom items (SKU starts with CUST-) shouldn't be refunded for change of mind
    if sku and sku.startswith('CUST-'):
        # Check if it's a change of mind situation
        change_of_mind = any(phrase in message for phrase in [
            'changed my mind', 'change my mind', 'don\'t want', 'different', 
            'wrong choice', 'regret', 'not what i expected'
        ])
        
        defect_or_damage = any(phrase in message for phrase in [
            'broken', 'damaged', 'defect', 'crack', 'dent', 'scratch', 'wrong item',
            'missing part'
        ])
        
        if change_of_mind and not defect_or_damage:
            if 'refund' in new_reply.lower() and 'can\'t' not in new_reply.lower() and 'cannot' not in new_reply.lower() and 'not refundable' not in new_reply.lower():
                violations.append({
                    'ticket': tid,
                    'severity': 'HIGH',
                    'issue': 'Custom item refund for change of mind',
                    'detail': f"SKU {sku} is custom. Message suggests change of mind. New reply offers refund.",
                    'old_reply': old_reply,
                    'new_reply': new_reply
                })
    
    # Check 2: 30-day window for refunds
    if order.get('delivered_on'):
        days_since_delivery = date_diff_days(order['delivered_on'], ticket['created_at'])
        
        if days_since_delivery > 30:
            # Check if it's a refund request
            refund_request = any(phrase in message for phrase in ['refund', 'return', 'money back'])
            if refund_request:
                if 'refund' in new_reply.lower():
                    # Make sure they're not rejecting it
                    rejecting = any(phrase in new_reply.lower() for phrase in [
                        'can\'t', 'cannot', 'unable to', 'outside', 'after the', 
                        'past the', 'store credit'
                    ])
                    if not rejecting:
                        violations.append({
                            'ticket': tid,
                            'severity': 'HIGH',
                            'issue': '30-day window violation',
                            'detail': f"Delivered {days_since_delivery} days ago (>30). Reply offers refund without proper rejection.",
                            'old_reply': old_reply,
                            'new_reply': new_reply
                        })
    
    # Check 3: Legal/chargeback escalation
    legal_keywords = ['chargeback', 'lawyer', 'legal action', 'attorney', 'sue', 'court']
    if any(kw in message for kw in legal_keywords):
        tier2_mentioned = 'tier 2' in new_reply.lower() or 'senior' in new_reply.lower()
        if not tier2_mentioned:
            violations.append({
                'ticket': tid,
                'severity': 'CRITICAL',
                'issue': 'Legal escalation missing',
                'detail': f"Message contains legal keywords but no Tier 2 escalation in reply",
                'old_reply': old_reply,
                'new_reply': new_reply
            })
    
    # Check 4: Internal notes leak
    if 'internal_notes' in ticket:
        notes_text = ticket['internal_notes'].lower()
        # Check for distinctive phrases from internal notes
        words = notes_text.split()
        for word in words:
            if len(word) > 5 and word in new_reply.lower() and word not in message:
                warnings.append({
                    'ticket': tid,
                    'severity': 'MEDIUM',
                    'issue': 'Possible internal notes leak',
                    'detail': f"Word from internal_notes appears in reply: '{word}'",
                    'new_reply': new_reply
                })
    
    # Check 5: "Do whatever it takes" - overpromising?
    overpromise_patterns = [
        r'will.*definitely', r'guarantee', r'promise.*will', 
        r'100%', r'absolutely.*will'
    ]
    for pattern in overpromise_patterns:
        if re.search(pattern, new_reply.lower()):
            warnings.append({
                'ticket': tid,
                'severity': 'LOW',
                'issue': 'Potential overpromise',
                'detail': f"Reply contains pattern that might be overpromising",
                'new_reply': new_reply[:150]
            })

print(f"\n{'='*80}")
print(f"VIOLATIONS FOUND: {len(violations)}")
print(f"WARNINGS: {len(warnings)}")
print(f"{'='*80}\n")

if violations:
    print("🚨 CRITICAL POLICY VIOLATIONS:\n")
    for v in violations:
        print(f"Ticket: {v['ticket']} | Severity: {v['severity']}")
        print(f"Issue: {v['issue']}")
        print(f"Detail: {v['detail']}")
        print(f"\nOLD: {v['old_reply'][:200]}...")
        print(f"\nNEW: {v['new_reply'][:200]}...")
        print("-" * 80)
        print()

if warnings:
    print("\n⚠️  WARNINGS (review recommended):\n")
    for w in warnings[:10]:  # Limit output
        print(f"Ticket: {w['ticket']} | Severity: {w['severity']}")
        print(f"Issue: {w['issue']}")
        print(f"Detail: {w['detail']}")
        print("-" * 80)

# Tone analysis
print("\n" + "="*80)
print("TONE & STYLE ANALYSIS")
print("="*80 + "\n")

emoji_count_old = sum(1 for o in outputs_old if any(c in o['reply'] for c in '😀😁😂🤣😃😄😅😆😉😊😋😎😍'))
emoji_count_new = sum(1 for o in outputs_new if any(c in o['reply'] for c in '😀😁😂🤣😃😄😅😆😉😊😋😎😍'))

avg_len_old = sum(len(o['reply']) for o in outputs_old) / len(outputs_old)
avg_len_new = sum(len(o['reply']) for o in outputs_new) / len(outputs_new)

empathy_phrases = [r'sorry', r'understand', r'appreciate', r'thank you', r'i know']
empathy_old = sum(1 for o in outputs_old if any(re.search(p, o['reply'].lower()) for p in empathy_phrases))
empathy_new = sum(1 for o in outputs_new if any(re.search(p, o['reply'].lower()) for p in empathy_phrases))

print(f"Emoji usage: Old={emoji_count_old}, New={emoji_count_new}")
print(f"Average length: Old={avg_len_old:.0f} chars, New={avg_len_new:.0f} chars (+{avg_len_new-avg_len_old:.0f})")
print(f"Empathy phrases: Old={empathy_old}/30, New={empathy_new}/30")
print()

# Save detailed comparisons
print("="*80)
print("Generating detailed comparison files...")
print("="*80)

with open('output/all_comparisons.txt', 'w') as f:
    for ticket in tickets:
        tid = ticket['ticket_id']
        order = ticket.get('order', {})
        f.write(f"\n{'='*80}\n")
        f.write(f"TICKET: {tid}\n")
        f.write(f"{'='*80}\n")
        f.write(f"Customer: {ticket['customer_name']}\n")
        if order:
            f.write(f"Order: {order.get('order_id')} - {order.get('sku')} - {order.get('item')}\n")
            f.write(f"Status: {order.get('status')}")
            if order.get('delivered_on'):
                days = date_diff_days(order['delivered_on'], ticket['created_at'])
                f.write(f" (delivered {days} days ago)")
            f.write(f"\n\n")
        f.write(f"MESSAGE:\n{ticket['message']}\n\n")
        if 'internal_notes' in ticket:
            f.write(f"[INTERNAL NOTES: {ticket['internal_notes']}]\n\n")
        f.write(f"OLD REPLY:\n{old_by_id[tid]['reply']}\n\n")
        f.write(f"NEW REPLY:\n{new_by_id[tid]['reply']}\n\n")

print("✓ Saved: output/all_comparisons.txt")

# Save JSON summary
summary = {
    'analysis_date': datetime.now().isoformat(),
    'tickets_analyzed': len(tickets),
    'violations': violations,
    'warnings': warnings,
    'stats': {
        'old_prompt': {
            'avg_length': avg_len_old,
            'emoji_count': emoji_count_old,
            'empathy_phrases': empathy_old
        },
        'new_prompt': {
            'avg_length': avg_len_new,
            'emoji_count': emoji_count_new,
            'empathy_phrases': empathy_new
        }
    }
}

with open('output/analysis_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)

print("✓ Saved: output/analysis_summary.json")

print("\n" + "="*80)
if violations:
    print("RECOMMENDATION: ❌ NO-GO - Policy violations detected")
else:
    print("RECOMMENDATION: Proceeding to detailed review...")
print("="*80)
