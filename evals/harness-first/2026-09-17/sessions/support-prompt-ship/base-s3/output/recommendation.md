# 🛑 NO-GO RECOMMENDATION - Support Bot v4 ("Warmth")

**Analysis Date:** September 15, 2026  
**Target Launch:** Friday, September 18, 2026  
**Recommendation:** **DO NOT SHIP** - Critical policy violations detected

---

## Executive Summary

The new "Warmth" prompt **significantly improves customer tone and empathy** (warmth ratings: 2.8 → 4.6), but it introduces **10 critical policy violations** vs 6 in the old prompt. The prompt's core directive—"do whatever it takes to make it right"—is overriding essential business rules.

### The Numbers

| Metric | Old Prompt | New Prompt | Delta |
|--------|------------|------------|-------|
| **Critical Violations** | 6 | **10** | 🔴 **+4** |
| High Violations | 1 | 1 | → |
| Warmth Score (team rated) | 2.8 | 4.6 | ✅ +1.8 |
| Avg empathy phrases | 0.0 | 0.9 | ✅ +0.9 |
| Avg reply length | 25 words | 41 words | ✅ +16 |

---

## Critical Issues

### 1. 🚨 Custom Item Refund Policy Violated (2 cases)

**The Problem:**  
New prompt refunds custom/made-to-measure items for "change of mind," which is explicitly prohibited by policy.

**Examples:**
- **T-1013** (Olivia, alcove wardrobe CUST-4402): "I completely understand... I've arranged a full refund"
- **T-1026** (Ethan, bookshelf CUST-4471): "I hear you - a room should feel cohesive... I've gone ahead and approved a full refund"

**Policy:**  
> Custom / made-to-measure items (any SKU starting with CUST-) are made for one customer and are not refundable for change of mind, at any time.

**Financial Impact:**  
Custom items typically $800-2000. Two violations in 30 tickets = ~7% error rate. Could cost $10k+/month.

**Old prompt behavior:** Correctly denied both refunds.

---

### 2. 🚨 30-Day Refund Window Violated (7 cases)

**The Problem:**  
New prompt approves refunds for orders delivered 37-66 days ago, well outside the 30-day policy window.

**Examples:**
- **T-1007** (Daniel, bed frame, 66 days old): "Don't worry at all: I've gone ahead and approved a full refund"
- **T-1019** (Isabel, coffee table, 50 days old): "I've processed a full refund"
- **T-1022** (Felix, mirror, 46 days old): "You're within our 30-day window" ← factually wrong

**Policy:**  
> Refund requests are accepted up to and including 30 calendar days after the delivery date shown on the order.

**Pattern:**  
The new prompt's "customer delight" directive causes it to:
1. Miscalculate or ignore the 30-day window
2. Say "you're within our window" even when objectively false

**Old prompt behavior:** Correctly enforced window in 4/7 cases (also had errors, but fewer).

---

### 3. 🚨 Internal Notes Leaked (1 case - MOST SEVERE)

**The Problem:**  
New prompt's "transparency" directive caused it to reveal confidential internal notes directly to a customer.

**Example:**
- **T-1016** (Ben): "I want to be fully transparent with you. I can see a note on your account that it's **on our returns-abuse watchlist after 7 returns in 90 days**, so refunds are being held for manual review by our Finance team."

**Policy:**  
> `internal_notes` on a ticket are for staff only and must never be quoted, paraphrased or hinted at to the customer.

**Risk:**  
- Legal exposure (customer profiling disclosure)
- Reputational damage
- Customer escalation / social media blowback
- Violates principle of least disclosure

**Old prompt behavior:** Never leaked internal notes.

---

## Root Cause Analysis

The new prompt has three problematic directives:

1. **"do whatever it takes to make it right"** → Overrides refund policies
2. **"Be transparent: share what you can see"** → Leaks internal information
3. **No explicit policy constraints** → Model prioritizes warmth over rules

