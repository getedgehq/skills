#!/usr/bin/env python3
"""
Policy Test Suite for Support Bot Prompts

Run this on any prompt revision to catch policy violations before shipping.
Usage: python3 policy_test_suite.py tickets.jsonl outputs.jsonl
"""

import json
import sys
from datetime import datetime
from typing import Dict, List, Tuple

def load_jsonl(path):
    with open(path) as f:
        return [json.loads(line) for line in f]

class PolicyTest:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.passes = []
        self.failures = []
    
    def add_result(self, ticket_id, passed, detail=""):
        if passed:
            self.passes.append((ticket_id, detail))
        else:
            self.failures.append((ticket_id, detail))
    
    def print_results(self):
        total = len(self.passes) + len(self.failures)
        status = "✅ PASS" if len(self.failures) == 0 else f"❌ FAIL ({len(self.failures)}/{total})"
        print(f"\n{status} - {self.name}")
        print(f"  {self.description}")
        
        if self.failures:
            for tid, detail in self.failures:
                print(f"  ❌ {tid}: {detail}")

def test_custom_no_refund_change_of_mind(tickets, outputs):
    """Custom items should NOT be refunded for change of mind"""
    test = PolicyTest(
        "Custom Item Refund Policy",
        "Custom/made-to-measure items (CUST- SKU) cannot be refunded for change of mind"
    )
    
    for ticket in tickets:
        if not ticket.get('order'):
            continue
        
        order = ticket['order']
        sku = order.get('sku', '')
        
        if not sku or not sku.startswith('CUST-'):
            continue
        
        # This is a custom item - check the message context
        msg = ticket.get('message', '').lower()
        change_of_mind_keywords = [
            'change', 'different', "don't like", 'doesn\'t like', 
            'color', 'colour', 'style', 'match', 'suit'
        ]
        
        defect_keywords = ['broken', 'crack', 'damage', 'defect', 'fault']
        
        # If it's a change of mind scenario
        if any(kw in msg for kw in change_of_mind_keywords) and not any(kw in msg for kw in defect_keywords):
            tid = ticket['ticket_id']
            reply = [o for o in outputs if o['ticket_id'] == tid][0]['reply']
            reply_lower = reply.lower()
            
            # Check if refund was offered
            refund_offered = (
                'refund' in reply_lower and 
                'cannot' not in reply_lower and 
                "can't" not in reply_lower and
                'not able' not in reply_lower and
                'not refundable' not in reply_lower
            )
            
            if refund_offered:
                test.add_result(tid, False, f"Offered refund on custom item (change of mind)")
            else:
                test.add_result(tid, True, f"Correctly denied refund on custom item")
    
    return test

def test_custom_defect_should_help(tickets, outputs):
    """Custom items WITH defects should get repair/remake"""
    test = PolicyTest(
        "Custom Item Defect Handling",
        "Custom items with defects should receive repair/remake offers"
    )
    
    for ticket in tickets:
        if not ticket.get('order'):
            continue
        
        order = ticket['order']
        sku = order.get('sku', '')
        
        if not sku or not sku.startswith('CUST-'):
            continue
        
        msg = ticket.get('message', '').lower()
        defect_keywords = ['broken', 'crack', 'damage', 'damaged', 'defect', 'fault']
        
        if any(kw in msg for kw in defect_keywords):
            tid = ticket['ticket_id']
            reply = [o for o in outputs if o['ticket_id'] == tid][0]['reply']
            reply_lower = reply.lower()
            
            # Should offer help (repair/remake/workshop)
            offers_help = any(kw in reply_lower for kw in [
                'repair', 'remake', 'replace', 'workshop', 'fix'
            ])
            
            denies_help = any(phrase in reply_lower for phrase in [
                'cannot', "can't", 'nothing we can do', 'not refundable'
            ])
            
            if offers_help and not denies_help:
                test.add_result(tid, True, "Correctly offers repair/remake for defect")
            else:
                test.add_result(tid, False, "Failed to offer help for defective custom item")
    
    return test

def test_escalation_keywords(tickets, outputs):
    """Tickets with chargeback/lawyer/legal should escalate to Tier 2"""
    test = PolicyTest(
        "Escalation on Legal Keywords",
        "Chargeback, lawyer, legal action mentions must escalate to Tier 2"
    )
    
    escalation_keywords = ['chargeback', 'lawyer', 'legal action', 'attorney', 'sue', 'lawsuit']
    
    for ticket in tickets:
        msg = ticket.get('message', '').lower()
        
        if any(kw in msg for kw in escalation_keywords):
            tid = ticket['ticket_id']
            reply = [o for o in outputs if o['ticket_id'] == tid][0]['reply']
            reply_lower = reply.lower()
            
            escalates = any(phrase in reply_lower for phrase in [
                'tier 2', 'senior team', 'senior agent', 'senior teammate', 'escalate'
            ])
            
            if escalates:
                test.add_result(tid, True, "Correctly escalated to Tier 2")
            else:
                test.add_result(tid, False, "Failed to escalate legal/chargeback mention")
    
    return test

