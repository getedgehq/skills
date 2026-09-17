#!/usr/bin/env python3
"""
Judge script for support bot golden set evaluation
Usage: python judge.py <outputs.jsonl>
"""
import json
import sys

def check_constraint(reply, constraint):
    """Check if reply satisfies a constraint"""
    reply_lower = reply.lower()
    ctype = constraint['type']
    patterns = constraint['pattern']
    
    if ctype == 'must_contain':
        # Reply must contain at least one of the patterns
        found = any(p in reply_lower for p in patterns)
        return found, f"contains {patterns}" if found else f"missing {patterns}"
    
    elif ctype == 'must_not_offer':
        # Reply must NOT contain any of the patterns
        found = any(p in reply_lower for p in patterns)
        return not found, f"correctly avoids {patterns}" if not found else f"incorrectly offers {patterns}"
    
    elif ctype == 'must_offer':
        # Reply must contain at least one of the patterns
        found = any(p in reply_lower for p in patterns)
        return found, f"offers {patterns}" if found else f"missing {patterns}"
    
    return None, "unknown constraint type"

def evaluate_outputs(golden_path, outputs_path, label):
    """Evaluate outputs against golden set"""
    # Load golden set
    with open(golden_path) as f:
        golden = {json.loads(line)['ticket_id']: json.loads(line) for line in f}
    
    # Load outputs
    with open(outputs_path) as f:
        outputs = {json.loads(line)['ticket_id']: json.loads(line) for line in f}
    
    results = []
    passed = 0
    failed = 0
    
    for tid, case in golden.items():
        if tid not in outputs:
            print(f"WARNING: {tid} not found in outputs")
            continue
        
        reply = outputs[tid]['reply']
        case_passed = True
        failures = []
        
        for constraint in case['constraints']:
            ok, reason = check_constraint(reply, constraint)
            if not ok:
                case_passed = False
                failures.append({
                    'check': constraint['check'],
                    'reason': reason
                })
        
        if case_passed:
            passed += 1
        else:
            failed += 1
        
        results.append({
            'ticket_id': tid,
            'passed': case_passed,
            'failures': failures,
            'message': case['input']['message'][:60]
        })
    
    # Print results
    print(f"\n{'='*70}")
    print(f"{label} EVALUATION")
    print(f"{'='*70}")
    print(f"Passed: {passed}/{passed+failed}")
    print(f"Failed: {failed}/{passed+failed}")
    
    if failed > 0:
        print(f"\n{'='*70}")
        print(f"FAILURES")
        print(f"{'='*70}")
        for r in results:
            if not r['passed']:
                print(f"\n{r['ticket_id']}: {r['message']}")
                for f in r['failures']:
                    print(f"  ✗ {f['check']}")
                    print(f"    {f['reason']}")
    
    return {
        'label': label,
        'passed': passed,
        'failed': failed,
        'total': passed + failed,
        'results': results
    }

if __name__ == '__main__':
    if len(sys.argv) < 2:
        # Run both evaluations
        old_eval = evaluate_outputs('output/golden_set.jsonl', 'outputs_old.jsonl', 'OLD PROMPT')
        new_eval = evaluate_outputs('output/golden_set.jsonl', 'outputs_new.jsonl', 'NEW PROMPT')
        
        # Save results
        with open('output/eval_results.json', 'w') as f:
            json.dump({
                'old_prompt': old_eval,
                'new_prompt': new_eval
            }, f, indent=2)
        
        print(f"\n{'='*70}")
        print("SUMMARY")
        print(f"{'='*70}")
        print(f"Old prompt: {old_eval['passed']}/{old_eval['total']} passed")
        print(f"New prompt: {new_eval['passed']}/{new_eval['total']} passed")
        
        if new_eval['failed'] > old_eval['failed']:
            print(f"\n⚠️  WARNING: New prompt has MORE failures ({new_eval['failed']} vs {old_eval['failed']})")
        elif new_eval['failed'] < old_eval['failed']:
            print(f"\n✓ New prompt has FEWER failures ({new_eval['failed']} vs {old_eval['failed']})")
        else:
            print(f"\nBoth prompts have {new_eval['failed']} failures")
        
        print(f"\nSaved to output/eval_results.json")
    else:
        # Evaluate single outputs file
        outputs_path = sys.argv[1]
        evaluate_outputs('output/golden_set.jsonl', outputs_path, outputs_path)

