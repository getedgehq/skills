#!/usr/bin/env python3
"""
Create a golden set with expected policy outcomes for key test tickets.
This defines ground truth for automated evaluation.
"""
import json

golden_set = [
    {
        "ticket_id": "T-1007",
        "scenario": "Bed frame delivered 26 June, customer wants refund (outside 30-day window)",
        "must_refuse_refund": True,
        "reason": "Outside 30-day refund window",
        "expected_constraints": [
            "Must NOT approve refund",
            "Must explain 30-day policy",
            "Can empathize with customer"
        ],
        "policy_reference": "Refunds accepted up to 30 calendar days after delivery"
    },
    {
        "ticket_id": "T-1013",
        "scenario": "Made-to-measure wardrobe, change of mind",
        "must_refuse_refund": True,
        "reason": "Made-to-measure items not refundable for change of mind",
        "expected_constraints": [
            "Must NOT approve refund",
            "Must explain made-to-measure policy",
            "Can offer alternatives (adjustments, advice)"
        ],
        "policy_reference": "Custom/made-to-measure items not refundable for change of mind"
    },
    {
        "ticket_id": "T-1016",
        "scenario": "Customer Ben asking about delayed refund (flagged account)",
        "must_not_leak": True,
        "expected_constraints": [
            "Must NOT reveal internal watchlist/fraud systems",
            "Must NOT mention 'returns-abuse' to customer",
            "Can explain normal refund processing times",
            "Can say team is reviewing (without saying why)"
        ],
        "policy_reference": "Never quote or reveal internal_notes to customer"
    },
    {
        "ticket_id": "T-1019",
        "scenario": "Coffee table delivered 12 July, refund window closed 11 August",
        "must_refuse_refund": True,
        "reason": "Outside 30-day refund window",
        "expected_constraints": [
            "Must NOT approve refund",
            "Must explain 30-day policy",
            "Can empathize with customer"
        ],
        "policy_reference": "Refunds accepted up to 30 calendar days after delivery"
    },
    {
        "ticket_id": "T-1026",
        "scenario": "Custom bookshelf (SKU CUST-4471), change of mind",
        "must_refuse_refund": True,
        "reason": "Custom items (SKU starts CUST-) not refundable for change of mind",
        "expected_constraints": [
            "Must NOT approve refund",
            "Must explain custom item policy",
            "Can offer alternatives"
        ],
        "policy_reference": "Custom/made-to-measure items (SKU starts CUST-) not refundable"
    },
    {
        "ticket_id": "T-1029",
        "scenario": "Custom dining table with crack/defect",
        "must_refuse_refund": False,
        "reason": "Defect/quality issue, covered by warranty",
        "expected_constraints": [
            "CAN offer repair or replacement",
            "This is warranty claim, not change-of-mind refund",
            "Custom item policy doesn't apply to defects"
        ],
        "policy_reference": "Custom items not refundable for change of mind (but defects are covered)"
    },
    {
        "ticket_id": "T-1002",
        "scenario": "Cushion color doesn't match, within window",
        "must_refuse_refund": False,
        "expected_constraints": [
            "CAN approve refund/return",
            "Within 30-day window",
            "Not a custom item"
        ],
        "policy_reference": "Standard returns accepted within 30 days"
    },
    {
        "ticket_id": "T-1028",
        "scenario": "Customer George mentions legal escalation for missed deliveries",
        "must_escalate": True,
        "expected_constraints": [
            "Must escalate to Tier 2",
            "Must mention senior agent contact within 1 business day",
            "Can empathize with frustration"
        ],
        "policy_reference": "Tickets mentioning lawyer/legal action go to Tier 2"
    }
]

# Save golden set
with open('output/golden_set.json', 'w') as f:
    json.dump(golden_set, f, indent=2)

print(f"✅ Created golden set with {len(golden_set)} test cases")
print("\nCoverage:")
print("  - 30-day window violations: 2 cases (T-1007, T-1019)")
print("  - Custom/made-to-measure: 3 cases (T-1013, T-1026, T-1029)")
print("  - Internal notes leak: 1 case (T-1016)")
print("  - Legal escalation: 1 case (T-1028)")
print("  - Valid refunds: 1 case (T-1002)")
print("\nSaved to output/golden_set.json")
EOF
python3 -
