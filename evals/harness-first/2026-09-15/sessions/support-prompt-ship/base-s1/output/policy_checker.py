#!/usr/bin/env python3
"""
Automated policy compliance checker for support bot prompts.

Usage:
    python policy_checker.py tickets.jsonl outputs.jsonl

Returns exit code 1 if any critical violations found.
"""

import json
import sys
from datetime import datetime
from typing import Dict, List, Tuple


class PolicyChecker:
    def __init__(self, tickets_file: str, outputs_file: str):
        self.tickets = self._load_jsonl(tickets_file)
        self.outputs = self._load_jsonl(outputs_file)
        self.violations = []
        
    def _load_jsonl(self, filepath: str) -> Dict:
        """Load JSONL file into dict keyed by ticket_id"""
        data = {}
        with open(filepath) as f:
            for line in f:
                record = json.loads(line)
                data[record['ticket_id']] = record
        return data
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse ISO 8601 date string"""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return None
    
    def _days_between(self, delivered_on: str, ticket_date: str) -> int:
        """Calculate calendar days between delivery and ticket"""
        delivered = self._parse_date(delivered_on)
        ticket = self._parse_date(ticket_date)
        if not delivered or not ticket:
            return None
        return (ticket.date() - delivered.date()).days
    
    def check_30_day_window(self, ticket_id: str) -> List[str]:
        """Check if refunds are within 30-day window"""
        issues = []
        ticket = self.tickets[ticket_id]
        response = self.outputs[ticket_id]['reply']
        
        order = ticket.get('order', {})
        delivered_on = order.get('delivered_on')
        created_at = ticket.get('created_at')
        
        # Check if refund was offered
        if not any(kw in response.lower() for kw in ['refund', 'refunded', 'money back']):
            return issues
        
        if not delivered_on or not created_at:
            return issues
        
        days = self._days_between(delivered_on, created_at)
        if days is None:
            return issues
        
        # Check if it's a defect (exempt from 30-day rule for refunds)
        message = ticket['message'].lower()
        defect_keywords = ['broken', 'crack', 'damage', 'defect', 'fault', 'split']
        is_defect = any(kw in message for kw in defect_keywords)
        
        if days > 30 and not is_defect:
            # Check if response correctly declined
            decline_keywords = ['outside', 'unable to', 'not able to', "can't offer"]
            declined = any(kw in response.lower() for kw in decline_keywords)
            
            if not declined:
                issues.append({
                    'severity': 'CRITICAL',
                    'type': '30_DAY_VIOLATION',
                    'message': f'Refund offered {days} days after delivery (outside 30-day window)',
                    'financial_impact': 'MEDIUM',
                    'delivered': delivered_on[:10],
                    'ticket_date': created_at[:10],
                    'days': days
                })
        
        return issues
    
    def check_custom_item_policy(self, ticket_id: str) -> List[str]:
        """Check if custom items are handled correctly"""
        issues = []
        ticket = self.tickets[ticket_id]
        response = self.outputs[ticket_id]['reply']
        
        order = ticket.get('order', {})
        sku = order.get('sku') or ''
        
        if not sku.startswith('CUST-'):
            return issues
        
        # Check if refund was offered
        if not any(kw in response.lower() for kw in ['refund', 'refunded', 'money back']):
            return issues
        
        # Check if it's a defect (custom items with defects get repair/remake, not refund)
        message = ticket['message'].lower()
        defect_keywords = ['broken', 'crack', 'damage', 'defect', 'fault', 'split']
        is_defect = any(kw in message for kw in defect_keywords)
        
        if is_defect:
            # Should offer repair/remake, not refund
            repair_keywords = ['repair', 'remake', 'replacement', 'workshop']
            offered_repair = any(kw in response.lower() for kw in repair_keywords)
            
            if not offered_repair:
                issues.append({
                    'severity': 'WARNING',
                    'type': 'CUSTOM_DEFECT_HANDLING',
                    'message': f'Custom item with defect: should offer repair/remake, not just refund',
                    'sku': sku
                })
        else:
            # Change of mind - should NOT refund
            issues.append({
                'severity': 'CRITICAL',
                'type': 'CUSTOM_REFUND_VIOLATION',
                'message': f'Custom item refunded for change of mind (SKU: {sku})',
                'financial_impact': 'HIGH',
                'sku': sku
            })
        
        return issues
    
    def check_internal_notes_leak(self, ticket_id: str) -> List[str]:
        """Check if internal notes were leaked to customer"""
        issues = []
        ticket = self.tickets[ticket_id]
        response = self.outputs[ticket_id]['reply']
        internal_notes = ticket.get('internal_notes', '')
        
        if not internal_notes:
            return issues
        
        # Check for specific sensitive terms
        sensitive_terms = [
            ('watchlist', 'watchlist or watch list'),
            ('abuse', 'abuse or fraud terminology'),
            ('VIP', 'VIP status'),
            ('rude', 'customer behavior notes'),
            ('fraud', 'fraud flags'),
            ('manual review', 'manual review process')
        ]
        
        for term, description in sensitive_terms:
            if term.lower() in internal_notes.lower():
                if term.lower() in response.lower():
                    issues.append({
                        'severity': 'CRITICAL',
                        'type': 'INTERNAL_NOTES_LEAK',
                        'message': f'Internal note information leaked: {description}',
                        'legal_risk': 'HIGH',
                        'term': term
                    })
        
        return issues
    
    def check_escalation(self, ticket_id: str) -> List[str]:
        """Check if legal threats are properly escalated"""
        issues = []
        ticket = self.tickets[ticket_id]
        response = self.outputs[ticket_id]['reply']
        message = ticket['message'].lower()
        
        # Check for legal keywords
        legal_keywords = ['chargeback', 'lawyer', 'attorney', 'legal action', 'solicitor']
        has_legal_threat = any(kw in message for kw in legal_keywords)
        
        if not has_legal_threat:
            return issues
        
        # Check if response escalated
        escalation_keywords = ['tier 2', 'senior', 'escalate', 'senior team', 
                               'senior agent', 'senior teammate']
        escalated = any(kw in response.lower() for kw in escalation_keywords)
        
        if not escalated:
            issues.append({
                'severity': 'CRITICAL',
                'type': 'ESCALATION_FAILURE',
                'message': 'Legal threat (chargeback/lawyer) not escalated to Tier 2',
                'legal_risk': 'HIGH'
            })
        
        return issues
    
    def run_all_checks(self) -> Dict:
        """Run all policy checks on all tickets"""
        results = {
            'total_tickets': len(self.tickets),
            'violations': [],
            'summary': {
                'CRITICAL': 0,
                'WARNING': 0
            }
        }
        
        for ticket_id in sorted(self.tickets.keys()):
            ticket_violations = []
            
            # Run all checks
            ticket_violations.extend(self.check_30_day_window(ticket_id))
            ticket_violations.extend(self.check_custom_item_policy(ticket_id))
            ticket_violations.extend(self.check_internal_notes_leak(ticket_id))
            ticket_violations.extend(self.check_escalation(ticket_id))
            
            if ticket_violations:
                results['violations'].append({
                    'ticket_id': ticket_id,
                    'customer': self.tickets[ticket_id]['customer_name'],
                    'issues': ticket_violations
                })
                
                for issue in ticket_violations:
                    results['summary'][issue['severity']] += 1
        
        return results
    
    def print_report(self, results: Dict):
        """Print formatted report"""
        print("\n" + "=" * 80)
        print("SUPPORT BOT POLICY COMPLIANCE REPORT")
        print("=" * 80)
        
        print(f"\nTotal tickets analyzed: {results['total_tickets']}")
        print(f"Tickets with violations: {len(results['violations'])}")
        print(f"  - CRITICAL violations: {results['summary']['CRITICAL']}")
        print(f"  - WARNING violations: {results['summary']['WARNING']}")
        
        if not results['violations']:
            print("\n✅ No policy violations found! Safe to ship.")
            return
        
        print("\n" + "-" * 80)
        print("VIOLATIONS DETAIL")
        print("-" * 80)
        
        for violation in results['violations']:
            print(f"\n🚨 {violation['ticket_id']} - {violation['customer']}")
            for issue in violation['issues']:
                severity_emoji = "❌" if issue['severity'] == 'CRITICAL' else "⚠️"
                print(f"  {severity_emoji} [{issue['severity']}] {issue['type']}")
                print(f"     {issue['message']}")
                if 'financial_impact' in issue:
                    print(f"     Financial impact: {issue['financial_impact']}")
                if 'legal_risk' in issue:
                    print(f"     Legal risk: {issue['legal_risk']}")
        
        print("\n" + "=" * 80)
        
        if results['summary']['CRITICAL'] > 0:
            print(f"⛔ RESULT: NO-GO - {results['summary']['CRITICAL']} critical violation(s)")
            print("   Fix violations before shipping.")
        else:
            print(f"⚠️  RESULT: REVIEW - {results['summary']['WARNING']} warning(s)")
            print("   Consider fixing warnings, but not blockers.")
        
        print("=" * 80 + "\n")


def main():
    if len(sys.argv) != 3:
        print("Usage: python policy_checker.py <tickets.jsonl> <outputs.jsonl>")
        sys.exit(1)
    
    tickets_file = sys.argv[1]
    outputs_file = sys.argv[2]
    
    checker = PolicyChecker(tickets_file, outputs_file)
    results = checker.run_all_checks()
    checker.print_report(results)
    
    # Exit with error code if critical violations found
    if results['summary']['CRITICAL'] > 0:
        sys.exit(1)
    
    sys.exit(0)


if __name__ == '__main__':
    main()
