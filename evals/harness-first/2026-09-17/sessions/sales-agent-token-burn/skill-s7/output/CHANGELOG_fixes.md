# CHANGELOG - Outreach Agent Fixes

## 2026-09-17 - Cost Optimization & Safety Improvements

### Fixed: Infinite retry loops causing 4x cost spike (Issue #1)

**Root cause:** Agent could retry failed operations indefinitely, reloading large account data each turn.

**Changes:**
1. **agent/loop.py**
   - Added `MAX_ITERATIONS = 8` limit (2x normal workflow)
   - Added `MAX_COST_PER_RUN = $0.50` per-lead cap
   - Added graceful error messages when limits are exceeded
   - Added cost tracking across turns
   
2. **agent/tools.py**
   - Improved `@with_retries` decorator to distinguish error types
   - Fail fast on client errors (400, 404, 422) - won't succeed on retry
   - Still retry transient errors (500, 502, 503, 504, 429)
   - Added `CLIENT_ERRORS` and `TRANSIENT_STATUSES` constants
   - Added note to `crm_get_account` schema: "Call ONCE at the start"

3. **agent/prompts.py**
   - Changed instruction from "At the start of EVERY turn" to "ONCE at the start"
   - Removed reference to `lead_score_v2` field (not deployed in CRM yet)
   - Changed to use `lead_score` field for all scores
   - Added explicit instruction: "If CRM update fails with validation error (422), DO NOT RETRY"
   - Clarified stopping condition in step 3

**Impact:**
- Projected cost reduction: 84% (from $26.66 to ~$5 for Sept 1-15 equivalent)
- Prevents infinite loops on validation errors
- Reduces token usage from unnecessary account data reloads
- Graceful degradation instead of runaway costs

**Evidence:**
- 5 conversations consumed 70% of budget before fixes
- Lead L-2012: 64 failed attempts at `lead_score_v2` field (16 turns × 4 retries)
- Average 4.1 account fetches per lead (should be 1.0)
- Input tokens growing from 1.9K (turn 1) to 147K (turn 15) in failed cases

### Testing
- ✅ Unit tests verify retry logic (see output/test_fixes.py)
- ✅ Validation errors (422) now fail after 1 attempt
- ✅ Server errors (503) still retry 4 times as expected
- ✅ Rate limits (429) still retry 4 times as expected

### Deployment Notes
- These changes are **backwards compatible**
- No config changes needed (unless you want to tune MAX_ITERATIONS or MAX_COST_PER_RUN)
- Existing conversations will complete normally
- Failed conversations will now stop gracefully instead of looping

### Monitoring Recommendations
1. Watch for leads hitting the 8-iteration limit (indicates new bugs)
2. Watch for leads hitting the $0.50 cost cap (indicates efficiency issues)
3. Monitor error rates on CRM tools (should decrease)
4. Track average cost per lead (should be ~$0.13, was $0.58)

### Known Limitations
- Still no quality checks (golden set/judge script in output/ directory)
- Email sending is still ungated (no approval flow)
- No alerting for cost anomalies
- `lead_score_v2` field removed from code but may be needed when CRM deploys it

### Files Changed
```
agent/loop.py         - +18 lines (cost caps, max iterations)
agent/tools.py        - +11 lines (smart retry logic)  
agent/prompts.py      - -3 lines (removed lead_score_v2, fixed instruction)
```

### Files Created
```
output/cost_analysis_report.md     - Full technical analysis with evidence
output/model_comparison.md          - Model options and cost projections  
output/EXECUTIVE_SUMMARY.md         - One-page summary for stakeholders
output/analyze_traces.py            - Reproducible trace analysis script
output/test_fixes.py                - Unit tests for retry logic
output/golden_set_starter.jsonl     - 4 example eval cases
output/README_golden_set.md         - Guide to building golden set
output/judge_template.py            - Template for quality evaluation
```

### Next Steps (Recommended)
1. **This week:** Monitor agent with fixes deployed
2. **Next sprint:** Build golden set (20-30 test cases) for quality validation
3. **If needed:** Evaluate Haiku model switch after golden set exists
4. **Q4:** Add automated quality checks and cost alerting

### Rollback Plan
If these changes cause issues:
1. Revert to git commit before this change
2. Increase MAX_ITERATIONS if hitting limit frequently
3. Increase MAX_COST_PER_RUN if legitimate high-value leads need more turns
4. Contact team lead for assistance

---

## Previous Changes

(see existing CHANGELOG.md for history)
