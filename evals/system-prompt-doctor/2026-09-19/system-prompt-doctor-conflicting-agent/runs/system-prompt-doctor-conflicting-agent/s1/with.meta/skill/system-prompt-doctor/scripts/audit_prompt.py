#!/usr/bin/env python3
"""Static system-prompt audit. This is diagnostic only; it is NOT a quality score."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path

RULES = {
    "contradictory_absolutes": [r"\balways\b", r"\bnever\b"],
    "chain_of_thought_request": [r"think step by step", r"chain[- ]of[- ]thought", r"internal (?:thought|reasoning)"],
    "vague_helpfulness": [r"be helpful", r"be smart", r"do your best"],
    "tool_policy": [r"\btool", r"\bsearch", r"\bread before write", r"\binspect"],
    "completion_criteria": [r"done when", r"completion", r"before finishing", r"validate", r"verify"],
    "ask_act_policy": [r"ask before", r"clarif", r"default to (?:act|implementation)", r"when .* ask"],
    "output_contract": [r"output format", r"respond with", r"final answer", r"format"],
}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('prompt', type=Path)
    ap.add_argument('--out', type=Path)
    args=ap.parse_args()
    text=args.prompt.read_text(encoding='utf-8', errors='replace')
    lower=text.lower()
    tokens_est=max(1, round(len(text)/4))
    findings=[]
    if len(text)>10000:
        findings.append({"type":"bloat","severity":"warn","detail":"Prompt exceeds 10k characters; test progressive disclosure."})
    contradiction_pairs=[
        (r'\balways act\b', r'\bnever act(?: before| without)?'),
        (r'\bnever ask\b', r'\bask before\b'),
        (r'\balways use tools?\b', r'\buse tools? only'),
        (r'\bbe concise\b', r'\bextremely detailed\b'),
    ]
    for a,b in contradiction_pairs:
        if re.search(a,lower) and re.search(b,lower):
            findings.append({"type":"possible-contradiction","severity":"warn","detail":f"Potentially conflicting rules detected: `{a}` vs `{b}`. Confirm intended precedence with evals."})
    if lower.count('always')>=3 and lower.count('never')>=3:
        findings.append({"type":"absolute-density","severity":"warn","detail":"Many absolute rules; inspect for conflicts and exceptions."})
    if any(re.search(p,lower) for p in RULES['chain_of_thought_request']):
        findings.append({"type":"cot-request","severity":"warn","detail":"Contains explicit hidden-reasoning / chain-of-thought request."})
    if any(re.search(p,lower) for p in RULES['vague_helpfulness']):
        findings.append({"type":"vague-rule","severity":"info","detail":"Contains vague behavior language; replace only if evals show ambiguity."})
    # Extend ask/act detection for common absolute phrasing.
    if re.search(r'\b(always act|never act|ask before|never ask)\b', lower):
        RULES['ask_act_policy'].append(r'\b(always act|never act|ask before|never ask)\b')
    for key,label in [('tool_policy','tool policy'),('completion_criteria','completion/validation criteria'),('ask_act_policy','ask-vs-act policy'),('output_contract','output contract')]:
        if not any(re.search(p,lower) for p in RULES[key]):
            findings.append({"type":"missing-"+key.replace('_','-'),"severity":"info","detail":f"No obvious {label} detected. Add only if relevant to the agent contract."})
    result={
        "diagnostic_only": True,
        "characters": len(text),
        "estimated_tokens": tokens_est,
        "lines": text.count('\n')+1,
        "findings": findings,
        "note": "Static findings do not prove prompt quality. Use held-out behavioral evals."
    }
    out=json.dumps(result,indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True); args.out.write_text(out+'\n')
    else: print(out)
if __name__=='__main__': main()

