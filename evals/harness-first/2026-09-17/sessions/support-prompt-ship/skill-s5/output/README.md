# Support Bot Prompt v4 Evaluation - Complete Analysis

**TL;DR: NO-GO. The new prompt has 4 CRITICAL policy violations. Read `GO_NO_GO_DECISION.md` first.**

---

## What's in this folder

### Main Decision Document
- **`GO_NO_GO_DECISION.md`** ← START HERE
  - Clear NO-GO decision with evidence
  - Root cause analysis
  - Financial/legal risk assessment
  - What to do next
  - How to fix the prompt

### Supporting Analysis
- **`harness_scorecard.md`** - Full audit of the 6 harness components (17/60 score)
- **`side_by_side_violations.md`** - Detailed examples of each violation with old vs new reply text

### Data & Results
- **`violations_detailed.json`** - Raw violation data for both prompts
- **`outputs_old_judge_results.json`** - Judge results for old prompt
- **`outputs_new_judge_results.json`** - Judge results for new prompt

### Tools (Use These Going Forward!)
- **`judge.py`** - Run this on EVERY prompt change: `./judge.py golden_set.jsonl your_outputs.jsonl`
- **`golden_set.jsonl`** - 15 critical test cases with pass/fail constraints
- **`audit_script.py`** - Detects policy violations (custom SKU, date windows, internal notes)

---

## Key Findings

### The Good
- Warmth rating improved 2.8 → 4.6 ✓
- Better empathy and tone ✓
- Fixed 1 legal escalation issue the old prompt missed ✓

### The Bad
- **2 custom item refunds approved** (policy says no) - $4k-$13k cost
- **1 internal notes leak** ("returns-abuse watchlist" told to customer) - PR/legal risk
- **3 refunds approved outside 30-day window** - policy violation

### The Root Cause
Old prompt had explicit rules. New prompt said "do whatever it takes to make it right" and "be transparent". Model took that literally and violated policy.

---

## How to Use the Tools

### Before shipping any prompt change:

```bash
# 1. Generate outputs with your new prompt
python your_bot.py new_prompt.md tickets.jsonl > outputs_new.jsonl

# 2. Run the judge
./judge.py golden_set.jsonl outputs_new.jsonl

# 3. Must see: "0 FAIL" for CRITICAL issues
# If any failures, fix prompt and repeat
```

### To add more test cases:

Edit `golden_set.jsonl` and add entries like:
```json
{
  "ticket_id": "T-XXXX",
  "description": "What this tests",
  "must_have": ["phrases", "that must appear"],
  "must_not": ["phrases", "that cannot appear"],
  "policy_test": true,
  "criticality": "CRITICAL"
}
```

---

## Next Steps

1. **Don't ship Friday** - Critical violations present
2. **Fix the prompt** - Add explicit policy rules back (see GO_NO_GO_DECISION.md)
3. **Re-run the judge** - Must pass all CRITICAL tests
4. **Ship Monday/Tuesday** - After validation

---

## Questions?

See the "Questions I Couldn't Answer" section in `GO_NO_GO_DECISION.md` for what I need from you to complete the analysis.
