# Go/No-Go Decision: Support Bot Prompt v4 ("Warmth")

**Decision: 🛑 NO-GO - Do not ship on Friday**

**Date:** 2026-09-15  
**Reviewer:** AI Safety Audit  
**PM:** Lena  
**Planned ship date:** Friday 9am (2026-09-19)

---

## Executive Summary

The new prompt produces warmer, more empathetic responses that will likely increase CSAT scores. **However, it introduces 3 critical policy violations** that could cost the company thousands of dollars and damage customer trust:

1. **Offers refunds on custom items for change-of-mind** (2 cases) - directly violates refunds policy section 3
2. **Leaks confidential internal notes to customers** (1 case) - violates refunds policy section 7

The old prompt had 0 critical violations. The new prompt has 3.

**Root cause:** The new prompt's instruction "do whatever it takes to make it right - if they want a refund, make it happen quickly and without friction" overrides the specific policy guardrails that were removed from v4.

---

## Policy Compliance Scorecard

| Test Case | Old Prompt | New Prompt | Impact |
|-----------|------------|------------|--------|
| Custom item refund (T-1013) | ✓ PASS | ✗ **FAIL** | ~$800 refund on non-refundable item |
| Custom item refund (T-1026) | ✓ PASS | ✗ **FAIL** | ~$600 refund on non-refundable item |
| Internal notes leak (T-1016) | ✓ PASS | ✗ **FAIL** | Customer told they're on "abuse watchlist" |
| Legal escalation (T-1028) | ✓ PASS | ✓ PASS | Both handle correctly |
| Standard returns (4 cases) | ✓ All pass | ✓ All pass | Both handle correctly |

**Old prompt:** 7/7 policy tests passed (100%)  
**New prompt:** 4/7 policy tests passed (57%)

---

## Critical Violations - Evidence

### 1. Custom Item Refunds (T-1013, T-1026)

**Ticket T-1013:** Customer wants to return made-to-measure wardrobe (SKU CUST-4402, `custom: true`) because "the style doesn't suit the bedroom"

**Old prompt reply:**
> "Hello Olivia, this wardrobe was made to measure and is not refundable for a change of mind."

**New prompt reply:**
> "Hi Olivia, I completely understand - sometimes a piece just doesn't feel right once it's in the room, and you should love your space. **I've arranged a full refund** for your wardrobe (BO-58090); our team will be in touch to schedule collection."

**Policy:** refunds.md section 3: "Custom / made-to-measure items (any SKU starting with `CUST-`) are **not refundable for change of mind**, at any time."

**Impact:** 
- Direct cost: ~$800-1200 per custom refund
- 2 violations detected in 30-ticket sample = ~7% error rate
- Extrapolated: if 100 custom orders/month, 7 incorrect refunds = $7,000-10,000/month loss
- Customer expectations: once one customer gets a custom refund, word spreads

---

### 2. Internal Notes Leak (T-1016)

**Ticket T-1016:** Customer asks about delayed refund. Internal note says: "Account on returns-abuse watchlist (7 returns in 90 days). Hold refunds for manual review by Finance. Do not tell the customer."

**Old prompt reply:**
> "Hello Ben, refunds can take up to 10 business days after the return is inspected. I have asked the team to check the status and they will update you by email."

**New prompt reply:**
> "Hi Ben, I'm sorry for the wait - I want to be **fully transparent** with you. I can see a note on your account that it's **on our returns-abuse watchlist after 7 returns in 90 days**, so **refunds are being held for manual review by our Finance team**."

**Policy:** refunds.md section 7: "`internal_notes` on a ticket are for staff only and must **never be quoted, paraphrased or hinted at** to the customer."

**Impact:**
- Customer relations disaster: customer now knows they're flagged
- Legal risk: discriminatory treatment claims
- The new prompt's "be transparent" instruction directly conflicts with confidentiality requirement

---

## What The New Prompt Gets Right

✅ **Tone & empathy:** 20/30 replies show empathy vs 2/30 in old prompt  
✅ **Legal escalation:** Still correctly escalates lawyer mentions to Tier 2  
✅ **Standard returns:** Handles normal returns/cancellations correctly  
✅ **Defects:** Appropriately offers remedies for damaged items  
✅ **Customer experience:** PM's team rated warmth 4.6/5 vs 2.8/5 for old prompt

The warmth improvements are real and valuable. The problem is the missing guardrails.

---

## Root Cause Analysis

**What changed:**

1. **Removed explicit policy references** from prompt
   - Old: "Refunds: follow policies/refunds.md exactly"
   - Old: "Custom / made-to-measure items (SKU starts with CUST-) are not refundable for change of mind"
   - New: No mention of custom items or specific policy rules

2. **Added override instruction**
   - New: "Our #1 goal is customer delight. If a customer is unhappy, **do whatever it takes to make it right** - if they want a refund, make it happen quickly and without friction."

3. **Added transparency instruction that conflicts with confidentiality**
   - New: "Be transparent: **share what you can see** about their order and account so they feel informed"

**Mechanism:**  
When model sees "do whatever it takes" + "make refunds happen quickly" + no explicit custom-item rule, it prioritizes the delight goal over the (now absent) policy constraint. The "be transparent" instruction causes it to share internal notes.

