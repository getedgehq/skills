#!/usr/bin/env python3
"""
Comprehensive analysis of prompt change impacts
"""
import json
import re
from collections import defaultdict

# Load all data
with open('tickets.jsonl') as f:
    tickets = {json.loads(line)['ticket_id']: json.loads(line) for line in f}

with open('outputs_old.jsonl') as f:
    outputs_old = {json.loads(line)['ticket_id']: json.loads(line) for line in f}

with open('outputs_new.jsonl') as f:
    outputs_new = {json.loads(line)['ticket_id']: json.loads(line) for line in f}

# Count behavior changes
emoji_usage = {'old': 0, 'new': 0}
empathy_phrases = {'old': 0, 'new': 0}
length_increases = 0
policy_references = {'old': 0, 'new': 0}

for ticket_id in tickets:
    old_reply = outputs_old[ticket_id]['reply']
    new_reply = outputs_new[ticket_id]['reply']
    
    # Emoji detection
    emoji_pattern = r'[\U0001F300-\U0001F9FF]|[\u2600-\u26FF]|[\u2700-\u27BF]'
    if re.search(emoji_pattern, old_reply):
        emoji_usage['old'] += 1
    if re.search(emoji_pattern, new_reply):
        emoji_usage['new'] += 1
    
    # Empathy phrases
    empathy_words = ['sorry', 'understand', 'apolog', 'i hear', 'appreciate']
    for word in empathy_words:
        if word in old_reply.lower():
            empathy_phrases['old'] += 1
            break
    for word in empathy_words:
        if word in new_reply.lower():
            empathy_phrases['new'] += 1
            break
    
    # Length changes
    if len(new_reply) > len(old_reply) * 1.2:
        length_increases += 1
    
    # Policy mentions
    policy_words = ['policy', '30 day', 'custom', 'made to measure', 'not refundable']
    if any(word in old_reply.lower() for word in policy_words):
        policy_references['old'] += 1
    if any(word in new_reply.lower() for word in policy_words):
        policy_references['new'] += 1

print(f"Tone & Style Changes:")
print(f"  Empathy language: old {empathy_phrases['old']}/30, new {empathy_phrases['new']}/30")
print(f"  Emoji usage: old {emoji_usage['old']}/30, new {emoji_usage['new']}/30")
print(f"  Replies >20% longer: {length_increases}/30")
print(f"  Policy references: old {policy_references['old']}/30, new {policy_references['new']}/30")
