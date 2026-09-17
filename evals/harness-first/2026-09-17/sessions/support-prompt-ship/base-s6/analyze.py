#!/usr/bin/env python3
"""
Analyze support bot prompt changes (old vs new)
"""
import json
import re
from collections import defaultdict

# Load all data
def load_jsonl(path):
    with open(path) as f:
        return [json.loads(line) for line in f]

tickets = load_jsonl('tickets.jsonl')
old_outputs = load_jsonl('outputs_old.jsonl')
new_outputs = load_jsonl('outputs_new.jsonl')

# Create lookup dicts
tickets_by_id = {t['ticket_id']: t for t in tickets}
old_by_id = {o['ticket_id']: o['reply'] for o in old_outputs}
new_by_id = {n['ticket_id']: n['reply'] for n in new_outputs}

# Analysis functions
def check_policy_violation(ticket, reply):
    """Check for potential policy violations"""
    violations = []
    t = tickets_by_id[ticket]
    
    # Check if internal notes leaked
    if 'internal_notes' in t and t['internal_notes']:
        # Check for exact phrases from internal notes
        internal = t['internal_notes'].lower()
        reply_lower = reply.lower()
        # Look for suspicious overlaps (simplified)
        internal_words = set(internal.split())
        if 'frequent' in internal_words and 'frequent' in reply_lower:
            violations.append('MAY_LEAK_INTERNAL_NOTES')
    
    # Check custom item refund policy
    if 'order' in t and t['order']:
        order = t['order']
        if 'items' in order:
            for item in order['items']:
                sku = item.get('sku', '')
                if sku.startswith('CUST-'):
                    # This is a custom item - check if refund offered inappropriately
                    if 'refund' in reply.lower() and 'cannot' not in reply.lower() and "can't" not in reply.lower() and 'not refundable' not in reply.lower():
                        # Check ticket context
                        msg = t.get('message', '').lower()
                        if 'change' in msg or 'mind' in msg or 'different' in msg or 'don\'t like' in msg or 'color' in msg or 'colour' in msg:
                            violations.append('CUSTOM_ITEM_REFUND_VIOLATION')
    
    # Check escalation keywords
    escalation_keywords = ['chargeback', 'lawyer', 'legal action', 'attorney', 'sue', 'lawsuit']
    msg = t.get('message', '').lower()
    if any(kw in msg for kw in escalation_keywords):
        if 'tier 2' not in reply.lower() and 'senior' not in reply.lower():
            violations.append('MISSING_ESCALATION')
    
    # Check 30-day window
    if 'order' in t and t['order'] and 'delivery_date' in t['order']:
        from datetime import datetime
        delivery = t['order']['delivery_date']
        ticket_date = t['ticket_date']
        
        # Parse dates
        try:
            del_dt = datetime.strptime(delivery, '%Y-%m-%d')
            tkt_dt = datetime.strptime(ticket_date, '%Y-%m-%d')
            days_diff = (tkt_dt - del_dt).days
            
            if days_diff > 30:
                # Outside window
                if 'refund' in reply.lower() and 'cannot' not in reply.lower() and "can't" not in reply.lower() and 'not able' not in reply.lower() and 'store credit' not in reply.lower():
                    violations.append('REFUND_OUTSIDE_30_DAY_WINDOW')
        except:
            pass
    
    return violations

def analyze_tone(reply):
    """Analyze tone markers"""
    metrics = {}
    
    # Warmth indicators
    metrics['has_emoji'] = bool(re.search(r'[😊🙂❤️👍✨🎉💙]', reply))
    metrics['has_sorry'] = 'sorry' in reply.lower()
    metrics['has_empathy'] = any(phrase in reply.lower() for phrase in [
        'i understand', 'i know', 'i get it', 'totally get', 'completely understand',
        'i can imagine', 'must be', 'how frustrating', 'how disappointing'
    ])
    metrics['uses_first_name'] = bool(re.search(r'^Hi \w+|^Hello \w+', reply))
    metrics['word_count'] = len(reply.split())
    
    # Formality markers
    metrics['formal_signoff'] = 'Brindle & Oak Support' in reply
    metrics['warm_signoff'] = 'Warmly, Oakley' in reply or 'Oakley at Brindle & Oak' in reply
    
    return metrics