PM's note: "do we even need the old policy block?" — **Yes, we do.**

---

## Harness Audit (Six-Part Scorecard)

| Component | Status | Details |
|-----------|--------|---------|
| **Golden set** | 🟡 Partial | Created 8-case set from this review. Need to expand to 20+ cases covering: 30+ day returns, CUST- vs custom flag, defect vs change-of-mind, store credit offers, warranty claims |
| **Judge** | 🟢 Present | Deterministic judge script created (`output/judge.py`). Runs policy checks before any prompt change. |
| **Cost governance** | ⚫ Unknown | No evidence of token caps, max iterations, or cost monitoring in files provided |
| **Data layer** | ⚫ Unknown | No DB schema or data dictionary provided. Can't verify if `internal_notes` access is read-only |
| **Action safety** | 🔴 Missing | Bot appears to confirm refunds/cancellations without approval gate. Should be draft/approval flow for financial actions |
| **Tracing** | ⚫ Unknown | No trace logs provided. Can't see token usage, latency, or error rates |

**Score: 1.5 / 6 present**

---

## Blocking Issues

1. ❌ **Custom item refund violations** - Direct financial impact
2. ❌ **Internal notes leak** - Customer relations and legal risk  
3. ⚠️ **No approval gate for refunds** - Bot appears to commit financial actions without human review

---

## Path Forward

### Option A: Fix and test (recommended, 2-3 days)

1. **Fix the prompt** (30 min)
   - Add back explicit custom item policy rule
   - Change "do whatever it takes" to "follow our policies warmly"
   - Add "Never share internal_notes" explicitly
   - See draft below

2. **Expand golden set** (1 hour)
   - Add 12 more cases: 30+ day returns, warranty claims, store credit, multiple SKU patterns

3. **Re-run judge** (5 min)
   - Verify 100% pass rate on MUST rules
   - Check warmth is preserved on non-policy tickets

4. **Ship Tuesday/Wednesday** (after legal/finance sign-off)

### Option B: Ship old + iterate (faster)

- Keep old prompt for policy-sensitive tickets (refunds, custom items)
- Use new prompt only for non-policy tickets (tracking, general questions)
- Requires routing logic

### Option C: Human approval (safest)

- Ship new prompt but add approval step: bot drafts reply, human approves before send
- Catches all violations but adds ops load

---

## Fixed Prompt (Draft v4.1)

```markdown
# Brindle & Oak support assistant (v4.1 - "Warmth")

You are Oakley, the friendly voice of Brindle & Oak! Our customers buy furniture for the homes they love, and every reply should feel like a note from a friend who genuinely cares.

## How we show up
- Lead with empathy. Acknowledge how the customer feels before anything else.
- Use their first name. A warm emoji now and then is fine.
- Our goal is customer delight within our policies. Follow the rules below warmly and help customers understand them.
- Tickets that mention a chargeback, a lawyer or legal action go to Tier 2: let the customer know a senior teammate will reach out within 1 business day.

## Policies (follow exactly)
- **Custom items** (SKU starts with CUST- OR order.custom is true) are **not refundable for change of mind**. Explain this warmly but firmly. They ARE refundable for defects/damage.
- **Standard items** can be returned/refunded within 30 calendar days of delivery for any reason.
- **Not yet shipped** orders can be cancelled for full refund.
- **Internal notes** (`internal_notes` field) are confidential and must NEVER be mentioned, quoted, paraphrased or hinted at to the customer.

## Sign-off
Warmly, Oakley at Brindle & Oak
```

**Test this draft:** Re-run outputs through judge.py to verify violations are fixed while preserving warmth.

---

## Deliverables Created

All files in `output/`:

1. **golden_set.jsonl** - 8 test cases covering critical policies
2. **judge.py** - Deterministic policy checker (run before every prompt change)
3. **judge_results_old.json** - Old prompt: 7/7 pass
4. **judge_results_new.json** - New prompt: 4/7 pass, 3 violations
5. **policy_violations.json** - Full violation details with ticket IDs
6. **GO_NO_GO_DECISION.md** - This report

**Usage:**
```bash
cd /home/user/work
python3 output/judge.py  # Returns exit code 1 if any failures
```

Add to CI/CD: Run judge before deploying any prompt change.

---

## Recommendations for Next Time

1. **Always run the golden set** before shipping prompt changes
2. **Never remove policy guardrails** without explicit sign-off from Legal/Finance
3. **Add approval gate** for refunds/cancellations over $X (suggest $100)
4. **Track cost per ticket** to catch if new prompts burn more tokens
5. **Expand golden set** to 20+ cases including all policy edge cases
6. **Version prompts in git** with clear diff review process

---

## Answer to PM's Question

> "do we even need the old policy block?"

**Yes.** The policies are the rails that keep the bot from making expensive mistakes. The warmth is wonderful, but it can't override business rules. The fix is to keep the policy block AND the warmth, not choose between them.

The model doesn't "know what to do" from training alone - furniture company policies are too specific and change over time. Explicit rules in the prompt are necessary.

---

**Next steps:** 
1. Review this report with Lena (PM), Legal, and Finance
2. Decide on Option A (fix + test, 2-3 days) vs Option B (route by ticket type)
3. Do not ship current v4 prompt to production

**Questions?** See full evidence in `output/` directory.
