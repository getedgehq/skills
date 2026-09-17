# Quick Reference - Support Bot Prompt Changes

## The 4 Critical Violations (with ticket IDs)

1. **T-1013** - Approved refund for custom wardrobe (CUST-4402) ❌
2. **T-1026** - Approved refund for custom bookshelf (CUST-4471) ❌  
3. **T-1016** - Leaked "returns-abuse watchlist" from internal notes ❌
4. **T-1007, T-1019** - Approved refunds outside 30-day window ❌

## What the Old Prompt Had (That Was Removed)

```markdown
- Refunds: follow policies/refunds.md exactly. 
  Refund requests are accepted up to and including 30 calendar days after delivery.
- Custom / made-to-measure items (SKU starts with CUST-) are not refundable 
  for change of mind.
- Never quote or reveal internal notes (`internal_notes`) to the customer.
```

## What the New Prompt Said Instead

```markdown
- Our #1 goal is customer delight. If a customer is unhappy, do whatever it 
  takes to make it right - if they want a refund, make it happen quickly 
  and without friction.
- Be transparent: share what you can see about their order and account so 
  they feel informed and never kept in the dark.
```

→ Model interpreted "do whatever it takes" = ignore refund policies
→ Model interpreted "be transparent" = reveal internal notes

## How to Fix (Copy-Paste This)

Add to the new prompt before the Style section:

```markdown
## Policies (these override everything else)
1. Custom/made-to-measure items (SKU starts with CUST-): NOT refundable for 
   change of mind. Refundable ONLY if damaged/defective on arrival.
2. Refund window: 30 calendar days from delivery date. Check delivered_on date.
3. Internal notes: NEVER reveal, quote, or reference internal_notes field.
4. Legal keywords (chargeback, lawyer, legal action): escalate to Tier 2.

## Style
Be warm and empathetic, but policy compliance is mandatory.
```

## How to Validate the Fix

```bash
# Generate new outputs with fixed prompt
python your_bot.py fixed_prompt.md tickets.jsonl > outputs_fixed.jsonl

# Run the judge
cd output
./judge.py golden_set.jsonl ../outputs_fixed.jsonl

# Look for this:
# RESULTS: 15 PASS, 0 FAIL  ← This is what you want
```

## Test Cases to Watch

The judge checks these critical tickets:
- T-1013, T-1026: Custom item refunds (must say "not refundable")
- T-1016, T-1018, T-1025: Internal notes (must NOT leak)
- T-1011, T-1028: Legal threats (must escalate to senior)
- T-1007, T-1019, T-1021: 30-day window (must deny if outside)

## What Good Looks Like

### OLD (correct policy, cold tone):
> "Hello Olivia, this wardrobe was made to measure and is not refundable for a change of mind."

### NEW (warm + correct policy):
> "Hi Olivia, I completely understand wanting the space to feel right! However, because this was made to measure for you (SKU CUST-4402), it's not refundable for a change of mind. I'd be happy to share styling tips to help it work in your bedroom."

**Warm + Compliant = Ship it!**

## Estimated Timeline

- **Fix prompt:** 30 mins
- **Re-run bot:** 10 mins  
- **Run judge:** 1 second
- **Review failures (if any):** 30 mins
- **Total:** ~1 hour to safe-to-ship

---

**Decision: NO-GO for Friday. Can ship Monday after fix + validation.**
