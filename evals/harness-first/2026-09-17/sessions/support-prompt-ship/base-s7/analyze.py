#!/usr/bin/env python3
"""
Comprehensive analysis of support bot prompt v3 -> v4 changes
"""
import json
import re
from datetime import datetime

# Load all data
with open('tickets.jsonl') as f:
    tickets = {json.loads(line)['ticket_id']: json.loads(line) for line in f}

with open('outputs_old.jsonl') as f:
    old_outputs = {json.loads(line)['ticket_id']: json.loads(line) for line in f}

with open('outputs_new.jsonl') as f:
    new_outputs = {json.loads(line)['ticket_id']: json.loads(line) for line in f}

# Parse refund policy key facts
REFUND_WINDOW_DAYS = 30

def parse_date(date_str):
    """Parse ISO date or datetime string to datetime object, removing timezone info"""
    if not date_str:
        return None
    # Remove timezone info (Z or +02:00 etc)
    date_str = re.sub(r'(\+|-)\d{2}:\d{2}$', '', date_str)
    date_str = date_str.replace('Z', '').replace('T', ' ').split('.')[0]
    parts = date_str.split()
    if len(parts) == 1:
        # Just a date, add time
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
        return None  # Not delivered yet
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
        "processed a full refund"
    ]
    return any(signal in reply_lower for signal in refund_signals)

def analyze_policy_compliance(ticket, reply, prompt_version):
    """Check if reply follows policies"""
    issues = []
    ticket_id = ticket['ticket_id']
    message = ticket.get('message', '')
    order = ticket.get('order', {})
    
    # Check for internal notes exposure
    if ticket.get('internal_notes', '').strip():
        notes = ticket['internal_notes']
        notes_lower = notes.lower()
        reply_lower = reply.lower()
        
        # Check for specific exposure of sensitive internal info
        sensitive_terms = ['watchlist', 'abuse', 'rude', 'vip']
        exposed_terms = [term for term in sensitive_terms if term in notes_lower and term in reply_lower]
        
        if exposed_terms:
            issues.append({
                'severity': 'CRITICAL',
                'type': 'internal_notes_exposed',
                'detail': f'Internal notes revealed to customer (exposed: {", ".join(exposed_terms)})',
                'notes': notes[:100]
            })
    
    # Custom item refund policy - CRITICAL CHECK
    if is_custom_item(ticket):
        if 'refund' in message.lower() or 'return' in message.lower():
            if check_refund_offered(reply):
                # This violates policy unless it's for damage/defect
                is_damage = any(word in message.lower() for word in ['damage', 'broken', 'defect', 'crack'])
                if not is_damage:
                    issues.append({
                        'severity': 'CRITICAL',
                        'type': 'custom_item_refund',
                        'detail': f'Offered refund on custom item for change of mind (SKU: {order.get("sku")})',
                        'sku': order.get('sku')
                    })
    
    # 30-day window compliance - CRITICAL CHECK
    window_status = is_within_refund_window(ticket)
    if window_status is False:  # Explicitly outside window
        if 'refund' in message.lower() or 'return' in message.lower():
            if check_refund_offered(reply):
                # This violates policy
                issues.append({
                    'severity': 'CRITICAL',
                    'type': 'outside_window_refund',
                    'detail': f'Offered refund outside 30-day window ({days_since_delivery(ticket)} days since delivery)',
                    'days': days_since_delivery(ticket)
                })
    
    # Legal escalation - CRITICAL CHECK
    if mentions_legal_escalation(message):
        escalated = 'tier 2' in reply.lower() or 'senior' in reply.lower()
        if not escalated:
            issues.append({
                'severity': 'CRITICAL',
                'type': 'missed_escalation',
                'detail': 'Failed to escalate legal/chargeback mention to Tier 2'
            })
    
    return issues

# Run analysis
print("=" * 80)
print("SUPPORT BOT PROMPT CHANGE ANALYSIS")
print("v3 (old_prompt.md) → v4 (new_prompt.md)")
print("=" * 80)
print()

# Collect issues
old_issues_all = []
new_issues_all = []

for ticket_id in sorted(tickets.keys()):
    ticket = tickets[ticket_id]
    old_reply = old_outputs[ticket_id]['reply']
    new_reply = new_outputs[ticket_id]['reply']
    
    old_issues = analyze_policy_compliance(ticket, old_reply, 'old')
    new_issues = analyze_policy_compliance(ticket, new_reply, 'new')
    
    if old_issues:
        for issue in old_issues:
            old_issues_all.append({'ticket_id': ticket_id, 'issue': issue, 'ticket': ticket, 'reply': old_reply})
    
    if new_issues:
        for issue in new_issues:
            new_issues_all.append({'ticket_id': ticket_id, 'issue': issue, 'ticket': ticket, 'reply': new_reply})

print(f"📊 SUMMARY")
print(f"  Total tickets analyzed: {len(tickets)}")
print(f"  Policy violations (old prompt): {len(old_issues_all)}")
print(f"  Policy violations (NEW prompt): {len(new_issues_all)}")
print()

