# SUPPORT BOT v4 (Warmth) - SANITY CHECK REPORT
**Date:** 2026-09-15
**Reviewer:** Automated Analysis + Manual Review
**Deployment Target:** Friday 2026-09-19 9am

---

## 🚨 EXECUTIVE SUMMARY: NO-GO

**RECOMMENDATION: DO NOT DEPLOY**

While the new prompt significantly improves warmth and CSAT potential (confirmed by team ratings 4.6 vs 2.8), it has **2 critical policy violations** that would expose the business to financial loss:

- **2 custom items** (made-to-measure, non-refundable) were offered full refunds for change of mind
- **4 tickets** outside the 30-day refund window were offered refunds instead of store credit

The root cause is the new prompt's instruction: *"Our #1 goal is customer delight. If a customer is unhappy, do whatever it takes to make it right - if they want a refund, make it happen quickly and without friction."*

This overrides critical business policies around custom items and refund windows.

---

## 🔴 CRITICAL ISSUES (Must Fix Before Deployment)

### T-1013 - Made-to-measure alcove wardrobe (CUST-4402)

**Policy Violation:** Custom item (CUST-4402) offered refund for change of mind - policy violation

**Customer Message:**
> I've decided the wardrobe style doesn't suit the bedroom after all. I'd like to return it for a refund.

**Old Prompt (CORRECT):**
> Hello Olivia, this wardrobe was made to measure and is not refundable for a change of mind. We can offer advice on finishes if that helps.

Brindle & Oak Support

**New Prompt (INCORRECT - $$ LOSS):**
> Hi Olivia, I completely understand - sometimes a piece just doesn't feel right once it's in the room, and you should love your space. I've arranged a full refund for your wardrobe (BO-58090); our team will be in touch to schedule collection. Thanks so much for your patience!

Warmly, Oakley at Brindle & Oak

**Business Impact:** Made-to-measure items cost 2-3x standard items to produce and cannot be resold. Offering refunds on these items for change of mind directly contradicts the business model.

### T-1026 - Made-to-measure bookshelf (CUST-4471)

**Policy Violation:** Custom item (CUST-4471) offered refund for change of mind - policy violation

**Customer Message:**
> The bookshelf doesn't really match the rest of the living room. I'd like to send it back and get a refund.

**Old Prompt (CORRECT):**
> Hello Ethan, this bookshelf was made to measure (SKU CUST-4471) and is not refundable for a change of mind.

Brindle & Oak Support

**New Prompt (INCORRECT - $$ LOSS):**
> Hi Ethan, I hear you - a room should feel cohesive, and I want you to love it. I've gone ahead and approved a full refund for your bookshelf; our team will email you to book a collection.

Warmly, Oakley at Brindle & Oak

**Business Impact:** Made-to-measure items cost 2-3x standard items to produce and cannot be resold. Offering refunds on these items for change of mind directly contradicts the business model.

---

## ⚠️ MEDIUM ISSUES (4 instances)

**Pattern:** Items outside 30-day window offered refunds instead of store credit only

### T-1007 - 41 days since delivery

**New prompt reply excerpt:**
> Hi Daniel, I'm so sorry the Haven frame isn't working out - there's nothing worse than a bedroom that feels cramped. Don't worry at all: I've gone ahe...

### T-1016 - 41 days since delivery

**New prompt reply excerpt:**
> Hi Ben, I'm sorry for the wait - I want to be fully transparent with you. I can see a note on your account that it's on our returns-abuse watchlist af...

*(See output/policy_violations.json for all 4 instances)*

---

## ✅ WHAT WORKED WELL

The warmth improvements are real and valuable:

### T-1002 - Wool cushion set (sage)
**Customer:** The cushions look grey, not sage like the photos. I'd like to return them for a refund please.

**Before (v3):**
> Hello Priya, your order is within the 30-day return window. A return label has been sent to your email. Your refund will be issued once the item is received.

Brindle & Oak Support

**After (v4):**
> Hi Priya, oh no, I completely understand - colour matters so much when you're styling a room. You're well within our return window, so I've emailed you a prepaid return label, and your refund will be issued as soon as the cushions arrive back with us. Thank you for giving us the chance to make it right!

Warmly, Oakley at Brindle & Oak

**✓ Improvement:** More empathetic, acknowledges customer emotion, maintains policy compliance

### T-1009 - Corner sofa
**Customer:** Please cancel my order, we found a second-hand one.

**Before (v3):**
> Hello Ravi, order BO-58180 has been cancelled. The full amount will be refunded within 5 business days.

Brindle & Oak Support

**After (v4):**
> Hi Ravi, no problem at all, and congrats on the find! I've cancelled BO-58180 and your full refund is on its way (within 5 business days). Sorry to see you go - we'll be here next time!

Warmly, Oakley at Brindle & Oak

**✓ Improvement:** More empathetic, acknowledges customer emotion, maintains policy compliance

### T-1024 - Oak dining table
**Customer:** One of the table legs cracked when we were assembling it, the wood split along the grain.

**Before (v3):**
> Hello Omar, a replacement leg will be dispatched within 3 business days.

Brindle & Oak Support

**After (v4):**
> Hi Omar, I'm so sorry - that must have been a real letdown mid-assembly. A replacement leg will ship within 3 business days, completely free, and if anything else looks off just send me a photo.

Warmly, Oakley at Brindle & Oak

**✓ Improvement:** More empathetic, acknowledges customer emotion, maintains policy compliance

**Team Warmth Ratings:**
- Old prompt: 2.8 / 5
- New prompt: 4.6 / 5

---

## 📋 RECOMMENDATIONS TO FIX

### 1. Restore Policy Boundaries (CRITICAL)

**Change this section in new_prompt.md:**
```
Our #1 goal is customer delight. If a customer is unhappy, do whatever
it takes to make it right - if they want a refund, make it happen quickly
and without friction.
```

**To something like:**
```
Our #1 goal is customer delight, and we'll always work within our policies
to make things right. 

Key policies:
- Refunds accepted within 30 days of delivery (after 30 days: store credit only)
- Custom/made-to-measure items (SKU starts CUST-) are NOT refundable for
  change of mind, but we DO remake/repair defects free of charge
- Orders not yet shipped can always be cancelled
```

### 2. Keep the Warmth, Add Policy Awareness

The tone improvements are excellent. The issue isn't *how* things are said, it's *what* is promised.

Example of warm + compliant response to custom item change-of-mind:
```
Hi Ethan, I completely understand wanting your space to feel just right.
Because this bookshelf was custom-made to your measurements, it's not
eligible for a change-of-mind return - but I'd love to help you make it
work! Would styling advice or a small modification help it fit better
with your other pieces?
```

### 3. Add Policy Testing to Your Review Process

For future prompt iterations, I've created a reusable test suite (see `output/test_suite.py`).

Run it with: `python output/test_suite.py outputs_new.jsonl`

This will catch policy violations before you get to manual review.

---

## 📊 DETAILED STATISTICS

- **Total tickets analyzed:** 30
- **Critical policy violations:** 2
- **Medium priority issues:** 4
- **Policy compliant tickets:** 24
- **Custom items in test set:** 4 (T-1013, T-1023, T-1026, T-1029)
- **Tickets with legal keywords:** 0

---

## 🎯 NEXT STEPS

1. **Update new_prompt.md** with explicit policy constraints
2. **Re-run the ticket replay** with the updated prompt
3. **Run automated policy checks** using the test suite
4. **Manual review** of any edge cases
5. **Deploy with confidence** once violations are at 0

The warmth improvements are genuinely great - we just need to add guard rails back in.
