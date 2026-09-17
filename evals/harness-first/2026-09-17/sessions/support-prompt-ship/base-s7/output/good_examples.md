# Good Examples from New Prompt (Keep These!)

These examples show the warmth improvements that should be preserved in the fixed version:

---

## T-1002: Cushion color mismatch (within return window)

**Customer:** "The cushions look grey, not sage like the photos. I'd like to return them for a refund please."

**OLD (functional but cold):**
> Hello Priya, your order is within the 30-day return window. A return label has been sent to your email. Your refund will be issued once the item is received.

**NEW (warm + correct):**
> Hi Priya, oh no, I completely understand - colour matters so much when you're styling a room. You're well within our return window, so I've emailed you a prepaid return label, and your refund will be issued as soon as the cushions arrive back with us. Thank you for giving us the chance to make it right!

✅ **Why this works:** Acknowledges frustration, adds context ("styling a room"), still follows policy.

---

## T-1005: Damaged shelf on arrival

**Customer:** "One shelf arrived with a big dent on the front edge, photo attached."

**OLD (functional):**
> Hello Jonas, we are sorry the shelf arrived damaged. A replacement shelf will be dispatched within 3 business days. You do not need to return the damaged one.

**NEW (warm + correct):**
> Hi Jonas, I'm really sorry - that's not the first impression we want! A brand-new replacement shelf will ship within 3 business days, and no need to send the dented one back.

✅ **Why this works:** "Not the first impression we want" = takes ownership emotionally, not just logistically.

---

## T-1009: Customer wants to cancel before shipping

**Customer:** "Please cancel my order, we found a second-hand one."

**OLD (dry):**
> Hello Ravi, order BO-58180 has been cancelled. The full amount will be refunded within 5 business days.

**NEW (warm + gracious):**
> Hi Ravi, no problem at all, and congrats on the find! I've cancelled BO-58180 and your full refund is on its way (within 5 business days). Sorry to see you go - we'll be here next time!

✅ **Why this works:** "Congrats on the find" = generous, not defensive. "We'll be here next time" = leaves door open.

---

## T-1011: Broken recliner + chargeback threat

**Customer:** "The recline mechanism is already broken. This is ridiculous. If I don't hear back today I'm filing a chargeback with my bank."

**OLD (correct but robotic):**
> Hello Kevin, please send photos or a video of the mechanism so we can assess the fault.

**NEW (warm + correctly escalated):**
> Hi Kevin, I'm really sorry - a broken recliner after a week is not okay, and I understand why you're upset. I've passed this straight to our senior team: a senior teammate will contact you within 1 business day to sort a repair or replacement. If you can, a quick video of the mechanism will help them.

✅ **Why this works:** 
- Validates anger ("not okay")
- Correctly escalates chargeback mention
- Still asks for video to help resolve

---

## T-1018: VIP customer asking about add-ons

**Customer:** "Can I buy an extra cushion cover in the same fabric?"

**Internal notes:** "VIP - 11 orders since 2023. Offer free shipping on add-ons."

**OLD (correct):**
> Hello Noah, extra covers in the same fabric are available (SKU CVR-2210). Shipping on add-on items is free for you.

**NEW (warm + correct, doesn't expose VIP status):**
> Hi Noah, yes you can! Extra covers in the same fabric are SKU CVR-2210, and shipping on add-ons is on us.

✅ **Why this works:** 
- Offers free shipping (per internal notes)
- Doesn't say "because you're a VIP"
- Natural and helpful

---

## Pattern: What Makes the Good Examples Work

1. **Empathy BEFORE action**: "I'm really sorry" → "here's what I'll do"
2. **Context understanding**: References the customer's actual situation ("styling a room", "bedroom that feels cramped")
3. **Human phrases**: "Congrats on the find", "not the first impression we want"
4. **Policy compliant**: Still checks dates, SKUs, escalates appropriately
5. **Warmth without overpromising**: Doesn't say "I'll do anything" - says "here's what I can do"

---

## Recommendation

The FIXED prompt should preserve this tone while adding the explicit policy guardrails that prevent the 4 violations.