def analyze_sentiment(text):
    """Simple sentiment scoring"""
    positive_words = ['happy', 'glad', 'excited', 'delight', 'wonderful', 'great', 'thank you', 'appreciate']
    negative_words = ['unfortunately', 'cannot', "can't", 'unable', 'not able', 'apologize']
    
    text_lower = text.lower()
    pos_count = sum(1 for w in positive_words if w in text_lower)
    neg_count = sum(1 for w in negative_words if w in text_lower)
    
    return {'positive_words': pos_count, 'negative_words': neg_count}

# Run analysis
print("=" * 80)
print("SUPPORT BOT PROMPT CHANGE ANALYSIS")
print("old_prompt.md (v3) vs new_prompt.md (v4 'Warmth')")
print("=" * 80)
print()

# 1. Policy violations check
print("1. POLICY COMPLIANCE CHECK")
print("-" * 80)

old_violations = defaultdict(list)
new_violations = defaultdict(list)

for ticket_id in old_by_id.keys():
    old_v = check_policy_violation(ticket_id, old_by_id[ticket_id])
    new_v = check_policy_violation(ticket_id, new_by_id[ticket_id])
    
    for v in old_v:
        old_violations[v].append(ticket_id)
    for v in new_v:
        new_violations[v].append(ticket_id)

print(f"Old prompt violations: {sum(len(v) for v in old_violations.values())} total")
for violation_type, ticket_ids in old_violations.items():
    print(f"  - {violation_type}: {ticket_ids}")

print(f"\nNew prompt violations: {sum(len(v) for v in new_violations.values())} total")
for violation_type, ticket_ids in new_violations.items():
    print(f"  - {violation_type}: {ticket_ids}")

print()

# 2. Tone analysis
print("2. TONE & STYLE COMPARISON")
print("-" * 80)

old_tone_stats = defaultdict(int)
new_tone_stats = defaultdict(int)
old_word_counts = []
new_word_counts = []

for ticket_id in old_by_id.keys():
    old_tone = analyze_tone(old_by_id[ticket_id])
    new_tone = analyze_tone(new_by_id[ticket_id])
    
    for key, val in old_tone.items():
        if key == 'word_count':
            old_word_counts.append(val)
        elif val:
            old_tone_stats[key] += 1
    
    for key, val in new_tone.items():
        if key == 'word_count':
            new_word_counts.append(val)
        elif val:
            new_tone_stats[key] += 1

total = len(old_by_id)

print(f"Metric                    Old (v3)      New (v4)      Change")
print(f"Emojis used               {old_tone_stats['has_emoji']:3}/{total} ({old_tone_stats['has_emoji']/total*100:4.1f}%)  {new_tone_stats['has_emoji']:3}/{total} ({new_tone_stats['has_emoji']/total*100:4.1f}%)  {new_tone_stats['has_emoji']-old_tone_stats['has_emoji']:+3}")
print(f"Contains 'sorry'          {old_tone_stats['has_sorry']:3}/{total} ({old_tone_stats['has_sorry']/total*100:4.1f}%)  {new_tone_stats['has_sorry']:3}/{total} ({new_tone_stats['has_sorry']/total*100:4.1f}%)  {new_tone_stats['has_sorry']-old_tone_stats['has_sorry']:+3}")
print(f"Empathy phrases           {old_tone_stats['has_empathy']:3}/{total} ({old_tone_stats['has_empathy']/total*100:4.1f}%)  {new_tone_stats['has_empathy']:3}/{total} ({new_tone_stats['has_empathy']/total*100:4.1f}%)  {new_tone_stats['has_empathy']-old_tone_stats['has_empathy']:+3}")
print(f"Uses first name           {old_tone_stats['uses_first_name']:3}/{total} ({old_tone_stats['uses_first_name']/total*100:4.1f}%)  {new_tone_stats['uses_first_name']:3}/{total} ({new_tone_stats['uses_first_name']/total*100:4.1f}%)  {new_tone_stats['uses_first_name']-old_tone_stats['uses_first_name']:+3}")

avg_old_words = sum(old_word_counts) / len(old_word_counts)
avg_new_words = sum(new_word_counts) / len(new_word_counts)
print(f"\nAvg word count:           {avg_old_words:.1f}          {avg_new_words:.1f}          {avg_new_words-avg_old_words:+.1f}")

print()

