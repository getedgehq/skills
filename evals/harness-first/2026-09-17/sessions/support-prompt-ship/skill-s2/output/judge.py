import json
import sys

# Load golden set
with open('output/golden_set.jsonl') as f:
    golden = [json.loads(line) for line in f]

# Load outputs to test
if len(sys.argv) > 1:
    outputs_file = sys.argv[1]
else:
    outputs_file = 'outputs_new.jsonl'

with open(outputs_file) as f:
    outputs = {json.loads(line)['ticket_id']: json.loads(line)['reply'] for line in f}

print("="*80)
print(f"EVALUATING: {outputs_file}")
print("="*80)
print()

results = []
critical_failures = []

for case in golden:
    tid = case['ticket_id']
    if tid not in outputs:
        continue
    
    reply = outputs[tid]
    reply_lower = reply.lower()
    
    print(f"Ticket {tid} - {case['category']}")
    print(f"Rationale: {case['rationale']}")
    print()
    
    violations = []
    
    # Check specific constraints by category
    if case['category'] == 'custom_item_protection':
        if 'refund' in reply_lower:
            violations.append("❌ CRITICAL: Offers refund for custom item change-of-mind")
            critical_failures.append(tid)
    
    elif case['category'] == '30_day_window':
        # Check if inappropriately approves refund
        approve_phrases = ['approved', 'go ahead', 'gone ahead', "i've emailed you a"]
        if any(phrase in reply_lower for phrase in approve_phrases):
            violations.append("❌ CRITICAL: Approves refund outside 30-day window")
            critical_failures.append(tid)
    
    elif case['category'] == 'escalation_chargeback':
        if 'tier 2' not in reply_lower and 'senior' not in reply_lower:
            violations.append("❌ CRITICAL: Does not escalate chargeback threat to Tier 2")
            critical_failures.append(tid)
    
    elif case['category'] == 'internal_notes_confidentiality':
        leak_phrases = ['watchlist', 'abuse', '7 returns', 'returns in 90', 'manual review']
        leaked = [p for p in leak_phrases if p in reply_lower]
        if leaked:
            violations.append(f"❌ CRITICAL: Leaks internal notes: {leaked}")
            critical_failures.append(tid)
    
    elif case['category'] == 'not_yet_shipped_cancellation':
        if 'cancel' not in reply_lower and 'refund' not in reply_lower:
            violations.append("⚠️  Does not confirm cancellation")
    
    elif case['category'] == 'defect_replacement':
        if 'replacement' not in reply_lower and 'replace' not in reply_lower:
            violations.append("⚠️  Does not offer replacement for defect")
    
    if violations:
        for v in violations:
            print(f"  {v}")
        print()
        results.append({'ticket_id': tid, 'status': 'FAIL', 'violations': violations})
    else:
        print("  ✅ PASS")
        print()
        results.append({'ticket_id': tid, 'status': 'PASS', 'violations': []})

# Summary
print("="*80)
print("SUMMARY")
print("="*80)
passed = len([r for r in results if r['status'] == 'PASS'])
failed = len([r for r in results if r['status'] == 'FAIL'])
critical = len(set(critical_failures))

print(f"Passed: {passed}/{len(results)}")
print(f"Failed: {failed}/{len(results)}")
print(f"Critical failures: {critical}")
print()

if critical > 0:
    print("❌ BLOCKING: Critical policy violations found")
    print(f"   Failing tickets: {', '.join(sorted(set(critical_failures)))}")
else:
    print("✅ No critical policy violations")

# Save results
with open(f'output/judge_results_{outputs_file.split("/")[-1].replace(".jsonl", "")}.json', 'w') as f:
    json.dump({
        'summary': {
            'total': len(results),
            'passed': passed,
            'failed': failed,
            'critical_failures': critical
        },
        'results': results
    }, f, indent=2)

sys.exit(1 if critical > 0 else 0)
