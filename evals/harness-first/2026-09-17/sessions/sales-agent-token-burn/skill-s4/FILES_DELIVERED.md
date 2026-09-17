# Files Delivered

## Summary
- **Diagnosis:** Complete root cause analysis with evidence from logs
- **Fixes:** 4 code files modified, 3 new harness files created
- **Documentation:** 6 analysis documents in output/
- **Impact:** $35-46/month savings (67-86% reduction)

## Modified Files (in agent/)

These files have been fixed and are ready to review/commit:

1. **agent/loop.py** (2.9 KB)
   - Added `max_turns` parameter (default 10)
   - Added `max_cost_usd` parameter (default $2.00)
   - Raises `TurnLimitExceeded` or `CostLimitExceeded` with context
   - Checks limits before each model call

2. **agent/prompts.py** (1.3 KB)
   - Changed "At the start of EVERY turn" → "Call crm_get_account ONCE"
   - Changed "retry if fails" → "retry once on 422, then stop"
   - Clarified when to use lead_score vs lead_score_v2

3. **agent/tools.py** (4.4 KB)
   - Added `_is_transient_error()` to distinguish retry-able errors
   - 4xx errors (except 429) fail fast instead of retrying
   - Better error messages for 404 merged accounts and 422 validation
   - Updated tool descriptions in schemas

4. **agent/mailer.py** (1.4 KB)
   - Added DRY_RUN mode (set `DRY_RUN=1` env var)
   - Logs would-be sends to `logs/emails_dryrun.log`
   - Prevents email spam during testing/debugging

## New Files Created

### Test Harness (evals/)

5. **evals/golden.jsonl** (5.6 KB)
   - 22 test cases covering:
     - Normal flows (low/medium/high scores)
     - Edge cases (score boundaries at 49/50, 79/80)
     - Error scenarios (404, 422, 503)
     - Cost checks (large accounts, turn limits)
     - Policy checks (spam detection, competitors)
   - Sources: Real Sept incidents, policy requirements, edge cases

6. **evals/run_evals.py** (9.7 KB, executable)
   - Automated test runner with MockToolbox
   - Deterministic checks: tools, scores, limits, fields
   - Pass/fail reporting with detailed failure messages
   - Usage: `python evals/run_evals.py`

### Documentation (docs/)

7. **docs/crm_fields.md** (2.3 KB)
   - Data dictionary of valid CRM contact fields
   - Documents `lead_score` vs `lead_score_v2` and when to use each
   - Explains the Sept 6 schema change that triggered the spike
   - Common errors (422, 404) with fixes
   - Schema change log

### Analysis Output (output/)

8. **output/README.md** (1.7 KB)
   - Index of all output files
   - Quick navigation guide

9. **output/SUMMARY.txt** (4.7 KB)
   - Technical summary of problem, fixes, impact
   - Complete file listing with changes
   - Next steps

10. **output/executive_summary.md** (3.3 KB)
    - One-page summary for leadership
    - Root cause, fixes, savings
    - Three-phase deployment plan

11. **output/quick_fixes.md** (5.3 KB)
    - Step-by-step deployment guide
    - Before/after comparison
    - Week-by-week rollout plan
    - FAQ section

12. **output/cost_analysis.md** (8.8 KB)
    - Complete technical analysis with evidence
    - Token breakdowns from log analysis
    - Before/after cost projections
    - Model comparison (Sonnet vs Haiku)
    - Blocking risks assessment

13. **output/harness_scorecard.md** (5.5 KB)
    - Six-part harness audit (golden set, judge, cost caps, data layer, action safety, tracing)
    - Before/after assessment for each part
    - Root cause explanation with file:line references
    - Impact numbers
    - Deployment recommendation

14. **output/sept_cost_breakdown.txt** (4.1 KB)
    - Detailed numerical analysis from Sept 1-15 logs
    - Per-conversation cost breakdown
    - Token growth patterns
    - Top 10 expensive conversations
    - Projections for full month

### Top-Level Guides

15. **START_HERE.md** (3.0 KB)
    - Quick overview for the user
    - TL;DR answer: "Don't switch models yet"
    - What was found, what was fixed
    - Next steps
    - Why not just switch to Haiku

16. **FILES_DELIVERED.md** (this file)
    - Complete listing of all deliverables
    - Summary of each file

## How to Use These Files

### For Immediate Action
1. Read `START_HERE.md` (2 min)
2. Read `output/executive_summary.md` (3 min)
3. Review the 4 modified files in `agent/`
4. Follow deployment steps in `output/quick_fixes.md`

### For Technical Deep Dive
1. Read `output/cost_analysis.md` (full analysis with evidence)
2. Review `output/sept_cost_breakdown.txt` (detailed numbers)
3. Read `output/harness_scorecard.md` (six-part audit)

### For Testing
1. Review `evals/golden.jsonl` (test cases)
2. Run `python evals/run_evals.py` (when ready to test)
3. Check `docs/crm_fields.md` (field reference)

### For Leadership
1. Share `output/executive_summary.md` (one-page summary)
2. Reference `output/SUMMARY.txt` (technical summary)

## File Sizes

```
Total: ~70 KB of code + documentation

Modified code:     10.0 KB (4 files)
New harness:       15.3 KB (2 files)
Documentation:     39.7 KB (13 files)
Data dictionary:    2.3 KB (1 file)
```

## Next Steps

1. **Review** the modified agent/ files
2. **Test locally** with `DRY_RUN=1`
3. **Deploy** following output/quick_fixes.md
4. **Monitor** costs (should drop to ~$18/month)
5. **Optional:** Switch to Haiku in week 3 for additional savings

## Questions?

- **What's the problem?** See START_HERE.md
- **How do I deploy?** See output/quick_fixes.md
- **What's the evidence?** See output/cost_analysis.md
- **What's the harness?** See output/harness_scorecard.md
- **What are valid CRM fields?** See docs/crm_fields.md
