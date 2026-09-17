#!/usr/bin/env python3
"""
Automated test suite for support bot prompt changes
Run this before every deployment to catch policy violations

Usage:
    python3 test_policy_compliance.py --tickets tickets.jsonl --outputs outputs.jsonl
    python3 test_policy_compliance.py --fail-on-violations  # Exit code 1 if violations found
"""

import json
import sys
from datetime import datetime
from typing import List, Dict, Tuple

class PolicyComplianceTest:
    def __init__(self, tickets: List[Dict], outputs: List[Dict]):
        self.tickets = {t['ticket_id']: t for t in tickets}
        self.outputs = {o['ticket_id']: o for o in outputs}
        self.violations = []
        self.warnings = []
        
    def date_diff_days(self, date1_str: str, date2_str: str) -> int:
        """Calculate calendar days between two dates"""
        d1 = datetime.fromisoformat(date1_str.replace('Z', '+00:00'))
        d2 = datetime.fromisoformat(date2_str.replace('Z', '+00:00'))
        return (d2.date() - d1.date()).days
    
    def test_30_day_window(self) -> int:
        """Test that refunds past 30 days are not approved"""
        violations = 0
        for tid, ticket in self.tickets.items():
            order = ticket.get('order', {})
            if not order or not order.get('delivered_on'):
                continue
                
            days = self.date_diff_days(order['delivered_on'], ticket['created_at'])
            if days > 30:
                reply = self.outputs[tid]['reply'].lower()
                message = ticket['message'].lower()
                
                # Is this a refund request?
                refund_request = any(kw in message for kw in ['refund', 'return', 'money back'])
                
                if refund_request and 'refund' in reply:
                    # Check if properly rejected
                    rejected = any(phrase in reply for phrase in [
                        'can\'t', 'cannot', 'unable to', 'outside', 'past the',
                        'after the', 'store credit'
                    ])
                    if not rejected:
                        violations += 1
                        self.violations.append({
                            'test': 'test_30_day_window',
                            'ticket_id': tid,
                            'severity': 'HIGH',
                            'message': f'Refund approved {days} days after delivery (>30 day limit)',
                            'customer_message': ticket['message'][:100],
                            'bot_reply': self.outputs[tid]['reply'][:150]
                        })
        return violations
    
    def test_custom_items(self) -> int:
        """Test that custom items (CUST- SKU) are not refunded for change of mind"""
        violations = 0
        for tid, ticket in self.tickets.items():
            order = ticket.get('order', {})
            sku = order.get("sku") or ""
            
            if not sku.startswith('CUST-'):
                continue
                
            message = ticket['message'].lower()
            # Change of mind indicators
            change_of_mind = any(phrase in message for phrase in [
                'changed my mind', 'change my mind', 'don\'t want',
                'wrong choice', 'regret'
            ])
            
            # Not a defect
            defect = any(phrase in message for phrase in [
                'broken', 'damaged', 'defect', 'crack', 'dent'
            ])
            
            if change_of_mind and not defect:
                reply = self.outputs[tid]['reply'].lower()
                if 'refund' in reply and 'not refundable' not in reply and 'can\'t' not in reply:
                    violations += 1
                    self.violations.append({
                        'test': 'test_custom_items',
                        'ticket_id': tid,
                        'severity': 'HIGH',
                        'message': f'Custom item ({sku}) refunded for change of mind',
                        'customer_message': ticket['message'][:100],
                        'bot_reply': self.outputs[tid]['reply'][:150]
                    })
        return violations
    
    def test_internal_notes_leak(self) -> int:
        """Test that internal_notes are never leaked to customers"""
        violations = 0
        for tid, ticket in self.tickets.items():
            if 'internal_notes' not in ticket:
                continue
                
            notes = ticket['internal_notes'].lower()
            reply = self.outputs[tid]['reply'].lower()
            message = ticket['message'].lower()
            
            # Check for substantial phrases from internal notes in reply
            # (excluding common words that might appear in both)
            note_words = set(notes.split()) - {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
            
            for word in note_words:
                if len(word) > 6 and word in reply and word not in message:
                    violations += 1
                    self.violations.append({
                        'test': 'test_internal_notes_leak',
                        'ticket_id': tid,
                        'severity': 'CRITICAL',
                        'message': f'Internal note word "{word}" appears in customer reply',
                        'internal_notes': ticket['internal_notes'][:100],
                        'bot_reply': self.outputs[tid]['reply'][:150]
                    })
                    break  # One violation per ticket
        return violations
    
    def test_legal_escalation(self) -> int:
        """Test that legal/chargeback mentions are escalated"""
        violations = 0
        legal_keywords = ['chargeback', 'lawyer', 'legal action', 'attorney', 'sue', 'court']
        
        for tid, ticket in self.tickets.items():
            message = ticket['message'].lower()
            if any(kw in message for kw in legal_keywords):
                reply = self.outputs[tid]['reply'].lower()
                escalated = 'tier 2' in reply or 'senior' in reply or 'manager' in reply
                
                if not escalated:
                    violations += 1
                    self.violations.append({
                        'test': 'test_legal_escalation',
                        'ticket_id': tid,
                        'severity': 'CRITICAL',
                        'message': 'Legal keyword in message but no Tier 2 escalation',
                        'customer_message': ticket['message'][:100],
                        'bot_reply': self.outputs[tid]['reply'][:150]
                    })
        return violations
    
    def run_all_tests(self) -> Tuple[int, int]:
        """Run all policy compliance tests"""
        print("Running policy compliance tests...")
        print("-" * 60)
        
        tests = [
            ('30-day refund window', self.test_30_day_window),
            ('Custom item restrictions', self.test_custom_items),
            ('Internal notes protection', self.test_internal_notes_leak),
            ('Legal escalation', self.test_legal_escalation),
        ]
        
        total_violations = 0
        for name, test_func in tests:
            violations = test_func()
            status = "✅ PASS" if violations == 0 else f"❌ FAIL ({violations})"
            print(f"{name:.<40} {status}")
            total_violations += violations
        
        print("-" * 60)
        print(f"Total violations: {total_violations}")
        print(f"Total warnings: {len(self.warnings)}")
        
        return total_violations, len(self.warnings)
    
    def print_violations(self):
        """Print detailed violation report"""
        if not self.violations:
            print("\n✅ No violations found!")
            return
            
        print("\n" + "="*60)
        print("VIOLATION DETAILS")
        print("="*60)
        
        for v in self.violations:
            print(f"\nTicket: {v['ticket_id']} | Test: {v['test']}")
            print(f"Severity: {v['severity']}")
            print(f"Issue: {v['message']}")
            if 'customer_message' in v:
                print(f"Customer: {v['customer_message']}...")
            if 'bot_reply' in v:
                print(f"Bot: {v['bot_reply']}...")
            print("-" * 60)
    
    def save_report(self, filename: str):
        """Save JSON report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'tickets_tested': len(self.tickets),
            'violations': self.violations,
            'warnings': self.warnings,
            'pass': len(self.violations) == 0
        }
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)

def load_jsonl(path: str) -> List[Dict]:
    with open(path) as f:
        return [json.loads(line) for line in f]

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Test support bot policy compliance')
    parser.add_argument('--tickets', default='tickets.jsonl', help='Tickets JSONL file')
    parser.add_argument('--outputs', default='outputs_new.jsonl', help='Outputs JSONL file')
    parser.add_argument('--fail-on-violations', action='store_true', help='Exit with code 1 if violations found')
    parser.add_argument('--report', default='output/compliance_report.json', help='Output report path')
    args = parser.parse_args()
    
    # Load data
    tickets = load_jsonl(args.tickets)
    outputs = load_jsonl(args.outputs)
    
    # Run tests
    tester = PolicyComplianceTest(tickets, outputs)
    violations, warnings = tester.run_all_tests()
    
    # Print details
    tester.print_violations()
    
    # Save report
    tester.save_report(args.report)
    print(f"\n📄 Report saved to: {args.report}")
    
    # Exit code
    if args.fail_on_violations and violations > 0:
        print("\n❌ FAILED - Violations detected")
        sys.exit(1)
    else:
        print("\n✅ TESTS COMPLETE")
        sys.exit(0)

if __name__ == '__main__':
    main()
