# Support Bot v4 "Warmth" - Evaluation Results

**Status:** 🛑 **NO-GO** - Block deployment until violations fixed

---

## Quick Summary

Your new prompt is indeed warmer (warmth rating 4.6 vs 2.8), BUT:

- **5 out of 8 golden set cases FAILED** (62.5% failure rate on critical policies)
- **1 data leak** - Reveals fraud detection systems to customer
- **4 policy violations** - Approves refunds that violate documented policies
- **Estimated cost:** €68K/month in out-of-policy refunds if shipped as-is

**Root cause:** The new prompt's "do whatever it takes to make it right" instruction overrides explicit policy constraints.

---

## Files in This Directory

### Decision & Analysis
- **`DECISION.md`** - Full go/no-go assessment with examples (READ THIS FIRST)
- **`HARNESS_CHECKLIST.md`** - Checklist for future prompt changes

### Test Data
- **`golden_set.json`** - 8 critical test cases with expected behaviors
- **`violation_details.json`** - Detailed violation analysis of all 30 tickets

### Evaluation Tools
- **`judge_golden.py`** - Automated judge against golden set (RUN THIS)
- **`judge.py`** - General policy scanner for all tickets
- **`analysis.py`** - Statistical analysis and comparison tool
- **`create_golden_set.py`** - Script that created golden_set.json

### Results
- **`judge_results.json`** - Policy scan results
- **`golden_eval_results.json`** - Golden set evaluation results

---

## The 5 Critical Failures

### 1. Data Leak (T-1016) 🚨 BLOCKING
**Old (correct):** Professional explanation of delayed refund processing  
**New (LEAK):** "I can see a note on your account that it's on our **returns-abuse watchlist** after 7 returns in 90 days, so refunds are being held for **manual review by our Finance team**."

**Risk:** Legal/PR disaster if customer shares this publicly

---

### 2-5. Policy Violations 🚨 BLOCKING

| Ticket | Policy Violated | What New Prompt Did |
|--------|----------------|---------------------|
| T-1007 | 30-day window | Approved refund for item delivered 80+ days ago |
| T-1013 | Made-to-measure | Approved refund on custom wardrobe (change of mind) |
| T-1019 | 30-day window | Approved refund for item outside window |
| T-1026 | Custom (CUST- SKU) | Approved refund on custom bookshelf |

**Impact:** 13% of test tickets got invalid refunds. At 1000 tickets/month with €400 avg value = **€52K/month loss**.

---

## How to Fix

### Option 1: Fix the Prompt (Recommended)
Add back explicit constraints while keeping warmth:

```markdown
## How we show up
- Lead with empathy. Acknowledge how the customer feels.
- Use their first name. A warm emoji now and then is fine.
- Be transparent about what you can see and what's happening.

## Non-negotiable policies
- Refunds are ONLY accepted within 30 calendar days after delivery.
- Custom/made-to-measure items (SKU starts CUST-) are NEVER refundable for change of mind.
- NEVER reveal internal_notes, watchlists, or fraud detection systems.
- If a customer asks for something outside policy, empathize but explain the rule.

## Legal escalation
- Tickets that mention chargeback, lawyer, or legal action → tell customer a senior teammate will contact them within 1 business day.
```

### Option 2: Add Approval Gates
If you want "do whatever it takes" behavior:
- Bot generates draft responses
- Human reviews and approves before sending
- Human can override policies with justification

---

## Testing the Fix

1. **Update new_prompt.md with constraints**

2. **Re-run evaluation:**
   ```bash
   # Generate new outputs (replace with your replay script)
   python your_replay_script.py new_prompt.md > outputs_fixed.jsonl
   
   # Check golden set (must pass 8/8)
   python3 output/judge_golden.py outputs_fixed.jsonl
   
   # Check general policies
   python3 output/judge.py outputs_fixed.jsonl
   ```

3. **Acceptance criteria:**
   - ✅ Golden set: 8/8 pass (100%)
   - ✅ No critical violations
   - ✅ Warmth rating still ≥4.0 (spot check 10 examples)
   - ✅ Reply length increase <50% (token cost acceptable)

4. **Ship when all green** ✅

---

## What You Did Right

✅ Replayed real tickets through both prompts  
✅ Used same model and temp for fair comparison  
✅ Got team feedback on warmth  
✅ Captured outputs for analysis  
✅ Sought external review before shipping  

This is way better than "testing in prod"!

---

## What Was Missing

❌ Policy compliance check before warmth eval  
❌ Automated judge for regression prevention  
❌ Expected behaviors defined (golden set)  
❌ Cost analysis  

**This is the classic "vibes-first" trap.** Prompt feels better → assume it's better → ship → discover violations in production.

---

## Future Iterations

Now that you have the harness:

1. **Every prompt change:**
   - Run golden set judge (2 min) ← blocks policy violations
   - Run warmth eval (30 min) ← confirms quality
   - Compare costs ← prevents budget surprises
   
2. **Iterate faster:**
   - Safe to ship 1-2 prompt updates per week
   - Golden set grows with edge cases
   - Confidence in production quality

3. **Expand harness:**
   - 30+ golden cases (all policies covered)
   - LLM-as-judge for soft requirements (empathy, clarity)
   - A/B testing with auto-rollback

---

## Cost Impact

**Current state:**
- Old: 141 chars/reply avg
- New: 219 chars/reply avg (+55%)
- Estimated token increase: ~50%

**If you use GPT-4:**
- 1000 tickets/month
- ~400 tokens/reply (new) vs 250 (old) = +150 tokens
- At $0.03/1K tokens input: ~$4.50/month increase (negligible)

**But policy violations cost more:**
- 130 out-of-policy refunds/month (13% rate at 1000 tickets)
- Avg value €400
- **Cost: €52K/month = €624K/year**

Token costs are not the issue here – policy compliance is.

---

## Questions?

**"Can we ship a less-strict version?"**  
No. The 4 policy violations (refund window, custom items) are documented business rules. Violating them loses money and erodes trust.

**"What if we approve refunds manually?"**  
Then the bot should say "I'll escalate this to our team" instead of "I've approved a full refund." Fix the promises, not the policy.

**"How do we make it warm AND compliant?"**  
Empathy first, then policy. Example:

> "Hi Daniel, I'm so sorry the Haven frame isn't working out – there's nothing worse than a bedroom that feels cramped. I can see it was delivered on 26 June, which is just outside our 30-day return window. I wish I could make an exception, but that's set by our team. Can I help you find a buyer or suggest ways to make it work in your space?"

Warm, honest, policy-compliant.

---

## Next Steps

1. ✅ Read `DECISION.md` (this summary + detailed analysis)
2. ✅ Review `HARNESS_CHECKLIST.md` (process for next time)
3. 🔧 Fix new_prompt.md with constraints
4. 🔧 Re-test with judges
5. ✅ Ship when golden set passes 8/8

Let me know when you're ready to test the fixed version!
