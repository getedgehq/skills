# Support Bot Prompt Review - Output Files

## Start Here 👇

**Read this first:** `EXECUTIVE_SUMMARY.md`  
**Quick decision:** NO-GO for Friday ship - critical policy violations found

---

## File Guide

### Main Documents
- **EXECUTIVE_SUMMARY.md** - Top-level decision memo (2-3 min read)
- **REVIEW.md** - Detailed analysis with evidence and recommendations (10 min read)
- **side_by_side.md** - Actual ticket comparisons showing violations vs wins

### Quick Reference
- **quick_reference.md** - One-page stats table
- **test_results.md** - Automated policy test outputs

### Deliverables for Next Steps
- **new_prompt_FIXED_v2.md** - Revised prompt ready for testing (addresses all violations)
- **policy_test_suite.py** - Automated testing tool for future prompt changes

---

## Key Findings

### ⭐ What's Great
- Empathy: 0% → 17% (+17pp)
- Apologies: 3% → 57% (+54pp)
- Escalation detection: fixed
- Custom defect handling: fixed

### 🚨 Critical Issues
- T-1013, T-1026: Offers refunds on custom items (change of mind) - **violates policy**
- T-1016: Leaks internal notes about returns-abuse watchlist - **privacy/legal risk**
- T-1007, T-1016: Offers refunds outside 30-day window - **worse than before**

### 📊 The Numbers
Old prompt: 3 policy failures  
New prompt: 5 policy failures  
**Net change: -2 (worse)**

---

## Next Steps

1. Review EXECUTIVE_SUMMARY.md
2. Review specific violations in side_by_side.md
3. Use new_prompt_FIXED_v2.md for next test
4. Run policy_test_suite.py on new outputs before manual review

---

## For Future Prompt Changes

**Workflow that saves 90% of review time:**

```bash
# After generating new outputs
python3 output/policy_test_suite.py tickets.jsonl outputs_new.jsonl

# If it shows failures, fix prompt and regenerate
# Once it shows 0 failures, then do manual review of tone/warmth
```

The test suite catches:
- Custom item refund violations
- Internal notes leaks
- 30-day window violations
- Missing escalations
- Defect handling issues

Manual review then focuses on:
- Tone/warmth (is it achieving the goal?)
- Edge cases not covered by tests
- Customer satisfaction potential

---

## Tools Created

**policy_test_suite.py** - Run on any outputs to check policy compliance

Usage:
```bash
python3 policy_test_suite.py tickets.jsonl outputs.jsonl
```

Returns exit code 0 if all tests pass, 1 if failures (good for CI/CD).

---

## Questions?

All analysis is reproducible from the source files (tickets.jsonl, outputs_old.jsonl, outputs_new.jsonl).
