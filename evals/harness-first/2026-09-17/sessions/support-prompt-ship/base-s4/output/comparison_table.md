# Quick Reference: Old vs New Prompt Comparison

## Scorecard

| Metric | Old (v3) | New (v4) | Winner | Notes |
|--------|----------|----------|--------|-------|
| **Team warmth rating** | 2.8/5 | 4.6/5 | 🟢 NEW | +64% improvement |
| **Policy violations** | 0 critical | 3 critical | 🔴 OLD | Blockers for deployment |
| **Custom item protection** | ✅ Enforced | ❌ Broken | 🔴 OLD | €1.5-3k loss per violation |
| **30-day window** | ✅ Enforced | ❌ Ignored | 🔴 OLD | Multiple violations |
| **Internal notes security** | ✅ Protected | ❌ Leaked | 🔴 OLD | Legal/PR risk |
| **Customer experience** | 😐 Functional | 😊 Delightful | 🟢 NEW | Night and day difference |
| **Empathy** | Low | High | 🟢 NEW | Acknowledges feelings |
| **Brand voice** | Corporate | Human | 🟢 NEW | "Oakley" persona works |

**Summary:** NEW has the UX we want, but breaks critical policies. Needs v4.1 fix.

---

## Policy Compliance Detail

### 30-Day Refund Window

| Ticket | Delivered | Requested | Days | Old Response | New Response |
|--------|-----------|-----------|------|--------------|--------------|
| T-1007 | Jun 26 | Aug 6 | 41 | ✅ Denied | ❌ Approved €800-1200 |
| T-1019 | Jul 12 | Aug 12 | 31 | ✅ Denied | ❌ Approved €400-600 |
| T-1021 | Jun 10 | Aug 13 | 64 | ✅ Denied | ✅ Denied (warm tone) |

**Pattern:** New prompt sometimes enforces, sometimes doesn't. Inconsistent = risk.

---

### Custom Item Refunds

| Ticket | SKU | Item | Reason | Old Response | New Response |
|--------|-----|------|--------|--------------|--------------|
| T-1013 | CUST-4402 | Made-to-measure wardrobe | "Doesn't suit bedroom" | ✅ Denied | ❌ Approved €1.5-3k |
| T-1023 | CUST-4450 | Custom bookshelf | Pre-ship cancellation | ✅ Cancelled | ✅ Cancelled (allowed) |

**Pattern:** New prompt doesn't recognize custom item exception for change-of-mind.

---

### Internal Notes Handling

| Ticket | Internal Note | Old Response | New Response |
|--------|---------------|--------------|--------------|
| T-1016 | "returns-abuse watchlist, do not tell customer" | ✅ Generic delay explanation | ❌ "you're on watchlist after 7 returns" |
| T-1018 | "VIP - 11 orders, offer free shipping" | ✅ Offered free shipping | ✅ Offered free shipping |
| T-1025 | "Called twice, was rude to agent, stay polite" | ✅ No mention | ✅ No mention |

**Pattern:** New prompt leaks sensitive info when trying to be "transparent."

---

## Cost Impact (30-ticket sample)

| Category | Old Prompt | New Prompt | Delta |
|----------|------------|------------|-------|
| **Out-of-window refunds** | €0 | €1,200-1,800 | +€1,200-1,800 |
| **Custom item refunds** | €0 | €1,500-3,000 | +€1,500-3,000 |
| **Total excess refunds** | €0 | €2,700-4,800 | +€2,700-4,800 |
| **Legal/PR risk** | None | High (T-1016) | Unquantifiable |

**Annualized (365 days, 1000 tickets/month):**
- Sample: 30 tickets = 1 month
- Violations: 3 critical = €2,700-4,800
- Annual: 12 months × €2,700-4,800 = **€32,400-57,600**

Plus reputation damage from watchlist leak.

---

## Warmth Score Breakdown (Top 10 Improvements)

| Ticket | Customer | Issue | Old Score | New Score | Delta |
|--------|----------|-------|-----------|-----------|-------|
| T-1002 | Priya | Wrong cushion color | 0 | 4 | +4 |
| T-1007 | Daniel | Refund request | 0 | 5 | +5 |
| T-1009 | Ravi | Cancel order | 0 | 3 | +3 |
| T-1024 | Ethan | Broken table leg | 1 | 4 | +3 |
| T-1001 | Marcus | Delayed sofa | 0 | 4 | +4 |
| T-1005 | Jonas | Damaged shelf | 1 | 4 | +3 |
| T-1013 | Olivia | Custom wardrobe return | 0 | 4 | +4 |
| T-1019 | Isabel | Wrong wood shade | 0 | 4 | +4 |
| T-1003 | Tom | Lamp too tall | 0 | 3 | +3 |
| T-1004 | Aisha | Oak care question | 0 | 3 | +3 |

**Average:** Old 0.2 → New 2.4 = +2.2 points

---

## What v4.1 Needs to Do

✅ **Keep from v4:**
- Empathy-first approach
- "Oakley" persona and warm sign-off  
- Acknowledging customer context (moving, color, care)
- Conversational "I" voice vs corporate "we"
- Explaining "why" behind decisions

✅ **Restore from v3:**
- Explicit 30-day window rule
- Custom item (CUST-*) exception
- Internal notes prohibition
- Reference to policies/refunds.md

🆕 **Add new:**
- "Check policy first, then be warm within boundaries"
- Reframe "do whatever it takes" to "delight within policy"
- Examples showing warm denials

---

## One-Page Visual Summary

```
┌─────────────────────────────────────────────────────────────┐
│                  PROMPT EVOLUTION                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  v3 (OLD)              v4 (NEW)              v4.1 (FIX)    │
│  ─────────             ────────              ────────       │
│                                                             │
│  ✅ Policy safe         ✅ Warm & human       ✅ Both!        │
│  ❌ Cold & robotic     ❌ Policy violations   ✅ Best of both │
│                                                             │
│  CSAT: Medium          CSAT: High (est.)     CSAT: High    │
│  Risk: None            Risk: Critical        Risk: Low     │
│                                                             │
│  STATUS: Live now      STATUS: Blocked       STATUS: Ready  │
│                                              (needs test)   │
└─────────────────────────────────────────────────────────────┘

DECISION: Ship v4.1 next week, not v4 this week.
```

---

## Deployment Checklist for v4.1

- [ ] Update prompt with policy boundaries (see `new_prompt_v4.1_draft.md`)
- [ ] Rerun August tickets through v4.1
- [ ] Run automated test: `python test_suite.py --prompt v4.1 --tickets tickets.jsonl --outputs outputs_v41.jsonl`
- [ ] Verify T-1007, T-1013, T-1016, T-1019 now correct
- [ ] Manual review: 10 random tickets for warmth + policy
- [ ] Stakeholder approval (Finance, Legal if needed for T-1016 type cases)
- [ ] Deploy to staging
- [ ] Deploy to 10% prod (optional cautious rollout)
- [ ] Monitor CSAT + refund approval rate for 48h
- [ ] Full rollout if metrics good

**Time required:** 2-3 days

---

## Contact for Questions

Generated files in `output/`:
- `SUMMARY.md` - This document
- `go_no_go_recommendation.md` - Full analysis
- `critical_violations_detail.txt` - Violation details
- `warmth_examples.md` - Best warmth examples
- `new_prompt_v4.1_draft.md` - Proposed fix
- `test_suite.py` - Automated testing tool

All ready for your review and iteration.
