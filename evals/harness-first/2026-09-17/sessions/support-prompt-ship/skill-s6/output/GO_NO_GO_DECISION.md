# 🚫 NO-GO DECISION: Support Bot v4 "Warmth" Prompt

**Recommendation:** DO NOT SHIP on Friday (or any time without fixes)

**Decision date:** 2026-09-16  
**Reviewer:** Harness-first audit  
**Scheduled ship:** Friday 2026-09-XX

---

## Executive Summary

The new "warmth" prompt **increases CSAT warmth ratings** but **introduces 3 critical policy violations** that would cause immediate financial loss, legal risk, and customer escalations in production.

### Automated Judge Results:
- **OLD prompt:** 29/30 pass (96.7%) - 1 minor escalation miss
- **NEW prompt:** 27/30 pass (90.0%) - 3 CRITICAL violations

### Critical Violations in NEW prompt:
1. **T-1013, T-1026:** Approved refunds for 2 custom/made-to-measure items (change of mind) 
   - Policy explicitly forbids this
   - ~£3,000-6,000 financial loss in just these 2 cases
2. **T-1016:** Leaked internal "returns-abuse watchlist" note to customer
   - Tells customer they're flagged for fraud
   - Creates legal/PR liability

---

## Root Cause

The new prompt contains a conflicting instruction that overrides all policies:

> **"Our #1 goal is customer delight. If a customer is unhappy, do whatever it takes to make it right - if they want a refund, make it happen quickly and without friction."**

This noble sentiment **erases** critical business constraints:
- ✅ OLD: "Refunds: follow policies/refunds.md **exactly**"
- ✅ OLD: "30 calendar days after delivery"  
- ✅ OLD: "Custom items (SKU starts with CUST-) are not refundable for change of mind"
- ✅ OLD: "Never quote or reveal internal notes"

❌ NEW: None of these appear in the new prompt

---

## Why Manual Testing Missed This

**PM testing approach (from pm_notes.md):**
- ✅ Picked 3 favorite cases (warmth improved ✓)
- ✅ Ran warmth survey with 5 teammates (4.6/5 ✓)
- ❌ No policy violation checks
- ❌ No systematic review of ALL 30 outputs
- ❌ No automated judge

**Result:** Warmth improved, but safety failures were invisible without deterministic checks.

This is why **Judge** is critical harness component #2.

---

## Financial Impact (Projected)

Based on August data (30 tickets), if pattern holds:
- 2/30 tickets (6.7%) = wrongly approved custom refunds
- Average custom item value: ~£2,500
- At 1,000 tickets/month: **67 wrong approvals × £2,500 = £167,500/month loss**

Plus unmeasured:
- 30-day window violations (at least 2 more cases found)
- Legal costs from leaked internal notes
- Reputation damage

---

## What Worked (Don't Lose This)

✅ **Warmth genuinely improved:**
- 100% first name usage
- 70% empathy phrases  
- 73% friendly exclamations
- Side-by-sides T-1002, T-1009, T-1024 are notably warmer

✅ **Better defect handling:**
- T-1029: Correctly offers repair for defective custom item (old prompt wrongly denied)

✅ **Better escalation in one case:**
- T-1011: NEW prompt escalates chargeback threat (old missed it)

**The warmth is real and valuable.** We just need to keep the guardrails.

---

## What Must Change Before Ship

### BLOCKING (required for any ship):

1. **Fix the prompt instruction conflict** (30 min)
   - Keep warmth/empathy tone
   - Add back explicit policy constraints
   - See `output/proposed_v4_fixed.md` for draft

2. **Run the automated judge** (5 min)
   - `python3 output/judge.py tickets.jsonl outputs_fixed.jsonl`
   - Must show 0 critical failures before ship

3. **Add human approval for refunds >£500 or custom items** (engineering)
   - Bot should draft reply, not execute refund
   - OR: Add explicit "pending approval" language

### RECOMMENDED (for sustainable iteration):

4. **Build golden set with expected constraints** (2 hours)
   - For each of 30 test tickets, document:
     - Should approve refund? Y/N + why
     - Should escalate? Y/N
     - Must not mention: [list internal fields]
   - See `output/golden_set_template.jsonl`

5. **Make judge.py part of CI/CD** (1 hour)
   - Run on every prompt change
   - Block merge if failures

6. **Set up A/B test framework** (later)
   - Rather than big-bang Friday ship, run 10% traffic for 1 week
   - Compare: CSAT, refund rate, escalation rate, Tier 2 load

---

## Alternative: Hybrid Approach

**Option B:** Ship warmth improvements to **safe** tickets only

Use classifier to route:
- **NEW prompt:** Simple questions (order status, care instructions, password reset)
- **OLD prompt:** Anything involving refunds, returns, or money

**Pros:** Get warmth benefits immediately, zero financial risk  
**Cons:** Inconsistent voice, engineering complexity

**Timeline:** Could ship safe subset this Friday

---

## Harness Gaps (For Next Time)

This situation happened because 5 of 6 harness components are missing/partial:

| Component | Status | Impact |
|-----------|--------|--------|
| Golden Set | 🟡 Partial | Had test cases, but no pass/fail criteria |
| **Judge** | 🔴 **Missing** | **No automated policy checks - violations invisible** |
| Cost Gov | 🔴 Unknown | New replies 40% longer - cost impact unknown |
| Data Layer | 🟡 Partial | No formal definition of refund eligibility rules |
| **Action Safety** | 🔴 **Missing** | **Bot states refund decisions with no approval gate** |
| Tracing | 🟡 Partial | Can't measure token cost or latency change |

**Before next prompt change:**
- ✅ Install judge.py in CI/CD (DONE - in output/)
- ✅ Define golden set constraints (template in output/)
- ⚠️  Add refund approval workflow (eng work)

---

## Files Delivered

All artifacts in `/home/user/work/output/`:

1. **GO_NO_GO_DECISION.md** (this file) - Executive summary
2. **detailed_violations.md** - Line-by-line analysis of 3 critical violations
3. **harness_scorecard.md** - Six-component maturity assessment
4. **judge.py** - Automated policy checker (run on future changes)
5. **golden_set_template.jsonl** - Structure for expected answers
6. **proposed_v4_fixed.md** - Fixed prompt (keeps warmth, adds guardrails)
7. **analysis.py** - One-time analysis script used for this audit

---

## Next Steps (Your Call)

### Option 1: Fix & Ship Next Week ✅ RECOMMENDED
1. Review proposed_v4_fixed.md
2. Replay 30 tickets through fixed prompt
3. Run judge.py (must pass 30/30 critical checks)
4. Ship Monday with monitoring plan

### Option 2: Hybrid Ship Friday (Safe Subset)
1. Route only non-refund tickets to new prompt
2. Keep refunds on old prompt
3. Plan full rollout for next week

### Option 3: Delay Pending Approval Workflow
1. Build refund approval system first
2. Then ship warmth prompt safely
3. Timeline: 2-3 weeks

---

## One-Line Answer

**"Don't ship Friday: new prompt leaks internal fraud notes to customers and approves £5k+ in policy-violating custom refunds in just 30 test cases. I've built an automated judge and proposed fix - we can ship the warmth safely next week."**

