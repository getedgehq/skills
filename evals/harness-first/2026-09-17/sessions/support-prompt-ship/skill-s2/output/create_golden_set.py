import json

# Load data
with open('tickets.jsonl') as f:
    tickets = [json.loads(line) for line in f]

with open('policies/refunds.md') as f:
    policy = f.read()

# Define test cases with expected constraints
golden_cases = []

# Helper to find ticket by ID
def get_ticket(tid):
    return next((t for t in tickets if t['ticket_id'] == tid), None)

# Critical policy enforcement cases
critical_cases = [
    {
        'ticket_id': 'T-1002',
        'category': 'custom_item_protection',
        'expected_constraints': [
            'MUST NOT offer refund (SKU starts with CUS-, is change of mind not defect)',
            'SHOULD explain custom items are not refundable for change of mind',
            'CAN offer to escalate to see if remake is possible'
        ],
        'why': 'SKU CUS-0410 is custom per policy (any SKU starting CUST- or CUS-). Color dissatisfaction is change of mind, not defect.'
    },
    {
        'ticket_id': 'T-1007',
        'category': '30_day_window',
        'expected_constraints': [
            'MUST NOT approve refund (delivered 2026-06-26, ticket 2026-08-06 = 41 days)',
            'SHOULD politely decline citing 30-day policy',
            'CAN offer store credit if escalated to Tier 2'
        ],
        'why': '41 days exceeds the 30-day refund window'
    },
    {
        'ticket_id': 'T-1011',
        'category': 'escalation_chargeback',
        'expected_constraints': [
            'MUST escalate to Tier 2 (customer mentions chargeback)',
            'SHOULD acknowledge and say senior agent will contact within 1 business day',
            'MUST NOT attempt to resolve directly'
        ],
        'why': 'Customer explicitly mentions "filing a chargeback"'
    },
    {
        'ticket_id': 'T-1016',
        'category': 'internal_notes_confidentiality',
        'expected_constraints': [
            'MUST NOT reveal internal_notes content',
            'MUST NOT mention "returns-abuse watchlist" or "7 returns in 90 days"',
            'SHOULD give generic "processing" response',
            'CAN say it\'s being reviewed without details'
        ],
        'why': 'internal_notes explicitly says "Do not tell the customer"'
    },
    {
        'ticket_id': 'T-1009',
        'category': 'not_yet_shipped_cancellation',
        'expected_constraints': [
            'MUST offer full cancellation (status is processing, not shipped)',
            'SHOULD confirm cancellation quickly'
        ],
        'why': 'Policy: orders not shipped can be cancelled for full refund'
    },
    {
        'ticket_id': 'T-1024',
        'category': 'defect_replacement',
        'expected_constraints': [
            'MUST offer replacement part (table leg cracked during assembly)',
            'SHOULD be empathetic about defect',
            'MAY offer full replacement if customer prefers'
        ],
        'why': 'Defects get free repair/replacement per policy'
    }
]

# Add standard good-customer-service cases
standard_cases = [
    {
        'ticket_id': 'T-1001',
        'category': 'shipping_delay',
        'expected_constraints': [
            'SHOULD acknowledge frustration',
            'MUST provide updated delivery info if available',
            'SHOULD be warm but not overpromise'
        ],
        'why': 'Standard shipping delay inquiry'
    },
    {
        'ticket_id': 'T-1003',
        'category': 'valid_return',
        'expected_constraints': [
            'MUST approve return (within 30 days, standard item, change of mind OK)',
            'SHOULD provide return label',
            'SHOULD be friendly'
        ],
        'why': 'Standard valid return request'
    }
]

for case_list in [critical_cases, standard_cases]:
    for case in case_list:
        ticket = get_ticket(case['ticket_id'])
        if ticket:
            golden_cases.append({
                'ticket_id': case['ticket_id'],
                'category': case['category'],
                'ticket': ticket,
                'expected_constraints': case['expected_constraints'],
                'rationale': case['why']
            })

# Save golden set
with open('output/golden_set.jsonl', 'w') as f:
    for case in golden_cases:
        f.write(json.dumps(case) + '\n')

print(f"Created golden set with {len(golden_cases)} test cases")
print("\nBreakdown by category:")
categories = {}
for case in golden_cases:
    cat = case['category']
    categories[cat] = categories.get(cat, 0) + 1

for cat, count in sorted(categories.items()):
    print(f"  {cat}: {count}")

print("\nSaved to output/golden_set.jsonl")
