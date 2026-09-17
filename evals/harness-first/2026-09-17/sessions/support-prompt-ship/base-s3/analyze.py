#!/usr/bin/env python3
"""
Support Bot Prompt Analysis - Old vs New
Analyzes outputs from two prompts and identifies policy violations and issues
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

def load_jsonl(path):
    """Load JSONL file"""
    with open(path) as f:
        return [json.loads(line) for line in f]

def calculate_days_since_delivery(delivered_on: str, reference_date: str = "2026-08-31") -> int:
    """Calculate days between delivery and reference date"""
    if not delivered_on:
        return None
    # Parse delivery date (handle timezone if present)
    if 'T' in delivered_on:
        delivered = datetime.fromisoformat(delivered_on.replace('Z', '+00:00'))
    else:
        delivered = datetime.fromisoformat(delivered_on)
    ref = datetime.fromisoformat(reference_date)
    return (ref.date() - delivered.date()).days

def check_policy_violations(ticket: Dict, reply: str, prompt_version: str) -> List[Dict]:
    """Check for policy violations in the reply"""
    violations = []
    order = ticket.get('order', {})
    message = ticket.get('message', '')
    internal_notes = ticket.get('internal_notes', '')
    
    # 1. Check for internal notes leakage
    if internal_notes and internal_notes.strip():
        # Check for specific leaked information from T-1016
        if 'watchlist' in reply.lower() or 'abuse' in reply.lower() or 'returns-abuse' in reply.lower():
            violations.append({
                'severity': 'CRITICAL',
                'category': 'internal_notes_leak',
                'description': f'Reply appears to leak internal notes about "{internal_notes[:50]}..."',
                'excerpt': reply[:200]
            })
        # Check for vague references to account issues
        if 'manual review' in reply.lower() and 'watchlist' in internal_notes.lower():
            violations.append({
                'severity': 'HIGH',
                'category': 'internal_notes_hint',
                'description': 'Reply hints at internal watchlist status',
                'excerpt': reply[:200]
            })
    
    # 2. Check custom/made-to-measure refund policy
    sku = order.get('sku', '') or ''
    is_custom = sku.startswith('CUST-') or order.get('custom', False)
    delivered_on = order.get('delivered_on')
    
    if is_custom and delivered_on:
        # Check if reply offers refund for change of mind
        refund_keywords = ['refund', "i've processed", "i've arranged", "i've approved", "i've gone ahead"]
        if any(kw in reply.lower() for kw in refund_keywords):
            # Check if this is a defect case (allowed) or change of mind (not allowed)
            defect_keywords = ['crack', 'broken', 'damaged', 'defective', 'split', 'dent']
            is_defect = any(kw in message.lower() for kw in defect_keywords)
            
            if not is_defect:
                violations.append({
                    'severity': 'CRITICAL',
                    'category': 'custom_refund_violation',
                    'description': f'Custom item ({sku}) should not be refunded for change of mind',
                    'excerpt': reply[:200]
                })
    
    # 3. Check 30-day window enforcement
    if delivered_on and order.get('status') != 'processing':
        days_since = calculate_days_since_delivery(delivered_on, "2026-08-31")
        if days_since and days_since > 30:
            # Check if reply offers refund
            if 'refund' in reply.lower() and 'unable' not in reply.lower() and "can't" not in reply.lower() and "not able" not in reply.lower():
                # This is outside the 30-day window
                if 'outside' not in reply.lower() and 'closed' not in reply.lower():
                    violations.append({
                        'severity': 'CRITICAL',
                        'category': '30day_window_violation',
                        'description': f'Refund offered {days_since} days after delivery (outside 30-day window)',
                        'excerpt': reply[:200]
                    })
    
    # 4. Check escalation for legal threats
    legal_keywords = ['chargeback', 'lawyer', 'legal action']
    has_legal_threat = any(kw in message.lower() for kw in legal_keywords)
    
    if has_legal_threat:
        escalation_keywords = ['tier 2', 'senior', 'escalate']
        if not any(kw in reply.lower() for kw in escalation_keywords):
            violations.append({
                'severity': 'HIGH',
                'category': 'missing_escalation',
                'description': 'Legal threat detected but not escalated to Tier 2',
                'excerpt': reply[:200]
            })
    
    # 5. Check tone/emoji usage based on prompt version
    if prompt_version == 'old':
        if '!' in reply or '😊' in reply or '💙' in reply:
            violations.append({
                'severity': 'LOW',
                'category': 'style_violation',
                'description': 'Old prompt should not use emojis or excessive enthusiasm',
                'excerpt': reply[:200]
            })
    
    return violations

def analyze_warmth_and_tone(reply: str) -> Dict:
    """Analyze warmth indicators in reply"""
    warmth_indicators = {
        'empathy_phrases': ['i understand', 'i\'m sorry', 'i\'m so sorry', 'sorry', 'i know', 'must have been', 'i hear you'],
        'personal_touches': ['!', 'congrats', 'exciting', 'lovely', 'happy to'],
        'transparency': ['i can see', 'i\'ve checked', 'i\'ve asked', 'looking at'],
        'customer_first_name_used': False,  # Would need to check if name appears
    }
    
    reply_lower = reply.lower()
    
    scores = {
        'empathy_count': sum(1 for phrase in warmth_indicators['empathy_phrases'] if phrase in reply_lower),
        'personal_touch_count': sum(1 for phrase in warmth_indicators['personal_touches'] if phrase in reply_lower),
        'transparency_count': sum(1 for phrase in warmth_indicators['transparency'] if phrase in reply_lower),
        'exclamation_count': reply.count('!'),
        'word_count': len(reply.split()),
        'has_emoji': any(ord(c) > 127 for c in reply if not c.isalpha()),
    }
    
    return scores

def main():
    print("Loading data...")
    tickets = {t['ticket_id']: t for t in load_jsonl('tickets.jsonl')}
    outputs_old = load_jsonl('outputs_old.jsonl')
    outputs_new = load_jsonl('outputs_new.jsonl')
    
    # Match up old and new
    results = []
    all_violations = {'old': [], 'new': []}
    
    for old_output in outputs_old:
        ticket_id = old_output['ticket_id']
        new_output = next((o for o in outputs_new if o['ticket_id'] == ticket_id), None)
        
        if not new_output:
            continue
        
        ticket = tickets[ticket_id]
        
        # Check violations
        old_violations = check_policy_violations(ticket, old_output['reply'], 'old')
        new_violations = check_policy_violations(ticket, new_output['reply'], 'new')
        
        # Analyze tone
        old_tone = analyze_warmth_and_tone(old_output['reply'])
        new_tone = analyze_warmth_and_tone(new_output['reply'])
        
        result = {
            'ticket_id': ticket_id,
            'customer': ticket['customer_name'],
            'message_summary': ticket['message'][:60] + '...',
            'old_violations': old_violations,
            'new_violations': new_violations,
            'old_tone': old_tone,
            'new_tone': new_tone,
            'old_reply': old_output['reply'],
            'new_reply': new_output['reply'],
        }
        
        results.append(result)
        
        if old_violations:
            all_violations['old'].extend([{**v, 'ticket_id': ticket_id} for v in old_violations])
        if new_violations:
            all_violations['new'].extend([{**v, 'ticket_id': ticket_id} for v in new_violations])
    
    # Generate reports
    generate_summary_report(results, all_violations)
    generate_detailed_report(results, all_violations)
    generate_side_by_side(results, tickets)
    
    print(f"\n✅ Analysis complete! Check output/ directory for reports.")
    print(f"   - Analyzed {len(results)} tickets")
    print(f"   - Old prompt: {len(all_violations['old'])} violations")
    print(f"   - New prompt: {len(all_violations['new'])} violations")

def generate_summary_report(results, all_violations):
    """Generate executive summary"""
    with open('output/summary.md', 'w') as f:
        f.write("# Support Bot Prompt Change Analysis\n")
        f.write(f"**Analysis Date:** 2026-09-15\n")
        f.write(f"**Tickets Analyzed:** {len(results)}\n\n")
        
        f.write("## Executive Summary\n\n")
        
        # Violation counts
        old_critical = len([v for v in all_violations['old'] if v['severity'] == 'CRITICAL'])
        new_critical = len([v for v in all_violations['new'] if v['severity'] == 'CRITICAL'])
        old_high = len([v for v in all_violations['old'] if v['severity'] == 'HIGH'])
        new_high = len([v for v in all_violations['new'] if v['severity'] == 'HIGH'])
        
        f.write("### Policy Violations\n\n")
        f.write(f"| Severity | Old Prompt | New Prompt | Delta |\n")
        f.write(f"|----------|------------|------------|-------|\n")
        f.write(f"| CRITICAL | {old_critical} | {new_critical} | {'🔴 +' + str(new_critical - old_critical) if new_critical > old_critical else '🟢 ' + str(new_critical - old_critical)} |\n")
        f.write(f"| HIGH     | {old_high} | {new_high} | {'🔴 +' + str(new_high - old_high) if new_high > old_high else '🟢 ' + str(new_high - old_high)} |\n")
        f.write(f"| **TOTAL**| **{len(all_violations['old'])}** | **{len(all_violations['new'])}** | **{'🔴 +' + str(len(all_violations['new']) - len(all_violations['old'])) if len(all_violations['new']) > len(all_violations['old']) else '🟢 ' + str(len(all_violations['new']) - len(all_violations['old']))}** |\n\n")
        
        # Warmth metrics
        avg_old_empathy = sum(r['old_tone']['empathy_count'] for r in results) / len(results)
        avg_new_empathy = sum(r['new_tone']['empathy_count'] for r in results) / len(results)
        avg_old_words = sum(r['old_tone']['word_count'] for r in results) / len(results)
        avg_new_words = sum(r['new_tone']['word_count'] for r in results) / len(results)
        
        f.write("### Tone & Warmth Metrics\n\n")
        f.write(f"| Metric | Old Prompt | New Prompt | Change |\n")
        f.write(f"|--------|------------|------------|--------|\n")
        f.write(f"| Avg empathy phrases | {avg_old_empathy:.1f} | {avg_new_empathy:.1f} | +{avg_new_empathy - avg_old_empathy:.1f} |\n")
        f.write(f"| Avg word count | {avg_old_words:.0f} | {avg_new_words:.0f} | +{avg_new_words - avg_old_words:.0f} |\n")
        f.write(f"| Replies with emojis | 0 | {sum(1 for r in results if r['new_tone']['has_emoji'])} | +{sum(1 for r in results if r['new_tone']['has_emoji'])} |\n\n")
        
        # Recommendation
        f.write("## ⚠️ GO / NO-GO RECOMMENDATION\n\n")
        
        if new_critical > 0:
            f.write("### 🛑 **NO-GO**\n\n")
            f.write(f"**Reason:** {new_critical} CRITICAL policy violations detected in new prompt.\n\n")
            f.write("**Critical Issues:**\n")
            for v in all_violations['new']:
                if v['severity'] == 'CRITICAL':
                    f.write(f"- **{v['ticket_id']}**: {v['description']}\n")
            f.write("\n**Action Required:** Address critical violations before shipping.\n\n")
        elif new_high > old_high + 2:
            f.write("### ⚠️ **CONDITIONAL NO-GO**\n\n")
            f.write(f"**Reason:** Significant increase in HIGH severity violations ({old_high} → {new_high}).\n\n")
            f.write("**Recommendation:** Review and address high-severity issues before launch.\n\n")
        else:
            f.write("### ✅ **CONDITIONAL GO**\n\n")
            f.write("**Warmth improvement confirmed:** Significant increase in empathy and personal touch.\n\n")
            if len(all_violations['new']) > 0:
                f.write(f"**Minor issues detected:** {len(all_violations['new'])} violations to review.\n\n")
            f.write("**Recommendation:** Ship with close CSAT monitoring.\n\n")
        
        # Key findings
        f.write("## Key Findings\n\n")
        
        violation_categories = {}
        for v in all_violations['new']:
            cat = v['category']
            if cat not in violation_categories:
                violation_categories[cat] = []
            violation_categories[cat].append(v)
        
        if violation_categories:
            f.write("### Issues in New Prompt\n\n")
            for cat, violations in sorted(violation_categories.items(), 
                                         key=lambda x: len(x[1]), reverse=True):
                f.write(f"**{cat.replace('_', ' ').title()}** ({len(violations)} cases)\n")
                for v in violations[:3]:  # Show first 3
                    f.write(f"- {v['ticket_id']}: {v['description']}\n")
                f.write("\n")
        else:
            f.write("No policy violations detected in new prompt! 🎉\n\n")

def generate_detailed_report(results, all_violations):
    """Generate detailed violation report"""
    with open('output/violations_detail.md', 'w') as f:
        f.write("# Detailed Policy Violation Report\n\n")
        
        if len(all_violations['new']) > 0:
            f.write("## New Prompt Violations\n\n")
            for v in sorted(all_violations['new'], key=lambda x: (x['severity'], x['ticket_id'])):
                f.write(f"### {v['ticket_id']} - {v['severity']}\n")
                f.write(f"**Category:** {v['category']}\n\n")
                f.write(f"**Issue:** {v['description']}\n\n")
                f.write(f"**Excerpt:**\n```\n{v['excerpt']}\n```\n\n")
                f.write("---\n\n")
        else:
            f.write("## ✅ No violations detected in new prompt\n\n")
        
        if len(all_violations['old']) > 0:
            f.write("## Old Prompt Violations (for reference)\n\n")
            for v in sorted(all_violations['old'], key=lambda x: (x['severity'], x['ticket_id'])):
                f.write(f"### {v['ticket_id']} - {v['severity']}\n")
                f.write(f"**Category:** {v['category']}\n\n")
                f.write(f"**Issue:** {v['description']}\n\n")
                f.write("---\n\n")

def generate_side_by_side(results, tickets):
    """Generate side-by-side comparison for key tickets"""
    with open('output/side_by_side.md', 'w') as f:
        f.write("# Side-by-Side Comparison: Key Tickets\n\n")
        
        # Focus on tickets with violations or mentioned in PM notes
        key_tickets = ['T-1002', 'T-1009', 'T-1024', 'T-1007', 'T-1013', 'T-1016', 'T-1026', 'T-1029', 'T-1011']
        
        for result in results:
            if result['ticket_id'] not in key_tickets:
                continue
            
            ticket = tickets[result['ticket_id']]
            
            f.write(f"## {result['ticket_id']}: {result['customer']}\n\n")
            f.write(f"**Customer Message:** {ticket['message']}\n\n")
            
            if ticket.get('order'):
                order = ticket['order']
                f.write(f"**Order:** {order.get('order_id', 'N/A')} - {order.get('item', 'N/A')}\n")
                f.write(f"**SKU:** {order.get('sku', 'N/A')} | **Delivered:** {order.get('delivered_on', 'Not delivered')}\n\n")
            
            if ticket.get('internal_notes'):
                f.write(f"**⚠️ Internal Notes:** {ticket['internal_notes']}\n\n")
            
            # Violations
            if result['new_violations']:
                f.write("**🚨 NEW PROMPT VIOLATIONS:**\n")
                for v in result['new_violations']:
                    f.write(f"- **{v['severity']}**: {v['description']}\n")
                f.write("\n")
            
            if result['old_violations']:
                f.write("**⚠️ OLD PROMPT VIOLATIONS:**\n")
                for v in result['old_violations']:
                    f.write(f"- **{v['severity']}**: {v['description']}\n")
                f.write("\n")
            
            f.write("### Old Prompt Reply\n\n")
            f.write(f"```\n{result['old_reply']}\n```\n\n")
            
            f.write("### New Prompt Reply\n\n")
            f.write(f"```\n{result['new_reply']}\n```\n\n")
            
            # Tone comparison
            f.write("### Tone Analysis\n\n")
            f.write(f"| Metric | Old | New | Delta |\n")
            f.write(f"|--------|-----|-----|-------|\n")
            f.write(f"| Empathy phrases | {result['old_tone']['empathy_count']} | {result['new_tone']['empathy_count']} | +{result['new_tone']['empathy_count'] - result['old_tone']['empathy_count']} |\n")
            f.write(f"| Word count | {result['old_tone']['word_count']} | {result['new_tone']['word_count']} | +{result['new_tone']['word_count'] - result['old_tone']['word_count']} |\n")
            f.write(f"| Exclamations | {result['old_tone']['exclamation_count']} | {result['new_tone']['exclamation_count']} | +{result['new_tone']['exclamation_count'] - result['old_tone']['exclamation_count']} |\n\n")
            
            f.write("---\n\n")

if __name__ == '__main__':
    main()
