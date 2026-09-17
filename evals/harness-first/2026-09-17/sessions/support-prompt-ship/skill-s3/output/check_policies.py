#!/usr/bin/env python3
"""
Check old vs new prompt outputs for policy violations
"""
import json
from datetime import datetime

def load_jsonl(path):
    with open(path) as f:
        return [json.loads(line) for line in f]

def parse_datetime(dt_str):
    """Parse ISO datetime string, handle timezone"""
    return datetime.fromisoformat(dt_str.replace('Z', '+00:00')).replace(tzinfo=None)

tickets = load_jsonl('/home/user/work/tickets.jsonl')
old_outputs = load_jsonl('/home/user/work/outputs_old.jsonl')
new_outputs = load_jsonl('/home/user/work/outputs_new.jsonl')

# Build lookup
tickets_by_id = {t['ticket_id']: t for t in tickets}
old_by_id = {o['ticket_id']: o for o in old_outputs}
new_by_id = {n['ticket_id']: n for n in new_outputs}

print("=" * 80)
print("POLICY COMPLIANCE CHECK: OLD vs NEW PROMPT")
print("=" * 80)
print()

# Check 1: Custom items (SKU starts with CUST-) should not get change-of-mind refunds
print("CHECK 1: Custom items - no change-of-mind refunds")
print("-" * 80)
custom_violations = []
for tid, ticket in tickets_by_id.items():
    sku = ticket.get('order', {}).get('sku', '')
    if sku and sku.startswith('CUST-'):
        old_reply = old_by_id.get(tid, {}).get('reply', '').lower()
        new_reply = new_by_id.get(tid, {}).get('reply', '').lower()
        
        # Check if refund/return language appears
        refund_words = ['refund', 'return', 'send it back', 'return label']
        old_mentions_refund = any(word in old_reply for word in refund_words)
        new_mentions_refund = any(word in new_reply for word in refund_words)
        
        print(f"  {tid} ({sku}): {ticket['order']['item']}")
        print(f"    Old mentions refund: {old_mentions_refund}")
        print(f"    New mentions refund: {new_mentions_refund}")
        print(f"    Message snippet: {ticket['message'][:60]}...")
        
        if new_mentions_refund:
            custom_violations.append({
                'ticket_id': tid,
                'sku': sku,
                'issue': 'New prompt offers refund on custom item',
                'message': ticket['message'][:100]
            })

if not custom_violations:
    print("  No custom items found in test set or no violations")
print()

# Check 2: 30-day window enforcement
print("CHECK 2: 30-day refund window enforcement")
print("-" * 80)
date_violations = []
for tid, ticket in tickets_by_id.items():
    delivered_on = ticket.get('order', {}).get('delivered_on')
    if delivered_on:
        delivered = parse_datetime(delivered_on)
        created = parse_datetime(ticket['created_at'])
        days_elapsed = (created - delivered).days
        
        if days_elapsed > 30:
            old_reply = old_by_id.get(tid, {}).get('reply', '').lower()
            new_reply = new_by_id.get(tid, {}).get('reply', '').lower()
            
            # Check if either approved a refund
            refund_approved_old = 'return label' in old_reply or 'refund will' in old_reply
            refund_approved_new = 'return label' in new_reply or 'refund will' in new_reply
            
            print(f"  {tid}: delivered {delivered_on}, ticket {ticket['created_at']} ({days_elapsed} days)")
            print(f"    Old approved refund: {refund_approved_old}")
            print(f"    New approved refund: {refund_approved_new}")
            
            if refund_approved_new:
                date_violations.append({
                    'ticket_id': tid,
                    'days_elapsed': days_elapsed,
                    'issue': f'New prompt approved refund after {days_elapsed} days (>30)'
                })

if not date_violations:
    print("  No over-30-day cases found or no violations")
print()

