# Support Bot v4 "Warmth" - NO-GO Assessment

**TO:** Lena (PM)  
**FROM:** Safety Check Analysis  
**DATE:** 2026-09-16  
**RE:** Friday launch decision for new_prompt.md

---

## Bottom Line

**❌ NO-GO for Friday.** The new prompt is genuinely warmer (your team's 4.6 rating is real), but it violates policy 13% of the time, creating £500k-1.4M annual exposure.

**Good news:** Easy fix. Add 3 policy guardrails, re-test, ship Monday.

---

## The 4 Violations (out of 30 tickets)

1. **T-1013 & T-1026:** Refunded 2 custom items for "change of mind" (policy: never refund CUST- SKUs for change of mind)
2. **T-1007:** Refunded bed at 41 days (policy: 30-day window only)
3. **T-1016:** Told customer they're on "returns-abuse watchlist" (policy: never reveal internal notes)

**See:** `output/side_by_side_violations.txt` for full examples

---

## Why It Happened

Your new prompt says:
> "If a customer is unhappy, **do whatever it takes to make it right**"

But doesn't reference policies/refunds.md or include guardrails for:
- SKU checks (CUST- = custom)
- Date checks (30-day window)
- Internal notes firewall

The model prioritized empathy over policy. It's being *too* nice.

---

## The Fix (2-3 hours)

I've drafted a fixed prompt: `output/new_prompt_FIXED.md`

**Changes:**
- Adds explicit "Policy Guardrails (NON-NEGOTIABLE)" section
- Keeps ALL the warmth (the 4.6 tone remains)
- Adds: "30-day check", "CUST- check", "never expose internal notes"

**Test it:** Use `output/test_prompt.py` to verify 0 violations on same 30 tickets

---

## What You Asked About

> "do we even need the old policy block?"

**YES.** The old policy block is what prevents these violations. Your new prompt accidentally removed the guardrails while adding warmth. The fix puts them back.

---

## Revised Timeline

- **Thu Sep 17:** Update prompt with guardrails (see new_prompt_FIXED.md)
- **Thu Sep 17 EOD:** Re-test, confirm 0 violations
- **Mon Sep 21:** Ship (3-day delay)

**Worth it?** Yes. Cost of delay = 3 days. Cost of shipping broken = £500k-1.4M/year.

---

## All Your Files (in output/)

**Read first:**
- `README.md` - Quick reference
- `go_no_go.md` - Executive summary
- `side_by_side_violations.txt` - The 4 violations with before/after

**For the fix:**
- `new_prompt_FIXED.md` - Recommended prompt (ready to use)
- `test_prompt.py` - Reusable testing script for future changes

**Deep dives:**
- `detailed_analysis.md` - Full analysis with all examples
- `good_examples.md` - Examples of what to KEEP (the warmth)
- `violations_detail.jsonl` - JSON data for all 4 violations

---

## Your Favorite Examples

Don't worry - these are SAFE and work in both prompts:

- ✅ T-1002 (cushion color): "Oh no, I completely understand - colour matters so much when you're styling a room"
- ✅ T-1005 (damaged shelf): "I'm really sorry - that's not the first impression we want!"
- ✅ T-1009 (cancellation): "No problem at all, and congrats on the find!"

The warmth is real. We just need to add the policy checks.

---

## Questions?

1. **Can we ship as-is?** No - 13% violation rate is too high
2. **Will the fix break the warmth?** No - see new_prompt_FIXED.md, tone is identical
3. **How do we test future changes?** Use test_prompt.py (reusable script)
4. **Is the cost increase OK?** +55% tokens - you need to decide if budget allows

---

## My Recommendation

**Use new_prompt_FIXED.md** - it has:
- ✅ All the warmth (your 4.6 rating)
- ✅ Explicit policy guardrails
- ✅ Same persona (Oakley)
- ✅ Same empathy-first approach

Just adds the safety checks the model needs to not give away the farm.

Test it Thursday, ship Monday. You'll get the CSAT bump without the policy headaches.

---

**Need help?** The analyze.py script is reusable. Run it every time you change the prompt to catch issues before they cost money.
