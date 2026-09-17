# Outreach Agent Cost Investigation - Files

All analysis and fixes for the Sept 2026 Anthropic bill spike.

## Start Here

1. **[SUMMARY.md](SUMMARY.md)** - Executive summary with one-line answer, root cause, recommendations
2. **[cost_breakdown_visual.txt](cost_breakdown_visual.txt)** - Visual cost breakdown with ASCII charts

## Full Analysis

3. **[cost_analysis.md](cost_analysis.md)** - Detailed cost breakdown with evidence from logs
4. **[harness_scorecard.md](harness_scorecard.md)** - Six-part harness audit (golden set, judge, cost caps, etc.)
5. **[token_burn_evidence.json](token_burn_evidence.json)** - Raw data on all 46 conversations

## Fixes (Ready to Deploy)

6. **[fixes/README.md](fixes/README.md)** - Installation & testing guide
7. **[fixes/loop.py](fixes/loop.py)** - Max iterations, cost cap per conversation
8. **[fixes/tools.py](fixes/tools.py)** - Smart error classification, only retry transient errors
9. **[fixes/prompts.py](fixes/prompts.py)** - Removed lead_score_v2, removed "try again" instruction
10. **[fixes/tracing.py](fixes/tracing.py)** - Log errors properly

## Testing Foundation

11. **[evals/golden_set_starter.jsonl](evals/golden_set_starter.jsonl)** - 10 test cases to expand

## Key Findings

- **Don't switch models yet** - the problem is the harness, not the model
- **69% of costs** from 4 conversations (9% of volume) stuck in infinite retry loops
- **Root causes:**
  1. No iteration cap (`while True` loop)
  2. Retry ALL errors including permanent 422/404 validation failures
  3. Prompt references nonexistent CRM field "lead_score_v2"
  
- **Fixes save $36-44/month** (71% reduction)
- **Haiku switch could save another $10-11/month** (but test quality first!)

## Next Steps

1. Deploy fixes from `fixes/` directory (urgent - stops the bleeding)
2. Fix lead_score_v2 field issue (either create field or revert to lead_score)
3. Expand golden set to 20-30 cases
4. Build judge script
5. Run Haiku eval
6. Switch models only if quality passes

## Questions?

See SUMMARY.md for questions to answer and contact info.
