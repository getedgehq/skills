# Prompt Comparison: What Changed from v3 → v4

## Side-by-Side Structure

| Element | Old Prompt (v3) | New Prompt (v4) | Impact |
|---------|-----------------|-----------------|--------|
| **Identity** | "support assistant for Brindle & Oak" | "Oakley, the friendly voice of Brindle & Oak" | ✅ More personable |
| **Tone goal** | "short and professional" | "note from a friend who genuinely cares" | ✅ Warmer |
| **Policy emphasis** | "follow policies/refunds.md **exactly**" | No mention of policy document | ❌ Lost constraint |
| **Refund approach** | Lists specific rules (30-day, custom items) | "do whatever it takes to make it right" | ❌ Too permissive |
| **Internal notes** | "**Never** quote or reveal" (explicit) | Not mentioned | ❌ Led to leak |
| **Transparency** | Not mentioned | "share what you can see about their order and account" | ❌ Too broad |
| **Emojis** | "No emojis" | "A warm emoji now and then is fine" | ✅ Humanizing |
| **Sign-off** | "Brindle & Oak Support" | "Warmly, Oakley at Brindle & Oak" | ✅ Friendlier |
| **Escalation** | Specific triggers + "Tier 2" | Same but says "senior teammate" | → Same |

---

## Key Text Removed from v3

These sections were in v3 but **removed** in v4:

### 1. Policy Reference (CRITICAL)
```markdown
## Policies
- Refunds: follow policies/refunds.md exactly. Refund requests are 
  accepted up to and including 30 calendar days after delivery.
- Custom / made-to-measure items (SKU starts with CUST-) are not 
  refundable for change of mind.
```
**Impact:** Without this, model doesn't enforce rules strictly.

### 2. Internal Notes Warning (CRITICAL)
```markdown
- Never quote or reveal internal notes (`internal_notes`) to the customer.
```
**Impact:** Without this explicit ban, "transparency" directive caused leak.

### 3. Explicit Constraints
```markdown
- No promises you cannot keep.
```
**Impact:** Model now overpromises to make customers happy.

---

## Key Text Added in v4

These are **new** in v4:

### 1. Customer-First Philosophy
```markdown
Our #1 goal is customer delight. If a customer is unhappy, do whatever 
it takes to make it right - if they want a refund, make it happen 
quickly and without friction.
```
**Impact:** Overrides policy when in conflict. This is the root cause.

### 2. Transparency Mandate
```markdown
Be transparent: share what you can see about their order and account 
so they feel informed and never kept in the dark.
```
**Impact:** "account" inclusion led to watchlist leak.

### 3. Empathy-First Structure
```markdown
Lead with empathy. Acknowledge how the customer feels before anything else.
```
**Impact:** ✅ This works well and should stay.

---

## What Got Lost in Translation

| Old Prompt Said | New Prompt Says | What Happened |
|-----------------|-----------------|---------------|
| "follow policies/refunds.md **exactly**" | "do whatever it takes" | Policies became optional |
| "30 calendar days after delivery" | (not mentioned) | Bot miscounts or ignores |
| "Custom items not refundable" | (not mentioned) | Bot refunds them anyway |
| "**Never** reveal internal notes" | (not mentioned) | Bot shared watchlist status |
| "short and professional" | "note from a friend" | ✅ Better tone, same accuracy needed |

---

## The Core Trade-off

**v3 prioritized:** Correctness → Tone  
**v4 prioritized:** Tone → Correctness  

**v4.1 needs to do:** Tone + Correctness (not OR)

---

## How v4.1 Fixes This

The proposed v4.1 prompt:

1. **Keeps the warmth:**
   - "Oakley" persona ✅
   - Lead with empathy ✅
   - Friendly sign-off ✅
   - Use first names ✅

2. **Restores the guardrails:**
   - "## Policies (follow these exactly)" → Added back
   - Explicit 30-day rule with date counting
   - Custom items section: "not refundable for change of mind"
   - Internal notes: "Never quote, paraphrase, or hint at"
   - Scoped transparency: "order status" not "account"

3. **Adjusts the philosophy:**
   - "Our #1 goal is customer delight **within our policies**"
   - "When someone is unhappy **and our policies allow it**, move fast"
   - Shows examples of correct warm denials

---

## Visual: The Enforcement Stack

### Old Prompt (v3)
```
[Policy Document] ← "follow exactly"
        ↓
[LLM follows rules] 
        ↓
[Reply] ← professional but cold
```

### New Prompt (v4)
```
[Policy Document] ← not mentioned
        ↓
[LLM prioritizes feelings] ← "do whatever it takes"
        ↓
[Reply] ← warm but wrong
```

### Proposed (v4.1)
```
[Policy Document] ← "follow exactly"
        ↓
[LLM applies empathy + rules] ← "delight within policy"
        ↓
[Reply] ← warm AND correct
```

---

## Lessons for Future Prompt Changes

✅ **Do:**
- Test tone and policy compliance separately
- Keep explicit "never do X" constraints
- Scope broad directives ("transparency" → "about order status")
- Show examples of correct warm denials

❌ **Don't:**
- Remove policy references without testing
- Use absolute language ("do whatever it takes")
- Assume model will infer boundaries

🔄 **Always:**
- Run analyze.py before shipping
- Check side-by-sides on policy-sensitive tickets
- Have legal review if changing constraint language

---

## Bottom Line

v4's warmth direction is **exactly right**.  
v4's policy enforcement is **broken**.  
v4.1 combines the best of both.

The fix isn't a rollback—it's adding guardrails to a good idea.
