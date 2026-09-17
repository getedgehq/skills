#!/usr/bin/env python3
"""
Golden set evaluator for FinBot
Run: cd /home/user/work && python output/evals/run_eval.py
"""
import json
import re
import sys
from pathlib import Path

def extract_number(text):
    """Extract first dollar amount or number from text"""
    # Try to find dollar amounts like $3,638,335.79 or $3.6M
    dollar_match = re.search(r'\$[\d,]+\.?\d*', text)
    if dollar_match:
        amount_str = dollar_match.group().replace('$', '').replace(',', '')
        return float(amount_str)
    
    # Try M/million notation like 3.6M
    million_match = re.search(r'([\d.]+)\s*M', text, re.IGNORECASE)
    if million_match:
        return float(million_match.group(1)) * 1_000_000
    
    # Try any number
    num_match = re.search(r'[\d,]+\.?\d*', text)
    if num_match:
        return float(num_match.group().replace(',', ''))
    
    return None


def run_eval_dry_run():
    """Document what the golden set would test (dry run without calling agent)"""
    
    golden_path = Path('output/evals/golden.jsonl')
    cases = []
    with open(golden_path) as f:
        for line in f:
            cases.append(json.loads(line))
    
    print(f"=== GOLDEN SET EVALUATION (DRY RUN) ===")
    print(f"Total test cases: {len(cases)}\n")
    print(f"Note: Agent not called (requires FINBOT_GATEWAY_TOKEN)")
    print(f"This shows what WOULD be tested when the agent is deployed.\n")
    print("="*80 + "\n")
    
    for i, case in enumerate(cases, 1):
        case_id = case['id']
        question = case['question']
        check_type = case['check']
        source = case.get('source', 'N/A')
        
        print(f"Test {i}: {case_id}")
        print(f"  Question: \"{question}\"")
        print(f"  Source: {source}")
        
        if check_type == 'revenue_match':
            expected = case['expected_value']
            tolerance = case.get('tolerance', 0.01) * 100
            print(f"  Check: Answer contains ${expected:,.2f} (±{tolerance:.0f}%)")
        elif check_type == 'range':
            min_val = case.get('expected_min', 'N/A')
            max_val = case.get('expected_max', 'N/A')
            print(f"  Check: Answer contains number in range [{min_val}, {max_val}]")
        elif check_type == 'text_contains':
            phrases = case['expected_contains']
            print(f"  Check: Answer contains one of: {', '.join(phrases)}")
        else:
            print(f"  Check: {check_type}")
        print()
    
    print("="*80)
    print(f"\nTo run live evaluation:")
    print(f"1. Deploy fixed agent + prompt to production")
    print(f"2. Set FINBOT_GATEWAY_TOKEN environment variable")
    print(f"3. Run: python output/evals/run_eval.py --live")


if __name__ == '__main__':
    run_eval_dry_run()
