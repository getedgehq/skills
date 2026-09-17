# Prompt Review Output - Quick Start

## TL;DR
❌ **NO-GO** - 4 critical policy violations found (13% rate)  
✅ **Warmth goals achieved** - 4.6/5 rating vs 2.8/5  
🔧 **Fix available** - See proposed_prompt_v4_fixed.md

---

## Read These First

1. **SUMMARY.md** ← Start here (2 min read)
2. **go_nogo_assessment.md** ← Full analysis (10 min read)
3. **proposed_prompt_v4_fixed.md** ← The fix

## Supporting Evidence

- **side_by_side_examples.md** - 7 key ticket comparisons
- **critical_violations.txt** - The 4 violations explained
- **test_results_new.json** - Automated test output

## Automation (for next time)

```bash
# Run automated policy checks
python test_suite.py ../tickets.jsonl ../outputs.jsonl

# Exit code 0 = pass, 1 = violations
# Use this before manual QA on future prompt changes
```

---

## The 4 Critical Issues

| Ticket | Issue | Impact |
|--------|-------|--------|
| T-1013 | Custom wardrobe refund approved | £1,500-3,000 loss |
| T-1026 | Custom bookshelf refund approved | £800-2,000 loss |
| T-1007 | Refund approved at 41 days (limit: 30) | Policy erosion |
| T-1016 | Internal fraud watchlist leaked to customer | Legal/compliance risk |

**Root cause:** "Do whatever it takes" instruction overrides policy logic

---

## What Changed From Old → New

### ✅ Improvements (Keep These)
- Empathy-first responses
- Uses customer first names
- Warmer sign-off (Oakley)
- Better explanations
- More conversational tone

### ❌ Problems (Fix These)
- Removed explicit policy constraints
- "Do whatever it takes" too permissive
- "Be transparent" leaked internal notes
- No mention of 30-day window
- No mention of custom item rules

---

## Recommended Action

**Option 1 (Best):** Use proposed_prompt_v4_fixed.md
- Keeps all warmth gains
- Restores policy guardrails
- Re-test with same 30 tickets
- Ship next Wed/Thu

**Option 2 (Fast):** Enhance old prompt with warmth
- Lower gains but zero risk
- Could ship Monday

---

## File Index

```
output/
├── README.md (this file)
├── SUMMARY.md (executive summary)
├── go_nogo_assessment.md (full analysis)
├── proposed_prompt_v4_fixed.md (the solution)
├── side_by_side_examples.md (7 examples)
├── critical_violations.txt (4 violations detailed)
├── test_suite.py (automated checker)
├── test_results_new.json (new prompt test)
├── test_results_old.json (old prompt test)
├── analysis_results.json (raw violation data)
└── refined_analysis.json (filtered violations)
```

---

Generated: 2026-09-16  
Reviewer: AI Analysis  
Tickets analyzed: 30  
Violations found: 4 (13% rate)
