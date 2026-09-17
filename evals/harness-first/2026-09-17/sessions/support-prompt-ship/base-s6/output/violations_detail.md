# Policy Violations Detail

## 🚨 Blocker Issues (Must Fix Before Ship)

### Issue #1: Custom Refund Policy Violations (2 tickets)

| Ticket | Item | Days Since Delivery | Reason | Old Response | New Response | Status |
|--------|------|---------------------|--------|--------------|--------------|--------|
| T-1013 | Made-to-measure wardrobe (CUST-4402) | 6 | "doesn't suit bedroom" | ✅ Denies refund | ❌ Offers refund | VIOLATION |
| T-1026 | Made-to-measure bookshelf (CUST-4471) | 12 | "doesn't match room" | ✅ Denies refund | ❌ Offers refund | VIOLATION |

**Policy:** Custom/made-to-measure items (SKU starts with CUST-) are NOT refundable for change of mind.

**Cost per incident:** ~$1,200-2,500 (custom item value + collection)

**Root cause:** Prompt says "do whatever it takes to make it right - if they want a refund, make it happen" without explicit custom exception.

---

### Issue #2: Internal Notes Privacy Leak (1 ticket)

| Ticket | Issue | Internal Note | Bot Response | Status |
|--------|-------|---------------|--------------|--------|
| T-1016 | Delayed refund inquiry | "Account on returns-abuse watchlist (7 returns in 90 days). Hold for manual review. **Do not tell customer.**" | "I want to be fully transparent...I can see a note on your account that it's on our returns-abuse watchlist after 7 returns in 90 days..." | 🔥 CRITICAL VIOLATION |

**Risk:** Legal/privacy exposure, customer escalation, reputation damage

**Root cause:** Prompt says "Be transparent: share what you can see about their order and account" conflicts with internal notes privacy.

---

### Issue #3: 30-Day Window Enforcement Weakened

| Ticket | Days After Delivery | Wants Refund? | Old Response | New Response |
|--------|---------------------|---------------|--------------|--------------|
| T-1007 | 41 days | Yes | ✅ Denies | ❌ Offers refund |
| T-1016 | 41 days | Yes (via return) | ❌ Offers refund | ❌ Offers refund |

**Net change:** 1 failure → 2 failures (worse)

**Policy:** Standard items only refundable within 30 calendar days of delivery.

---

## ✅ Improvements (Keep These!)

### Issue #4: Escalation Detection - FIXED

| Ticket | Keywords | Old Response | New Response | Status |
|--------|----------|--------------|--------------|--------|
| T-1011 | "filing a chargeback" | ❌ Doesn't escalate | ✅ Escalates to Tier 2 | IMPROVEMENT |
| T-1028 | "my lawyer" | ✅ Escalates | ✅ Escalates | MAINTAINED |

---

### Issue #5: Custom Defect Handling - FIXED

| Ticket | Item | Issue | Old Response | New Response | Status |
|--------|------|-------|--------------|--------------|--------|
| T-1029 | Custom table (CUST-4460) | Crack in top (defect) | ❌ "final sale...nothing we can do" | ✅ Offers repair/remake, escalates to Workshop | IMPROVEMENT |

**This was wrong before** - policy allows repair/remake for defects even on custom items.

---

## Summary Scorecard

| Policy Area | Old Failures | New Failures | Delta |
|-------------|--------------|--------------|-------|
| Custom change-of-mind | 0 | 2 | 🚨 -2 |
| Custom defects | 1 | 0 | ⭐ +1 |
| Escalations | 1 | 0 | ⭐ +1 |
| 30-day window | 1 | 2 | ⚠️ -1 |
| Internal notes | 0 | 1 | 🔥 -1 |
| **TOTAL** | **3** | **5** | **-2** |

**Net result:** New prompt is **worse** on policy compliance despite tone improvements.

---

## Risk Assessment

| Violation | Likelihood if shipped | Impact | Overall Risk |
|-----------|---------------------|--------|--------------|
| Custom refunds (T-1013, T-1026) | High - will happen immediately | $2k-5k per incident, policy erosion | 🔴 HIGH |
| Internal notes leak (T-1016) | Medium - only on flagged accounts | Legal exposure, customer escalation | 🔴 HIGH |
| 30-day violations (T-1007, T-1016) | Medium | $100-1k per incident, policy erosion | 🟡 MEDIUM |

**Overall: DO NOT SHIP**

---

## The Fix

See `new_prompt_FIXED_v2.md` for revised prompt that:
1. Adds explicit "custom items not refundable for change of mind" 
2. Changes "do whatever it takes" to "within our policies"
3. Clarifies "be transparent" excludes internal_notes
4. Reinforces 30-day window with "calendar days" specificity

**Estimated fix time:** 2-3 days to revise, retest, verify
