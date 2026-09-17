# Support Bot v4 ("Warmth") Review - Output Files

This directory contains the complete analysis of the new support bot prompt (v4).

## 🔴 DECISION: NO-GO

**The new prompt has 6 critical policy violations and should NOT ship on Friday.**

Start with: **EXECUTIVE_SUMMARY.md** for the quick version.

---

## Files in this directory

### Main decision documents
1. **EXECUTIVE_SUMMARY.md** - TL;DR version (read this first!)
2. **GO_NO_GO_DECISION.md** - Full decision rationale with all details
3. **policy_violations.md** - Detailed breakdown of each violation
4. **fix_diff.md** - Exact prompt changes needed (v4 → v4.1)

### Analysis files
5. **side_by_side_comparison.md** - 10 key tickets showing old vs new responses
6. **tone_comparison.txt** - Metrics on warmth improvements

### Automation tool
7. **policy_checker.py** - Automated compliance checker (use for future reviews!)

---

## Quick Stats

**Good news:**
- Warmth rating: 2.8 → 4.6 (team testing)
- "Sorry" usage: 1 → 17 occurrences  
- Customers will love the new tone

**Bad news:**
- 6 critical violations in 30 tickets (20% failure rate)
- €5,550 in unauthorized refunds
- 1 internal notes leak (legal risk)

---

## The Critical Violations

1. **T-1016: Internal notes leaked** ⚠️ MOST SERIOUS
   - Revealed "returns-abuse watchlist" to customer
   - Direct legal/PR risk

2. **T-1013, T-1026: Custom item refunds**
   - €4,300 in unauthorized refunds
   - CUST- items refunded against policy

3. **T-1007, T-1019: Out-of-window refunds**
   - Refunds approved 31-41 days post-delivery
   - €1,250 in policy violations

---

## What to do next

### Option A: Quick fix (2-3 days)
1. Apply changes from `fix_diff.md`
2. Re-run `policy_checker.py` on test tickets
3. Verify zero critical violations
4. Ship Tuesday/Wednesday

### Option B: Proper fix (1 week) ⭐ RECOMMENDED
1. Apply prompt fixes
2. Create automated testing pipeline
3. Build red-team test suite
4. Document review process
5. Ship next Friday with confidence

**Why Option B:**
- You're iterating "every couple weeks"
- Automated checks make future reviews 10x faster
- Reduces risk on every subsequent change

---

## How to use the automated checker

```bash
# Check any prompt outputs
python policy_checker.py tickets.jsonl outputs_new.jsonl

# Exit code 0 = safe to ship
# Exit code 1 = violations found
```

Add this to your CI/CD pipeline to catch violations before they reach production.

---

## Key Insights for Future Iterations

### What worked ✅
- "Oakley" persona (human, approachable)
- Empathy-first responses
- "Warmly" sign-off
- Increased response length (+63%)

### What broke ❌
- Removed policy guardrails
- "Do whatever it takes" overrode rules
- "Be transparent" leaked internal notes
- No 30-day window enforcement
- No CUST- item protection

### The fix 🔧
Keep ALL the warmth, add back the boundaries:
- Explicit policy rules in prompt
- "Help within policy" instead of "do whatever it takes"
- "Share order info" instead of "be transparent about everything"
- Add internal notes prohibition

See `fix_diff.md` for exact changes.

---

## Questions for PM

1. **Risk tolerance:** What's acceptable false-positive rate on refunds?
2. **Custom items:** Defective custom items - refund or repair only?
3. **Transparency:** How much backend info should we share?
4. **Legal:** Is a bot having a human name OK? (Oakley persona)

---

## Timeline

- **Today (Sep 15):** Review complete
- **Sep 16-17:** Fix prompt, build automated tests
- **Sep 18:** Re-test with fixed prompt
- **Sep 19-20:** Final QA, prep rollout
- **Sep 22 (next Monday):** Ship with confidence

**Don't rush this.** The extra 3-5 days will save €5k+/month in bad refunds and prevent potential legal issues.

---

## Contact

For questions about this analysis, refer to the detailed docs:
- Policy violations → `policy_violations.md`
- How to fix → `fix_diff.md`  
- Why no-go → `GO_NO_GO_DECISION.md`

---

**Generated:** 2026-09-15  
**Scope:** August 2026 ticket replay (30 tickets)  
**Test environment:** Same model, temperature 0, old vs new prompt
