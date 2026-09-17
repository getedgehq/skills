#!/usr/bin/env python3
"""Generate a visual comparison of cost impact."""

import json

# Load trace data
calls = []
with open('logs/calls-2026-09-01_15.jsonl', 'r') as f:
    for line in f:
        call = json.loads(line)
        if call.get('cost_usd') is not None:
            calls.append(call)

# Aggregate
conversations = {}
for call in calls:
    cid = call['conversation_id']
    if cid not in conversations:
        conversations[cid] = {
            'lead_id': call['lead_id'],
            'turns': 0,
            'cost': 0,
        }
    conversations[cid]['turns'] = max(conversations[cid]['turns'], call['turn'])
    conversations[cid]['cost'] += call['cost_usd']

# Categorize
normal = [c for c in conversations.values() if c['turns'] <= 4]
broken = [c for c in conversations.values() if c['turns'] >= 15]

print("BEFORE vs AFTER Cost Comparison")
print("=" * 60)
print()
print("BEFORE (current broken state):")
print(f"  Normal workflows: {len(normal)} conversations = ${sum(c['cost'] for c in normal):.2f}")
print(f"  Retry loop bugs:  {len(broken)} conversations = ${sum(c['cost'] for c in broken):.2f}")
print(f"  TOTAL Sept 1-15:  ${sum(c['cost'] for c in conversations.values()):.2f}")
print()
print("  Breakdown of retry loop costs:")
for conv in sorted(broken, key=lambda c: c['cost'], reverse=True):
    print(f"    Lead {conv['lead_id']}: {conv['turns']:2d} turns → ${conv['cost']:6.2f}")
print()

# Calculate projections
total_before = sum(c['cost'] for c in conversations.values())
normal_cost = sum(c['cost'] for c in normal)
broken_cost = sum(c['cost'] for c in broken)

# After fixing loops
total_after_fix = normal_cost
monthly_before = total_before / 15 * 30  # Scale to full month
monthly_after_fix = total_after_fix / 15 * 30

print("AFTER (with harness fixes):")
print(f"  All 46 conversations run normally")
print(f"  Projected cost: ${total_after_fix:.2f} (Sept 1-15 equivalent)")
print(f"  **Savings: ${broken_cost:.2f} ({broken_cost/total_before*100:.0f}% reduction)**")
print()

print("Monthly Projections:")
print(f"  Current trajectory (broken):  ${monthly_before:.2f}/month")
print(f"  After fixes:                  ${monthly_after_fix:.2f}/month")
print(f"  **Savings: ${monthly_before - monthly_after_fix:.2f}/month**")
print()

# With model switch
monthly_with_haiku = monthly_after_fix / 3  # Haiku is 1/3 the price of Sonnet

print("After fixes + switching to Haiku:")
print(f"  Projected:   ${monthly_with_haiku:.2f}/month")
print(f"  vs current:  ${monthly_before:.2f}/month")
print(f"  **Total savings: ${monthly_before - monthly_with_haiku:.2f}/month (${(monthly_before - monthly_with_haiku)*12:.0f}/year)**")
print()
print("=" * 60)
