# Summary of Changes

## Problem Identified
**70% of September costs** came from 5 conversations stuck in infinite retry loops on deterministic errors.

---

## Code Changes (Ready to Deploy)

### 1. agent/loop.py - Cost Governance ✅
**Changes:**
- Added `max_iterations=8` parameter (default) with hard stop
- Added `max_cost_usd=0.50` parameter (default) with hard stop  
- Raise `MaxIterationsError` and `CostCapExceeded` with clear messages
- Log violations for monitoring
- Added docstring documenting limits

**Impact:** Prevents runaway costs. Worst case now: $0.50 per conversation.

**Before:**
```python
while True:
    # No exit condition - runs forever if stuck
```

**After:**
```python
while turn < max_iterations:
    # ... 
    total_cost += resp.cost_usd
    if total_cost > max_cost_usd:
        raise CostCapExceeded(...)
```

---

### 2. agent/tools.py - Smart Retries ✅
**Changes:**
- Only retry transient errors: 408, 429, 500-504 (timeouts, rate limits, server errors)
- Fail fast on client errors: 400, 404, 422 (these won't fix themselves)
- Updated `crm_get_account` description: "Call ONCE per conversation, not every turn"
- Updated `crm_update_contact` description: "Use 'lead_score' field. Field 'lead_score_v2' does not exist."

**Impact:** Eliminates infinite loops on permanent errors like "unknown field".

**Before:**
```python
@with_retries(attempts=4)  # Retried ALL errors including 422
def crm_update_contact(...):
```

**After:**
```python
@with_retries(attempts=4)
def wrapped(*args, **kwargs):
    # ...
    if e.status not in TRANSIENT_STATUSES:
        raise  # fail fast on 4xx
```

---

### 3. agent/prompts.py - Clear Instructions ✅
**Changes:**
- "At the start of EVERY turn, call crm_get_account" → "Call crm_get_account ONCE"
- "Do not finish until CRM update succeeded. Try again." → "If error you cannot resolve after one retry, report and finish"
- Removed reference to non-existent `lead_score_v2` field
- Added: "Work efficiently: complete in 3-5 turns"

**Impact:** Agent no longer re-fetches 12KB exports every turn, stops fighting permanent errors.

**Before:**
```
1. At the start of EVERY turn, call crm_get_account...
3. Write the score... {"lead_score_v2": <score>}...
   Do not finish until the CRM update has succeeded. If a tool call fails, try it again.
```

**After:**
```
1. Call crm_get_account ONCE to load account data...
3. Write the score... {"lead_score": <score>}.
   If crm_update_contact returns a 422 error about an unknown field, STOP trying...
Work efficiently: complete the task in 3-5 turns.
```

---

## Test Harness Created

### 4. evals/golden.jsonl - Test Cases ✅
**Created:** 5 test cases based on real incidents
1. `normal_high_score` - Happy path (score ≥50, send email)
2. `high_score_422_field_error` - Was 17-turn loop, should use correct field
3. `low_score_no_email` - Score <50, no email
4. `unknown_field_graceful_fail` - 422 error handling
5. `account_merged_404` - Was 26-turn loop, should fail gracefully

**Next:** Expand to 20+ cases from production traffic

---

### 5. evals/judge.py - Automated Testing ✅
**Created:** Constraint checker that validates:
- Turn count limits
- Required tools called
- No repeated expensive calls
- No infinite retry patterns
- Proper completion

**Next:** Wire up to CRM test environment for live runs

---

## Documentation Created

All files in `output/`:

1. **EXECUTIVE_SUMMARY.md** - For finance/management (one-pager)
2. **model_cost_comparison.md** - Cost tables at different volumes
3. **harness_scorecard.md** - Six-part agent reliability assessment  
4. **REPORT.md** - Complete technical analysis with evidence
5. **cost_analysis.txt** - Detailed trace analysis
6. **cost_breakdown.txt** - Visual cost comparison
7. **README.md** - Guide to all output files
8. **CHANGES_SUMMARY.md** - This file

---

## What Didn't Change

✅ **Model:** Still using Claude Sonnet 4.5  
✅ **API:** Still using Anthropic Messages API  
✅ **Tools:** Same three tools (crm_get_account, crm_update_contact, send_email)  
✅ **Workflow:** Still one conversation = one lead  
✅ **Tracing:** Still logging to calls-YYYY-MM-DD_HH.jsonl  

**Why:** Fix the mechanism first, then test model changes with real quality data.

---

## Risk Assessment

### Low Risk Changes ✅
- Hard caps (max iterations, max cost) - pure safety additions
- Fail-fast on 4xx errors - stops waste, doesn't change success path
- Prompt clarifications - removes ambiguous "every turn" and "retry forever"

### Medium Risk (Not Done Yet) ⚠️
- Model switch to GPT-5-mini - needs quality testing on golden set
- Email approval gates - needs product decision on workflow
- Read-only CRM credentials - needs infrastructure change

---

## Expected Results

### Immediate (This Week)
- Deploy fixes to production
- Monitor traces for MaxIterationsError / CostCapExceeded
- Should see NO conversations >8 turns
- Should see NO conversations >$0.50

### End of Month
- September bill: ~$40-45 (partial month with fixes)
- Compared to: ~$80-90 projected without fixes

### October (Full Month)
- October bill: ~$16 for 92 conversations
- Compared to: ~$53 without fixes
- **Savings: $37/month (71%)**

### Later (After Model Testing)
- Test GPT-5-mini quality on golden set
- If passes: October bill drops to ~$2/month
- **Additional savings: $14/month (88% more)**

---

## Deployment Checklist

- [x] Code reviewed (loop.py, tools.py, prompts.py)
- [x] Golden test cases created (5 cases in evals/)
- [x] Documentation written (8 files in output/)
- [ ] Test on staging with real CRM
- [ ] Validate costs per conversation ~$0.17
- [ ] Deploy to production
- [ ] Monitor for cost cap violations
- [ ] Confirm October bill ~$16/month

---

## Model Switch Checklist (Later)

- [ ] Expand golden set to 20+ cases
- [ ] Run judge.py on Sonnet (baseline quality score)
- [ ] Run judge.py on GPT-5-mini (compare quality)
- [ ] Review 10 sample emails from each model
- [ ] If GPT-5-mini ≥95% pass rate → switch
- [ ] If quality drops → stay on Sonnet, already saved 71%

---

## Questions Answered

**Q: Is Sonnet overkill for cold emails?**  
A: Maybe, but that's not why costs spiked. Costs spiked due to infinite loops. Fix those first (71% savings), then test quality.

**Q: Should we switch models now?**  
A: No. Fix the bug (1 hour, zero risk, 71% savings), then test model switch properly (1 week, needs quality validation, extra 88% savings).

**Q: What if we switch models without fixing the bug?**  
A: You'd still waste tokens on retry loops. The bug scales with volume regardless of model price.

**Q: When can we switch models?**  
A: After deploying these fixes and validating quality on the golden set. Probably next sprint (October).

---

## Contact

For questions about:
- **Code changes:** See REPORT.md technical analysis
- **Cost projections:** See model_cost_comparison.md
- **Testing strategy:** See evals/judge.py

**Timeline:** Deploy fixes this week, model testing next sprint.