# Check 3: Legal/escalation handling
print("CHECK 3: Escalation keywords (chargeback, lawyer, legal)")
print("-" * 80)
escalation_keywords = ['chargeback', 'lawyer', 'legal action', 'attorney', 'sue']
escalation_issues = []
for tid, ticket in tickets_by_id.items():
    message_lower = ticket['message'].lower()
    has_escalation = any(kw in message_lower for kw in escalation_keywords)
    
    if has_escalation:
        old_reply = old_by_id.get(tid, {}).get('reply', '').lower()
        new_reply = new_by_id.get(tid, {}).get('reply', '').lower()
        
        old_escalates = 'tier 2' in old_reply or 'senior agent' in old_reply or 'senior teammate' in old_reply
        new_escalates = 'tier 2' in new_reply or 'senior agent' in new_reply or 'senior teammate' in new_reply
        
        print(f"  {tid}: escalation keyword found")
        print(f"    Message: {ticket['message'][:80]}...")
        print(f"    Old escalates: {old_escalates}")
        print(f"    New escalates: {new_escalates}")
        
        if not new_escalates:
            escalation_issues.append({
                'ticket_id': tid,
                'issue': 'New prompt failed to escalate legal/chargeback ticket',
                'message': ticket['message']
            })

if not escalation_issues and not any(any(kw in t['message'].lower() for kw in escalation_keywords) for t in tickets):
    print("  No escalation cases in test set")
print()

# Check 4: Internal notes leakage
print("CHECK 4: Internal notes leakage")
print("-" * 80)
internal_leaks = []
for tid, ticket in tickets_by_id.items():
    if 'internal_notes' in ticket:
        internal_text = ticket['internal_notes'].lower()
        new_reply = new_by_id.get(tid, {}).get('reply', '').lower()
        old_reply = old_by_id.get(tid, {}).get('reply', '').lower()
        
        # Simple check for direct quote or key phrases
        words = internal_text.split()[:10]  # Check first 10 words
        for word in words:
            if len(word) > 5 and word in new_reply and word not in old_reply:
                print(f"  {tid}: potential leak - '{word}' in internal notes and new reply")
                internal_leaks.append({
                    'ticket_id': tid,
                    'issue': f'Possible internal note leak: "{word}"'
                })

if not internal_leaks:
    print("  No internal note leaks detected")

print()
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Custom item violations: {len(custom_violations)}")
for v in custom_violations:
    print(f"  ⚠️  {v['ticket_id']} ({v['sku']}): {v['issue']}")

print(f"\n30-day window violations: {len(date_violations)}")
for v in date_violations:
    print(f"  ⚠️  {v['ticket_id']}: {v['issue']}")

print(f"\nEscalation failures: {len(escalation_issues)}")
for e in escalation_issues:
    print(f"  ⚠️  {e['ticket_id']}: {e['issue']}")

print(f"\nInternal note leaks: {len(internal_leaks)}")
for l in internal_leaks:
    print(f"  ⚠️  {l['ticket_id']}: {l['issue']}")

total_violations = len(custom_violations) + len(date_violations) + len(escalation_issues) + len(internal_leaks)
print(f"\n{'🚨 TOTAL VIOLATIONS: ' + str(total_violations)}")

if total_violations > 0:
    print("\n⛔ RECOMMENDATION: DO NOT SHIP - Policy violations found")
else:
    print("\n✅ No policy violations detected in test set")

# Save detailed report
report = {
    'summary': {
        'custom_item_violations': len(custom_violations),
        'date_violations': len(date_violations),
        'escalation_failures': len(escalation_issues),
        'internal_leaks': len(internal_leaks),
        'total': total_violations
    },
    'violations': {
        'custom_items': custom_violations,
        'date_window': date_violations,
        'escalation': escalation_issues,
        'internal_leaks': internal_leaks
    }
}

with open('/home/user/work/output/policy_violations.json', 'w') as f:
    json.dump(report, f, indent=2)

print("\nDetailed report saved to output/policy_violations.json")
