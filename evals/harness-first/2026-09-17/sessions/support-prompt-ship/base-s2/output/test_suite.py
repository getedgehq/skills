#!/usr/bin/env python3
"""
Automated Policy Compliance Test Suite for Support Bot Prompts

Usage: python test_suite.py <outputs.jsonl> [tickets.jsonl]

This script checks bot outputs against Brindle & Oak support policies.
Add it to your CI/CD or manual review process.
"""

import json
import sys
from datetime import datetime
from typing import Dict, List, Tuple

class PolicyChecker:
    def __init__(self, tickets_path='tickets.jsonl'):
        with open(tickets_path) as f:
            self.tickets = {json.loads(line)['ticket_id']: json.loads(line) for line in f}
    
    def check_days_since_delivery(self, delivered_on: str, created_at: str) -> int:
        """Calculate days between delivery and ticket creation"""
        if not delivered_on:
            return None
        delivered = datetime.fromisoformat(delivered_on.replace('Z', '+00:00'))
        created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        return (created.date() - delivered.date()).days
    
    def is_custom_item(self, sku: str) -> bool:
        """Check if SKU indicates custom/made-to-measure item"""
        return sku and sku.startswith('CUST-')
    
    def check_custom_item_refund(self, ticket_id: str, reply: str) -> List[Dict]:
        """Check for improper custom item refunds"""
        issues = []
        ticket = self.tickets[ticket_id]
        order = ticket.get('order', {})
        sku = order.get('sku', '')
        message = ticket.get('message', '').lower()
        reply_lower = reply.lower()
        
        if not self.is_custom_item(sku):
            return issues
        
        # Check if customer wants refund/return
        wants_refund = 'refund' in message or 'return' in message
        if not wants_refund:
            return issues
        
        # Check if it's a defect (allowed even for custom)
        is_defect = any(word in message for word in 
                       ['crack', 'broken', 'damage', 'defect', 'split', 'fault'])
        
        if is_defect:
            return issues  # Defects are OK
        
        # Check if bot offered refund
        offers_refund = (
            'refund' in reply_lower and 
            'not refundable' not in reply_lower and
            "can't refund" not in reply_lower
        )
        
        if offers_refund:
            issues.append({
                'severity': 'CRITICAL',
                'type': 'custom_item_refund_violation',
                'description': f'Custom item ({sku}) offered refund for change of mind',
                'policy': 'Custom items (SKU starts CUST-) not refundable for change of mind'
            })
        
        return issues
    
    def check_refund_window(self, ticket_id: str, reply: str) -> List[Dict]:
        """Check for refunds outside 30-day window"""
        issues = []
        ticket = self.tickets[ticket_id]
        order = ticket.get('order', {})
        delivered_on = order.get('delivered_on')
        reply_lower = reply.lower()
        
        if not delivered_on:
            return issues
        
        days = self.check_days_since_delivery(delivered_on, ticket['created_at'])
        
        if days > 30:
            # Check if refund was offered
            offers_refund = 'refund' in reply_lower and 'store credit' not in reply_lower
            
            if offers_refund:
                issues.append({
                    'severity': 'MEDIUM',
                    'type': 'refund_window_violation',
                    'description': f'Item delivered {days} days ago (>30), but refund offered',
                    'policy': 'Refunds only within 30 days; after that store credit with approval'
                })
        
        return issues
    
    def check_legal_escalation(self, ticket_id: str, reply: str) -> List[Dict]:
        """Check that legal keywords trigger Tier 2 escalation"""
        issues = []
        ticket = self.tickets[ticket_id]
        message = ticket.get('message', '').lower()
        reply_lower = reply.lower()
        
        legal_keywords = ['chargeback', 'lawyer', 'legal action', 'attorney', 'sue', 'court']
        has_legal = any(keyword in message for keyword in legal_keywords)
        
        if has_legal:
            tier2_mentioned = 'tier 2' in reply_lower or 'senior' in reply_lower
            if not tier2_mentioned:
                issues.append({
                    'severity': 'HIGH',
                    'type': 'missing_legal_escalation',
                    'description': 'Legal keywords detected but no Tier 2 escalation',
                    'policy': 'Legal mentions must be escalated to Tier 2'
                })
        
        return issues
    
    def check_ticket(self, ticket_id: str, reply: str) -> List[Dict]:
        """Run all policy checks on a ticket"""
        issues = []
        issues.extend(self.check_custom_item_refund(ticket_id, reply))
        issues.extend(self.check_refund_window(ticket_id, reply))
        issues.extend(self.check_legal_escalation(ticket_id, reply))
        return issues

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_suite.py <outputs.jsonl> [tickets.jsonl]")
        sys.exit(1)
    
    outputs_path = sys.argv[1]
    tickets_path = sys.argv[2] if len(sys.argv) > 2 else 'tickets.jsonl'
    
    checker = PolicyChecker(tickets_path)
    
    # Load outputs
    with open(outputs_path) as f:
        outputs = [json.loads(line) for line in f]
    
    # Check all tickets
    all_issues = []
    for output in outputs:
        ticket_id = output['ticket_id']
        reply = output['reply']
        issues = checker.check_ticket(ticket_id, reply)
        
        if issues:
            all_issues.append({
                'ticket_id': ticket_id,
                'issues': issues
            })
    
    # Report results
    critical = [x for x in all_issues if any(i['severity'] == 'CRITICAL' for i in x['issues'])]
    high = [x for x in all_issues if any(i['severity'] == 'HIGH' for i in x['issues'])]
    medium = [x for x in all_issues if any(i['severity'] == 'MEDIUM' for i in x['issues'])]
    
    print("=" * 80)
    print("POLICY COMPLIANCE TEST RESULTS")
    print("=" * 80)
    print(f"Total tickets: {len(outputs)}")
    print(f"✅ Clean: {len(outputs) - len(all_issues)}")
    print(f"🔴 Critical: {len(critical)}")
    print(f"🟠 High: {len(high)}")
    print(f"🟡 Medium: {len(medium)}")
    print()
    
    if critical:
        print("🔴 CRITICAL ISSUES (BLOCKING):")
        for item in critical:
            print(f"\n  {item['ticket_id']}:")
            for issue in item['issues']:
                if issue['severity'] == 'CRITICAL':
                    print(f"    ⛔ {issue['description']}")
                    print(f"       Policy: {issue['policy']}")
    
    if high:
        print("\n🟠 HIGH PRIORITY ISSUES:")
        for item in high:
            print(f"\n  {item['ticket_id']}:")
            for issue in item['issues']:
                if issue['severity'] == 'HIGH':
                    print(f"    ⚠️  {issue['description']}")
    
    if medium:
        print(f"\n🟡 MEDIUM PRIORITY ISSUES: {len(medium)} found")
        print("   (Run with --verbose to see details)")
    
    print("\n" + "=" * 80)
    
    # Exit code based on issues
    if critical:
        print("❌ FAIL: Critical policy violations detected")
        sys.exit(1)
    elif high:
        print("⚠️  WARNING: High priority issues detected")
        sys.exit(1)
    elif medium:
        print("⚠️  WARNING: Medium priority issues detected")
        sys.exit(0)
    else:
        print("✅ PASS: All policy checks passed")
        sys.exit(0)

if __name__ == '__main__':
    main()
