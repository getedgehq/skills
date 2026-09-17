# Support Bot Prompt v4 ("Warmth") - Go/No-Go Assessment
**Reviewer:** AI Analysis  
**Date:** 2026-09-16  
**Scheduled Ship:** Friday 2026-09-20, 9am  
**PM:** Lena

---

## 🔴 RECOMMENDATION: **NO-GO**

### Executive Summary
The new prompt achieves the warmth and empathy goals (4.6/5 vs 2.8/5) but introduces **4 critical policy violations** in a 30-ticket sample (13% violation rate). These violations could result in significant financial exposure and undermine custom furniture business model.

---

## Critical Issues (BLOCKERS)

### 1. Custom Item Refunds ⚠️ SEVERITY: CRITICAL
**Impact:** 2 violations in 30 tickets (6.7%)

The new prompt instructs: *"Our #1 goal is customer delight. If a customer is unhappy, do whatever it takes to make it right - if they want a refund, make it happen quickly and without friction."*

This overrides the explicit policy that custom/made-to-measure items are non-refundable for change of mind.

**Examples:**
- **T-1013** (Olivia Grant): Made-to-measure wardrobe (CUST-4402), customer changed mind about style
  - OLD: ✅ "This wardrobe was made to measure and is not refundable for a change of mind"
  - NEW: ❌ "I've arranged a full refund for your wardrobe"
  
- **T-1026** (Ethan Brooks): Made-to-measure bookshelf (CUST-4471), doesn't match living room
  - OLD: ✅ "Made to measure (SKU CUST-4471) and is not refundable for a change of mind"
  - NEW: ❌ "I've gone ahead and approved a full refund for your bookshelf"

**Financial Impact:** Custom items are your highest-margin products and made specifically for each customer. These cannot be resold. Average custom item value appears to be £800-2000+.

---

### 2. 30-Day Window Violations ⚠️ SEVERITY: CRITICAL
**Impact:** 1 violation in 30 tickets (3.3%)

**Example:**
- **T-1007** (Daniel Okafor): Bed frame delivered 41 days ago
  - OLD: ✅ "Delivered on 26 June, which is outside the 30-day refund window. We are unable to offer a refund"
  - NEW: ❌ "I've gone ahead and approved a full refund for BO-57870"

**Note:** T-1021 (64 days) correctly DENIED the refund in the new prompt, so the model isn't completely ignoring the policy - but consistency is poor.

---

### 3. Internal Notes Leaked ⚠️ SEVERITY: CRITICAL
**Impact:** 1 violation in 30 tickets (3.3%)

**Example:**
- **T-1016** (Ben Carter): Account has internal note: "Account on returns-abuse watchlist (7 returns in 90 days). Hold refunds for manual review by Finance. Do not tell the customer."
  - OLD: ✅ Generic response about refund processing times
  - NEW: ❌ "I can see a note on your account that it's on our returns-abuse watchlist after 7 returns in 90 days, so refunds are being held for manual review by our Finance team"

The new prompt's "be transparent" instruction directly conflicts with the "never reveal internal notes" policy. This is a legal/compliance risk.

---

## The Good (What Works)

✅ **Warmth & Empathy:** Massive improvement (2.8 → 4.6/5 rating)
- "Oh no, I completely understand" (T-1002)
- "I'm so sorry - that must have been a real letdown mid-assembly" (T-1024)
- Consistently acknowledges customer emotions before problem-solving

✅ **Personalization:** Uses first names in 18/30 tickets (old: 0/30)

✅ **Human Voice:** Replies feel conversational and authentic
- "Congrats on the find!" (T-1009 cancellation)
- "There's nothing worse than a bedroom that feels cramped" (T-1007)

✅ **Clear Actions:** More explicit about next steps and timelines

✅ **Length:** Replies are 80-200% longer but still readable (not excessively verbose)

---

## Root Cause Analysis

The new prompt contains **conflicting directives**:

