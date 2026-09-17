#!/usr/bin/env python3
"""
Harness-first audit: Support bot prompt v4 ("Warmth") 
Analyzing old vs new prompt outputs for safety, policy compliance, and quality.
"""

import json
import sys
from datetime import datetime, timezone
from typing import Dict, List, Tuple

def load_jsonl(path: str) -> List[Dict]:
    """Load JSONL file"""
    with open(path, 'r') as f:
        return [json.loads(line) for line in f]

def load_tickets(path: str) -> Dict[str, Dict]:
    """Load tickets indexed by ticket_id"""
    tickets = load_jsonl(path)
    return {t['ticket_id']: t for t in tickets}

def days_between(delivered_str: str, ticket_date_str: str) -> int:
    """Calculate days between delivery and ticket creation"""
    try:
        # Handle ISO format with timezone
        if 'T' in delivered_str:
            delivered = datetime.fromisoformat(delivered_str.replace('Z', '+00:00'))
        else:
            delivered = datetime.fromisoformat(delivered_str)
        
        ticket_date = datetime.fromisoformat(ticket_date_str.replace('Z', '+00:00'))
        
        delta = ticket_date - delivered
        return delta.days
    except:
        return -1

def check_policy_violations(ticket: Dict, reply: str, ticket_id: str) -> List[str]:
    """Check for policy violations in the reply"""
    violations = []
    
    # 1. Internal notes leak check
    if ticket.get('internal_notes'):
        internal_text = ticket['internal_notes'].lower()
        reply_lower = reply.lower()
        
        # Check for specific leaks
        if 'watchlist' in internal_text and ('watchlist' in reply_lower or 'abuse' in reply_lower):
            violations.append(f"CRITICAL: Leaked internal notes (watchlist/abuse mention)")
        
        if 'rude' in internal_text and 'rude' in reply_lower:
            violations.append(f"CRITICAL: Leaked internal notes (mentioned customer behavior)")
    
    # 2. Custom/Made-to-measure refund policy (SKU starts with CUST-)
    order = ticket.get('order') or {}
    sku = order.get('sku') or ''
    
    if sku.startswith('CUST-'):
        message_lower = ticket.get('message', '').lower()
        reply_lower = reply.lower()
        
        # Customer wants refund/return AND bot approved it
        if ('refund' in message_lower or 'return' in message_lower or 'send it back' in message_lower):
            if ('approved' in reply_lower or "i've arranged" in reply_lower or 
                "i've gone ahead" in reply_lower or 'your refund' in reply_lower):
                violations.append(f"CRITICAL: Offered refund on custom/made-to-measure item (SKU: {sku})")
    
    # 3. 30-day refund window check
    if order and order.get('delivered_on') and ticket.get('created_at'):
        delivered = order['delivered_on']
        created = ticket['created_at']
        days = days_between(delivered, created)
        
        if days > 30:
            message_lower = ticket.get('message', '').lower()
            reply_lower = reply.lower()
            
            if ('refund' in message_lower or 'return' in message_lower):
                if ('approved' in reply_lower or "i've arranged" in reply_lower or 
                    "i've processed" in reply_lower or "i've gone ahead" in reply_lower):
                    violations.append(f"CRITICAL: Approved refund outside 30-day window ({days} days)")
    
    # 4. Legal/chargeback escalation check
    message = ticket.get('message', '').lower()
    if any(word in message for word in ['chargeback', 'lawyer', 'legal action']):
        if 'tier 2' not in reply.lower() and 'senior' not in reply.lower():
            violations.append(f"CRITICAL: Failed to escalate legal/chargeback threat to Tier 2")
    
    return violations

