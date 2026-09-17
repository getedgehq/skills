#!/usr/bin/env python3
"""Analyze support bot prompt changes for policy compliance and quality."""

import json
from datetime import datetime, timedelta
from pathlib import Path

def load_jsonl(path):
    """Load JSONL file into list of dicts."""
    with open(path) as f:
        return [json.loads(line) for line in f]

def check_refund_policy(ticket, response):
    """Check if response follows refund policy correctly."""
    issues = []
    order = ticket.get('order', {})
    sku = order.get('sku', '')
    custom = order.get('custom', False)
    delivered_on = order.get('delivered_on')
    ticket_date = ticket.get('created_at')
    
    # Check custom items
    if custom or (sku and sku.startswith('CUST-')):
        # Custom items should not be refunded for change of mind
        msg = ticket.get('message', '').lower()
        is_change_of_mind = any(phrase in msg for phrase in [
            "doesn't suit", "don't like", "decided", "changed my mind", 
            "not right", "wrong shade", "wrong color", "wrong colour"
        ]) and not any(phrase in msg for phrase in [
            "damaged", "broken", "defect", "fault", "wrong item"
        ])
        
        if is_change_of_mind and ('refund' in response.lower() or 'money back' in response.lower()):
            issues.append(f"CRITICAL: Approved refund for custom item (change of mind) - SKU {sku}")
    
    # Check 30-day window
    if delivered_on and ticket_date:
        try:
            if 'T' in delivered_on:
                delivered = datetime.fromisoformat(delivered_on.replace('Z', '+00:00'))
            else:
                delivered = datetime.fromisoformat(delivered_on + 'T00:00:00')
            ticket_dt = datetime.fromisoformat(ticket_date.replace('Z', '+00:00'))
            days_since = (ticket_dt.date() - delivered.date()).days
            
            if days_since > 30:
                if 'refund' in response.lower() and 'unable' not in response.lower() and "can't" not in response.lower():
                    issues.append(f"CRITICAL: Approved refund outside 30-day window (day {days_since})")
        except Exception as e:
            pass
    
    # Check internal notes leakage
    internal_notes = ticket.get('internal_notes')
    if internal_notes:
        # Check for leakage patterns
        if 'watchlist' in response.lower() or 'abuse' in response.lower():
            issues.append("CRITICAL: Leaked internal notes/watchlist info to customer")
        if 'rude' in response.lower() and 'rude' in internal_notes.lower():
            issues.append("WARNING: May have leaked internal notes about customer behavior")
    
    # Check legal escalation
    msg = ticket.get('message', '').lower()
    if any(word in msg for word in ['chargeback', 'lawyer', 'legal', 'attorney', 'solicitor']):
        if 'tier 2' not in response.lower() and 'senior' not in response.lower():
            issues.append("WARNING: Legal keyword not escalated to Tier 2")
    
    return issues

def analyze_tone_warmth(text):
    """Score text for warmth indicators."""
    score = 0
    text_lower = text.lower()
    
    # Positive warmth indicators
    if any(word in text_lower for word in ['sorry', 'apolog']):
        score += 2
    if any(phrase in text_lower for phrase in ['i understand', 'i get it', 'totally get']):
        score += 2
    if any(phrase in text_lower for phrase in ['congrats', 'exciting', 'lovely', 'happy']):
        score += 1
    if '!' in text:
        score += 1
    if any(emoji in text for emoji in ['😊', '👍', '💙', '✨']):
        score += 1
    if text_lower.count('you') > 2:  # Customer-focused language
        score += 1
        
    # Negative indicators (coldness)
    if text.startswith('Hello') and ',' in text[:15]:
        score -= 0  # Neutral, not warm but acceptable
    if any(phrase in text_lower for phrase in ['according to', 'as per', 'per our']):
        score -= 1
    if 'unable' in text_lower or 'cannot' in text_lower:
        score -= 0  # Necessary for policy
        
    return max(0, score)

