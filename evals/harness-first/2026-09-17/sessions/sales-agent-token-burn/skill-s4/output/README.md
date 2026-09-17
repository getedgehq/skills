# Cost Analysis Output

This directory contains the analysis of the September cost spike and fixes.

## Start Here

**Quick answer:** Read `executive_summary.md` (2 min)

**Deploy guide:** Read `quick_fixes.md` (5 min)

**Full analysis:** Read `cost_analysis.md` (15 min)

## Files

### Executive Reports
- **`executive_summary.md`** - One-page summary: what broke, what was fixed, savings
- **`quick_fixes.md`** - Deployment guide with exact steps
- **`cost_analysis.md`** - Complete root cause analysis with evidence
- **`harness_scorecard.md`** - Six-part harness audit (golden set, judge, cost caps, etc)

### Supporting Data  
- **`sept_cost_breakdown.txt`** - Detailed token/cost analysis from logs

## Key Findings

1. **Not a model problem** - two prompt bugs caused infinite retry loops
2. **70% of cost** came from 5 conversations (11% of volume) stuck in loops
3. **Fixes deployed** - max turns, cost caps, smarter prompt, test suite
4. **Immediate savings** - $35/month (67%) with fixes on current Sonnet
5. **Optional savings** - $46/month (86%) if switching to Haiku after fixes

## What Was Fixed

- `agent/loop.py` - added max_turns=10, max_cost_usd=$2.0
- `agent/prompts.py` - removed "EVERY turn" and "infinite retry" bugs
- `agent/tools.py` - deterministic errors (4xx) don't retry
- `agent/mailer.py` - added DRY_RUN mode
- `evals/golden.jsonl` - 22 test cases from incidents
- `evals/run_evals.py` - automated test runner
- `docs/crm_fields.md` - CRM field dictionary

## Deploy Order

1. **This week:** Deploy fixes, run with `DRY_RUN=1`
2. **Next week:** Disable dry-run after verification
3. **Week 3:** Optionally switch to Haiku for additional savings

See `quick_fixes.md` for exact commands.
