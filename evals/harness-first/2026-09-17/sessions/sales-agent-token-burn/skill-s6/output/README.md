# Cost Analysis Output - Brightkiln Outreach Agent

This directory contains the complete analysis of the September 2026 cost spike.

## Quick Start

1. **For Finance/Management:** Read `EXECUTIVE_SUMMARY.md` (3 min)
2. **For detailed costs:** Read `model_cost_comparison.md` (5 min)  
3. **For engineering:** Read `REPORT.md` (full technical analysis)

## Files in This Directory

### Executive Documents
- **EXECUTIVE_SUMMARY.md** - One-page summary: problem, fix, savings, timeline
- **model_cost_comparison.md** - Cost tables comparing all scenarios (current, fixed, model switch)
- **harness_scorecard.md** - Six-part assessment of agent reliability/safety

### Analysis Data
- **cost_analysis.txt** - Detailed trace analysis with token counts and patterns

## What Was Fixed

### Code Changes (in parent `/agent` directory)
- ✅ `agent/loop.py` - Added max_iterations=8, max_cost_usd=$0.50 caps
- ✅ `agent/tools.py` - Fixed retry logic (fail fast on 4xx errors, only retry 5xx)
- ✅ `agent/prompts.py` - Removed "call every turn" and "retry forever" instructions

### Test Harness Created (in parent `/evals` directory)
- ✅ `evals/golden.jsonl` - 5 test cases from real incidents
- ✅ `evals/judge.py` - Automated constraint checker

## The Findings

**Root Cause:** Infinite retry loops on deterministic errors  
**Cost Impact:** 70% of budget ($18.77 of $26.66) from 5 conversations  
**Solution:** Hard caps + smarter retry logic + clearer prompts  
**Savings:** 71% ($37/month) with no model change  

**Model Switch:** Optional future optimization (extra 88% savings) after quality testing

## Next Steps

1. **This week:** Deploy fixes to production, monitor costs
2. **Next sprint:** Run `evals/judge.py` on Sonnet vs GPT-5-mini
3. **Future:** Expand golden set to 20+ cases, gate email sends, read-only CRM

## Questions?

See detailed technical analysis in `REPORT.md` or reach out to eng team.

---

**Analysis Date:** 2026-09-16  
**Data Sources:** logs/calls-2026-09-01_15.jsonl, logs/crm_client.log  
**Methodology:** Harness-First (audit before model swap)