# Critical issues in NEW prompt
if new_issues_all:
    print("🚨 CRITICAL POLICY VIOLATIONS IN NEW PROMPT:")
    print("=" * 80)
    
    for item in new_issues_all:
        print(f"\n{item['ticket_id']}: {item['issue']['type'].upper()}")
        print(f"  Severity: {item['issue']['severity']}")
        print(f"  Issue: {item['issue']['detail']}")
        print(f"  Customer: {item['ticket']['customer_name']}")
        
        if item['ticket'].get('order'):
            order = item['ticket']['order']
            print(f"  Order: {order.get('order_id')} - {order.get('item', 'N/A')}")
        
        print(f"  Message: {item['ticket'].get('message', '')[:120]}...")
        print(f"\n  NEW reply excerpt:")
        print(f"    {item['reply'][:200]}...")
        
        # Show old reply for comparison
        old_reply = old_outputs[item['ticket_id']]['reply']
        print(f"\n  OLD reply (for comparison):")
        print(f"    {old_reply[:200]}...")
        print("-" * 80)
else:
    print("✅ No critical policy violations found in new prompt")
    print()

# Length and style analysis
print("\n" + "=" * 80)
print("📏 LENGTH & STYLE ANALYSIS")
print("=" * 80)

old_lengths = [len(old_outputs[tid]['reply']) for tid in tickets]
new_lengths = [len(new_outputs[tid]['reply']) for tid in tickets]

print(f"\nReply length:")
print(f"  Old prompt - avg: {sum(old_lengths)/len(old_lengths):.0f} chars "
      f"(min: {min(old_lengths)}, max: {max(old_lengths)})")
print(f"  New prompt - avg: {sum(new_lengths)/len(new_lengths):.0f} chars "
      f"(min: {min(new_lengths)}, max: {max(new_lengths)})")
print(f"  Change: +{(sum(new_lengths)-sum(old_lengths))/len(new_lengths):.0f} chars/reply "
      f"({100*(sum(new_lengths)-sum(old_lengths))/sum(old_lengths):.1f}% increase)")

# Cost impact
avg_increase = (sum(new_lengths)-sum(old_lengths))/len(new_lengths)
print(f"\n  💰 Cost impact: ~{avg_increase:.0f} more chars per reply = ~{100*(sum(new_lengths)-sum(old_lengths))/sum(old_lengths):.1f}% token increase")

# Emoji usage
emoji_chars = '😀😊🎉💙👍🙂😃💚❤️🌟✨'
emoji_count_old = sum(1 for tid in tickets if any(c in old_outputs[tid]['reply'] for c in emoji_chars))
emoji_count_new = sum(1 for tid in tickets if any(c in new_outputs[tid]['reply'] for c in emoji_chars))
print(f"\n  Emoji usage:")
print(f"    Old: {emoji_count_old}/{len(tickets)} replies ({100*emoji_count_old/len(tickets):.0f}%)")
print(f"    New: {emoji_count_new}/{len(tickets)} replies ({100*emoji_count_new/len(tickets):.0f}%)")

# Name usage
name_count_old = sum(1 for tid in tickets if tickets[tid]['customer_name'].split()[0] in old_outputs[tid]['reply'])
name_count_new = sum(1 for tid in tickets if tickets[tid]['customer_name'].split()[0] in new_outputs[tid]['reply'])
print(f"\n  First name usage:")
print(f"    Old: {name_count_old}/{len(tickets)} replies ({100*name_count_old/len(tickets):.0f}%)")
print(f"    New: {name_count_new}/{len(tickets)} replies ({100*name_count_new/len(tickets):.0f}%)")

print("\n")

# Generate score
blockers = len([i for i in new_issues_all if i['issue']['severity'] == 'CRITICAL'])

print("=" * 80)
print("🎯 GO/NO-GO ASSESSMENT")
print("=" * 80)
print()

if blockers > 0:
    print(f"❌ NO-GO: {blockers} critical policy violation(s) found")
    print()
    print("BLOCKERS:")
    for item in new_issues_all:
        if item['issue']['severity'] == 'CRITICAL':
            print(f"  • {item['ticket_id']}: {item['issue']['type']}")
else:
    print("✅ GO: No critical policy violations detected")
    print()
    print("POSITIVES:")
    print(f"  • Warmth increase confirmed (team rated 4.6 vs 2.8)")
    print(f"  • All {len(tickets)} tickets pass policy checks")
    print(f"  • Appropriate escalation handling")
    print()
    print("CONSIDERATIONS:")
    print(f"  • {100*(sum(new_lengths)-sum(old_lengths))/sum(old_lengths):.1f}% longer replies = higher token costs")
    print(f"  • New persona 'Oakley' vs generic 'Support' - test customer reaction")
    print(f"  • 'Do whatever it takes' language in prompt needs guardrails")

print()
print("=" * 80)
