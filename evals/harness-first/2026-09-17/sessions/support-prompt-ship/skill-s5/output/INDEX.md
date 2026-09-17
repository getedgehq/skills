# Support Bot Prompt v4 Evaluation - File Index

## Start Here

1. **EXECUTIVE_SUMMARY.txt** - Visual summary, key numbers, decision
2. **GO_NO_GO_DECISION.md** - Full decision document with evidence and recommendations
3. **QUICK_REFERENCE.md** - Fast action guide with copy-paste fix

## Supporting Documentation

### Analysis
- **harness_scorecard.md** - Audit of 6 harness components (17/60 score)
- **side_by_side_violations.md** - Detailed violation examples with reply text
- **README.md** - Overview of all files and how to use them

### Data
- **violations_detailed.json** - Raw violation data (both prompts)
- **outputs_old_judge_results.json** - Judge results for old prompt (7 pass, 8 fail)
- **outputs_new_judge_results.json** - Judge results for new prompt (6 pass, 9 fail)

## Tools (Use on Every Prompt Change)

### Core Tools
- **judge.py** - Automated policy checker
  ```bash
  ./judge.py golden_set.jsonl your_outputs.jsonl
  ```
  
- **golden_set.jsonl** - 15 test cases with must-have/must-not constraints
  - 5 CRITICAL tests (custom items, internal notes)
  - 6 HIGH tests (legal, 30-day window, damaged custom)
  - 4 LOW tests (standard operations)

- **audit_script.py** - Detailed violation detector (used to generate initial analysis)

## Quick Links to Key Violations

In **side_by_side_violations.md**:
- T-1013: Custom wardrobe refund (should deny)
- T-1026: Custom bookshelf refund (should deny)
- T-1016: Internal notes leak ("abuse watchlist" revealed)
- T-1007, T-1019: Refunds outside 30-day window

## Workflow for Next Prompt Change

```bash
# 1. Edit prompt
vim new_prompt_v5.md

# 2. Generate outputs
python bot.py new_prompt_v5.md tickets.jsonl > outputs_v5.jsonl

# 3. Run judge
cd output
./judge.py golden_set.jsonl ../outputs_v5.jsonl

# 4. Check results
# Must see: 0 CRITICAL failures
# Target: 15 PASS, 0 FAIL

# 5. If failures:
#    - Read judge output to see which tests failed
#    - Fix prompt
#    - Repeat from step 2
```

## File Sizes

```
EXECUTIVE_SUMMARY.txt (3KB)    - Read in 2 min
QUICK_REFERENCE.md (3KB)       - Read in 3 min
GO_NO_GO_DECISION.md (9KB)     - Read in 10 min
harness_scorecard.md (4KB)     - Reference
side_by_side_violations.md (4KB) - Reference
```

## What Each Tool Does

| Tool | Purpose | When to Use |
|------|---------|-------------|
| judge.py | Pass/fail on constraints | Every prompt change |
| audit_script.py | Deep policy analysis | Initial audit, debugging |
| golden_set.jsonl | Test case definitions | Add cases as you find new issues |

## Adding New Test Cases

When you find a new issue:
1. Add ticket to golden_set.jsonl
2. Define must_have/must_not phrases
3. Set criticality (CRITICAL/HIGH/LOW)
4. Re-run judge to validate

Example:
```json
{
  "ticket_id": "T-XXXX",
  "description": "Description of what this tests",
  "must_have": ["phrases that must appear"],
  "must_not": ["phrases that must not appear"],
  "policy_test": true,
  "criticality": "CRITICAL"
}
```

## Questions or Issues?

See "Questions I Couldn't Answer" section in GO_NO_GO_DECISION.md
