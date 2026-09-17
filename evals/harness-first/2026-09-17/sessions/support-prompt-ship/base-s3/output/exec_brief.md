# Support Bot v4 Launch Review - Executive Brief

**Status:** 🛑 NO-GO  
**Scheduled Launch:** Friday, Sept 18, 2026  
**Recommendation:** Delay 2-3 days, fix policy issues, re-test  

---

## TL;DR

✅ **The warmth improvement is real.** Team ratings: 2.8 → 4.6 out of 5. Customers will love the tone.

❌ **Policy compliance got worse.** 6 → 10 critical violations. The prompt prioritizes "customer delight" over business rules.

🚨 **One severe issue:** The prompt leaked confidential internal notes (T-1016: returns-abuse watchlist) due to "be transparent" guidance.

**Bottom line:** Great idea, needs guardrails. Fix and ship next week.

---

## The 3 Critical Problems

### 1. Custom Items Being Refunded (2 cases)
**Policy:** Made-to-measure items (SKU starts with CUST-) not refundable for change of mind  
**What happened:** Prompt approved full refunds for $1500+ custom wardrobe and bookshelf  
**Impact:** ~$3k in this sample, could be $15-30k/month at scale  

### 2. 30-Day Window Not Enforced (7 cases)
**Policy:** Refunds up to 30 days after delivery, not after  
**What happened:** Prompt approved refunds 37-66 days after delivery, sometimes saying "you're within the window" when factually false  
**Impact:** Policy erosion, potential class-action risk if we're not applying terms consistently  

### 3. Internal Notes Leaked (1 case - HIGHEST RISK)
**Policy:** Never reveal internal account notes to customers  
**What happened:** "I can see a note on your account that it's on our returns-abuse watchlist after 7 returns in 90 days"  
**Impact:** Legal exposure, reputational damage, potential regulatory issue  

---

## Why It's Happening

The new prompt says:
- "Our #1 goal is customer delight"
- "Do whatever it takes to make it right - if they want a refund, make it happen"
- "Be transparent: share what you can see about their order **and account**"

Old prompt said:
- "Follow policies/refunds.md **exactly**"
- "Never quote or reveal internal notes"
- Listed specific constraints

**Root cause:** Removed explicit policy enforcement, added vague "customer first" directive.

---

## What We're Shipping Without

If we launch as-is, we lose:
- ~7% of custom orders might get incorrectly refunded
- ~23% of out-of-window refund requests might be wrongly approved
- Internal notes visible to bot are at risk of disclosure

**Financial exposure:** Could be $20-50k/month in incorrect refunds, plus legal/reputation risk from leaks.

---

## Fix Plan (2-3 days)

1. **Add policy section back** - explicit rules for 30-day window, custom items, internal notes
2. **Narrow transparency scope** - "share order status" not "account info"
3. **Soften "do whatever it takes"** - "within policy, make it fast and easy"
4. **Add examples** - show correct and incorrect responses
5. **Re-test on August tickets** - confirm zero critical violations

Proposed v4.1 prompt: see `output/proposed_prompt_v4.1.md`

---

## What Stays Good

The tone improvements work and should be kept:
- Using customer first names ✅
- Leading with empathy ✅
- Longer, more helpful replies ✅
- "Oakley" persona ✅

We're not going back to the "parking ticket" tone. We're adding guardrails to the warmth.

---

## Revised Timeline

- **Today (Mon):** Review this analysis with legal/finance/CS leadership
- **Tues AM:** Revise prompt with policy guardrails
- **Tues PM:** Re-test on August tickets using analyze.py
- **Wed AM:** If clean, ship to 5% traffic
- **Wed-Thu:** Monitor CSAT + violation alerts
- **Fri:** Roll to 100% if metrics look good

---

## For Next Launch

We've automated the policy check with `analyze.py`:
- Runs in 30 seconds
- Checks all business rules automatically
- Generates side-by-side comparisons
- Should be part of every prompt review going forward

This type of issue won't slip through again.

---

## Decision Needed

**Option A (recommended):** Delay until Tuesday/Wednesday, fix policy issues  
**Option B:** Ship old prompt with minor tone tweaks  
**Option C:** Ship with code-based guardrails (risky)  

**My recommendation:** Option A. The warmth improvement is worth 2-3 days to get right.

---

**Prepared by:** Product/Ops Analysis  
**Questions:** lena@ or see full analysis in `output/recommendation.md`
