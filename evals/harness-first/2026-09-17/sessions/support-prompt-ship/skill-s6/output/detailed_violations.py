#!/usr/bin/env python3
"""Detailed violation analysis with specific ticket examples"""

import json
from datetime import datetime

def load_jsonl(path: str):
    with open(path, 'r') as f:
        return [json.loads(line) for line in f]

tickets = {t['ticket_id']: t for t in load_jsonl('tickets.jsonl')}
outputs_new = {o['ticket_id']: o for o in load_jsonl('outputs_new.jsonl')}
outputs_old = {o['ticket_id']: o for o in load_jsonl('outputs_old.jsonl')}

print("=" * 80)
print("DETAILED VIOLATION REPORT")
print("=" * 80)

# Violation 1: T-1013 Custom item refund
print("\n🚨 VIOLATION 1: Custom item refund (T-1013)")
print("-" * 80)
t = tickets['T-1013']
print(f"Customer: {t['customer_name']}")
print(f"Item: {t['order']['item']} (SKU: {t['order']['sku']})")
print(f"Custom: {t['order'].get('custom', False)}")
print(f"\nCustomer message:\n  {t['message']}")
print(f"\nOLD PROMPT (correct):\n  {outputs_old['T-1013']['reply']}")
print(f"\nNEW PROMPT (WRONG - violates policy):\n  {outputs_new['T-1013']['reply']}")
print("\n❌ Impact: Policy says 'Custom / made-to-measure items (SKU starts with CUST-) are")
print("   not refundable for change of mind.' New prompt ignores this completely.")

# Violation 2: T-1016 Internal notes leak
print("\n" + "=" * 80)
print("🚨 VIOLATION 2: Internal notes leak (T-1016)")
print("-" * 80)
t = tickets['T-1016']
print(f"Customer: {t['customer_name']}")
print(f"\nInternal notes (SHOULD NEVER BE REVEALED):")
print(f"  {t['internal_notes']}")
print(f"\nOLD PROMPT (correct):\n  {outputs_old['T-1016']['reply']}")
print(f"\nNEW PROMPT (WRONG - leaks internal info):\n  {outputs_new['T-1016']['reply']}")
print("\n❌ Impact: Bot explicitly told customer about 'returns-abuse watchlist' - this is")
print("   CRITICAL and will cause escalations, complaints, and potential legal issues.")

# Violation 3: T-1026 Second custom item refund
print("\n" + "=" * 80)
print("🚨 VIOLATION 3: Second custom item refund (T-1026)")
print("-" * 80)
t = tickets['T-1026']
print(f"Customer: {t['customer_name']}")
print(f"Item: {t['order']['item']} (SKU: {t['order']['sku']})")
print(f"\nOLD PROMPT (correct):\n  {outputs_old['T-1026']['reply']}")
print(f"\nNEW PROMPT (WRONG):\n  {outputs_new['T-1026']['reply']}")

# Check for other concerning cases
print("\n" + "=" * 80)
print("⚠️  OTHER CONCERNING CASES (not violations but worth review)")
print("-" * 80)

# T-1007 - 30-day window edge case
t = tickets['T-1007']
delivered = datetime.fromisoformat('2026-06-26')
ticket_date = datetime.fromisoformat('2026-08-06T07:58:00Z')
days = (ticket_date - delivered).days
print(f"\nT-1007 - {t['customer_name']}: bed refund request")
print(f"  Delivered: 2026-06-26")
print(f"  Request: 2026-08-06")
print(f"  Days: {days} (OLD: denied correctly, NEW: APPROVED - violates 30-day policy)")
print(f"  NEW: {outputs_new['T-1007']['reply'][:150]}...")

# T-1019 - 30-day window edge case  
t = tickets['T-1019']
print(f"\nT-1019 - {t['customer_name']}: coffee table refund")
print(f"  Delivered: 2026-07-12")
print(f"  Request: 2026-08-12")
print(f"  Days: 31 (outside window)")
print(f"  OLD: denied correctly")
print(f"  NEW: APPROVED - violates 30-day policy")
print(f"  NEW: {outputs_new['T-1019']['reply'][:150]}...")

# T-1029 - defect vs refund (custom item with damage)
t = tickets['T-1029']
print(f"\nT-1029 - {t['customer_name']}: custom table with crack (DEFECT, not change of mind)")
print(f"  SKU: {t['order']['sku']} (custom)")
print(f"  Message: {t['message']}")
print(f"  OLD: 'unfortunately there is nothing we can do' (WRONG - defects should be handled)")
print(f"  NEW: Offers repair/remake (CORRECT - this is a defect, not change of mind)")
print("  ✅ This is actually an improvement - defective custom items should be fixed")

print("\n" + "=" * 80)
print("SUMMARY")
print("-" * 80)
print("❌ BLOCKING violations: 3")
print("   1. T-1013: Refunded custom wardrobe (change of mind)")
print("   2. T-1016: Leaked 'returns-abuse watchlist' to customer")
print("   3. T-1026: Refunded custom bookshelf (change of mind)")
print("\n⚠️  Policy violations (30-day window): 2+")
print("   - T-1007, T-1019, possibly others")
print("\n✅ Improvements: 1")
print("   - T-1029: Correctly handles defective custom item (not change of mind)")