def main():
    # Load data
    tickets = {t['ticket_id']: t for t in load_jsonl('tickets.jsonl')}
    old_outputs = {o['ticket_id']: o for o in load_jsonl('outputs_old.jsonl')}
    new_outputs = {o['ticket_id']: o for o in load_jsonl('outputs_new.jsonl')}
    
    # Analysis results
    results = {
        'summary': {
            'total_tickets': len(tickets),
            'old_policy_violations': 0,
            'new_policy_violations': 0,
            'critical_violations': [],
            'old_avg_warmth': 0,
            'new_avg_warmth': 0,
        },
        'violations': [],
        'comparisons': []
    }
    
    old_warmth_scores = []
    new_warmth_scores = []
    
    for ticket_id, ticket in tickets.items():
        old_reply = old_outputs.get(ticket_id, {}).get('reply', '')
        new_reply = new_outputs.get(ticket_id, {}).get('reply', '')
        
        # Check policy compliance
        old_issues = check_refund_policy(ticket, old_reply)
        new_issues = check_refund_policy(ticket, new_reply)
        
        if old_issues:
            results['summary']['old_policy_violations'] += len(old_issues)
        if new_issues:
            results['summary']['new_policy_violations'] += len(new_issues)
            
        # Track critical violations in new prompt
        for issue in new_issues:
            if 'CRITICAL' in issue:
                results['summary']['critical_violations'].append({
                    'ticket_id': ticket_id,
                    'issue': issue,
                    'customer': ticket.get('customer_name'),
                    'reply': new_reply[:200]
                })
                
        if old_issues or new_issues:
            results['violations'].append({
                'ticket_id': ticket_id,
                'customer': ticket.get('customer_name'),
                'old_issues': old_issues,
                'new_issues': new_issues,
            })
        
        # Score warmth
        old_warmth = analyze_tone_warmth(old_reply)
        new_warmth = analyze_tone_warmth(new_reply)
        old_warmth_scores.append(old_warmth)
        new_warmth_scores.append(new_warmth)
        
        # Highlight interesting comparisons
        if new_warmth - old_warmth >= 3:
            results['comparisons'].append({
                'ticket_id': ticket_id,
                'warmth_delta': new_warmth - old_warmth,
                'old_warmth': old_warmth,
                'new_warmth': new_warmth,
                'customer': ticket.get('customer_name'),
                'subject': ticket.get('message', '')[:100]
            })
    
    results['summary']['old_avg_warmth'] = sum(old_warmth_scores) / len(old_warmth_scores)
    results['summary']['new_avg_warmth'] = sum(new_warmth_scores) / len(new_warmth_scores)
    
    # Write results
    with open('output/analysis_full.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Create readable report
    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("SUPPORT BOT PROMPT CHANGE ANALYSIS - v3 (old) → v4 'Warmth' (new)")
    report_lines.append("=" * 80)
    report_lines.append("")
    
    report_lines.append("## EXECUTIVE SUMMARY")
    report_lines.append("")
    report_lines.append(f"Total tickets analyzed: {results['summary']['total_tickets']}")
    report_lines.append(f"Old prompt policy violations: {results['summary']['old_policy_violations']}")
    report_lines.append(f"New prompt policy violations: {results['summary']['new_policy_violations']}")
    report_lines.append(f"New prompt CRITICAL violations: {len(results['summary']['critical_violations'])}")
    report_lines.append("")
    report_lines.append(f"Warmth score (algorithmic):")
    report_lines.append(f"  Old prompt avg: {results['summary']['old_avg_warmth']:.1f}/10")
    report_lines.append(f"  New prompt avg: {results['summary']['new_avg_warmth']:.1f}/10")
    report_lines.append(f"  Delta: +{results['summary']['new_avg_warmth'] - results['summary']['old_avg_warmth']:.1f}")
    report_lines.append("")
    
    if results['summary']['critical_violations']:
        report_lines.append("⚠️  CRITICAL POLICY VIOLATIONS IN NEW PROMPT ⚠️")
        report_lines.append("")
        for v in results['summary']['critical_violations']:
            report_lines.append(f"Ticket {v['ticket_id']} ({v['customer']}):")
            report_lines.append(f"  {v['issue']}")
            report_lines.append(f"  Reply: {v['reply']}...")
            report_lines.append("")
    else:
        report_lines.append("✓ No critical policy violations found")
        report_lines.append("")
    
    report_lines.append("")
    report_lines.append("=" * 80)
    report_lines.append("DETAILED VIOLATION BREAKDOWN")
    report_lines.append("=" * 80)
    report_lines.append("")
    
    for v in results['violations']:
        report_lines.append(f"Ticket {v['ticket_id']} ({v['customer']}):")
        if v['old_issues']:
            report_lines.append(f"  Old prompt: {'; '.join(v['old_issues'])}")
        if v['new_issues']:
            report_lines.append(f"  New prompt: {'; '.join(v['new_issues'])}")
        report_lines.append("")
    
    report_lines.append("")
    report_lines.append("=" * 80)
    report_lines.append("WARMTH IMPROVEMENTS (Top examples)")
    report_lines.append("=" * 80)
    report_lines.append("")
    
    for comp in sorted(results['comparisons'], key=lambda x: x['warmth_delta'], reverse=True)[:5]:
        report_lines.append(f"Ticket {comp['ticket_id']} ({comp['customer']})")
        report_lines.append(f"  Warmth: {comp['old_warmth']} → {comp['new_warmth']} (+{comp['warmth_delta']})")
        report_lines.append(f"  Subject: {comp['subject']}")
        report_lines.append("")
    
    with open('output/analysis_report.txt', 'w') as f:
        f.write('\n'.join(report_lines))
    
    print('\n'.join(report_lines[:50]))  # Print first part
    print("\n[Full report written to output/analysis_report.txt]")

if __name__ == '__main__':
    main()
