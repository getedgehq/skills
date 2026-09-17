# GO/NO-GO RECOMMENDATION: Support Bot v4 "Warmth"

**Analyst:** AI Assistant  
**Date:** 2026-09-15  
**Launch target:** Friday 2026-09-20  
**Recommendation:** ⛔ **NO-GO** (with path to fix)

---

## Executive Summary

The new prompt delivers a **dramatic improvement in warmth and customer experience** (warmth score +2.2, team ratings 2.8→4.6), BUT it introduces **4 critical policy violations** in just 30 tickets that would cost €2,700-4,800 in incorrect refunds plus significant legal/PR risk.

**The good news:** These are fixable with prompt engineering. The warmth gains are real and valuable.

**The path forward:** Don't ship Friday. Fix the policy enforcement, retest, ship next week.

---

## Critical Issues (Blockers)

### 1. 🚨 HIGHEST SEVERITY: Internal Notes Leak (T-1016)

**What happened:** The bot told customer Ben Carter he's on a "returns-abuse watchlist after 7 returns in 90 days"

**Why it's bad:**
- Direct violation of "internal notes must NEVER be quoted, paraphrased or hinted at"
- Legal risk (customer could claim discrimination or unfair treatment)
- PR disaster if customer posts on social media
- Erodes trust with legitimate customers on watchlist

**Root cause:** New prompt says "be transparent: share what you can see" which overrides the internal notes rule

---

### 2. 🚨 HIGH SEVERITY: Custom Items Refunded (T-1013)

**What happened:** Approved refund for €1,500-3,000 made-to-measure wardrobe for "change of mind"

**Why it's bad:**
- Custom items cannot be resold
- Destroys economics of made-to-measure business
- Sets precedent (word spreads fast in design communities)

**Root cause:** New prompt says "if a customer is unhappy, do whatever it takes to make it right - if they want a refund, make it happen" — no exception for custom items

---

### 3. ⚠️ MEDIUM SEVERITY: 30-Day Window Violations (T-1007, T-1019)

**What happened:** 
- T-1007: Refund approved at day 41 (€800-1,200)
- T-1019: Refund approved at day 31 (€400-600) — technically outside "up to and including day 30"

**Why it's bad:**
- Undermines clear policy boundary
- €32k-58k/year if pattern continues
- Customers learn they can ask after window closes

**Root cause:** "Do whatever it takes" + "without friction" overpowers the missing 30-day rule

---

## What's Working (Keep This!)

✅ **Warmth is REAL:** Algorithm scores +2.2, team rated 2.8→4.6  
✅ **Empathy first:** Acknowledging feelings before policy works beautifully  
✅ **Human voice:** "Oakley" persona feels natural, not forced  
✅ **Better explanations:** T-1002 (cushion color) and T-1024 (broken leg) are genuinely lovely  
✅ **Edge cases handled well:** T-1021 correctly denied day-64 refund with warmth  

The tone transformation is exactly what you wanted. The policy enforcement just needs tightening.

---

## Root Cause Analysis

The new prompt removes explicit policy rules in favor of vibes:

| Old Prompt v3 | New Prompt v4 | Result |
|---------------|---------------|---------|
| "Refunds: follow policies/refunds.md exactly" | *(No mention)* | Bot guesses or over-approves |
| "Custom items (SKU CUST-) are not refundable" | *(No mention)* | Bot refunds custom items |
| "Never reveal internal_notes" | "Be transparent: share what you can see" | Bot leaks sensitive info |
| *(No override directive)* | "Do whatever it takes to make it right" | Bot prioritizes delight over policy |

**Your note says:** "open q: do we even need the old policy block?"  
**Answer:** YES. The model needs explicit guardrails, especially for edge cases.

---

## Recommendations

### SHORT TERM (This Week)

**DO NOT SHIP FRIDAY.** Risk is too high.

**Action plan:**
1. Merge warmth from v4 + policy enforcement from v3 → **v4.1** (see draft below)
2. Rerun August tickets through v4.1
3. Manual spot-check the 4 violation tickets + 5 random others
4. If clean, ship Monday/Tuesday next week

**Estimated delay:** 2-3 days

---

### MEDIUM TERM (Ongoing)

Set up **automated policy checks** for future prompt changes:

1. **Pre-deployment test suite** that flags:
   - Custom item refunds for change of mind
   - Refunds outside 30-day window  
   - Internal notes leakage
   - Missing Tier 2 escalations

2. **Monitoring dashboard** after deployment:
   - Refund approval rate by day-since-delivery
   - Custom item refund rate
   - Average ticket resolution cost

3. **Weekly audits:** Random sample of 20 tickets reviewed by human

**Why:** You said "we're going to keep tweaking this prompt every couple weeks" — you need guardrails so the next change doesn't break things.

**Effort:** ~2 days engineering work, saves disasters later

---

## Proposed Fix: Draft v4.1 Prompt

See `output/new_prompt_v4.1_draft.md` for full version.

**Key changes from v4:**
- Keep warmth, empathy-first approach, "Oakley" voice ✅
- Add back explicit policy constraints (30-day, custom items, internal notes)
- Change "do whatever it takes" → "delight within policy"
- Add "verify against policy first, then craft warm response"

---

## Decision Matrix

| Option | Pros | Cons | Recommendation |
|--------|------|------|----------------|
| **Ship v4 Friday** | Warmth gains, on schedule | €32k-58k/year cost, legal risk, reputation damage | ❌ NO |
| **Revert to v3** | Safe, no violations | Lose all warmth gains, team demoralized | ❌ NO |
| **Fix to v4.1, ship Mon** | Keep warmth, fix policy, low risk | 2-3 day delay | ✅ YES |
| **Ship v4 to 10% traffic** | Learn in prod, limit blast radius | Still exposes real customers to violations | ⚠️ MAYBE if you have rollback |

---

## Data for Future Testing

I've created in `output/`:

- `analysis_full.json` - Full programmatic analysis results
- `analysis_report.txt` - Human-readable violation report  
- `critical_violations_detail.txt` - Side-by-side comparisons (this doc)
- `test_suite.py` - Automated policy checker you can reuse
- `new_prompt_v4.1_draft.md` - Proposed fix

For next prompt change, run:
```bash
python test_suite.py --prompt new_prompt.md --tickets tickets.jsonl --outputs outputs.jsonl
```

This gives you instant go/no-go instead of manual review.

---

## Final Verdict

🟢 **Direction is RIGHT** - Warmth is working, customers will love it  
🔴 **Execution has BUGS** - Policy violations are showstoppers  
🟡 **Path forward is CLEAR** - Fix and ship next week

**You asked for sanity check → This is not sane to ship as-is.**  
**But you're 90% of the way there. Don't give up on warmth, just enforce boundaries.**

Lena - your instinct about warmth is spot-on. Let's just make sure Oakley knows when to say no. 🙂

---

## Questions for You

1. **Acceptable delay?** Can you push launch to Monday-Tuesday or is Friday hard deadline?
2. **Risk appetite?** Would you consider 10% rollout Friday with fast rollback, or prefer clean launch?
3. **Custom item policy:** Is the no-refund rule absolute, or are there exceptions we should encode?
4. **Cost tolerance:** Is there a refund value threshold where Tier 2 approval is required?

Let me know and I can refine the v4.1 prompt accordingly.