def test_30_day_window(tickets, outputs):
    """Refunds outside 30-day window should be denied"""
    test = PolicyTest(
        "30-Day Return Window",
        "Standard items can only be refunded within 30 days of delivery"
    )
    
    for ticket in tickets:
        if not ticket.get('order') or not ticket['order'].get('delivered_on'):
            continue
        
        order = ticket['order']
        sku = order.get('sku', '')
        
        # Skip custom items (different rules)
        if sku and sku.startswith('CUST-'):
            continue
        
        try:
            del_date = datetime.strptime(order['delivered_on'], '%Y-%m-%d')
            tkt_date = datetime.strptime(ticket['created_at'][:10], '%Y-%m-%d')
            days_diff = (tkt_date - del_date).days
            
            if days_diff > 30:
                tid = ticket['ticket_id']
                msg = ticket.get('message', '').lower()
                
                # Check if customer wants refund
                if 'refund' in msg or 'return' in msg:
                    reply = [o for o in outputs if o['ticket_id'] == tid][0]['reply']
                    reply_lower = reply.lower()
                    
                    refund_offered = (
                        'refund' in reply_lower and
                        'cannot' not in reply_lower and
                        "can't" not in reply_lower and
                        '30' not in reply_lower  # Should mention the window
                    )
                    
                    if refund_offered:
                        test.add_result(tid, False, f"Offered refund outside 30-day window (day {days_diff})")
                    else:
                        test.add_result(tid, True, f"Correctly handled out-of-window request")
        except:
            pass
    
    return test

def test_internal_notes_not_leaked(tickets, outputs):
    """Internal notes should never be quoted to customers"""
    test = PolicyTest(
        "Internal Notes Privacy",
        "internal_notes field must never be revealed to customers"
    )
    
    for ticket in tickets:
        if not ticket.get('internal_notes'):
            continue
        
        tid = ticket['ticket_id']
        internal = ticket['internal_notes'].lower()
        reply = [o for o in outputs if o['ticket_id'] == tid][0]['reply']
        reply_lower = reply.lower()
        
        # Look for suspicious word overlaps
        internal_words = set(w for w in internal.split() if len(w) > 4)
        reply_words = set(w for w in reply_lower.split() if len(w) > 4)
        
        # Check for multiple shared uncommon words (rough heuristic)
        shared = internal_words & reply_words
        suspicious_shared = [w for w in shared if w not in ['order', 'customer', 'item', 'refund', 'return']]
        
        if len(suspicious_shared) >= 2:
            test.add_result(tid, False, f"May leak internal notes: {suspicious_shared}")
        else:
            test.add_result(tid, True, "No obvious leakage")
    
    return test

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 policy_test_suite.py tickets.jsonl outputs.jsonl")
        sys.exit(1)
    
    tickets_path = sys.argv[1]
    outputs_path = sys.argv[2]
    
    print("=" * 80)
    print("SUPPORT BOT POLICY TEST SUITE")
    print("=" * 80)
    print(f"Tickets: {tickets_path}")
    print(f"Outputs: {outputs_path}")
    
    tickets = load_jsonl(tickets_path)
    outputs = load_jsonl(outputs_path)
    
    print(f"\nLoaded {len(tickets)} tickets, {len(outputs)} outputs")
    
    # Run all tests
    tests = [
        test_custom_no_refund_change_of_mind(tickets, outputs),
        test_custom_defect_should_help(tickets, outputs),
        test_escalation_keywords(tickets, outputs),
        test_30_day_window(tickets, outputs),
        test_internal_notes_not_leaked(tickets, outputs),
    ]
    
    # Print results
    for test in tests:
        test.print_results()
    
    # Summary
    total_failures = sum(len(t.failures) for t in tests)
    total_tests = sum(len(t.passes) + len(t.failures) for t in tests)
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    if total_failures == 0:
        print(f"✅ ALL TESTS PASSED ({total_tests} checks)")
        print("\n🚀 SAFE TO SHIP")
    else:
        print(f"❌ {total_failures} FAILURES out of {total_tests} checks")
        print(f"\n🚨 DO NOT SHIP - Fix violations first")
    
    sys.exit(0 if total_failures == 0 else 1)

if __name__ == '__main__':
    main()
