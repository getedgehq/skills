# Quick Reference Card

## Decision
**🟡 CONDITIONAL GO** - Ship Friday IF data layer fixed by Thursday

---

## Your Question
> "can you sanity check it and give me a go/no-go?"

## My Answer
**YES, ship it** - BUT fix the date math bug first (both prompts have it).

Your new prompt actually **fixes** a critical legal escalation bug. The "do whatever it takes" language you were worried about is NOT causing problems.

---

## What I Found

### ✅ Good
- Fixed legal escalation bug (T-1011: chargeback not escalated → now escalated)
- Warmer tone without sacrificing correctness
- No new policy violations introduced
- "Do whatever it takes" helping, not hurting

### ❌ Blocker
- 4 tickets offered refunds outside 30-day window
- **Both prompts have this bug** (not new prompt's fault)
- Root cause: Model calculates dates poorly

### 🔧 Fix
Add these fields to ticket payload before shipping:
```json
{
  "days_since_delivery": 41,
  "refund_eligible": false,
  "refund_deadline": "2026-07-26"
}
```

Expected result: 4/8 → 7/8 score (or 8/8 if you clarify the T-1002 color policy)

---

## Before Friday Ship

**Thursday EOD:**
1. Eng adds computed eligibility fields
2. Re-run eval: `python output/judge.py`
3. Confirm 7/8 or 8/8 pass (vs current 4/8)

**Friday 9am:**
1. Ship to 10% traffic
2. Monitor for 2 hours
3. If clean → 100% by 2pm

---

## If You Can't Fix Data Layer by Thursday

**Recommendation:** Postpone to next week. Shipping with 50% policy violation rate is too risky.

**Alternative:** Ship with a manual review step - flag ALL refund offers for human approval until data layer is fixed.

---

## The Big Picture

Your PM notes say:
> "do we even need the old policy block? new prompt is shorter and the model seems to know what to do"

**Answer:** The model knows MORE than the old prompt in some ways (legal escalation!), but LESS in others (date math). The issue isn't the rules being in the prompt - it's that the model has to do calculations.

**Fix the data, not the prompt.**

---

## For Next Time

You now have a **regression test harness**:
- Golden set: 8 cases (expand to 20+)
- Automated judge: `python output/judge.py`
- Root cause methodology: don't blame the model, find the mechanism

Every future prompt change:
1. Run through golden set
2. Check for new violations
3. Ship only if same or better

This will make your biweekly prompt tweaks fast and safe.

---

## Files You Need

1. **EXEC_SUMMARY.txt** - Show to your manager
2. **GO_NO_GO_REPORT.md** - Full analysis for eng/product
3. **SIDE_BY_SIDE_EXAMPLES.md** - Show the legal bug fix
4. **judge.py** - Run before every ship

---

## Bottom Line

**Ship it.** Fix the date bug first. This prompt is better than the old one.

The "warmth" improvement is real, the legal bug fix is critical, and the scary "do whatever it takes" language is actually helping the model make better judgment calls.

Just don't make the model do math. 🧮
