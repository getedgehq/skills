# 📁 Audit Deliverables Index

All files in `/home/user/work/output/`

## 🎯 Start Here

1. **EXECUTIVE_SUMMARY.txt** - One-page overview with decision
2. **README.md** - Complete guide to using these files
3. **violations_summary.txt** - Visual breakdown of failures

## 📋 Decision Documents

4. **GO_NO_GO_DECISION.md** - Full decision analysis with 3 options
5. **detailed_violations.md** - Line-by-line violation analysis with examples
6. **harness_scorecard.md** - Six-component harness maturity audit

## 🛠️ Tools & Artifacts You'll Use

7. **judge.py** ⭐ - Automated policy checker (executable)
   - Usage: `python3 judge.py tickets.jsonl outputs.jsonl`
   - Returns exit code 0 (pass) or 1 (fail)
   - CI/CD ready

8. **proposed_v4_fixed.md** - Fixed prompt that keeps warmth + adds guardrails
   - Test this version next
   - Should pass all judge.py checks

9. **golden_set_template.jsonl** - Expected answer structure for test cases
   - Expand to full 30 tickets for sustainable testing
   - Documents what "correct" looks like per scenario

## 📊 Analysis Scripts

10. **cost_analysis.md** - Token/cost impact (54% longer, ~£1-5/month)
11. **analysis.py** - One-time audit script used for this review
12. **detailed_violations.py** - Helper script for violation reporting

## 📈 Key Metrics Summary

| Metric | Old Prompt | New Prompt | Change |
|--------|-----------|-----------|--------|
| Policy pass rate | 96.7% (29/30) | 90.0% (27/30) | -6.7% ❌ |
| Critical violations | 1 | 3 | +2 ❌ |
| Warmth survey | 2.8/5 | 4.6/5 | +64% ✅ |
| First name usage | 0% | 100% | +100% ✅ |
| Empathy phrases | ~20% | 70% | +50% ✅ |
| Reply length | 141 chars | 219 chars | +54% |
| Estimated cost | baseline | +£1-5/mo | negligible |
| Financial risk | low | £167k/mo | CRITICAL ❌ |

## 🚦 Decision

**NO-GO for Friday ship**

**Recommended path:** Fix prompt → test with judge.py → ship Monday

## 💬 Three Key Takeaways

1. **The warmth is real and valuable** - Your intuition was right
2. **The violations are fixable** - Small prompt changes restore safety
3. **The judge prevents future issues** - Run on every change going forward

---

Generated: 2026-09-16  
Method: Harness-first audit  
Status: Complete