# 3. Identify high-risk changes
print("3. HIGH-RISK TICKETS (policy-sensitive scenarios)")
print("-" * 80)

high_risk_tickets = []

for t in tickets:
    tid = t['ticket_id']
    risk_factors = []
    
    # Custom items
    if 'order' in t and t['order'] and 'items' in t['order']:
        for item in t['order']['items']:
            if item.get('sku', '').startswith('CUST-'):
                risk_factors.append('CUSTOM_ITEM')
                break
    
    # Outside 30-day window
    if 'order' in t and t['order'] and 'delivery_date' in t['order']:
        from datetime import datetime
        try:
            del_dt = datetime.strptime(t['order']['delivery_date'], '%Y-%m-%d')
            tkt_dt = datetime.strptime(t['ticket_date'], '%Y-%m-%d')
            days_diff = (tkt_dt - del_dt).days
            if days_diff > 30:
                risk_factors.append(f'OUTSIDE_WINDOW_{days_diff}d')
        except:
            pass
    
    # Escalation keywords
    msg_lower = t.get('message', '').lower()
    if any(kw in msg_lower for kw in ['chargeback', 'lawyer', 'legal', 'attorney']):
        risk_factors.append('ESCALATION_NEEDED')
    
    if risk_factors:
        high_risk_tickets.append((tid, risk_factors))

print(f"Found {len(high_risk_tickets)} policy-sensitive tickets:")
for tid, factors in high_risk_tickets:
    print(f"  {tid}: {', '.join(factors)}")

print()

# 4. Flag concerning changes
print("4. SPECIFIC CONCERNS")
print("-" * 80)

concerns = []

# Check for "do whatever it takes" interpretation
for tid in new_by_id.keys():
    t = tickets_by_id[tid]
    new_reply = new_by_id[tid]
    
    # Check if custom item inappropriately refunded
    if tid in [t[0] for t in high_risk_tickets if 'CUSTOM_ITEM' in t[1]]:
        if 'refund' in new_reply.lower():
            msg = t.get('message', '').lower()
            if any(phrase in msg for phrase in ['change', 'different', "don't like", 'color', 'colour', 'size']):
                concerns.append({
                    'ticket': tid,
                    'issue': 'CUSTOM_REFUND_RISK',
                    'detail': 'New prompt may offer refund on custom item for change of mind'
                })
    
    # Check if outside-window refund offered
    if tid in [t[0] for t in high_risk_tickets if any('OUTSIDE_WINDOW' in f for f in t[1])]:
        if 'refund' in new_reply.lower() and 'cannot' not in new_reply.lower() and "can't" not in new_reply.lower():
            concerns.append({
                'ticket': tid,
                'issue': 'OUT_OF_WINDOW_REFUND',
                'detail': 'New prompt may offer refund outside 30-day window'
            })

# Check for missing policy references
policy_aware_old = sum(1 for r in old_by_id.values() if '30-day' in r or '30 day' in r)
policy_aware_new = sum(1 for r in new_by_id.values() if '30-day' in r or '30 day' in r)

if policy_aware_new < policy_aware_old * 0.7:
    concerns.append({
        'ticket': 'GENERAL',
        'issue': 'POLICY_VISIBILITY',
        'detail': f'New prompt mentions 30-day policy less often ({policy_aware_new} vs {policy_aware_old})'
    })

if concerns:
    for c in concerns:
        print(f"⚠️  {c['ticket']}: {c['issue']}")
        print(f"   {c['detail']}")
else:
    print("✓ No major concerns detected")

print()

# Summary
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print()

print("Tone improvements:")
print(f"  ✓ {new_tone_stats['has_empathy']} replies now show empathy (was {old_tone_stats['has_empathy']})")
print(f"  ✓ {new_tone_stats['has_sorry']} replies apologize/acknowledge (was {old_tone_stats['has_sorry']})")
print(f"  ✓ Average reply length: {avg_new_words:.0f} words (was {avg_old_words:.0f})")

print()
print("Policy compliance:")
if new_violations:
    print(f"  ⚠️  {sum(len(v) for v in new_violations.values())} potential violations detected")
else:
    print(f"  ✓ No automated violations detected")

if concerns:
    print(f"  ⚠️  {len(concerns)} concerns flagged for review")

print()

# Save detailed comparison
print("Saving detailed outputs to output/ directory...")
