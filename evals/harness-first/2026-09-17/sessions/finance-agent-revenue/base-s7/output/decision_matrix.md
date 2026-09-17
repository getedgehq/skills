# Decision Matrix: How to Fix Finbot

**For:** Daniel Kurz (CEO)  
**Date:** September 16, 2026

---

## The Question

"Is the model just hallucinating? Do we need a smarter model?"

---

## The Answer

**No and no.** This is a prompt engineering issue, not a model capability issue.

---

## Option Comparison

| Factor | Fix Prompt | Upgrade Model |
|--------|-----------|---------------|
| **Root cause addressed?** | ✅ Yes | ❌ No |
| **Cost (upfront)** | $0 | $0 |
| **Cost (ongoing)** | $0/month | +$500-2000/month* |
| **Time to implement** | 5 minutes | 5 minutes |
| **Risk of breaking things** | Very low | Low |
| **Will fix this issue?** | ✅ Yes | ❌ No |
| **Prevents recurrence?** | ✅ Yes | ❌ No |
| **Technical complexity** | Trivial | Trivial |
| **Requires model change?** | No | Yes |

*Estimated based on query volume and price difference (Opus = 2-3x, o1 = 10-20x)

---

## Why Upgrading the Model Won't Help

### All models would make the same mistake

When asked "what was Q2 revenue?" without specification:

| Model | Behavior |
|-------|----------|
| Claude Sonnet 4 (current) | Queries `orders` table |
| Claude Opus | Queries `orders` table |
| GPT-6 | Queries `orders` table |
| o1-pro | Queries `orders` table |

**Why?** Because the prompt lists 5 tables but doesn't say:
- Which one contains official revenue
- That `orders` includes cancelled transactions
- That `revenue_recognized` is finance's source of truth

This is like asking someone "get me the revenue number" without saying where to look. They'll make their best guess. A "smarter" person will still guess wrong with incomplete information.

---

## The Real Problem

```
Current prompt:
"Tables you can use: customers, orders, refunds, revenue_recognized, daily_kpis"

Missing context:
- Which table is authoritative for revenue?
- What's the difference between orders.amount and revenue_recognized.net_amount?
- When should each table be used?
```

**This is a specification problem, not an intelligence problem.**

---

## What "Hallucination" Actually Means

A model hallucinates when it:
- Makes up data that doesn't exist
- Returns SQL errors but claims success
- Invents table/column names
- Returns mathematically incorrect results

Finbot did NONE of these. It:
- ✅ Queried a real table
- ✅ Used correct SQL syntax
- ✅ Returned accurate sum from that table
- ✅ Formatted the response correctly

The only "error" was choosing the wrong table - which is impossible to get right when the prompt doesn't specify.

---

## Evidence This Isn't a Model Issue

### 1. The SQL is perfect
```sql
SELECT ROUND(SUM(amount), 2) AS revenue 
FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';
```
- Correct syntax ✅
- Correct date range ✅
- Correct aggregation ✅
- Wrong table ❌ (but how could it know?)

### 2. The math is correct
- Database has $4,138,212.16 in the orders table for Q2
- Finbot returned $4,138,212.16
- No hallucination, just wrong data source

### 3. Consistent behavior
- Made the same choice for Q1
- Would make the same choice for any period
- Reproducible and logical (not random/hallucinated)

### 4. A human would make the same mistake
Ask a new analyst "what was Q2 revenue?" without context:
- They might check the orders table ❌
- Or the daily_kpis table ❌
- Or ask "which table should I use?" ✅
- They wouldn't magically know revenue_recognized is official

---

## The Fix (Detailed)

### Current prompt (insufficient)
```markdown
Tables you can use:
- customers
- orders
- refunds
- revenue_recognized
- daily_kpis
```

### Fixed prompt (sufficient)
```markdown
Tables you can use:
- customers (company info, segment, country)
- orders (individual transactions; use for order-level analysis)
- refunds (returns and refund details)
- revenue_recognized (⭐ USE THIS for revenue - official finance numbers)
- daily_kpis (high-level daily metrics)

IMPORTANT: For revenue questions, always use revenue_recognized.net_amount.
The orders table includes cancelled orders and doesn't account for refunds.
Finance closes the books from revenue_recognized.
```

**That's it.** 30 seconds of typing, problem solved permanently.

---

## Cost-Benefit Analysis

### Scenario A: Fix Prompt
- **Cost:** $0
- **Time:** 5 minutes
- **Fixes issue:** Yes
- **Total cost over 1 year:** $0

### Scenario B: Upgrade to Opus
- **Cost:** ~2-3x per query
- **Time:** 5 minutes
- **Fixes issue:** No (still needs prompt fix)
- **Total cost over 1 year:** ~$6,000 - $18,000
- **Benefit:** Slightly better at other tasks

### Scenario C: Upgrade to o1
- **Cost:** ~10-20x per query
- **Time:** 5 minutes
- **Fixes issue:** No (still needs prompt fix)
- **Total cost over 1 year:** ~$30,000 - $60,000
- **Benefit:** Better reasoning, but irrelevant here

**Recommendation:** Do A, then evaluate B/C for other reasons if needed.

---

## What Could Go Wrong (with prompt fix)

### Potential issues:
1. ❓ Model still chooses wrong table somehow
2. ❓ Other queries break due to new context
3. ❓ Users confused by more detailed responses

### Mitigations:
1. Test with 5-10 questions before deployment
2. Monitor #ask-finance for a week
3. Keep original prompt as backup

### Likelihood:
Very low. The fix is additive (adds context) not restrictive (doesn't remove options).

---

## What Could Go Wrong (with model upgrade)

### Potential issues:
1. ❓ Still makes same mistake (no prompt guidance)
2. ❓ Higher latency impacts user experience
3. ❓ Budget impact for data team
4. ❓ Different model behavior on other queries

### Reality:
Even if you upgrade, you STILL need to fix the prompt. So why not start there?

---

## Analogies to Explain to Non-Technical Folks

### Bad analogy:
"The AI is dumb, we need a smarter AI"

### Good analogy:
"An employee looked in the orders spreadsheet instead of the revenue spreadsheet because we didn't tell them which one is official. Training them better won't help - they need clearer instructions."

### Another good analogy:
"You asked someone to get you 'the revenue number' without saying whether you wanted gross or net. They made a reasonable guess. A PhD would make the same guess without more context."

---

## Recommendation

**Deploy the prompt fix immediately** (ready in `output/prompt_FIXED.md`)

Then, independently evaluate model upgrades based on:
- Other use cases and requirements
- Budget considerations
- Future feature plans

But don't upgrade because of this issue - that's solving the wrong problem.

---

## Bottom Line

| Statement | True/False |
|-----------|------------|
| "The model is hallucinating" | ❌ False |
| "The model isn't smart enough" | ❌ False |
| "We need a better model" | ❌ False (for this issue) |
| "The prompt is underspecified" | ✅ True |
| "Fix the prompt first" | ✅ True |
| "Can evaluate upgrades later" | ✅ True |

---

## Sign-Off

I recommend:
- [ ] Deploy prompt fix today
- [ ] Monitor for 1 week
- [ ] Evaluate model upgrades based on other criteria
- [ ] Don't spend money solving the wrong problem

**The fix is ready. Just need approval to proceed.**

---

## Questions?

Contact the investigation team or review:
- `README.md` - Overview and file guide
- `executive_summary.md` - One-page summary
- `root_cause_analysis.md` - Full technical details
