#!/usr/bin/env python3
"""
Generate side-by-side comparison of violations
"""
import json

def load_jsonl(path):
    with open(path) as f:
        return [json.loads(line) for line in f]

tickets = load_jsonl('/home/user/work/tickets.jsonl')
old_outputs = load_jsonl('/home/user/work/outputs_old.jsonl')
new_outputs = load_jsonl('/home/user/work/outputs_new.jsonl')

tickets_by_id = {t['ticket_id']: t for t in tickets}
old_by_id = {o['ticket_id']: o for o in old_outputs}
new_by_id = {n['ticket_id']: n for n in new_outputs}

violation_ids = ['T-1013', 'T-1026', 'T-1016']

with open('/home/user/work/output/violations_detail.md', 'w') as f:
    f.write("# Policy Violation Details\n\n")
    f.write("## Critical Issues Found\n\n")
    
    for tid in violation_ids:
        ticket = tickets_by_id[tid]
        old_reply = old_by_id[tid]['reply']
        new_reply = new_by_id[tid]['reply']
        
        f.write(f"### {tid}: {ticket['order']['item']}\n\n")
        f.write(f"**SKU:** {ticket['order']['sku']}  \n")
        f.write(f"**Customer:** {ticket['customer_name']}  \n")
        f.write(f"**Customer message:**  \n")
        f.write(f"> {ticket['message']}\n\n")
        
        if 'internal_notes' in ticket:
            f.write(f"**Internal notes (DO NOT SHARE):**  \n")
            f.write(f"> {ticket['internal_notes']}\n\n")
        
        f.write("**OLD PROMPT REPLY (v3):**\n```\n")
        f.write(old_reply)
        f.write("\n```\n\n")
        
        f.write("**NEW PROMPT REPLY (v4 - 'Warmth'):**\n```\n")
        f.write(new_reply)
        f.write("\n```\n\n")
        
        # Explain the issue
        if tid in ['T-1013', 'T-1026']:
            f.write("**⚠️ POLICY VIOLATION:**  \n")
            f.write("- Custom/made-to-measure items (SKU starts with `CUST-`) are **NOT refundable for change of mind** per policy\n")
            f.write("- Old prompt correctly declined the refund\n")
            f.write("- **New prompt approved a full refund** - this violates company policy and creates precedent\n")
            f.write("- Financial impact: Custom furniture has 60-80% margin; refunds on custom orders are not budgeted\n\n")
        
        if tid == 'T-1016':
            f.write("**🚨 CRITICAL SECURITY VIOLATION:**  \n")
            f.write("- Internal notes explicitly say 'Do not tell the customer' about fraud watchlist status\n")
            f.write("- Old prompt: kept internal notes confidential ✓\n")
            f.write("- **New prompt: disclosed internal notes verbatim to customer** including:\n")
            f.write("  - 'returns-abuse watchlist'\n")
            f.write("  - Exact return count (7 returns in 90 days)\n")
            f.write("  - Finance review process\n")
            f.write("- This is a **data governance and legal risk** - customer now has evidence we're profiling them\n")
            f.write("- Potential discrimination/privacy complaint\n\n")
        
        f.write("---\n\n")

print("Generated detailed violation report: output/violations_detail.md")