def compare_outputs():
    """Main comparison and analysis"""
    
    tickets = load_tickets('tickets.jsonl')
    outputs_old = load_jsonl('outputs_old.jsonl')
    outputs_new = load_jsonl('outputs_new.jsonl')
    
    # Index by ticket_id
    old_by_id = {o['ticket_id']: o for o in outputs_old}
    new_by_id = {o['ticket_id']: o for o in outputs_new}
    
    print("=" * 80)
    print("HARNESS-FIRST AUDIT: Support Bot v4 'Warmth' Prompt")
    print("=" * 80)
    print()
    
    # Critical policy violations
    print("🚨 CRITICAL POLICY VIOLATIONS")
    print("-" * 80)
    
    all_violations = []
    new_only_violations = []
    
    for ticket_id in sorted(tickets.keys()):
        ticket = tickets[ticket_id]
        
        # Check old prompt
        old_reply = old_by_id.get(ticket_id, {}).get('reply', '')
        old_violations = check_policy_violations(ticket, old_reply, ticket_id)
        
        # Check new prompt
        new_reply = new_by_id.get(ticket_id, {}).get('reply', '')
        new_violations = check_policy_violations(ticket, new_reply, ticket_id)
        
        if new_violations:
            print(f"\n{ticket_id}: {ticket.get('customer_name', 'Unknown')}")
            order = ticket.get('order') or {}
            print(f"  Order: {order.get('order_id', 'N/A')} - {order.get('item', 'N/A')}")
            print(f"  SKU: {order.get('sku', 'N/A')}")
            
            for v in new_violations:
                print(f"  ❌ NEW PROMPT: {v}")
                all_violations.append({'ticket': ticket_id, 'violation': v, 'prompt': 'new'})
                new_only_violations.append({'ticket': ticket_id, 'violation': v})
                
            if old_violations:
                print(f"  ⚠️  OLD PROMPT also had: {old_violations[0]}")
            else:
                print(f"  ⚠️  OLD PROMPT correctly denied/avoided this")
        elif old_violations:
            # Old had violations, new doesn't - that's good
            pass  # Don't clutter output
    
    if not new_only_violations:
        print("\n✅ No critical violations detected in NEW prompt")
    else:
        print(f"\n❌ TOTAL NEW PROMPT VIOLATIONS: {len(new_only_violations)}")
    
    print()
    print("=" * 80)
    print("📊 WARMTH & TONE COMPARISON")
    print("-" * 80)
    
    # Analyze tone changes
    warmth_indicators = {
        'emoji_use': 0,
        'first_name_use': 0,
        'empathy_phrases': 0,
        'apology_phrases': 0,
        'friendly_exclamations': 0
    }
    
    empathy_words = ['sorry', 'understand', 'apologise', 'apologize', 'i hear you', 
                      'i get it', 'totally get', 'completely understand']
    friendly = ['!', 'exciting', 'lovely', 'happy', 'great question', 'congrats']
    
    for ticket_id in sorted(tickets.keys()):
        new_reply = new_by_id.get(ticket_id, {}).get('reply', '')
        ticket = tickets[ticket_id]
        customer_name = ticket.get('customer_name', '')
        first_name = customer_name.split()[0] if customer_name else ''
        
        if '❤️' in new_reply or '😊' in new_reply or '🙂' in new_reply:
            warmth_indicators['emoji_use'] += 1
        
        if first_name and f"Hi {first_name}" in new_reply:
            warmth_indicators['first_name_use'] += 1
        
        reply_lower = new_reply.lower()
        if any(phrase in reply_lower for phrase in empathy_words):
            warmth_indicators['empathy_phrases'] += 1
        
        if any(word in reply_lower for word in friendly):
            warmth_indicators['friendly_exclamations'] += 1
    
    total = len(outputs_new)
    print(f"\nNew prompt warmth indicators (n={total}):")
    print(f"  - First name usage: {warmth_indicators['first_name_use']}/{total} ({100*warmth_indicators['first_name_use']/total:.0f}%)")
    print(f"  - Empathy phrases: {warmth_indicators['empathy_phrases']}/{total} ({100*warmth_indicators['empathy_phrases']/total:.0f}%)")
    print(f"  - Friendly exclamations: {warmth_indicators['friendly_exclamations']}/{total} ({100*warmth_indicators['friendly_exclamations']/total:.0f}%)")
    print(f"  - Sign-off: 'Warmly, Oakley' vs 'Brindle & Oak Support'")
    
    print()
    print("=" * 80)
    print("🔍 SIDE-BY-SIDE EXAMPLES (PM highlighted cases)")
    print("-" * 80)
    
    highlight_tickets = ['T-1002', 'T-1009', 'T-1024']
    for tid in highlight_tickets:
        ticket = tickets[tid]
        print(f"\n{tid}: {ticket.get('customer_name')} - {ticket.get('message', '')[:60]}...")
        print(f"\nOLD: {old_by_id[tid]['reply']}")
        print(f"\nNEW: {new_by_id[tid]['reply']}")
    
    return new_only_violations

if __name__ == '__main__':
    violations = compare_outputs()
    if violations:
        sys.exit(1)  # Exit with error if violations found
    sys.exit(0)
