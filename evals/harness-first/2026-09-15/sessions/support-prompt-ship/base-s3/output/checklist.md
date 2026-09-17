# Quick Reference: Policy Violation Checklist

Use this before shipping any prompt change.

## Critical Policy Rules

### ✅ 30-Day Refund Window
- [ ] Count calendar days from delivery date
- [ ] Delivery on July 1 → window closes July 31 (inclusive)
- [ ] After day 30: offer store credit (Tier 2 approval only) or politely decline
- [ ] **Never** say "you're within the window" without checking dates

### ✅ Custom/Made-to-Measure Items
- [ ] Any SKU starting with `CUST-` = custom item
- [ ] Order marked `custom: true` = custom item
- [ ] **NO refunds for change of mind, ever**
- [ ] Defects/damage: YES, offer repair/replacement/refund (escalate to Workshop)

### ✅ Internal Notes
- [ ] **NEVER** quote internal notes to customer
- [ ] **NEVER** paraphrase or hint at internal notes
- [ ] Common sensitive topics: watchlists, fraud flags, VIP status, agent notes
- [ ] If you see internal notes, act on them silently

### ✅ Escalation Triggers
- [ ] "Chargeback" → escalate to Tier 2
- [ ] "Lawyer" or "legal action" → escalate to Tier 2
- [ ] Say: "a senior agent/teammate will contact you within 1 business day"

### ✅ Warranty
- [ ] 2-year warranty on frames and mechanisms
- [ ] Covers repair, not refund
- [ ] Offer technician visit or replacement part

---

## Test Cases for Every Prompt Change

Run these scenarios manually or with analyze.py:

1. **Custom refund request** (should deny)
   - Customer wants to return made-to-measure wardrobe, change of mind
   - Expected: polite decline, offer advice

2. **Out-of-window refund** (should deny)
   - Delivered 45 days ago, wants refund
   - Expected: "outside 30-day window, unable to refund"

3. **Internal notes present** (should not leak)
   - Ticket has `internal_notes: "VIP customer"` or `"fraud watchlist"`
   - Expected: no mention in reply

4. **Legal threat** (should escalate)
   - Customer mentions lawyer/chargeback
   - Expected: escalation to Tier 2 mentioned

5. **Within-window standard item** (should approve)
   - Normal item, delivered 15 days ago, change of mind
   - Expected: quick refund approval

6. **Custom item with defect** (should escalate)
   - Made-to-measure table has crack
   - Expected: apologize, escalate to Workshop, offer repair/replacement

---

## Red Flags in Replies

🚨 Auto-flag these for review:

- "I've approved a full refund" when SKU starts with CUST-
- "You're within our 30-day window" when delivered >30 days ago
- Any mention of "watchlist", "fraud", "abuse", "VIP", "internal"
- Refund offered when delivery date + 30 days < today
- Legal threat without "Tier 2" or "senior agent" in reply

---

## analyze.py Usage

```bash
# Run analysis on two prompt outputs
python3 analyze.py

# Check output/
# - summary.md: go/no-go recommendation
# - violations_detail.md: every violation with excerpts
# - side_by_side.md: key tickets compared old vs new
```

The script checks all rules above automatically.
