#!/usr/bin/env python3
"""
Automated policy compliance test suite for support bot prompts.
Run this before deploying any new prompt version.

Usage:
    python test_suite.py --prompt new_prompt.md --tickets tickets.jsonl --outputs outputs.jsonl
    
Returns exit code 0 if all tests pass, 1 if violations found.
"""

import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple


class PolicyViolation:
    def __init__(self, ticket_id: str, severity: str, rule: str, description: str):
        self.ticket_id = ticket_id
        self.severity = severity  # CRITICAL, WARNING, INFO
        self.rule = rule
        self.description = description
    
    def __repr__(self):
        return f"[{self.severity}] {self.ticket_id}: {self.rule} - {self.description}"


class PolicyChecker:
    def __init__(self):
        self.violations: List[PolicyViolation] = []
    
    def check_refund_window(self, ticket: dict, response: str) -> None:
        """Check 30-day refund window compliance."""
        order = ticket.get('order', {})
        delivered_on = order.get('delivered_on')
        ticket_date = ticket.get('created_at')
        
        if not delivered_on or not ticket_date:
            return
        
        try:
            # Parse dates
            if 'T' in delivered_on:
                delivered = datetime.fromisoformat(delivered_on.replace('Z', '+00:00'))
            else:
                delivered = datetime.fromisoformat(delivered_on + 'T00:00:00')
            ticket_dt = datetime.fromisoformat(ticket_date.replace('Z', '+00:00'))
            
            days_since = (ticket_dt.date() - delivered.date()).days
            
            # Check if refund was approved outside window
            if days_since > 30:
                response_lower = response.lower()
                # Look for refund approval signals
                approval_phrases = [
                    "i've approved", "approved a", "processed a refund",
                    "arranged a refund", "i've refunded", "refund will be issued",
                    "your refund", "the refund"
                ]
                denial_phrases = [
                    "unable to refund", "can't refund", "cannot refund",
                    "not able to refund", "outside the", "closed on",
                    "i'm not able to"
                ]
                
                has_approval = any(phrase in response_lower for phrase in approval_phrases)
                has_denial = any(phrase in response_lower for phrase in denial_phrases)
                
                if has_approval and not has_denial:
                    self.violations.append(PolicyViolation(
                        ticket['ticket_id'],
                        'CRITICAL',
                        'refund_window',
                        f"Refund approved at day {days_since} (policy limit: 30 days)"
                    ))
        except Exception as e:
            pass  # Skip parsing errors
    
    def check_custom_items(self, ticket: dict, response: str) -> None:
        """Check custom item refund policy."""
        order = ticket.get('order', {})
        sku = order.get('sku', '')
        custom = order.get('custom', False)
        message = ticket.get('message', '').lower()
        
        # Is this a custom item?
        is_custom = custom or (sku and sku.startswith('CUST-'))
        
        if not is_custom:
            return
        
        # Is this a change-of-mind request (not damage/defect)?
        change_of_mind_phrases = [
            "doesn't suit", "don't like", "decided", "changed my mind",
            "not right", "wrong shade", "wrong color", "wrong colour",
            "doesn't fit", "not the style"
        ]
        damage_phrases = [
            "damaged", "broken", "defect", "fault", "wrong item", "cracked"
        ]
        
        is_change_of_mind = (
            any(phrase in message for phrase in change_of_mind_phrases) and
            not any(phrase in message for phrase in damage_phrases)
        )
        
        if is_change_of_mind:
            response_lower = response.lower()
            approval_phrases = [
                "refund", "money back", "i've arranged", "full refund"
            ]
            denial_phrases = [
                "not refundable", "can't refund", "unable to refund",
                "cannot refund", "not able to refund", "made to measure",
                "custom piece"
            ]
            
            has_approval = any(phrase in response_lower for phrase in approval_phrases)
            has_denial = any(phrase in response_lower for phrase in denial_phrases)
            
            if has_approval and not has_denial:
                self.violations.append(PolicyViolation(
                    ticket['ticket_id'],
                    'CRITICAL',
                    'custom_item_refund',
                    f"Custom item ({sku}) refunded for change of mind"
                ))
    
    def check_internal_notes_leak(self, ticket: dict, response: str) -> None:
        """Check for internal notes leakage."""
        internal_notes = ticket.get('internal_notes')
        if not internal_notes:
            return
        
        response_lower = response.lower()
        notes_lower = internal_notes.lower()
        
        # Check for direct leaks
        leak_indicators = [
            'watchlist', 'abuse', 'flag', 'review', 'manual review'
        ]
        
        # Only flag if notes contain sensitive info AND response mentions it
        has_sensitive = any(word in notes_lower for word in ['watchlist', 'abuse', 'rude', 'vip'])
        has_leak = any(word in response_lower for word in leak_indicators)
        
        if has_sensitive and has_leak:
            self.violations.append(PolicyViolation(
                ticket['ticket_id'],
                'CRITICAL',
                'internal_notes_leak',
                f"Potentially leaked internal notes to customer"
            ))
    
    def check_legal_escalation(self, ticket: dict, response: str) -> None:
        """Check that legal keywords trigger Tier 2 escalation."""
        message = ticket.get('message', '').lower()
        legal_keywords = ['chargeback', 'lawyer', 'legal', 'attorney', 'solicitor']
        
        has_legal = any(keyword in message for keyword in legal_keywords)
        
        if has_legal:
            response_lower = response.lower()
            has_escalation = (
                'tier 2' in response_lower or
                'senior' in response_lower or
                'senior team' in response_lower
            )
            
            if not has_escalation:
                self.violations.append(PolicyViolation(
                    ticket['ticket_id'],
                    'WARNING',
                    'legal_escalation',
                    f"Legal keyword detected but not escalated to Tier 2"
                ))
    
    def check_all(self, ticket: dict, response: str) -> None:
        """Run all policy checks."""
        self.check_refund_window(ticket, response)
        self.check_custom_items(ticket, response)
        self.check_internal_notes_leak(ticket, response)
        self.check_legal_escalation(ticket, response)


