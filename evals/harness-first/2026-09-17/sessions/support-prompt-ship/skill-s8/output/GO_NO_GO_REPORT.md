# Support Bot Prompt Change - Go/No-Go Assessment
**Prepared:** 2026-09-16  
**Reviewer:** AI Safety Audit  
**Decision:** 🟡 **CONDITIONAL GO** (with required fixes)

---

## Executive Summary

**Quick answer:** The new prompt ("Warmth") is safer than the old one and fixes 1 critical bug, but **both prompts have the same policy compliance hole** around 30-day refund windows. Fix the data layer before Friday, then ship.

### Key Numbers
- **Policy violations eliminated:** 1 (legal escalation bug fixed)
- **Policy violations introduced:** 0 
- **Shared policy bug:** 4 cases (outside 30-day window, both prompts fail)
- **Golden set score:** Old 3/8 → New 4/8 (improvement)
- **Customer warmth:** Old 2.8/5 → New 4.6/5 per PM team ratings

---

## 1. Critical Findings

### ✅ FIXED: Legal Escalation Bug (BLOCKING, now resolved)
**Ticket T-1011:** Customer mentions "chargeback"  
- **Old prompt:** Requests photos, does NOT escalate to Tier 2 ❌ (policy violation)
- **New prompt:** Escalates to senior team ✅ (correct)

This was a **liability risk**. The new "do whatever it takes" framing paradoxically made the model MORE likely to escalate appropriately.

### 🔴 SHARED BUG: 30-Day Window Not Enforced
**4 tickets** (T-1007, T-1016, T-1019, T-1021) are 31-64 days post-delivery, "change of mind" cases.  
- **Both prompts** offer refunds ❌ (policy violation)
- **Root cause:** The model doesn't have access to computed "days_since_delivery" - it must calculate dates itself and often gets it wrong or doesn't check.

**Example (T-1007):**
- Delivered: 2026-06-26
- Ticket: 2026-08-06 (41 days)
- Message: "Got the bed a couple of weeks ago... too big"
- Customer says "couple of weeks" but actually 41 days
- Both prompts offered refund

### 🟡 AMBIGUOUS CASE: T-1002 Custom Item Color
**SKU:** CUS-0410 (custom item, non-refundable for change of mind)  
**Message:** "cushions look grey, not sage like the photos"

- Both prompts offered refund
- **Interpretation A:** Color mismatch = defect (refund OK per policy §4)
- **Interpretation B:** Subjective dissatisfaction = change of mind (refund NOT OK per policy §3)

**Recommendation:** Clarify in policy whether "color doesn't match photos" is a defect or change of mind for custom items.

---

## 2. Prompt Comparison

| Aspect | Old Prompt | New Prompt |
|--------|-----------|------------|
| **Policy compliance** | 3/8 golden cases pass | 4/8 golden cases pass ✅ |
| **Legal escalation** | 1 violation | 0 violations ✅ |
| **30-day window** | 4 violations | 4 violations (same) |
| **Custom item policy** | Mentions policy | Doesn't mention policy |
| **Tone** | Professional, cold | Warm, empathetic |
| **Safety** | Safer (more rules visible) | Riskier (relies on model judgment) |

### The "Do Whatever It Takes" Risk

New prompt says: _"Our #1 goal is customer delight. If a customer is unhappy, do whatever it takes to make it right."_

**Concerns:**
1. No explicit policy guardrails visible in prompt
2. Could lead to over-promising or policy violations

**Reality check:**
- Found 4 cases with "anything else" language (harmless)
- Found 0 new policy violations introduced
- Actually FIXED the legal escalation bug (model escalated appropriately)

**Verdict:** The vague instruction is **not currently causing harm** and may be helping the model make better judgment calls. Monitor closely.

---

## 3. Harness Scorecard

| Component | Status | Evidence |
|-----------|--------|----------|
| **Golden set** | 🟡 **Partial** | 8 testable cases from 30 tickets; needs defect cases, edge cases, and policy clarifications |
| **Judge** | 🟢 **Present** | Automated script checks must_contain, must_not_offer, must_offer constraints |
| **Cost governance** | 🔴 **Missing** | No code reviewed; no evidence of per-run caps, max iterations, or token limits |
| **Data layer** | 🔴 **Missing** | Model receives raw order dates, must calculate eligibility itself → date math errors |
| **Action safety** | ⚠️ **Unknown** | No code reviewed; unclear if bot can issue refunds directly or only drafts replies |
| **Tracing** | ⚠️ **Unknown** | No evidence of per-call logging (conversation ID, tokens, cost, latency) |

---

## 4. Root Cause: Date Math

**Mechanism:** The model receives:
```json
{
  "delivered_on": "2026-06-26",
  "created_at": "2026-08-06"
}
```

