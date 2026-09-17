# Outreach Agent Cost Spike Analysis & Fixes

This directory contains the harness audit results and fixes for the 4x September cost spike.

## Quick Start

1. **Read this first:** `EXECUTIVE_SUMMARY.md` (5 min read)
2. **See the numbers:** Run `python3 cost_calculator.py`
3. **Deploy fixes:** Changes are in `../agent/` (prompts.py, loop.py, tools.py)
4. **Validate later:** Run `python3 judge.py` on new traces after deploying

## Files

| File | Purpose |
|------|---------|
| `EXECUTIVE_SUMMARY.md` | One-page overview with recommendation |
| `HARNESS_AUDIT_REPORT.md` | Full analysis with evidence (file:line citations) |
| `cost_calculator.py` | Compare costs: current vs fixes vs model switches |
| `judge.py` | Automated quality checks (run on trace logs) |
| `golden_set.jsonl` | 5 starter test cases from incidents |

## The Three Bugs (Fixed)

1. **Prompt bug:** "Call crm_get_account at the start of EVERY turn" → wasted 6.4M tokens
2. **No max iterations:** 5 conversations looped 16-26 turns → $18.77 of $26.66 total
3. **Retry on permanent errors:** Retrying 404/422 4x instead of failing fast

## Savings Estimate

| Scenario | Monthly Cost | Savings |
|----------|--------------|---------|
| Current (Sonnet, bugs) | $53.32 | baseline |
| Fix harness (keep Sonnet) | $14.82 | 72% |
| Fix + switch to Haiku | $4.94 | 91% |

## Next Steps

1. Deploy fixes from `../agent/`
2. Check with CRM admin about `lead_score_v2` field (causing 422 errors)
3. Run judge.py after a few days to validate
4. Add per-conversation cost cap ($0.50 limit)
5. Consider Haiku after quality validation

## Harness Scorecard: 1.5/6

- ❌ Golden set: Created starter set (5 cases), need 20+ more
- ❌ Judge: Created script, needs email content checks
- ❌ Cost governance: Fixed max_iterations, still need per-conversation cap
- ⚠️  Data layer: CRM schema exists, but no data dictionary
- ⚠️  Action safety: No approval gate on send_email
- ✅ Tracing: Sufficient (conversation_id, tokens, cost, tools)

## Blocking Risks

- **No email approval:** Agent sends cold emails without human review
- **Unknown field:** lead_score_v2 causes infinite retries (check CRM)

---

**Questions?** See HARNESS_AUDIT_REPORT.md for detailed evidence.
