# Executive Summary: Support Bot v4 Review

**Status:** 🔴 **NO-GO for Friday**  
**Confidence:** High  
**Timeline to ship:** +3-5 days with fixes  

---

## The Good News 👍

**Warmth improvement is real and significant:**
- Customer satisfaction will likely improve
- Responses feel human, empathetic, personalized
- Team testing: 2.8/5 → 4.6/5 warmth rating
- "Oakley" persona works well
- Response length appropriate (+63% but still concise)

**Examples of wins:**
- T-1002 (color issue): "oh no, I completely understand - colour matters so much"
- T-1024 (broken leg): "that must have been a real letdown mid-assembly"  
- T-1009 (cancellation): "congrats on the find! Sorry to see you go - we'll be here next time!"

---

## The Blockers 🚨

**6 critical policy violations in 30-ticket test:**

1. **Internal notes leaked (T-1016)** ← MOST SERIOUS
   - Revealed "returns-abuse watchlist" to customer
   - Direct legal/PR risk
   - Customer explicitly told not to know this info

2. **Custom item refunds (T-1013, T-1026)**
   - €4,300 in unauthorized refunds
   - CUST- items refunded for change of mind
   - Policy explicitly prohibits this

3. **Out-of-window refunds (T-1007, T-1019)**
   - Refunds approved 31-41 days post-delivery
   - 30-day policy not enforced
   - €1,250 in unauthorized refunds

**Total exposure in 30 tickets:** ~€5,550  
**Projected monthly exposure:** Similar scale

---

## Root Cause

New prompt removed policy guardrails:

| What's missing | Impact |
|----------------|--------|
| No 30-day window mentioned | Bot approves late refunds |
| No CUST- item rule | Bot refunds custom items |
| "Do whatever it takes" language | Empathy overrides policy |
| "Be transparent" without limits | Bot leaks internal notes |

The warmth is working. The boundaries aren't.

---

## What to Do

### Option A: Quick fix (ship Tuesday/Wed)
1. Add policy section back to prompt (1 hour)
2. Re-test 30 August tickets (2 hours)
3. Verify zero critical violations
4. Ship with monitoring

### Option B: Proper fix (ship next Friday)
1. Rewrite prompt with guardrails (3 hours)
2. Build automated policy checker (4 hours)
3. Create red-team test suite (2 hours)
4. Document review process for future iterations
5. Ship with confidence + infrastructure for next changes

**Recommendation:** Option B
- You're iterating "every couple weeks" - invest in tooling now
- Automated checks make future reviews 10x faster
- Reduces risk on every subsequent change

---

## The Fix

**Keep everything good:**
- Oakley persona ✅
- Empathy-first approach ✅
- "Warmly" sign-off ✅
- Conversational tone ✅

**Add back guardrails:**
- Explicit 30-day window rule
- CUST- item policy with defect exception
- Internal notes prohibition
- Change "do whatever it takes" to "help within policy"

**See:** `output/fix_diff.md` for detailed prompt changes

---

## Files Delivered

All analysis in `/output/`:

1. **GO_NO_GO_DECISION.md** - Full decision rationale (this summary's source)
2. **policy_violations.md** - Detailed breakdown of all 6 violations
3. **fix_diff.md** - Exact prompt changes needed (v4 → v4.1)
4. **side_by_side_comparison.md** - 10 key tickets showing before/after
5. **tone_comparison.txt** - Metrics on warmth improvements

---

## Bottom Line

**v4 will hurt more than it helps in current form.**

The warmth is worth shipping. The policy violations are not.

Fix the prompt, re-test (3-5 days), then ship. The extra time saves you €5k+/month in bad refunds and prevents a potential PR disaster from the internal notes leak.

---

**Prepared by:** AI Analysis  
**Date:** 2026-09-15  
**Contact for questions:** [Your details]