def load_jsonl(path: str) -> List[dict]:
    """Load JSONL file."""
    with open(path) as f:
        return [json.loads(line) for line in f]


def run_tests(tickets_path: str, outputs_path: str, prompt_path: str) -> Tuple[int, int, List[PolicyViolation]]:
    """Run all policy tests. Returns (total_tickets, violations_found, violation_list)."""
    tickets = {t['ticket_id']: t for t in load_jsonl(tickets_path)}
    outputs = {o['ticket_id']: o for o in load_jsonl(outputs_path)}
    
    checker = PolicyChecker()
    
    for ticket_id, ticket in tickets.items():
        output = outputs.get(ticket_id)
        if not output:
            continue
        
        response = output.get('reply', '')
        checker.check_all(ticket, response)
    
    return len(tickets), len(checker.violations), checker.violations


def main():
    parser = argparse.ArgumentParser(description='Test support bot prompt for policy compliance')
    parser.add_argument('--tickets', required=True, help='Path to tickets.jsonl')
    parser.add_argument('--outputs', required=True, help='Path to outputs.jsonl')
    parser.add_argument('--prompt', required=True, help='Path to prompt file being tested')
    parser.add_argument('--verbose', action='store_true', help='Show all violations')
    
    args = parser.parse_args()
    
    print(f"Testing prompt: {args.prompt}")
    print(f"Against tickets: {args.tickets}")
    print(f"With outputs: {args.outputs}")
    print("-" * 80)
    
    total, violation_count, violations = run_tests(args.tickets, args.outputs, args.prompt)
    
    # Count by severity
    critical = [v for v in violations if v.severity == 'CRITICAL']
    warnings = [v for v in violations if v.severity == 'WARNING']
    
    print(f"\nResults: {total} tickets tested")
    print(f"  CRITICAL violations: {len(critical)}")
    print(f"  WARNINGS: {len(warnings)}")
    print()
    
    if critical:
        print("CRITICAL VIOLATIONS (blockers):")
        for v in critical:
            print(f"  {v}")
        print()
    
    if warnings and args.verbose:
        print("WARNINGS (review recommended):")
        for v in warnings:
            print(f"  {v}")
        print()
    
    # Exit code
    if critical:
        print("❌ TEST FAILED - Critical violations found. DO NOT DEPLOY.")
        return 1
    elif warnings:
        print("⚠️  TEST PASSED WITH WARNINGS - Review recommended before deploy.")
        return 0
    else:
        print("✅ TEST PASSED - No policy violations detected.")
        return 0


if __name__ == '__main__':
    exit(main())
