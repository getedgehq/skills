# File Manifest - Support Bot Prompt Review

All deliverables saved to `/home/user/work/output/`

## 📋 Executive Summaries (Read These First)

### 1. DECISION_SUMMARY.txt
- Visual one-page summary
- Decision, numbers, violations, path forward
- **START HERE** if you have 2 minutes

### 2. QUICK_SUMMARY.md
- Text-based quick summary
- Key facts and next steps
- **START HERE** if you want markdown format

### 3. GO_NO_GO_DECISION.md
- Complete 10-page report
- Evidence, impact analysis, root cause
- Path forward with 3 options
- Blocking issues identified
- Read if you need full context or are presenting to leadership

---

## 🔍 Evidence & Analysis

### 4. violation_examples.md
- Side-by-side comparison of old vs new prompt
- All 3 violations shown in detail with context
- Shows what new prompt gets RIGHT (warmth, standard returns, escalation)
- **Read this** if you want to see the actual bot outputs

### 5. policy_violations.json
- Machine-readable violation data
- Full details for all 3 violations
- Use for further analysis or dashboards

---

## 🧪 Test Infrastructure (Reusable!)

### 6. golden_set.jsonl
- 8 test cases covering critical policies
- Format: ticket_id, test_case, expected_behavior, constraint, policy_ref
- **Expand to 20+** cases covering all edge cases
- Use for every prompt change going forward

### 7. judge.py
- Automated policy compliance checker
- Runs deterministic checks on bot outputs
- Exit code 1 if violations found (CI/CD ready)
- **Run before shipping ANY prompt change:**
  ```bash
  cd /home/user/work
  python3 output/judge.py
  ```

### 8. judge_results_old.json
- Old prompt test results: 7/7 pass (100%)
- Detailed pass/fail reasons per test case

### 9. judge_results_new.json
- New prompt test results: 4/7 pass, 3 fail (57%)
- Shows which tests failed and why

---

## 🔧 Solutions & Next Steps

### 10. prompt_v4.1_FIXED.md
- Recommended fixed prompt
- Keeps warmth + adds guardrails back
- Changes:
  - Explicit custom item policy (both `custom` flag and `CUST-` SKU)
  - Explicit internal notes confidentiality rule
  - "Delight within policies" instead of "do whatever it takes"
  - "Be transparent about order status" not "share everything"
- **Test this** on August tickets before shipping

### 11. HARNESS_SCORECARD.md
- Six-part agent safety audit
- Scores: Golden set (2/5), Judge (4/5), Cost (0/5), Data (0/5), Actions (0/5), Tracing (0/5)
- Overall: 1.2/5.0
- Priority list for next 6 months
- Critical finding: **No action safety gate visible**
- **Read if** you're planning long-term bot improvements

---

## 📖 Documentation

### 12. README.md
- Guide to all files in this directory
- How to use the test suite
- Numbers and key lessons
- **Read if** someone new needs to understand the review

### 13. FILE_MANIFEST.md (this file)
- List of all deliverables with descriptions
- Quick reference guide

---

## 📊 Quick Reference Table

| File | Type | Priority | Time to Read |
|------|------|----------|--------------|
| DECISION_SUMMARY.txt | Summary | ⭐⭐⭐ URGENT | 2 min |
| QUICK_SUMMARY.md | Summary | ⭐⭐⭐ URGENT | 2 min |
| GO_NO_GO_DECISION.md | Report | ⭐⭐ HIGH | 10 min |
| violation_examples.md | Evidence | ⭐⭐ HIGH | 5 min |
| prompt_v4.1_FIXED.md | Solution | ⭐⭐ HIGH | 3 min |
| judge.py | Tool | ⭐⭐ HIGH | Run now |
| golden_set.jsonl | Tool | ⭐ MEDIUM | Reference |
| HARNESS_SCORECARD.md | Deep dive | ⭐ MEDIUM | 15 min |
| judge_results_*.json | Data | Reference | N/A |
| policy_violations.json | Data | Reference | N/A |
| README.md | Docs | As needed | 5 min |
| FILE_MANIFEST.md | Docs | As needed | 2 min |

---

## 🎯 Suggested Reading Path

### If you have 5 minutes:
1. DECISION_SUMMARY.txt (2 min)
2. violation_examples.md - just read the 3 violations (3 min)

### If you have 15 minutes:
1. DECISION_SUMMARY.txt (2 min)
2. GO_NO_GO_DECISION.md - Executive Summary + Policy Compliance sections (8 min)
3. prompt_v4.1_FIXED.md (3 min)
4. Run `python3 output/judge.py` (2 min)

### If you have 30 minutes:
1. QUICK_SUMMARY.md (2 min)
2. GO_NO_GO_DECISION.md (full read, 10 min)
3. violation_examples.md (5 min)
4. prompt_v4.1_FIXED.md (3 min)
5. HARNESS_SCORECARD.md (10 min)

### If you're implementing the fix:
1. DECISION_SUMMARY.txt (2 min)
2. prompt_v4.1_FIXED.md (3 min) - this is your starting point
3. golden_set.jsonl (2 min) - understand the test cases
4. judge.py (5 min) - understand how tests work
5. Run tests on your fixed version
6. violation_examples.md (5 min) - manually verify the 3 violations are fixed

---

## 🚀 Next Actions Checklist

For PM/Eng Team:

- [ ] Read DECISION_SUMMARY.txt
- [ ] Review prompt_v4.1_FIXED.md
- [ ] Decide: Fix & ship Tuesday OR pause & iterate OR revert
- [ ] If fixing: Re-run August tickets through v4.1
- [ ] Run judge.py on new outputs
- [ ] Manual review 10 random tickets for warmth
- [ ] Get Legal sign-off (internal notes handling)
- [ ] Get Finance sign-off (custom item refunds)
- [ ] Add judge.py to CI/CD pipeline
- [ ] Schedule follow-up to expand golden set to 20+ cases
- [ ] Schedule follow-up to add action safety gates (see HARNESS_SCORECARD)

---

## 📧 Stakeholder Communication

### For Leadership (CEO, VP):
Send: DECISION_SUMMARY.txt + 2-line email:
> "New prompt has great warmth (4.6/5 vs 2.8/5) but introduces 3 policy violations that could cost $5-10K/month. Recommend: delay Friday ship, fix today, ship Tuesday. Full details attached."

### For Legal:
Send: GO_NO_GO_DECISION.md + violation_examples.md (section on T-1016 internal notes leak)
> "Need sign-off on T-1016 handling. Bot revealed confidential 'abuse watchlist' note to customer. Fixed prompt ensures internal_notes never shared."

### For Finance:
Send: GO_NO_GO_DECISION.md + violation_examples.md (sections on T-1013, T-1026)
> "Need sign-off on custom item refund policy. New prompt incorrectly approved 2 custom refunds (~$1400). Fixed prompt enforces 'custom items not refundable for change of mind' rule."

### For Engineering:
Send: README.md + judge.py + golden_set.jsonl
> "Before shipping any future prompt changes, run judge.py. Expand golden_set.jsonl to 20+ cases. Add to CI/CD. See HARNESS_SCORECARD for infrastructure gaps."

---

**Total Files:** 13  
**Total Pages:** ~50  
**Test Cases:** 8 (expand to 20+)  
**Violations Found:** 3  
**Time to Review:** 5-30 min depending on depth needed  
**Time to Fix:** 2-3 days (includes testing + approvals)

---

**Audit Completed:** 2026-09-15  
**Methodology:** Harness-first (audit test infrastructure before blaming model)  
**Outcome:** NO-GO with clear path to YES-GO
