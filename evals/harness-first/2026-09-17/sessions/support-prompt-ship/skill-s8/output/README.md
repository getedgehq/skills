# Support Bot Prompt Change Review - Output Files

**Review Date:** 2026-09-16  
**Decision:** 🟡 CONDITIONAL GO (fix data layer by Thursday)

## Quick Links

- **[GO_NO_GO_REPORT.md](GO_NO_GO_REPORT.md)** - Full analysis and recommendation
- **[SIDE_BY_SIDE_EXAMPLES.md](SIDE_BY_SIDE_EXAMPLES.md)** - Key reply comparisons
- **[judge.py](judge.py)** - Automated evaluation script
- **[golden_set.jsonl](golden_set.jsonl)** - 8 test cases with constraints

## TL;DR

### ✅ Ship the new prompt IF:
1. Engineering adds `refund_eligible` computed field by Thursday EOD
2. Add guardrail check: flag replies that offer refunds when `refund_eligible=false`
3. 10% rollout Friday 9am, monitor for 2 hours, then 100%

### ❌ Don't ship IF:
- Can't fix data layer by Thursday
- Bot issues refunds directly (vs drafting replies for human approval)
- No rollback plan

## What Changed

**Old → New:**
- Tone: Professional → Warm & empathetic
- Sign-off: "Brindle & Oak Support" → "Warmly, Oakley at Brindle & Oak"
- Instructions: Explicit policy rules → "Do whatever it takes" (judgment-based)

**Results:**
- FIXED: Legal escalation bug (1 critical violation eliminated)
- SAME: 30-day window violations (4 cases, both prompts fail)
- WARMTH: Team rating 2.8/5 → 4.6/5

## Root Cause Found

**Problem:** Model calculates date math (delivered_on → ticket_created → days) and fails ~50% of the time.

**Solution:** Add computed fields:
```json
{
  "days_since_delivery": 41,
  "refund_eligible": false,
  "refund_deadline": "2026-07-26"
}
```

**Impact:** Expected to fix 4 violations, bringing score from 4/8 → 7/8 or 8/8.

## Files in This Directory

| File | Purpose |
|------|---------|
| **GO_NO_GO_REPORT.md** | Full audit: findings, decision, next steps |
| **SIDE_BY_SIDE_EXAMPLES.md** | Visual comparison of key replies |
| **judge.py** | Automated checker (run on every prompt change) |
| **golden_set.jsonl** | 8 test cases with policy constraints |
| **eval_results.json** | Old vs new prompt scores (3/8 vs 4/8) |
| **policy_violations.json** | Detailed violation analysis |
| **critical_analysis.json** | Case-by-case legal/refund checks |
| **risky_language.json** | "Anything else" / "always" flagged phrases |
| **refund_compliance.json** | Refund decision correctness |

## How to Use This for Next Prompt Change

1. **Add new cases to golden_set.jsonl** (especially any incidents, CSAT=1 tickets, edge cases)
2. **Run eval:**
   ```bash
   python output/judge.py new_prompt_outputs.jsonl
   ```
3. **Check for regressions:** Any new failures? Any violations introduced?
4. **Ship only if:** Pass rate same or better, no new violations

## Harness Status

| Component | Status | Next Step |
|-----------|--------|-----------|
| Golden set | 🟡 Partial (8 cases) | Expand to 20+ cases |
| Judge | ✅ Present | Add LLM judge for warmth |
| Cost caps | ❌ Missing | Add per-ticket token limit |
| Data layer | ❌ Missing | Add refund_eligible field |
| Action safety | ❓ Unknown | Audit code (draft vs direct refund) |
| Tracing | ❓ Unknown | Add conversation_id + token logging |

## Questions for Engineering

1. Can you add `refund_eligible`, `days_since_delivery`, `refund_deadline` to ticket payload by Thursday EOD?
2. Can you add a guardrail check: if `refund_eligible=false` and reply contains "refund", flag for review?
3. Does this bot draft replies or issue refunds directly?
4. Do we have per-conversation token/cost logging?
5. What's the rollback process if violations spike?

## Contact

Questions? Check the harness-first skill docs or review the methodology in GO_NO_GO_REPORT.md section 3 (Harness Scorecard).

---

**Bottom line:** New prompt is better, but fix the date math first. You now have the tools to ship prompt changes safely every 2 weeks.