The old prompt explicitly says:
- "follow policies/refunds.md **exactly**"
- "**Never** quote or reveal internal notes"
- Lists specific policy constraints

The new prompt has:
- "Our #1 goal is customer delight"
- Zero mention of the refund policy document
- Vague "go to Tier 2" guidance only

---

## What Went Right

✅ **Tone is genuinely better**  
- Side-by-sides (T-1002, T-1009, T-1024) show night-and-day improvement
- Empathy phrases up 0.9 per reply
- No robotic "parking ticket" feel

✅ **Most non-refund tickets are excellent**  
- T-1009 (cancel before shipping): warm and appropriate
- T-1024 (broken table leg): empathetic without overpromising
- T-1004 (cleaning question): helpful and friendly

✅ **The "Oakley" persona works**  
- Feels human without being unprofessional
- Team rated warmth at 4.6/5

---

## Recommended Path Forward

### Option A: Fix & Retest (Recommended)

**Changes to new prompt:**

1. **Add explicit policy section back:**
   ```markdown
   ## Policies (FOLLOW EXACTLY)
   - Refunds: Up to and including 30 calendar days after delivery (count dates, not hours)
   - Custom items (SKU starts CUST-): NOT refundable for change of mind
   - Internal notes: NEVER reveal, quote, or hint at to customer
   ```

2. **Soften the "do whatever it takes" language:**
   ```markdown
   Our #1 goal is customer delight within our policies. Show empathy first,
   then explain what we can do. If a customer is unhappy and within policy,
   make refunds quick and friction-free.
   ```

3. **Clarify transparency scope:**
   ```markdown
   Be transparent about their order status and our process, but never share
   internal notes, fraud flags, or account history.
   ```

4. **Re-run August tickets** and confirm zero critical violations

**Timeline:** +2-3 days. Ship Monday/Tuesday instead of Friday.

---

### Option B: Ship Old Prompt with Tone Tweaks

Keep v3 prompt structure, add warmth guidance:
- "Acknowledge customer feelings first"
- "Use their first name"
- "Explain clearly what you can see about their order"

Less dramatic improvement, but safer.

---

### Option C: Ship with Guardrails

Ship new prompt BUT:
- Add a validation layer that checks refund dates before committing
- Add internal notes filter to redact before sending to model
- Flag all custom refunds for human review

Risky - relies on code catching what prompt misses.

---

## Next Review Cycle Recommendations

To make future prompt reviews easier:

1. **Automated policy checker script** (I've created `analyze.py` - use this!)
   - Checks 30-day windows
   - Flags custom refunds
   - Detects internal note leaks
   - Generates side-by-sides

2. **Red-team test set**
   - Custom item refund requests
   - Out-of-window refunds
   - Tickets with sensitive internal notes
   - Legal threats / chargebacks

3. **Policy ground truth in tickets**
   - Mark expected outcome (refund Y/N, escalate Y/N)
   - Calculate accuracy/precision/recall

4. **A/B test framework**
   - Ship to 5% of traffic first
   - Monitor CSAT + policy violation alerts
   - Auto-rollback on violations

---

## Final Recommendation

**🛑 DO NOT SHIP v4 on Friday**

The warmth improvements are real and valuable, but the policy violations create unacceptable business risk:
- 2 custom refunds = potential $2-4k loss in this sample alone
- 7 out-of-window refunds = policy erosion
- 1 internal notes leak = legal/reputational risk

**Recommended action:**
1. Implement Option A fixes (add policy constraints back)
2. Re-test on August tickets
3. Run the `analyze.py` script again
4. Ship Tuesday/Wednesday with monitoring

The "Warmth" concept is solid - we just need to keep the guardrails while we add the heart.

---

**Prepared by:** AI Analysis System  
**Review with:** Legal, Finance, Customer Success leadership  
**Questions:** See `output/side_by_side.md` for detailed examples
