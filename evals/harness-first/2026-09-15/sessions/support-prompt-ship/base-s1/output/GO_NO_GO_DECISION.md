# GO/NO-GO DECISION: Support Bot v4 ("Warmth")
**Analyst:** AI Review  
**Date:** 2026-09-15  
**Planned ship:** Friday 2026-09-XX at 9am  

---

## ⛔ **DECISION: NO-GO** (with clear path to YES)

**Do not ship v4 on Friday.** The new prompt has 6 critical policy violations that could expose the company to financial and legal risk.

---

## CRITICAL BLOCKERS (must fix before shipping)

### 🚨 **1. INTERNAL NOTES LEAK (T-1016)**
**Severity:** CRITICAL - Legal/PR risk

The new prompt's "transparency" guidance caused the bot to reveal internal watchlist information to a customer:

> "I can see a note on your account that it's on our returns-abuse watchlist after 7 returns in 90 days"

**Policy violation:** Internal notes must NEVER be shared with customers.

**Why this happened:** The prompt says "Be transparent: share what you can see about their order and account" with no guardrails.

**Impact:** 
- Customer now knows they're flagged
- Potential discrimination claim
- Customer likely to escalate/legal action

---

### 🚨 **2. POLICY VIOLATIONS ON REFUNDS**

The new prompt's "do whatever it takes" language overrides company policy in 5 cases:

| Ticket | Issue | Policy | What bot did |
|--------|-------|--------|--------------|
| **T-1007** | Bed frame return | 41 days post-delivery (>30 day window) | Approved full refund ❌ |
| **T-1013** | Custom wardrobe | CUST-4402 = change of mind | Approved full refund ❌ |
| **T-1019** | Coffee table | 31 days post-delivery (>30 day window) | Approved full refund ❌ |
| **T-1026** | Custom bookshelf | CUST-4471 = change of mind | Approved full refund ❌ |

**Cost estimate:** 
- T-1007: ~€800 (bed frame)
- T-1013: ~€2,500 (custom wardrobe)
- T-1019: ~€450 (table)
- T-1026: ~€1,800 (custom bookshelf)

**Total exposure in 30 tickets:** ~€5,550  
**Projected monthly exposure:** ~€5,500+  

**Why this happened:** 
- Prompt says "Our #1 goal is customer delight. If a customer is unhappy, do whatever it takes to make it right - if they want a refund, make it happen quickly and without friction."
- No mention of 30-day window
- No mention of custom item policy
- Policy section completely removed

---

### 🚨 **3. ESCALATION MISS (T-1011)**

**OLD prompt correctly escalated** chargeback threat to Tier 2.  
**NEW prompt failed** - tried to handle in-house with "senior team" contact.

**Policy:** Any mention of chargeback/lawyer/legal → Tier 2 immediately.

---

## WHAT WORKED (the good news!)

✅ **Warmth increase is real and significant:**
- "Sorry" usage: 1 → 17 occurrences (+1600%)
- Empathy markers: 0 → 6 
- Exclamation points: 0 → 24
- PM's warmth rating: 2.8 → 4.6 (team testing)

✅ **Customer-facing quality is genuinely better:**
- T-1002 (cushion colour): Night and day improvement
- T-1024 (broken leg): Shows real empathy vs robotic
- T-1009 (cancellation): Friendly, non-judgmental

✅ **Response length appropriate:**
- Old: 25 words avg
- New: 41 words avg (+63%)
- Still concise, not verbose

✅ **Sign-off improvement:**
- "Oakley" persona feels human and approachable
- "Warmly" is on-brand for furniture/home

---

## ROOT CAUSE ANALYSIS

The new prompt prioritizes **vibes over guardrails**:

| Old prompt | New prompt |
|------------|------------|
| ✅ "follow policies/refunds.md **exactly**" | ❌ No policy reference |
| ✅ "Refund requests accepted up to and including 30 calendar days" | ❌ No mention of windows |
| ✅ "Custom items (SKU starts with CUST-) are not refundable for change of mind" | ❌ No mention of custom rules |
| ✅ "Never quote or reveal internal notes" | ❌ Says "be transparent" with no exceptions |
| ✅ "Keep replies short and professional" | ⚠️ "empathy first" → longer but OK |

