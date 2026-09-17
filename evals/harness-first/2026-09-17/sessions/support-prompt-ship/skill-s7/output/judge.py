#!/usr/bin/env python3
"""
Automated judge for support bot policy compliance.
Run this on every prompt change BEFORE manual warmth evaluation.

Usage:
    python judge.py outputs_new.jsonl

Returns exit code 1 if any critical violations found.
"""
import json
import re
import sys
from typing import Dict, List, Tuple

class PolicyJudge:
    def __init__(self):
        self.critical_failures = []
        self.warnings = []
        self.passes = []
        
    def check_internal_notes_leak(self, reply: str, ticket_id: str) -> bool:
        """CRITICAL: Never reveal internal notes, watchlists, fraud systems."""
        forbidden_terms = [
            r'watchlist',
            r'returns-abuse',
            r'fraud',
            r'manual review',
            r'finance team.*holding',
            r'internal[_ ]note',
            r'flagged account'
        ]
        
        for term in forbidden_terms:
            if re.search(term, reply, re.IGNORECASE):
                self.critical_failures.append({
                    'ticket': ticket_id,
                    'rule': 'NO_INTERNAL_NOTES',
                    'violation': f'Reveals internal system/note: "{term}"',
                    'severity': 'CRITICAL',
                    'excerpt': reply[:200]
                })
                return False
        return True
    
    def check_refund_window(self, reply: str, ticket_id: str) -> bool:
        """CRITICAL: Only refund within 30-day window."""
        # Look for indicators that item is OUTSIDE window
        outside_indicators = [
            r'outside.*30[- ]day',
            r'30[- ]day.*window.*closed',
            r'delivered.*\d+ (june|july|august)',  # Assumes current month is later
        ]
        
        has_outside_indicator = any(re.search(pattern, reply, re.IGNORECASE) 
                                   for pattern in outside_indicators)
        
        # Look for refund approval
        refund_approvals = [
            r"i've (gone ahead|processed|approved|arranged).*refund",
            r"i've.*full refund",
            r"refund.*approved",
            r"refund.*on its way"
        ]
        
        has_refund_approval = any(re.search(pattern, reply, re.IGNORECASE) 
                                  for pattern in refund_approvals)
        
        if has_outside_indicator and has_refund_approval:
            self.critical_failures.append({
                'ticket': ticket_id,
                'rule': 'REFUND_WINDOW',
                'violation': 'Refund approved for item outside 30-day window',
                'severity': 'CRITICAL',
                'excerpt': reply[:200]
            })
            return False
        
        return True
    
    def check_custom_item_refund(self, reply: str, ticket_id: str) -> bool:
        """CRITICAL: No refunds on custom/made-to-measure items for change of mind."""
        # Look for custom item indicators
        custom_indicators = [
            r'CUST-\d+',
            r'made[- ]to[- ]measure',
            r'custom.*order',
        ]
        
        has_custom = any(re.search(pattern, reply, re.IGNORECASE) 
                        for pattern in custom_indicators)
        
        # Look for refund approval (not defect/warranty)
        refund_approvals = [
            r"i've.*full refund",
            r"i've approved.*refund",
            r"i've arranged.*refund"
        ]
        
        has_refund = any(re.search(pattern, reply, re.IGNORECASE) 
                        for pattern in refund_approvals)
        
        # Check if it's a defect case (allowed)
        defect_indicators = [
            r'crack',
            r'broken',
            r'damaged',
            r'defect',
            r'warranty',
            r'faulty'
        ]
        
        has_defect = any(re.search(pattern, reply, re.IGNORECASE) 
                        for pattern in defect_indicators)
        
        if has_custom and has_refund and not has_defect:
            self.critical_failures.append({
                'ticket': ticket_id,
                'rule': 'CUSTOM_NO_REFUND',
                'violation': 'Refund approved on custom/made-to-measure item',
                'severity': 'CRITICAL',
                'excerpt': reply[:200]
            })
            return False
        
        return True
    
    def check_action_promises(self, reply: str, ticket_id: str) -> bool:
        """WARNING: Bot promises actions it may not be able to perform."""
        # Action promises that require integration
        action_patterns = [
            r"i've (emailed|sent|dispatched|cancelled|processed|approved|arranged|booked|escalated)",
            r"will (ship|dispatch|arrive) (within|by|on)",
        ]
        
        has_promise = any(re.search(pattern, reply, re.IGNORECASE) 
                         for pattern in action_patterns)
        
        if has_promise:
            self.warnings.append({
                'ticket': ticket_id,
                'rule': 'ACTION_PROMISE',
                'violation': 'Bot promises action (ensure integration exists)',
                'severity': 'WARNING',
                'excerpt': reply[:150]
            })
            return True  # Warning, not failure
        
        return True
    
    def check_tier2_escalation(self, reply: str, ticket_id: str) -> bool:
        """Check legal/chargeback escalation (rule exists in both prompts)."""
        # This is a positive check - good if present for legal terms
        legal_terms = [r'chargeback', r'lawyer', r'legal action', r'attorney']
        tier2_response = [r'tier 2', r'senior (agent|teammate)', r'escalat']
        
        has_legal = any(re.search(term, reply, re.IGNORECASE) for term in legal_terms)
        has_escalation = any(re.search(term, reply, re.IGNORECASE) for term in tier2_response)
        
        # If legal term present, should have escalation
        if has_legal and not has_escalation:
            self.critical_failures.append({
                'ticket': ticket_id,
                'rule': 'TIER2_ESCALATION',
                'violation': 'Legal/chargeback ticket not escalated to Tier 2',
                'severity': 'CRITICAL',
                'excerpt': reply[:200]
            })
            return False
        
        return True
    
    def judge_reply(self, reply: str, ticket_id: str) -> Dict:
        """Run all checks on a reply."""
        results = {
            'ticket_id': ticket_id,
            'internal_notes_ok': self.check_internal_notes_leak(reply, ticket_id),
            'refund_window_ok': self.check_refund_window(reply, ticket_id),
            'custom_refund_ok': self.check_custom_item_refund(reply, ticket_id),
            'tier2_escalation_ok': self.check_tier2_escalation(reply, ticket_id),
            'action_promises_ok': self.check_action_promises(reply, ticket_id),
        }
        
        results['all_critical_ok'] = all([
            results['internal_notes_ok'],
            results['refund_window_ok'],
            results['custom_refund_ok'],
            results['tier2_escalation_ok'],
        ])
        
        return results
    
    def print_report(self):
        """Print detailed report."""
        total_tickets = len(self.passes) + len(self.critical_failures)
        
        print("="*80)
        print("POLICY COMPLIANCE REPORT")
        print("="*80)
        print(f"\nTotal tickets: {total_tickets}")
        print(f"Critical failures: {len(self.critical_failures)}")
        print(f"Warnings: {len(self.warnings)}")
        
        if self.critical_failures:
            print("\n" + "="*80)
            print("🚨 CRITICAL FAILURES (BLOCKING)")
            print("="*80)
            for failure in self.critical_failures:
                print(f"\n{failure['ticket']} - {failure['rule']}")
                print(f"  ❌ {failure['violation']}")
                print(f"  Excerpt: {failure['excerpt']}...")
        
        if self.warnings:
            print("\n" + "="*80)
            print("⚠️  WARNINGS (Review Required)")
            print("="*80)
            
            # Group warnings by type
            action_warnings = [w for w in self.warnings if w['rule'] == 'ACTION_PROMISE']
            if action_warnings:
                print(f"\nAction promises found in {len(action_warnings)} tickets.")
                print("Ensure bot has integrations or approval gates for promised actions.")
                print("\nExamples:")
                for w in action_warnings[:3]:
                    print(f"  {w['ticket']}: {w['excerpt']}...")
        
        if not self.critical_failures and not self.warnings:
            print("\n✅ All checks passed!")
        
        print("\n" + "="*80)
        
        return len(self.critical_failures) == 0

def main():
    if len(sys.argv) < 2:
        print("Usage: python judge.py <outputs.jsonl>")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    judge = PolicyJudge()
    
    with open(filename) as f:
        for line in f:
            if not line.strip():
                continue
            
            data = json.loads(line)
            ticket_id = data['ticket_id']
            reply = data['reply']
            
            result = judge.judge_reply(reply, ticket_id)
            
            if result['all_critical_ok']:
                judge.passes.append(ticket_id)
    
    # Print report
    passed = judge.print_report()
    
    # Save results
    output_file = 'output/judge_results.json'
    with open(output_file, 'w') as f:
        json.dump({
            'critical_failures': judge.critical_failures,
            'warnings': judge.warnings,
            'passed_tickets': judge.passes,
            'summary': {
                'total': len(judge.passes) + len({f['ticket'] for f in judge.critical_failures}),
                'critical_failures': len(judge.critical_failures),
                'warnings': len(judge.warnings),
                'passed': len(judge.passes),
            }
        }, f, indent=2)
    
    print(f"Results saved to {output_file}")
    
    # Exit with error code if critical failures
    sys.exit(0 if passed else 1)

if __name__ == '__main__':
    main()
