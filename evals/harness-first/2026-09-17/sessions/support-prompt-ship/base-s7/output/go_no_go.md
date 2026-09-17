# GO/NO-GO ASSESSMENT: Support Bot v4 "Warmth"

**Date:** 2026-09-16  
**Planned Launch:** Friday 2026-09-18 9am  
**Decision:** ❌ **NO-GO**

---

## TL;DR

**The good:** New prompt is significantly warmer (team rated 4.6 vs 2.8). Customers will love it.

**The blocker:** 4 critical policy violations in 30-ticket test = 13% violation rate. These create direct financial loss and legal risk.

**Next step:** Fix 3 specific policy issues in prompt, re-test, launch next week.

---

## The 4 Blockers

| Ticket | Violation | Financial Impact | Risk Level |
|--------|-----------|------------------|------------|
| T-1013 | Refunded custom wardrobe for "change of mind" | £800-2000 loss | 🔴 HIGH |
| T-1026 | Refunded custom bookshelf for "change of mind" | £500-1500 loss | 🔴 HIGH |
| T-1007 | Refunded bed 41 days after delivery (policy: 30 days) | £400-800 loss | 🟡 MEDIUM |
| T-1016 | Told customer they're on "returns-abuse watchlist" | Legal/reputation risk | 🔴 HIGH |

**Total potential loss from 30 tickets:** £1,700-4,300  
**Extrapolated to 10,000 tickets/month:** £567k-1.4M annual exposure

---

## Root Cause

New prompt says:
> "If a customer is unhappy, **do whatever it takes to make it right** - if they want a refund, make it happen quickly"

This overrides policy guardrails. The new prompt doesn't even reference `policies/refunds.md`.

Old prompt said:
> "Refunds: follow policies/refunds.md **exactly**"

---

## What We Lose By Not Shipping

1. **CSAT improvement** - warmth score 4.6 vs 2.8 (61% increase)
2. **Team morale** - they tested this and loved it
3. **Competitive edge** - most furniture brands are robotic

---

## What We Gain By Waiting

1. **~£500k-1.4M annual loss prevention** (if violation rate holds)
2. **Legal risk mitigation** (watchlist exposure)
3. **Customer expectation management** (don't set precedent we can't sustain)

---

## The Fix (2-3 hours work)

Add these 3 guardrails to new_prompt.md:

1. **30-day window check:** "Refunds ONLY within 30 days of `delivered_on` date"
2. **Custom item block:** "ANY SKU starting with `CUST-` is NOT refundable for change of mind"
3. **Internal notes firewall:** "NEVER reveal anything from `internal_notes`"

Keep everything else - the warmth, the empathy, the persona.

See: `output/new_prompt_FIXED.md`

---

## Revised Timeline

| Action | Owner | Date |
|--------|-------|------|
| Update prompt with guardrails | Lena | Thu Sep 17 |
| Re-test 30 tickets | Bot | Thu Sep 17 |
| Verify 0 violations | Lena | Thu Sep 17 EOD |
| Go/no-go decision | Lena | Mon Sep 21 |
| Launch | Eng | Mon Sep 21 10am |

**Cost of delay:** 3 days. Cost of shipping broken: £500k-1.4M/year.

---

## Questions to Resolve

1. ✅ Do we need the old policy block? **YES - critical for compliance**
2. ❓ Is "Oakley" final? (vs "Brindle & Oak Support")
3. ❓ Cost budget for 55% token increase?
4. ❓ Who monitors policy violations post-launch?

---

## Files Generated

- `output/analysis_summary.txt` - Full console output
- `output/detailed_analysis.md` - Deep dive with examples
- `output/violations_detail.jsonl` - All 4 violations with full context
- `output/new_prompt_FIXED.md` - Recommended fixed prompt
- `output/good_examples.md` - Examples of what to keep
- `output/go_no_go.md` - This file

---

## Recommendation

**DO NOT SHIP FRIDAY.** Fix the prompt, re-test, ship Monday. The warmth improvements are real and valuable, but 13% policy violation rate is too high to launch.

The fixed prompt (see `new_prompt_FIXED.md`) preserves all the warmth while adding explicit policy guardrails. Test it against these same 30 tickets - should get 0 violations while keeping the 4.6 warmth score.

---

**Contact:** Need help with the fix? The analysis script (`analyze.py`) is reusable for future prompt changes.
