# Outreach Agent Cost Fix - Summary

## What I Changed

### 1. Fixed agent/loop.py (Stop infinite loops)
- Added `max_turns=10` parameter (default, can override)
- Changed `while True:` to `while turn < max_turns:`
- Added graceful stop message when max iterations reached

### 2. Fixed agent/prompts.py (Stop wasteful re-fetching and bad retries)
- Changed: "At the start of EVERY turn, call crm_get_account" → "Call crm_get_account ONCE at the start"
- Removed: "Leads scoring 80 or higher must get... lead_score_v2" (field doesn't exist in CRM)
- Changed: All leads now use {"lead_score": <score>}
- Added: "If the CRM update fails with a 4xx error... do NOT retry it"

### 3. Fixed agent/tools.py (Smart retry logic)
- Changed `with_retries` decorator to fail fast on 4xx errors (404, 422, etc.)
- Only retry 5xx errors and timeouts (transient failures)
- Prevents agent from retrying validation errors, merged accounts, unknown fields

## What I Created

### 4. evals/golden.jsonl (10 test cases)
- 3 normal flows (low/mid/high score)
- 2 incident replays (L-3489 404 loop, L-2012 422 loop)  
- 2 edge cases (no data, boundary conditions)
- 3 policy checks (email threshold, single fetch, max iterations)

### 5. evals/judge.py (Eval harness)
- Defines deterministic checks for each case
- Tool call counts, turn limits, policy compliance
- Ready to run when you add agent executor + mock CRM

### 6. output/cost_analysis.md (Full diagnosis)
- Root cause analysis with evidence
- Per-conversation cost breakdown
- Harness scorecard
- Projected savings

## Expected Savings

**Before fixes:** $26.66 / half-month (46 conversations)
- 5 runaway conversations: $18.77 (70% of cost)
- Normal conversations inefficient: resending 12K tokens/turn

**After fixes:** ~$3.68 / half-month
- Runaway conversations: eliminated
- Normal conversations: 89% fewer input tokens

**Monthly savings: ~$46/month** ($53 current → $7 projected)

## Don't Switch Models Yet

Switching to Haiku after these fixes would save another $2/month.
Switching to GPT-5-mini would save $4/month.

**Not worth the migration effort vs. the $46/month from fixing the harness.**

Run the golden set on Sonnet vs Haiku if you want to compare quality, but fix the harness first.

## Next Steps (Priority Order)

### Blocking
1. **Deploy the 3 code fixes above** (loop.py, prompts.py, tools.py)
2. **Test on staging with a few leads** - confirm cost drops to ~$0.08/conversation
3. **Remove send_email approval gate or add human review** - right now agent sends real emails with no gate

### High Priority  
4. **Implement mock CRM for evals** - so you can run judge.py end-to-end
5. **Run golden set before every prompt change** - prevent regression
6. **Add per-run cost cap** - e.g., stop if cost > $0.50 for one conversation

### Medium Priority
7. **Create data dictionary** - document what lead_score means, where it's stored
8. **Add field validation** - check CRM schema before using fields
9. **Expand golden set** - add more real incidents, edge cases from production

## Files Modified
- agent/loop.py (added max_turns, graceful stop)
- agent/prompts.py (fixed wasteful fetch, removed bad field, added 4xx guidance)
- agent/tools.py (fail fast on 4xx errors)

## Files Created
- output/cost_analysis.md (full diagnostic report)
- output/fix_summary.md (this file)
- evals/golden.jsonl (10 test cases)
- evals/judge.py (eval harness skeleton)

## How to Deploy

```bash
# Review the changes
git diff agent/

# Test on one lead in staging
export BK_CRM_TOKEN="staging_token"
python -m agent.run_batch --leads L-TEST-001

# Check cost in trace log
tail -1 logs/calls-*.jsonl | jq '.cost_usd'

# If cost is ~$0.02-0.08, deploy to prod
git add agent/ evals/
git commit -m "fix: stop infinite retry loops and wasteful re-fetching

- Add max_turns=10 to prevent runaways
- Call crm_get_account once per conversation (was: every turn)
- Fail fast on 4xx CRM errors (was: retry forever)
- Remove lead_score_v2 field (doesn't exist in CRM)

Expected savings: $46/month (from $53 to $7)
See output/cost_analysis.md for full diagnosis"

git push
```
