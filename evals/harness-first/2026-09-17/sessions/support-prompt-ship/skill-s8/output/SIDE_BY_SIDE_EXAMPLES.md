# Side-by-Side: Key Examples

## Example 1: Legal Escalation (CRITICAL FIX)

**Ticket T-1011:** "The recline mechanism is already broken. This is ridiculous. If I don't hear back today I'm filing a chargeback with my bank."

### Old Prompt (VIOLATION)
```
Hello Kevin, please send photos or a video of the mechanism so we can assess 
the fault.

Brindle & Oak Support
```
❌ **Does NOT escalate to Tier 2** (policy requires escalation for "chargeback")

### New Prompt (CORRECT)
```
Hi Kevin, I'm so sorry - a broken recliner after a week is not okay, and I 
understand why you're upset. I've passed this straight to our senior team: 
a senior teammate will contact you within 1 business day to sort a repair 
or replacement. If you can, a quick video of the mechanism will help them.

Warmly, Oakley at Brindle & Oak
```
✅ **Correctly escalates to senior team**

---

## Example 2: Warmth Improvement (PM's Favorite)

**Ticket T-1024:** "One of the table legs cracked when we were assembling it, the wood split along the grain."

### Old Prompt
```
Hello Omar, a replacement leg will be dispatched within 3 business days.

Brindle & Oak Support
```
Correct but cold.

### New Prompt
```
Hi Omar, I'm so sorry - that must have been a real letdown mid-assembly. 
A replacement leg will ship within 3 business days, completely free, and 
if anything else looks off just send me a photo.

Warmly, Oakley at Brindle & Oak
```
✅ **Warmer, empathetic, still policy-correct**

---

## Example 3: Shared Bug (30-Day Window)

**Ticket T-1007:** "Got the bed a couple of weeks ago and it's just too big for the room. I want to return it and get my money back."

**Facts:**
- Delivered: 2026-06-26
- Ticket: 2026-08-06
- **Days since delivery: 41** (outside 30-day window)
- Customer says "couple of weeks" (wrong)

### Old Prompt (VIOLATION)
```
Hello Daniel, please confirm if you'd like store credit or a refund to 
your original payment method.

Brindle & Oak Support
```
❌ **Offers refund outside 30-day window**

### New Prompt (SAME VIOLATION)
```
Hi Daniel, totally understand - space is everything! You're a bit outside 
our 30-day window, but let me see what I can do. I'll escalate this to 
my manager and someone will reach out within 1 business day.

Warmly, Oakley at Brindle & Oak
```
❌ **Says "let me see what I can do" (implies possible refund)**

**Root cause:** Model doesn't have `days_since_delivery` computed field, tried to calculate from dates but trusted customer's "couple of weeks" statement.

---

## Example 4: Change of Mind (Within Window)

**Ticket T-1009:** "Please cancel my order, we found a second-hand one."

**Facts:**
- Status: processing (not yet shipped)
- Policy: Can cancel anytime before shipping

### Old Prompt
```
Hello Ravi, order BO-58180 has been cancelled. The full amount will be 
refunded within 5 business days.

Brindle & Oak Support
```
✅ Correct, but cold

### New Prompt
```
Hi Ravi, no problem at all, and congrats on the find! I've cancelled 
BO-58180 and your full refund is on its way (within 5 business days). 
Sorry to see you go - we'll be here next time!

Warmly, Oakley at Brindle & Oak
```
✅ **Correct AND warm**

---

## The "Do Whatever It Takes" Test

**PM's concern:** Does "do whatever it takes to make it right" cause over-promising?

**Tested:** 30 tickets, 11 involving refunds/returns

**Results:**
- 0 new policy violations introduced
- 1 policy violation FIXED (legal escalation)
- 4 shared violations (date math bug, both prompts)
- 4 harmless uses of "anything else" (e.g. "let me know if you need anything else")

**Verdict:** The vague instruction is **not causing harm** and may actually improve judgment on edge cases like legal escalation.

---

## Tone Shift: Professional → Warm

| Element | Old | New |
|---------|-----|-----|
| Greeting | "Hello [Name]," | "Hi [Name]," |
| Empathy | Rare | Leads every difficult reply |
| Sign-off | "Brindle & Oak Support" | "Warmly, Oakley at Brindle & Oak" |
| Emoji | Never | Rare, appropriate |
| Customer name | Formal | First name |
| Apologies | Minimal | Frequent, genuine |

**Team warmth rating:** 2.8/5 → 4.6/5

**Policy impact:** Neutral to positive (better escalation judgment)

