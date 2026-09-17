# Support Bot v4 "Warmth" Prompt - Audit Results

**Audit Date:** 2026-09-15  
**Auditor:** AI Safety Review  
**Proposed Ship:** Friday 2026-09-20 9am  
**Decision:** 🛑 **NO-GO**

---

## Start Here

1. **Read first:** [SUMMARY.md](SUMMARY.md) - 2-minute overview
2. **Full analysis:** [GO_NO_GO_DECISION.md](GO_NO_GO_DECISION.md) - Complete findings and recommendations
3. **See the violations:** [violations_detail.md](violations_detail.md) - Side-by-side comparison of what went wrong

## What You Need to Do

1. **Don't ship the v4 draft** - it has critical policy violations
2. **Use the fixed version** - [SUGGESTED_v4_REVISION.md](SUGGESTED_v4_REVISION.md) keeps the warmth, adds back safety
3. **Run the checker** - Use `check_policies.py` on every prompt change going forward

## Tools Provided

### Immediate Use
- **SUGGESTED_v4_REVISION.md** - Fixed prompt (warmth + policy compliance)
- **check_policies.py** - Policy compliance checker
  - Run: `python3 check_policies.py` (edit paths to point to your new outputs)
  - Checks: custom item refunds, 30-day windows, internal note leaks, escalations
  - Returns: Pass/fail + violation details

### Analysis (if you want to dig deeper)
- **policy_violations.json** - Machine-readable violation data
- **violations_detail.md** - Detailed side-by-side of the 3 worst violations
- **harness_audit.py** - Test coverage and methodology analysis

## The Core Problem

Your new prompt said:
- ❌ "Do whatever it takes to make it right"
- ❌ "Be transparent: share what you can see"
- ❌ Removed: "follow policies/refunds.md exactly"
- ❌ Removed: "Never quote or reveal internal_notes"

The model did exactly what you asked - prioritized warmth over policy. This isn't a model problem, it's a prompt problem.

## The Fix

The revised prompt:
- ✅ Keeps "Oakley" persona and warm, empathetic tone
- ✅ Adds back "follow policies/refunds.md exactly"
- ✅ Adds back "never mention internal_notes"
- ✅ Clarifies that "delight" means getting things right, not saying yes to everything

## Next Prompt Change

Before you ship the next iteration:

1. Run your warmth eval (keep doing this!)
2. **Also run** `check_policies.py` (new requirement)
3. Both must pass
4. Then ship

This way you can iterate on tone/warmth safely, knowing you won't violate policies.

## Questions?

- Why did this happen? See "Root Cause Analysis" in GO_NO_GO_DECISION.md
- What's a harness? See "Harness Scorecard" section
- Can I still improve warmth? Yes! Just keep the policy guardrails
- How often should I check? On every prompt change, before shipping

---

**Bottom line:** You were right to test before shipping, and you were right that warmth matters. You just needed to test the right things. Now you have the tools to do both.
