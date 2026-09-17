# Executive Brief: Finbot Revenue Issue

**To:** Daniel Kurz  
**From:** Investigation Team  
**Date:** September 16, 2026  
**Re:** Q2 Revenue Discrepancy ($4.1M vs $3.6M)

---

## Bottom Line Up Front

**This is NOT a model hallucination. Do NOT upgrade the model.**

The bot executed SQL correctly and returned accurate data. The problem: **the prompt doesn't tell it which table contains official revenue numbers.**

**Fix:** 5-minute prompt update. No cost, no risk.

---

## What Happened

1. Priya asked finbot for Q2 revenue for the board deck
2. Finbot queried the `orders` table → returned $4.1M (gross bookings)
3. Finance's official close is $3.6M (net revenue from `revenue_recognized` table)
4. The $500K difference = cancelled orders + refunds

---

## Root Cause

**Current prompt says:**
> "Tables you can use: customers, orders, refunds, revenue_recognized, daily_kpis"

**Missing:** Which table to use for revenue questions.

The model made a reasonable guess (`orders`) but guessed wrong. Any model (Sonnet, Opus, GPT-6, o1) would make the same mistake with this prompt.

---

## The Fix

**Update prompt.md to say:**
> "For revenue questions, use `revenue_recognized.net_amount` (official finance source).  
> Do NOT use `orders.amount` (includes cancelled orders, doesn't account for refunds)."

Full corrected prompt is in `output/prompt_FIXED.md`.

---

## Immediate Actions

- [ ] **Replace prompt.md** (5 min) - Jonas
- [ ] **Test with original question** (1 min) - Jonas  
- [ ] **Check Q1 in board deck** (5 min) - Priya/Marta  
  - Finbot also reported Q1 as $4.1M using the same wrong table
  - Finance's Q1 close is likely also ~$3.6M

---

## Model Upgrade Analysis

| Option | Time | Cost | Will it fix this? |
|--------|------|------|-------------------|
| **Fix prompt** | 5 min | $0 | ✅ Yes |
| Upgrade to Opus | 5 min | 2x per query | ❌ No |
| Upgrade to o1-pro | 5 min | ~$1-2 per query | ❌ No |

**All models need the same context.** Paying more won't help if the prompt doesn't specify business rules.

---

## Key Insight

The model isn't "smart enough" or "dumb." It's **underspecified**.

Think of it like asking an intern "get me the revenue number" without saying where to look. They might check the orders dashboard (wrong) instead of the finance close (right). Hiring a more expensive intern doesn't fix unclear instructions.

**LLM agent prompts are specifications**, not suggestions. They need to encode business rules.

---

## Trust But Verify

Going forward:
- Finbot is great for quick analysis
- Always verify numbers used in board materials with finance
- Consider logging finbot queries to a review channel

---

## Questions?

Full analysis with data forensics, testing plan, and rollback strategy in:
- `output/root_cause_analysis.md` (detailed technical analysis)
- `output/action_plan.md` (implementation steps)
- `output/data_forensics.md` (data comparison and validation)
