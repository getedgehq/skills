# Output Directory

All analysis and fixes for the outreach agent token burn incident.

## Start Here

**[QUICK_ANSWER.md](QUICK_ANSWER.md)** - Executive summary with the answer to "should we switch models?"

## Full Documentation

1. **[cost_breakdown.txt](cost_breakdown.txt)** - Visual breakdown of where the money went
2. **[cost_analysis.md](cost_analysis.md)** - Complete analysis with evidence, file:line references, mechanism diagrams
3. **[fixes_applied.md](fixes_applied.md)** - What was changed in the code and why

## Code Changes

- **[agent_fixes.patch](agent_fixes.patch)** - Git-style diff of all changes

The actual fixes are already applied to:
- `../agent/loop.py` - Added max turns (10) and cost cap ($0.50)
- `../agent/prompts.py` - Fetch CRM once, removed retry instruction, removed lead_score_v2
- `../agent/tools.py` - Only retry 5xx errors, not 4xx validation errors

## Testing & Eval

- **[golden_set_template.jsonl](golden_set_template.jsonl)** - Starter evaluation set with 5 leads (including the 4 problem cases)
- **[eval_judge.py](eval_judge.py)** - Evaluation harness skeleton (needs implementation to actually run conversations)

## Bottom Line

**Don't switch models.** Three code bugs burned 92% of your budget ($24.54 of $26.66):

1. **Retry loop on validation errors (71%):** 4 leads hit `lead_score_v2` field errors, retried 14-16 times each
2. **Excessive CRM fetching (21%):** Prompt said fetch every turn, each fetch is 30-40KB
3. **No max iterations (8%):** Unbounded loop let conversations run wild

**Fixes reduce cost by 88%**, bringing Sept monthly from $53 → $6 (same as August).

**Model comparison after fixes:**
- Current (Sonnet): $7.24/month
- Haiku (drop-in): $2.41/month (-67%)
- GPT-5-mini: $1.13/month (-84%, needs new SDK)

**Next steps:**
1. Deploy fixes (code already updated)
2. Monitor for 1 week (should see ~$0.40/day)
3. Build full golden set (20+ leads)
4. Run Haiku eval if you want to save another $4.83/month
