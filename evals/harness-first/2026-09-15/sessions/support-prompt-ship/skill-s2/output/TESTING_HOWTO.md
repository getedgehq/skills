# How to Test Future Prompt Changes (Quick Start)

This testing harness was built during the v3→v4 audit. Use it every time you change the prompt.

---

## 🚀 Quick Test (2 minutes)

Every time you edit the prompt:

```bash
# 1. Generate outputs with new prompt
python your_bot.py --prompt new_version.md --input tickets.jsonl > outputs_test.jsonl

# 2. Run the policy judge
python3 output/judge.py outputs_test.jsonl

# 3. Check result
# Exit code 0 = pass (no critical violations)
# Exit code 1 = fail (blocking issues found)
```

**Shipping rule:** Don't ship if judge fails.

---

## 📋 What the Judge Checks (Critical Policies)

The automated judge (`output/judge.py`) validates:

1. ✅ **Custom items** (SKU starts with CUST- or CUS-) are NOT refunded for change of mind
2. ✅ **30-day window** is enforced (no refunds outside calendar days from delivery)
3. ✅ **Chargeback/legal threats** are escalated to Tier 2 (not handled directly)
4. ✅ **Internal notes** are never exposed to customers
5. ✅ **Unkeepable promises** are avoided (no "immediately", "guaranteed", etc)

If any critical check fails → blocking, don't ship.

---

## 📊 Golden Set (Test Cases)

Located in: **`output/golden_set.jsonl`**

Currently contains **8 test cases**:
- 4 critical policy enforcement cases (custom items, 30-day window, escalation, confidentiality)
- 4 standard customer service cases (defects, valid returns, delays, cancellations)

### Expand the golden set

Add edge cases to `golden_set.jsonl`:
- Day 28, 30, 31, 32 refund requests (boundary testing)
- Custom item defects (should get replacement)
- Multi-issue tickets (defect + angry + wants refund)
- Ambiguous escalation terms ("dispute" vs "chargeback")

**Target:** 20-30 cases covering all policy branches.

Format:
```json
{
  "ticket_id": "T-XXXX",
  "category": "descriptive_name",
  "ticket": { /* full ticket JSON */ },
  "expected_constraints": [
    "MUST do X",
    "MUST NOT do Y",
    "SHOULD explain Z"
  ],
  "rationale": "Why this case matters"
}
```

---

## 🔧 Judge Script Details

**File:** `output/judge.py`

**Checks:**
- ❌ Custom item refunds (SKU prefix + change of mind detection)
- ❌ Out-of-window refunds (date math)
- ❌ Missing escalation (keyword detection: chargeback, lawyer, legal)
- ❌ Internal notes leaks (phrase matching from internal_notes field)
- ⚠️  Risky promises (keyword detection: immediately, guaranteed, etc)

**Output:**
- Prints pass/fail per ticket
- Summary with critical failure count
- Saves detailed results to `output/judge_results_*.json`
- Exit code 1 if any critical failures

**Extend the judge:**
Edit `output/judge.py`, add new check functions:
```python
def check_your_policy(ticket, reply):
    """Check if reply violates your new policy"""
    if some_violation_detected:
        return True, "Description of violation"
    return False, None
```

Add to the `checks` list in the main loop.

---

## 📈 Metrics Tracking

**File:** `output/metrics.py`

Tracks quantitative changes between prompts:
- Reply length (chars, words)
- First name usage
- Empathy/apology phrase frequency
- Emoji usage

Run to compare old vs new:
```bash
python3 output/metrics.py
```

Use this to track if changes increase/decrease verbosity, warmth, etc.

---

## 🎯 Workflow for Every Prompt Change

### Before you start
1. Decide what you're changing and why
2. Add a test case to `golden_set.jsonl` if it's a new scenario
3. Run current prompt through judge to establish baseline

### Make the change
1. Edit the prompt file
2. Generate new outputs: `python bot.py > outputs_new.jsonl`
3. Run judge: `python3 output/judge.py outputs_new.jsonl`
4. If judge fails: fix prompt, goto step 1
5. If judge passes: continue to manual review

