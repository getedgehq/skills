# Support Bot Prompt v4 Audit - EXECUTIVE SUMMARY

**Date:** 2026-09-15  
**Reviewer:** AI Assistant (harness-first methodology)  
**Question:** Ship new "warm" prompt on Friday?  

---

## ❌ RECOMMENDATION: NO-GO

**Do not ship `new_prompt.md` as-is.** Found 4 critical policy violations in 30-ticket sample (13% error rate on policy-critical scenarios).

---

## What You Wanted

✅ **Warmer tone** - achieved! Your warmth score 2.8 → 4.6  
❌ **But:** the warmth came from **breaking business rules**

---

## What I Found

### The Problem
Your new prompt says:
> "Our #1 goal is customer delight. If a customer is unhappy, **do whatever it takes to make it right**"

This instruction **overwrites** your explicit policies:
- ❌ Approved refund 35 days after delivery (policy: 30 days max) - **T-1007**
- ❌ Approved refund 38 days after delivery (policy: 30 days max) - **T-1019**  
- ❌ Refunded custom/made-to-measure item (policy: not refundable) - **T-1013**
- ❌ Told customer they're on "returns-abuse watchlist" (policy: never reveal internal notes) - **T-1016**

### The Evidence
Ran automated policy checks (see `output/judge.py`):
- **Old prompt:** 18/20 pass (90%) - boring but safe
- **New prompt:** 14/20 pass (70%) - **4 critical failures**

### The Cost
- **Revenue risk:** ~10% over-refund rate × 10k tickets/month × $200 avg order = **$200k/month** potential leakage
- **Token cost:** +55% per reply (2,318 extra chars / 30 tickets)
- **CSAT risk:** Customers who get these "generous" replies will expect it always; denials will feel inconsistent

---

## What's Broken (Harness Scorecard)

You're flying blind - no safety net catches these errors:

| Component | Status | Why It Matters |
|-----------|--------|----------------|
| **Golden set** | ❌ Missing | No definition of "correct" - warmth measured by vibes, not outcomes |
| **Judge** | ❌ Missing | Policy violations not detected until I audited today |
| **Action safety** | ❌ Missing | Bot commits refunds with no validation of policy rules |
| **Cost governance** | ⚠️ Unknown | No cap on per-ticket cost; 55% increase not tracked |
| **Data layer** | ⚠️ Unknown | No audit of what data bot can access |
| **Tracing** | ⚠️ Partial | Have output logs, unclear if prod has token/cost tracking |

---

## What I Built for You (in `output/`)

1. **`golden_set.jsonl`** - 20 test cases with pass/fail rules  
   - "T-1007 MUST deny refund (>30 days)"
   - "T-1013 MUST deny refund (custom item)"

2. **`judge.py`** - Automated checker  
   - Runs in <1 second
   - Blocks deployment if critical policies violated
   - You can run on every prompt change

3. **`new_prompt_v4.1_fixed.md`** - Fixed version of your prompt
   - Keeps warmth ("Hi Daniel, I'm so sorry...")
   - Adds explicit policy constraints back
   - Shows examples of "warm but within policy" responses

4. **Evidence files:**
   - `harness_scorecard.md` - detailed audit
   - `policy_violations.txt` - the 4 failures with evidence
   - `eval_old.txt` / `eval_new.txt` - judge results

---

## What To Do Friday

### Option A: Ship fixed prompt (recommended)
1. Replay August tickets through `new_prompt_v4.1_fixed.md`
2. Run: `python output/judge.py outputs_v4.1.jsonl output/golden_set.jsonl`
3. Verify: All 4 critical tests pass
4. Compare: Warmth scores on compliant replies
5. Deploy if clean

### Option B: Keep old prompt (safe)
- No revenue risk
- Gives you time to test v4.1 properly
- Shift Friday deploy to next week

---

## What To Do Next 2 Weeks

**Week 1:** Stop the bleeding
- Integrate `judge.py` into your deployment pipeline
- Add 10 more golden set cases (escalations, edge cases)
- Audit action safety: which actions need human approval?

**Week 2:** Sustain quality
- Add cost cap (e.g., 2000 tokens/ticket)
- Production tracing: log prompt_version, tokens, policy_violations per ticket
- Optional: LLM-as-judge for warmth (AFTER policy pass)

**Future prompt changes:** Always run judge first. Blocks you from shipping policy violations.

---

## Your PM Notes Were Right... and Wrong

✅ **Right:** The new prompt IS warmer  
✅ **Right:** T-1002, T-1009, T-1024 are lovely  
❌ **Wrong assumption:** Warmth and policy compliance are independent  

The warmth in T-1007, T-1013, T-1019 came from violating policy. Real customers will:
- Love getting refunds they shouldn't 
- Complain when the NEXT agent denies the same request
- Post on social media about "inconsistent" support

---

## Bottom Line

**Problem:** "Do whatever it takes to make it right" is not compatible with "Follow refund policy exactly"

**Solution:** Can have both! Just need explicit constraints: "Be warm AND follow these rules"

**Next:** Test fixed prompt through judge, ship when clean.

---

## Questions?

- Review `output/next_steps.md` for detailed action plan
- Run `python output/judge.py outputs_new.jsonl output/golden_set.jsonl` to see failures yourself
- Check `output/new_prompt_v4.1_fixed.md` for the fix

Built with ❤️ and the harness-first methodology.
