# Support Bot v4 Analysis - File Index

## Start Here

1. **EXEC_BRIEF.md** - For Lena (PM): NO-GO decision + what to do next
2. **go_no_go.md** - Executive summary with timeline
3. **README.md** - Quick reference guide

## The Problems

4. **side_by_side_violations.txt** - All 4 violations shown side-by-side (easiest to read)
5. **violations_detail.jsonl** - Same violations in JSON format
6. **detailed_analysis.md** - Deep dive with financial impact

## The Solution

7. **new_prompt_FIXED.md** - Recommended fixed prompt (ready to use)
8. **good_examples.md** - Examples of warmth to preserve
9. **test_prompt.py** - Reusable testing script for future changes

## Raw Data

10. **analysis_summary.txt** - Console output from full analysis

---

## Quick Facts

- **Violations found:** 4 out of 30 tickets (13.3%)
- **Types:** 2× custom item refunds, 1× outside window, 1× exposed internal notes
- **Estimated annual loss:** £500k-1.4M if shipped as-is
- **Fix time:** 2-3 hours
- **Recommended action:** Don't ship Friday, fix + re-test, ship Monday

## The Fix in 3 Bullets

1. Add "Policy Guardrails (NON-NEGOTIABLE)" section to new prompt
2. Explicitly check: 30-day window, CUST- SKUs, internal notes firewall
3. Keep all the warmth (it's genuinely good!)

See: `new_prompt_FIXED.md`

---

All files generated: 2026-09-16
Analysis covered: August 2026 tickets (30 total)