### Manual review (when judge passes)
1. Run metrics: `python3 output/metrics.py` - check for unexpected changes
2. Review 5-10 random replies side-by-side for tone/quality
3. Pay special attention to tickets that used to fail but now pass (verify they're actually correct)

### Ship decision
- ✅ Judge passes (0 critical failures)
- ✅ Metrics are expected (no surprise 3x length increase)
- ✅ Manual review looks good
- ✅ PM/stakeholder approval

→ Ship it

### After shipping
1. Monitor real traffic for unexpected issues
2. If issues found, add them to golden_set.jsonl
3. Re-run judge on production outputs weekly

---

## 🔍 Debugging Failed Cases

When judge reports a failure:

```
❌ CRITICAL: Offers refund for custom item change-of-mind
   Ticket: T-1002
```

1. **Look at the ticket:**
   ```bash
   cat tickets.jsonl | jq 'select(.ticket_id == "T-1002")'
   ```

2. **Look at the reply:**
   ```bash
   cat outputs_new.jsonl | jq 'select(.ticket_id == "T-1002") | .reply'
   ```

3. **Understand why it failed:**
   - What constraint was violated?
   - Which part of the prompt caused this?
   - Is it the prompt wording, or the data, or the policy ambiguity?

4. **Fix in order of preference:**
   - **Best:** Fix the data (add computed fields like `refund_eligible: false`)
   - **Good:** Make policy explicit in prompt ("MUST NOT refund if SKU starts with CUS-")
   - **OK:** Rephrase prompt instruction that caused the issue

5. **Re-test:**
   ```bash
   python bot.py > outputs_fixed.jsonl
   python3 output/judge.py outputs_fixed.jsonl
   ```

---

## 📁 Files Reference

```
output/
├── GO_NO_GO_DECISION.md           # Main audit report
├── critical_failures_sidebyside.md # Detailed failure analysis
├── recommended_prompt_v3.5.md      # Quick-fix hybrid prompt
├── golden_set.jsonl                # Test cases with expected behavior
├── judge.py                        # Automated policy checker
├── judge_results_outputs_old.json  # Old prompt test results
├── judge_results_outputs_new.json  # New prompt test results
├── metrics.py                      # Quantitative comparison script
└── policy_violations.json          # Full list of detected issues
```

---

## 🚨 Red Flags (Stop and Fix)

If you see any of these, don't ship:

1. **Judge fails** - Critical policy violations detected
2. **Reply length doubles** - Token cost will double (check if you have budget)
3. **Empathy goes to 0** - You made it too robotic
4. **Internal notes mentioned** - Confidentiality breach
5. **"I've gone ahead and approved"** - Unauthorized action claims
6. **Promises with "immediately", "guaranteed"** - Will create escalations when not met

---

## 💡 Pro Tips

1. **Run judge in CI/CD** - Make it block deploys on failure
2. **Version your prompts** - Keep v3.md, v3.5.md, v4.md in git
3. **Track metrics over time** - Create a CSV of length/warmth/violations per version
4. **Test on prod data weekly** - Catch drift and new edge cases
5. **Golden set > 20 cases** - Current 8 is minimum, 20-30 is comfortable
6. **Add LLM-as-judge for tone** - Deterministic checks catch policy, LLM checks catch tone/quality
7. **Cost cap per conversation** - If using this in a loop, add max tokens limit

---

## 🆘 Need Help?

If something's unclear:

1. Read the main report: `output/GO_NO_GO_DECISION.md`
2. Check detailed failures: `output/critical_failures_sidebyside.md`
3. Look at golden set examples: `output/golden_set.jsonl`
4. Review judge logic: `output/judge.py`

The harness is designed to be self-documenting. All checks are explicit, all failures show the ticket ID and reason.

---

## Next Steps (Recommended)

1. **This week:** Implement Option A (v3.5) and ship safely
2. **Next week:** Expand golden set to 20 cases
3. **Next sprint:** Add LLM-as-judge for warmth scoring
4. **Next month:** Add cost monitoring and per-conversation caps

The goal: **every prompt change takes 30 minutes to validate, not 3 days of manual testing.**

You now have a systematic way to improve the bot without breaking policies. Use it!
