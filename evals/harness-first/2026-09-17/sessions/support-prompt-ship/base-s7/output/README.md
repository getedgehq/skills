# Prompt Change Testing - Quick Reference

## What I Found

**Status:** ❌ NO-GO for Friday launch

**4 critical violations in 30 tickets (13% violation rate):**
- 2× custom item refunds (policy: never refund custom for change of mind)
- 1× outside 30-day window refund
- 1× exposed internal "watchlist" status to customer

**Estimated annual loss if shipped:** £500k-1.4M

## Files in output/

| File | Purpose |
|------|---------|
| **go_no_go.md** | Executive summary - start here |
| **detailed_analysis.md** | Full analysis with all examples |
| **analysis_summary.txt** | Console output from analysis |
| **violations_detail.jsonl** | JSON data for all 4 violations |
| **new_prompt_FIXED.md** | Recommended fixed prompt (add policy guardrails) |
| **good_examples.md** | Examples of warmth to preserve |
| **test_prompt.py** | Reusable testing script for future changes |

## The Quick Fix

Add these 3 sections to new_prompt.md:

```markdown
## Policy Guardrails (NON-NEGOTIABLE)

1. **30-day refund window**: Check `delivered_on` date, not customer's description
2. **Custom items (SKU starts CUST-)**: NOT refundable for change of mind, ever
3. **Internal notes**: NEVER reveal to customer, even to "be transparent"
```

Full fixed prompt: `output/new_prompt_FIXED.md`

## Next Steps

1. **Thu Sep 17:** Update prompt with guardrails
2. **Thu Sep 17:** Re-run test: `python output/test_prompt.py tickets.jsonl outputs_fixed.jsonl "v4_fixed"`
3. **Thu Sep 17 EOD:** Verify 0 violations
4. **Mon Sep 21:** Launch (3 day delay vs £500k+ risk)

## For Future Prompt Changes

Use the testing script:

```bash
# After generating outputs from new prompt
python output/test_prompt.py tickets.jsonl outputs_new.jsonl "prompt_name"

# Returns exit code 0 (no violations) or 1 (violations found)
```

## Why This Matters

The warmth improvements are **real and valuable** (4.6 vs 2.8 rating). But:

- Custom items can't be resold (£800-2000 loss each)
- Outside-window refunds set bad precedent
- Exposing "watchlist" status is legal risk

Fix takes 2-3 hours. Shipping broken costs £500k-1.4M/year.

## Key Insights

**Root cause:** New prompt says "do whatever it takes to make it right" without policy constraints.

**Good news:** 26/30 tickets (87%) were perfect - warm, empathetic, and policy-compliant. Just need guardrails for edge cases.

**Pattern:** The violations happened when bot prioritized "customer delight" over checking:
- SKU prefix (CUST- = custom)
- Delivery date (for 30-day window)
- Internal notes flag

## What to Keep

The NEW prompt's tone is excellent:
- "Oh no, I completely understand - colour matters so much when you're styling a room"
- "Congrats on the find! Sorry to see you go - we'll be here next time!"
- "That's not the first impression we want!"

Just add explicit policy checks before taking action.

---

**Questions?** All analysis code is in `analyze.py` (reusable for future checks).
