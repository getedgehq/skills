#!/usr/bin/env python3
"""Analyze trace logs to find the token burn root cause."""
import json
import sys
from collections import Counter, defaultdict

data = []
with open("/home/user/work/logs/calls-2026-09-01_15.jsonl") as f:
    for line in f:
        row = json.loads(line)
        # Handle None values
        if row.get('cost_usd') is None:
            row['cost_usd'] = 0
        if row.get('input_tokens') is None:
            row['input_tokens'] = 0
        if row.get('output_tokens') is None:
            row['output_tokens'] = 0
        data.append(row)

print(f"Total calls: {len(data)}")
print(f"Unique conversations: {len(set(r['conversation_id'] for r in data))}")
print()

# Aggregate by conversation
by_conv = defaultdict(list)
for row in data:
    by_conv[row['conversation_id']].append(row)

# Conversation-level stats
turns_per_conv = [len(turns) for turns in by_conv.values()]
cost_per_conv = [sum(t['cost_usd'] for t in turns) for turns in by_conv.values()]

print(f"Turns per conversation: min={min(turns_per_conv)}, max={max(turns_per_conv)}, avg={sum(turns_per_conv)/len(turns_per_conv):.1f}")
print(f"Cost per conversation: min=${min(cost_per_conv):.4f}, max=${max(cost_per_conv):.4f}, avg=${sum(cost_per_conv)/len(cost_per_conv):.4f}")
print()

# Total cost
total_cost = sum(r['cost_usd'] for r in data)
total_input_tok = sum(r['input_tokens'] for r in data)
total_output_tok = sum(r['output_tokens'] for r in data)
print(f"Sept 1-15 total cost: ${total_cost:.2f}")
print(f"Total input tokens: {total_input_tok:,} ({total_input_tok/1e6:.2f}M)")
print(f"Total output tokens: {total_output_tok:,} ({total_output_tok/1e6:.2f}M)")
print()

# Token growth per turn
turn_data = defaultdict(lambda: {"count": 0, "input": 0, "output": 0, "cost": 0})
for row in data:
    t = row['turn']
    turn_data[t]['count'] += 1
    turn_data[t]['input'] += row['input_tokens']
    turn_data[t]['output'] += row['output_tokens']
    turn_data[t]['cost'] += row['cost_usd']

print("Token usage by turn number:")
print("Turn | Count | Avg Input | Avg Output | Avg Cost")
for turn in sorted(turn_data.keys()):
    td = turn_data[turn]
    print(f"{turn:4} | {td['count']:5} | {td['input']/td['count']:9.0f} | {td['output']/td['count']:10.0f} | ${td['cost']/td['count']:.5f}")
print()

# Find expensive outliers
sorted_convs = sorted(by_conv.items(), key=lambda x: sum(t['cost_usd'] for t in x[1]), reverse=True)
print("Top 10 most expensive conversations:")
for conv_id, turns in sorted_convs[:10]:
    cost = sum(t['cost_usd'] for t in turns)
    lead = turns[0]['lead_id']
    num_turns = len(turns)
    print(f"  {conv_id} (lead {lead}): {num_turns} turns, ${cost:.4f}")
print()

# Retry analysis - look for same tool repeated
retry_count = 0
retry_examples = []
for conv_id, turns in by_conv.items():
    for i in range(1, len(turns)):
        prev_tools = turns[i-1].get('tool_calls', [])
        curr_tools = turns[i].get('tool_calls', [])
        if prev_tools and curr_tools:
            # Check if crm_update_contact is being retried
            if 'crm_update_contact' in prev_tools and 'crm_update_contact' in curr_tools:
                retry_count += 1
                retry_examples.append((conv_id, turns[0]['lead_id'], i))

print(f"CRM update retries detected: {retry_count}")
if retry_examples[:5]:
    print("Example retry conversations:")
    for cid, lead, turn in retry_examples[:5]:
        print(f"  {cid} (lead {lead}) retry at turn {turn}")
print()

# Tool call distribution
all_tools = []
for row in data:
    all_tools.extend(row.get('tool_calls', []))
print("Tool call distribution:")
for tool, count in Counter(all_tools).most_common():
    print(f"  {tool}: {count}")
print()

# Check for conversations with many turns (potential loops)
long_convs = [(cid, len(turns)) for cid, turns in by_conv.items() if len(turns) > 5]
if long_convs:
    print(f"Conversations with >5 turns (potential infinite loops): {len(long_convs)}")
    for cid, num in sorted(long_convs, key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {cid}: {num} turns")
        conv_turns = by_conv[cid]
        for t in conv_turns:
            print(f"    Turn {t['turn']}: {t['tool_calls']} (${t['cost_usd']:.5f})")
print()

# Calculate what % of cost is from retry loops
retry_conv_ids = set(cid for cid, _, _ in retry_examples)
retry_cost = sum(sum(t['cost_usd'] for t in by_conv[cid]) for cid in retry_conv_ids)
print(f"Cost from conversations with CRM retries: ${retry_cost:.2f} ({100*retry_cost/total_cost:.1f}% of total)")

