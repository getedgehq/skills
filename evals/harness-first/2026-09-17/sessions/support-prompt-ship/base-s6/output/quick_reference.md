# Quick Reference: Prompt Performance

## Overall Stats

| Metric | Old (v3) | New (v4) | Status |
|--------|----------|----------|--------|
| **Tone: Contains "sorry"** | 3% | 57% | ⭐ HUGE WIN |
| **Tone: Empathy phrases** | 0% | 17% | ⭐ WIN |
| **Tone: Avg word count** | 25 | 41 | ⭐ WIN |
| **Policy: Custom refund violations** | 0 | 2 | 🚨 BLOCKER |
| **Policy: Escalation handling** | 1 miss | 0 miss | ⭐ WIN |
| **Policy: Defect handling (custom)** | WRONG | RIGHT | ⭐ WIN |

## The Problem

**New prompt instruction:**
> "If a customer is unhappy, do whatever it takes to make it right - if they want a refund, make it happen quickly"

**Result:** Bot offers refunds on custom furniture when customers express disappointment, even though policy prohibits this.

**Financial impact:** ~$2k-5k per inappropriate custom refund

## The Fix

**Revised instruction:**
> "Our #1 goal is customer delight, within our policies. If a customer is unhappy and a refund is allowed by policy, make it happen quickly and warmly."

**Plus:** Add explicit custom item policy back to prompt.

## Critical Test Cases

| Ticket | Scenario | Old | New (v4) | Fixed? |
|--------|----------|-----|----------|--------|
| T-1013 | Custom item, change of mind | ✅ Denies | ❌ Refunds | Need to test |
| T-1026 | Custom item, doesn't match | ✅ Denies | ❌ Refunds | Need to test |
| T-1029 | Custom item, defect | ❌ Denies | ✅ Repairs | Should stay good |
| T-1002 | Standard, color issue | ✅ Refunds | ✅ Refunds warmly | Should stay good |
| T-1011 | Chargeback threat | ❌ Misses | ✅ Escalates | Should stay good |

## Recommendation

**NO-GO on Friday ship**

**Timeline to fix:**
- Wed 9/17: Revise prompt (done - see `new_prompt_FIXED.md`)
- Thu 9/18: Re-run 30 tickets through fixed prompt
- Fri 9/19: Verify T-1013 & T-1026 now deny refunds correctly while keeping warmth
- Mon 9/22: Ship if tests pass

**Alternative:** Ship with manual review of all custom refunds (not recommended - defeats automation purpose)