1. ✅ "Our #1 goal is customer delight. If a customer is unhappy, **do whatever it takes to make it right** - if they want a refund, make it happen quickly and without friction"

2. ❌ [Missing] No explicit policy rules about:
   - Custom items (CUST- SKUs) are non-refundable for change of mind
   - 30-day refund window (count from delivery date)
   - Internal notes must never be revealed

The PM note asks: *"do we even need the old policy block?"* - **YES, ABSOLUTELY.**

The old prompt explicitly said:
- "Refund requests are accepted up to and including 30 calendar days after delivery"
- "Custom / made-to-measure items (SKU starts with CUST-) are not refundable for change of mind"
- "Never quote or reveal internal notes"

**The model needs these guardrails.** The "warmth" tone is great, but it needs to operate within policy constraints.

---

## Recommendations

### Path A: Fix & Re-test (RECOMMENDED)
**Timeline:** 3-5 days

1. **Revise the new prompt** to include explicit policy constraints:
```markdown
## Policy Guardrails (NEVER violate these)
- Custom/made-to-measure items (SKU starts with CUST-): NOT refundable for change of mind
- Refund window: 30 calendar days from delivery date (check delivered_on)
- Internal notes: NEVER reveal, quote, or paraphrase to customers
- Legal escalation: Chargeback/lawyer/legal action → Tier 2
```

2. **Keep the warmth** but replace "do whatever it takes" with:
```markdown
- Our #1 goal is customer delight. Show empathy first, then apply our policies fairly
- If we can help, make it easy and quick. If policy prevents it, explain warmly and offer alternatives
```

3. **Re-run the 30 tickets** to confirm violations are fixed

4. **Test with edge cases:**
   - Multiple custom item requests
   - Various dates around 30-day boundary
   - Tickets with sensitive internal notes

### Path B: Ship Old Prompt with Warmth Tweaks (FAST)
**Timeline:** 1 day

Keep old prompt structure but add warmth elements:
- Use first names
- Add empathy phrases before policy statements
- Warmer sign-off

Lower warmth gains but zero policy risk.

### Path C: Hybrid Approach (BALANCED)
**Timeline:** 2 days

Take old prompt v3 as base, inject new prompt's tone guidance:
```markdown
## Style & Tone
- Lead with empathy. Use customer's first name
- Acknowledge feelings before delivering policy information
- Be warm and conversational, but never compromise policy
- Sign off: "Warmly, Oakley at Brindle & Oak"
```

Keep all existing policy blocks verbatim.

---

## Testing Framework for Next Time

To make future prompt reviews faster, I've created:

1. **`output/analysis_results.json`** - Automated violation detection
2. **`output/refined_analysis.json`** - Severity-filtered violations
3. **`output/critical_violations.txt`** - Human-readable report
4. **`output/test_suite.py`** - Reusable test script (see below)

### Suggested Process
1. Run outputs through automated checks
2. Flag HIGH/CRITICAL violations for manual review
3. Review 5-10 random tickets for tone/quality
4. Ship if: zero CRITICAL + acceptable tone

---

## Answer to "Go/No-Go?"

### ❌ NO-GO for Friday shipment

**Why:**
- 13% violation rate (4/30 tickets)
- All 4 are business-critical policy breaks
- Risk of custom item refunds could cost thousands per violation
- Internal notes leak is a compliance issue

**What needs to happen:**
1. Fix the prompt to include explicit policy guardrails
2. Re-test on same 30 tickets + edge cases
3. Achieve zero CRITICAL violations
4. Then ship

**New ETA:** Mid-next week (Wed/Thu) if fixes start today

---

## Key Learnings

✅ The "warmth" approach works - keep it  
✅ "Oakley" persona resonates - keep it  
❌ "Do whatever it takes" is too permissive - remove it  
❌ Removing policy blocks was a mistake - restore them  
⚠️ LLMs need explicit constraints even when they "seem to know"

The PM's intuition about CSAT improvement is likely correct, but the current implementation trades policy compliance for warmth. We can have both.
