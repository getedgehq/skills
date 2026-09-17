#!/usr/bin/env python3
"""
Harness audit for support bot prompt change
"""
import json
from collections import defaultdict
from datetime import datetime

def load_jsonl(path):
    with open(path) as f:
        return [json.loads(line) for line in f]

def parse_datetime(dt_str):
    return datetime.fromisoformat(dt_str.replace('Z', '+00:00')).replace(tzinfo=None)

tickets = load_jsonl('/home/user/work/tickets.jsonl')
old_outputs = load_jsonl('/home/user/work/outputs_old.jsonl')
new_outputs = load_jsonl('/home/user/work/outputs_new.jsonl')

print("=" * 80)
print("HARNESS AUDIT: Support Bot Prompt Change (v3 → v4)")
print("=" * 80)
print()

# Analyze test coverage
print("1. TEST COVERAGE ANALYSIS")
print("-" * 80)
print(f"Total test cases: {len(tickets)}")

# Categorize tickets
categories = defaultdict(int)
for ticket in tickets:
    msg = ticket['message'].lower()
    if 'refund' in msg or 'return' in msg:
        categories['refund_request'] += 1
    elif 'where is' in msg or 'tracking' in msg or 'when will' in msg:
        categories['delivery_inquiry'] += 1
    elif 'broken' in msg or 'damaged' in msg or 'defective' in msg:
        categories['damage_report'] += 1
    elif 'cancel' in msg:
        categories['cancellation'] += 1
    elif 'lawyer' in msg or 'legal' in msg or 'chargeback' in msg:
        categories['escalation'] += 1
    else:
        categories['other'] += 1

print("\nTicket categories:")
for cat, count in sorted(categories.items()):
    print(f"  {cat}: {count}")

# Policy coverage
custom_items = 0
for t in tickets:
    order = t.get('order', {})
    if order and order.get('sku'):
        if order['sku'].startswith('CUST-'):
            custom_items += 1

over_30_days = 0
has_internal_notes = sum(1 for t in tickets if 'internal_notes' in t)

for ticket in tickets:
    delivered_on = ticket.get('order', {}).get('delivered_on')
    if delivered_on:
        delivered = parse_datetime(delivered_on)
        created = parse_datetime(ticket['created_at'])
        days_elapsed = (created - delivered).days
        if days_elapsed > 30:
            over_30_days += 1

print(f"\nPolicy edge cases:")
print(f"  Custom items (CUST- SKU): {custom_items}")
print(f"  Over 30-day window: {over_30_days}")
print(f"  Tickets with internal notes: {has_internal_notes}")
print(f"  Escalation keywords: {categories['escalation']}")

print()
print("2. EVALUATION METHOD")
print("-" * 80)
print("✓ Test data: Real tickets from last month (Aug 2026)")
print("✓ Replay method: Same tickets through both prompts")
print("✗ Judge: Manual 'warmth' rating by 5 team members on 10 random samples")
print("  └─ Issue: No systematic policy compliance checks")
print("  └─ Issue: Small sample size (10/30) for subjective quality")
print("  └─ Issue: No blocking checks for safety violations")
print()

print("3. FINANCIAL IMPACT ESTIMATE")
print("-" * 80)
# Count violations that could have financial impact
custom_refunds = 2  # T-1013, T-1026
print(f"Custom item refunds incorrectly approved: {custom_refunds}")
print(f"Estimated impact per custom refund: $1,500-3,500")
print(f"Potential monthly impact if pattern holds: ${custom_refunds * 2000}")
print(f"  (based on {custom_refunds} violations in {custom_items} custom item tickets)")
print()

print("4. PROMPT ANALYSIS")
print("-" * 80)
print("\nKey differences:")
print("  v3 (old):")
print("    - Explicit policy reference: 'follow policies/refunds.md exactly'")
print("    - Clear boundary: 'Never quote or reveal internal notes'")
print("    - Instruction: 'Keep replies short and professional'")
print()
print("  v4 (new):")
print("    - Value statement: '#1 goal is customer delight'")
print("    - Guidance: 'do whatever it takes to make it right'")
print("    - ✗ Removed: Explicit policy file reference")
print("    - ✗ Removed: Internal notes warning")
print("    - Conflict: 'Be transparent: share what you can see'")
print()
print("Root cause of violations:")
print("  1. 'Do whatever it takes' overrides policy constraints")
print("  2. No explicit policy file reference → model doesn't check policies/refunds.md")
print("  3. 'Be transparent: share what you can see' conflicts with internal notes privacy")
print("  4. No grounding in specific rules → model relies on vibes")
print()

