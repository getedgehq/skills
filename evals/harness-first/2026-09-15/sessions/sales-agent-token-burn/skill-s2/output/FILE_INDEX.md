# File Index

Complete list of all deliverables.

## Quick Start (Read These First)

| File | Purpose | Time |
|------|---------|------|
| `EXECUTIVE_SUMMARY.txt` | Formal incident report for finance/eng | 5 min |
| `QUICK_ANSWER.md` | Answer to "should we switch models?" | 2 min |
| `cost_breakdown.txt` | Visual breakdown of token burn | 3 min |

## Detailed Analysis

| File | Purpose |
|------|---------|
| `cost_analysis.md` | Complete forensic analysis with evidence, file:line references, log excerpts, numbers |
| `fixes_applied.md` | What was changed in the code, why, and expected impact |
| `agent_fixes.patch` | Git-style unified diff of all code changes |

## Code (Already Fixed)

| File | What Changed |
|------|--------------|
| `../agent/loop.py` | Added MAX_TURNS=10, MAX_COST=$0.50, cost tracking |
| `../agent/prompts.py` | Fetch CRM once (not every turn), removed lead_score_v2, removed retry instruction |
| `../agent/tools.py` | Only retry 5xx errors, not 4xx validation errors |

## Evaluation & Testing

| File | Purpose |
|------|---------|
| `golden_set_template.jsonl` | Starter eval set with 5 leads (including the 4 problem cases) |
| `eval_judge.py` | Evaluation harness skeleton (needs implementation) |

## Supporting Files

| File | Purpose |
|------|---------|
| `README.md` | This directory overview |
| `FILE_INDEX.md` | This file |

## The Bottom Line

**Problem:** Sept 1-15 cost was $26.66 (4x August), projected $53/month

**Root Cause:** Three bugs from Sept 3 code changes:
1. Retry loop on validation errors (71% of cost)
2. Excessive CRM fetching every turn (21% of cost)
3. No max iterations (8% of cost)

**Solution:** Fixed all 3 bugs → projected cost drops to $6/month (back to August)

**Model Question:** Don't switch yet. Sonnet isn't the problem. After fixes:
- Sonnet: $7.24/month
- Haiku: $2.41/month (if quality holds on evals)

Deploy fixes first, then evaluate model options.