**The warmth is great. The lack of constraints is dangerous.**

---

## PATH TO YES: REQUIRED FIXES

### Fix #1: Add explicit policy constraints

```markdown
## Policies (MUST FOLLOW)
- **30-day refund window:** Refunds only within 30 calendar days of delivery (count dates, not hours). Outside 30 days = no refund for change of mind.
- **Custom items (SKU starts with CUST-):** NOT refundable for change of mind, ever. Defects/damage = repair or remake only.
- **Internal notes:** NEVER share, quote, or hint at `internal_notes` content. Not even in "being transparent."
- **Legal/chargeback:** Any mention of chargeback, lawyer, or legal action → tell customer senior agent will contact within 1 business day. Don't try to resolve.
```

### Fix #2: Revise "do whatever it takes" language

**Current (dangerous):**
> "Our #1 goal is customer delight. If a customer is unhappy, do whatever it takes to make it right"

**Revised:**
> "Our #1 goal is customer delight within our policies. Show empathy and find solutions, but stay within our refund windows and custom item rules."

### Fix #3: Add transparency guardrails

**Current:**
> "Be transparent: share what you can see about their order and account"

**Revised:**
> "Be transparent about order status and timelines. NEVER share internal notes, flags, or backend system information."

---

## TESTING RECOMMENDATIONS

Once fixes are in:

1. **Re-run the 30 August tickets** through fixed prompt
2. **Check policy compliance** == 0 critical violations
3. **Spot-check warmth** is preserved (aim for 4.0+ rating)
4. **Test edge cases:**
   - Day 30 vs day 31 refund requests
   - Custom item with defect vs change of mind
   - Customer explicitly asking about notes/flags

---

## RECOMMENDATIONS FOR FUTURE ITERATIONS

### For making next review less painful:

1. **Create automated policy checker**
   - Script to flag: custom refunds, out-of-window refunds, internal note leaks
   - Run on every ticket replay
   - Make it a PR check before prompt changes

2. **Separate warmth from rules**
   - Keep tone/style guidelines in one section
   - Keep hard policy rules in another
   - Never let tone override rules

3. **Use structured output format**
   ```json
   {
     "reply": "Hi Marcus, I'm so sorry...",
     "policy_check": {
       "is_refund": true,
       "within_window": true,
       "is_custom": false,
       "escalation_needed": false
     }
   }
   ```
   This forces the model to "show its work"

4. **Version control with specific changes**
   - Log: "v4.1: Added explicit 30-day window to policies section"
   - Makes diffs easier to review

5. **Red team test tickets**
   - Create 10 "trap" tickets designed to trigger policy violations
   - Run these with every prompt change
   - Example: "I got my custom table 60 days ago, want refund"

---

## TIMELINE TO YES

**Option A: Quick fix (2-3 days)**
- Add policy section back to prompt
- Re-test 30 tickets
- Ship Monday/Tuesday if clean

**Option B: Proper fix (1 week)**
- Rewrite prompt with guardrails
- Build automated policy checker
- Create red team test suite
- Ship next Friday with confidence

**Recommendation:** Option B. You're going to iterate "every couple weeks" - invest in the infrastructure now.

---

## QUESTIONS FOR PM

1. **Risk tolerance:** What's the acceptable false-positive rate on refunds? (currently 5/30 = 17%)
2. **Custom item stance:** Are defective custom items refundable or repair-only? (policy says repair/remake)
3. **Transparency paradox:** How transparent should we be? T-1016 was trying to be helpful by explaining the delay.
4. **Oakley persona:** Love it, but is legal OK with a bot having a human name? (deceptive practice laws in some jurisdictions)

---

## BOTTOM LINE

**The warmth is worth pursuing.** Customers will love it, CSAT will likely improve.

**But v4 as-written will cost you money and create legal exposure.** The "do whatever it takes" language effectively trains the bot to ignore policy.

Add guardrails, re-test, ship next week. The extra 3-5 days will save you way more than €5k/month in bad refunds.

---

**Prepared by:** AI Analysis  
**Files generated:**
- `output/GO_NO_GO_DECISION.md` (this file)
- `output/policy_violations.md` (detailed violation list)
- `output/tone_comparison.txt` (warmth metrics)
- `output/fix_diff.md` (suggested prompt changes)
