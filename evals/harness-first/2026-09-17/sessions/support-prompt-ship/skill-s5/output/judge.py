#!/usr/bin/env python3
"""
Judge script for support bot outputs
Run this on every prompt change before shipping
"""

import json
import sys

def load_jsonl(path):
    with open(path, 'r') as f:
        return [json.loads(line) for line in f]

def check_constraints(reply, must_have, must_not):
    """Check if reply meets constraints"""
    reply_lower = reply.lower()
    failures = []
    
    for phrase in must_have:
        # Flexible matching - any word in phrase
        words = phrase.lower().split()
        if not any(word in reply_lower for word in words):
            failures.append(f"MISSING: '{phrase}'")
    
    for phrase in must_not:
        if phrase.lower() in reply_lower:
            failures.append(f"FORBIDDEN: '{phrase}' found in reply")
    
    return failures

def judge_outputs(golden_set_path, outputs_path):
    """Judge outputs against golden set"""
    golden = {g['ticket_id']: g for g in load_jsonl(golden_set_path)}
    outputs = {o['ticket_id']: o for o in load_jsonl(outputs_path)}
    
    results = {
        'pass': 0,
        'fail': 0,
        'failures': []
    }
    
    for ticket_id, constraints in golden.items():
        if ticket_id not in outputs:
            results['fail'] += 1
            results['failures'].append({
                'ticket_id': ticket_id,
                'criticality': constraints['criticality'],
                'description': constraints['description'],
                'error': 'Output not found'
            })
            continue
        
        reply = outputs[ticket_id]['reply']
        failures = check_constraints(
            reply,
            constraints['must_have'],
            constraints['must_not']
        )
        
        if failures:
            results['fail'] += 1
            results['failures'].append({
                'ticket_id': ticket_id,
                'criticality': constraints['criticality'],
                'description': constraints['description'],
                'failures': failures,
                'reply_snippet': reply[:200] + '...'
            })
        else:
            results['pass'] += 1
    
    return results

def main():
    if len(sys.argv) != 3:
        print("Usage: ./judge.py golden_set.jsonl outputs.jsonl")
        sys.exit(1)
    
    golden_path = sys.argv[1]
    outputs_path = sys.argv[2]
    
    print(f"Judging {outputs_path} against {golden_path}...")
    results = judge_outputs(golden_path, outputs_path)
    
    print("\n" + "="*80)
    print(f"RESULTS: {results['pass']} PASS, {results['fail']} FAIL")
    print("="*80)
    
    if results['failures']:
        print("\nFAILURES:\n")
        
        # Group by criticality
        critical = [f for f in results['failures'] if f['criticality'] == 'CRITICAL']
        high = [f for f in results['failures'] if f['criticality'] == 'HIGH']
        low = [f for f in results['failures'] if f['criticality'] == 'LOW']
        
        for category, failures in [('CRITICAL', critical), ('HIGH', high), ('LOW', low)]:
            if failures:
                print(f"\n{category} ({len(failures)}):")
                print("-" * 80)
                for f in failures:
                    print(f"\n{f['ticket_id']}: {f['description']}")
                    if 'failures' in f:
                        for failure in f['failures']:
                            print(f"  ✗ {failure}")
                    else:
                        print(f"  ✗ {f['error']}")
    
    # Save detailed results
    output_file = outputs_path.replace('.jsonl', '_judge_results.json')
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nDetailed results saved to {output_file}")
    
    # Exit with error code if any failures
    sys.exit(0 if results['fail'] == 0 else 1)

if __name__ == '__main__':
    main()