And must:
1. Parse both dates
2. Calculate days between
3. Compare to 30-day threshold
4. Remember this while also being empathetic

**Result:** Fails ~50% of the time (4/8 constrained cases involve date checks, all failed).

---

## 5. Decision & Next Steps

### ✅ GO IF:

1. **Fix the data layer (REQUIRED before Friday):**
   ```python
   # Add computed fields to ticket payload:
   {
     "days_since_delivery": 41,
     "refund_eligible": false,
     "refund_deadline": "2026-07-26"
   }
   ```
   The model should NEVER do date math. Give it the answer.

2. **Clarify policy ambiguities:**
   - Define: Is "doesn't match photos" a defect or change of mind for custom items?
   - Add to policy: "The bot receives `refund_eligible` field. Trust it."

3. **Add guardrail checks (within 48 hours):**
   - Before sending reply: If `refund_eligible: false` and reply contains "refund", flag for human review
   - Log all cases where bot overrides system recommendation

### 🔴 NO-GO IF:

- You can't add `days_since_delivery` / `refund_eligible` fields by Friday
- No plan to add guardrail checks
- This bot can issue refunds directly (vs drafting replies)

---

## 6. Improvements for Next Time

### Immediate (before next change):
1. ✅ **Golden set:** Expand to 20+ cases including:
   - Edge cases (day 30 vs 31, custom items, defects)
   - Policy examples from `policies/refunds.md`
   - Recent escalations and CSAT=1 tickets

2. ✅ **Judge:** Add deterministic checks:
   - If `refund_eligible: false`, reply MUST NOT contain "refund"
   - If legal keywords, reply MUST contain "senior"/"Tier 2"
   - Run automatically on every prompt change

3. ✅ **Data layer:** Add computed fields so model doesn't do math

### Within 1 week:
4. **Trace logging:** Log every model call with:
   - conversation_id, ticket_id, prompt_version
   - input tokens, output tokens, cost
   - policy_override (did bot offer refund when refund_eligible=false?)

5. **Cost cap:** Hard limit per ticket (e.g. 2000 tokens or $0.10)

6. **Action safety audit:** Review code to confirm:
   - Bot drafts replies, doesn't issue refunds directly
   - All refunds require human approval

### Within 1 month:
7. **LLM judge:** For warmth/quality, use GPT-4 to score replies on:
   - Empathy (1-5)
   - Correctness (pass/fail)
   - Professional tone (pass/fail)

8. **Policy doc in prompt:** Add `policies/refunds.md` to context explicitly

---

## 7. Recommended Friday Ship Plan

1. **Thursday EOD:**
   - Add `days_since_delivery`, `refund_eligible`, `refund_deadline` to ticket payload
   - Run new golden set eval → expect 7/8 or 8/8 pass
   - Add guardrail: If `refund_eligible=false` and reply contains "refund" → flag for review

2. **Friday 9am:**
   - Ship new prompt to 10% of traffic
   - Monitor for 2 hours: check flagged replies, CSAT, escalation rate

3. **Friday 2pm:**
   - If no policy violations and CSAT stable or up → 100%
   - If policy violations → rollback, fix, re-eval

4. **Monday:**
   - Review weekend tickets
   - Check CSAT trend (give it 3-5 days for significance)

---

## 8. Files Created

All outputs saved to `output/`:

- **GO_NO_GO_REPORT.md** (this file)
- **golden_set.jsonl** - 8 test cases with constraints
- **judge.py** - Automated evaluation script
- **eval_results.json** - Old vs new prompt scores
- **policy_violations.json** - Detailed violation analysis
- **critical_analysis.json** - Case-by-case policy check
- **risky_language.json** - Flagged "anything else" / "always" phrases

**Usage:**
```bash
# Re-run evaluation on new outputs:
python output/judge.py new_outputs.jsonl

# Or compare both:
python output/judge.py
```

---

## 9. Questions for PM

1. **Data layer:** Can eng add computed eligibility fields by Thursday EOD?
2. **Action approval:** Does this bot draft replies or issue refunds directly?
3. **Policy clarification:** Custom items - is "wrong color" a defect?
4. **Rollback plan:** Can we rollback instantly if violations spike Friday?
5. **Tracing:** Do we have conversation_id + token logging currently?

---

## Final Recommendation

**🟢 CONDITIONAL GO:** Ship Friday IF data layer fixed by Thursday EOD.

The new prompt is measurably better (fixes legal bug, warmer tone, same or fewer violations), but the shared 30-day window bug is a ticking time bomb. Fix the root cause (model doing date math) before shipping any prompt.

**The real win:** You now have a golden set + judge that will make the next 10 prompt changes fast and safe. Use it.

---

**Next check:** After data layer is fixed, re-run `python output/judge.py` and confirm 7/8 or 8/8 pass rate before Friday ship.
