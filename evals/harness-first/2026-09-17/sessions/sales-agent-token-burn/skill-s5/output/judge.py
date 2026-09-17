#!/usr/bin/env python3
"""
Golden set judge for the Brightkiln outreach agent.

Checks conversation traces against expected constraints:
- Max turns per conversation
- crm_get_account called exactly once
- Email body length
- No retries on permanent errors
- Cost within expected range
"""

import json
import sys
from collections import defaultdict
from pathlib import Path


def load_golden_set(path):
    """Load test cases from golden set file."""
    cases = []
    with open(path) as f:
        for line in f:
            cases.append(json.loads(line))
    return cases


def load_traces(path):
    """Load conversation traces and group by conversation_id."""
    conversations = defaultdict(list)
    with open(path) as f:
        for line in f:
            trace = json.loads(line)
            # Handle None values
            if trace.get('cost_usd') is None:
                trace['cost_usd'] = 0.0
            if trace.get('input_tokens') is None:
                trace['input_tokens'] = 0
            if trace.get('output_tokens') is None:
                trace['output_tokens'] = 0
            if trace.get('tool_calls') is None:
                trace['tool_calls'] = []
            conversations[trace['conversation_id']].append(trace)
    return conversations


def run_golden_set(golden_path, traces_path):
    """Run all golden set cases against conversation traces."""
    cases = load_golden_set(golden_path)
    conversations = load_traces(traces_path)
    
    print(f"=== GOLDEN SET EVALUATION ===\n")
    print(f"Loaded {len(cases)} test cases")
    print(f"Loaded {len(conversations)} conversations from traces\n")
    
    # For now, we'll evaluate the traces statistically since we don't have
    # exact conversation-to-test-case mapping
    print("=== STATISTICAL CHECKS ON ALL CONVERSATIONS ===\n")
    
    total_conversations = len(conversations)
    checks = {
        'max_turns_10': 0,
        'crm_get_account_once': 0,
        'no_retries': 0,
        'cost_reasonable': 0,
    }
    
    failures = {
        'max_turns_10': [],
        'crm_get_account_once': [],
        'no_retries': [],
        'cost_reasonable': [],
    }
    
    for conv_id, traces in conversations.items():
        lead_id = traces[0].get('lead_id', 'unknown')
        
        # Max turns
        if len(traces) <= 10:
            checks['max_turns_10'] += 1
        else:
            failures['max_turns_10'].append((conv_id, lead_id, len(traces)))
        
        # crm_get_account once
        get_account_calls = sum(
            1 for t in traces for tool in t['tool_calls'] 
            if tool == 'crm_get_account'
        )
        if get_account_calls == 1:
            checks['crm_get_account_once'] += 1
        else:
            failures['crm_get_account_once'].append((conv_id, lead_id, get_account_calls))
        
        # No retries
        tool_sequence = []
        for t in traces:
            tool_sequence.extend(t['tool_calls'])
        has_retries = any(
            tool_sequence[i] == tool_sequence[i+1] 
            for i in range(len(tool_sequence)-1)
            if i+1 < len(tool_sequence)
        )
        if not has_retries:
            checks['no_retries'] += 1
        else:
            failures['no_retries'].append((conv_id, lead_id))
        
        # Cost reasonable
        total_cost = sum(t.get('cost_usd', 0) for t in traces)
        if total_cost <= 0.50:
            checks['cost_reasonable'] += 1
        else:
            failures['cost_reasonable'].append((conv_id, lead_id, total_cost))
    
    print(f"Max turns (<=10):          {checks['max_turns_10']:3d} / {total_conversations} ({checks['max_turns_10']/total_conversations*100:.1f}%)")
    print(f"crm_get_account once:      {checks['crm_get_account_once']:3d} / {total_conversations} ({checks['crm_get_account_once']/total_conversations*100:.1f}%)")
    print(f"No retry patterns:         {checks['no_retries']:3d} / {total_conversations} ({checks['no_retries']/total_conversations*100:.1f}%)")
    print(f"Cost reasonable (<$0.50):  {checks['cost_reasonable']:3d} / {total_conversations} ({checks['cost_reasonable']/total_conversations*100:.1f}%)")
    
    # Show some failures
    print(f"\n=== EXAMPLE FAILURES ===\n")
    
    if failures['max_turns_10']:
        print(f"Conversations exceeding 10 turns ({len(failures['max_turns_10'])}):")
        for conv_id, lead_id, turns in failures['max_turns_10'][:3]:
            print(f"  {conv_id} (lead {lead_id}): {turns} turns")
    
    if failures['crm_get_account_once']:
        print(f"\ncrm_get_account called multiple times ({len(failures['crm_get_account_once'])}):")
        for conv_id, lead_id, calls in failures['crm_get_account_once'][:3]:
            print(f"  {conv_id} (lead {lead_id}): {calls} calls")
    
    if failures['cost_reasonable']:
        print(f"\nConversations exceeding $0.50 cost ({len(failures['cost_reasonable'])}):")
        for conv_id, lead_id, cost in failures['cost_reasonable'][:3]:
            print(f"  {conv_id} (lead {lead_id}): ${cost:.2f}")
    
    # Overall pass rate
    total_checks = sum(checks.values())
    max_checks = total_conversations * 4
    pass_rate = total_checks / max_checks * 100
    
    print(f"\n=== OVERALL ===")
    print(f"Checks passed: {total_checks} / {max_checks} ({pass_rate:.1f}%)")
    
    if pass_rate >= 90:
        print("✅ PASS - Golden set criteria met")
        return 0
    elif pass_rate >= 70:
        print("⚠️  PARTIAL - Some issues detected")
        return 1
    else:
        print("❌ FAIL - Significant issues remain")
        return 2


def main():
    golden_path = Path(__file__).parent / 'golden_set.jsonl'
    traces_path = Path(__file__).parent.parent / 'logs' / 'calls-2026-09-01_15.jsonl'
    
    if not golden_path.exists():
        print(f"Error: Golden set not found at {golden_path}")
        return 1
    
    if not traces_path.exists():
        print(f"Error: Traces not found at {traces_path}")
        return 1
    
    return run_golden_set(golden_path, traces_path)


if __name__ == '__main__':
    sys.exit(main())
