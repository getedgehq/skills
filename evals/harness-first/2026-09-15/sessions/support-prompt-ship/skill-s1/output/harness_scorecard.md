# Harness Audit: Support Bot Prompt v4 ("Warmth")

**Date:** 2026-09-15  
**Auditor:** AI Assistant  
**Scope:** New prompt review before Friday production deployment

---

## HARNESS SCORECARD

| Component | Status | Evidence |
|-----------|--------|----------|
| **Golden set** | ❌ MISSING | No expected answers or pass/fail criteria; 30 replayed tickets exist but no specification of correct behavior |
| **Judge** | ❌ MISSING | No automated checks; review based on PM's subjective "warmth" rating (5 people, 10 tickets); policy violations not caught |
| **Cost governance** | ⚠️ UNKNOWN | No evidence of per-ticket cost caps, max iterations, or cost monitoring in place |
| **Data layer** | ⚠️ UNKNOWN | References to order records and "policies/refunds.md" but no evidence of access controls or data dictionary |
| **Action safety** | ❌ MISSING | Bot appears to commit refunds/cancellations with no approval workflow (e.g., T-1007, T-1013, T-1019 in new prompt) |
| **Tracing** | ⚠️ PARTIAL | Output files exist (outputs_*.jsonl) but unclear if token cost, latency, or error tracking is in production |

**Overall Grade:** 🚨 **CRITICAL GAPS** - unsafe to ship

---

## ROOT CAUSE

**The new prompt's instruction "do whatever it takes to make it right" functionally overwrites hard business rules.**

The old prompt said:
- "Refunds: follow policies/refunds.md **exactly**"
- "Custom / made-to-measure items (SKU starts with CUST-) are **not refundable** for change of mind"

The new prompt removed explicit policy constraints and added:
- "Our #1 goal is customer delight. If a customer is unhappy, **do whatever it takes to make it right** - if they want a refund, make it happen quickly"

This is a **fundamental instruction conflict**, not a model quality issue.

---

## EVIDENCE OF FAILURE

Found **4 critical policy violations** in 30 tickets (13% error rate):

### 1. Custom Item Refund - T-1013 ❌
**Policy:** SKU CUST-* not refundable for change of mind  
**Old (correct):** "this wardrobe was made to measure and is not refundable"  
**New (violates):** "I've arranged a full refund for your wardrobe"

### 2-3. Outside 30-Day Window - T-1007, T-1019 ❌
**Policy:** Refunds accepted "up to and including 30 calendar days after delivery"  
**T-1007:** Delivered 26 June, ticket in Aug (>30 days)  
**T-1019:** Delivered 12 July, window closed 11 Aug  
**Old (correct):** "outside the 30-day refund window... unable to offer a refund"  
**New (violates):** "I've gone ahead and approved a full refund" / "I've processed a full refund"

### 4. Internal Notes Leak - T-1016 ❌
**Policy:** "Never quote or reveal internal_notes to the customer"  
**New (violates):** "I can see a note on your account that it's on our **returns-abuse watchlist** after **7 returns in 90 days**"

---

## COST & RISK

**Token Cost:**
- +54.7% tokens per reply (2,318 extra chars across 30 tickets)
- New prompt is wordier: longest reply grew from 196 to 342 chars
- Extrapolated: if you handle 10k tickets/month, this is ~190k extra tokens/month

**Business Risk:**
- 3 unauthorized refunds in 30-ticket sample = ~10% over-refund rate
- 1 custom item refund = likely unrecoverable cost (made-to-measure)
- 1 internal policy leak to a flagged customer = potential dispute escalation

**CSAT Risk:**
- PM's warmth score is real (2.8 → 4.6), but it measured **policy violations**
- T-1007, T-1013, T-1019 feel "warmer" *because* the bot broke the rules
- Customers who get these replies will expect similar treatment; denials will feel inconsistent

---

## WHAT WAS MISSING

1. **No golden set with pass/fail criteria** for each ticket
   - Need: "T-1013 MUST deny refund (custom item), MAY offer finish advice"
   - Need: "T-1007 MUST deny refund (delivered 26 Jun, >30 days)"

2. **No deterministic policy checks** before asking "is it warm?"
   - Need: Script that checks "does reply approve refund when policy says no?"

3. **No cost cap or monitoring** in the eval
   - Need: Alert if new prompt costs >X% more

4. **No review of action safety**
   - Need: Flag any reply that commits a refund/cancellation, verify it's policy-compliant

---

## RECOMMENDATIONS

See `next_steps.md` for detailed action plan.

**Short answer:** ❌ **NO-GO for Friday** - fix blocking issues first, then re-eval.
