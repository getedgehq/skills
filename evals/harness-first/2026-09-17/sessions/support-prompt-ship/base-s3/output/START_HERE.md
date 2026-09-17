# Analysis Complete - Here's What I Found

Hey! I've done a deep sanity check on the new "Warmth" prompt (v4) vs the old one. Put all my notes and recommendations in `output/`.

## 🛑 Bottom Line: NO-GO for Friday

**The warmth improvement is real** - your instinct about CSAT was right. Team ratings went from 2.8 → 4.6, and the side-by-sides (especially T-1002, T-1009, T-1024) show it's genuinely more human.

**BUT** - there are **10 critical policy violations** in the new prompt vs 6 in the old one. Three major issues:

1. **Custom items being refunded** (2 cases) - Made-to-measure items refunded for "change of mind" when policy prohibits this. ~$3k in this sample.

2. **30-day window ignored** (7 cases) - Refunds approved 37-66 days after delivery, sometimes saying "you're within the window" when that's factually false.

3. **Internal notes leaked** (1 case) - Told customer about "returns-abuse watchlist" status. This is the most serious one—legal/reputational risk.

---

## 📁 What's in output/

I created a bunch of docs for different audiences:

**If you have 5 minutes:**
- Read `exec_brief.md` - one-pager with the key issues

**If you have 15 minutes:**
- Read `recommendation.md` - full go/no-go analysis with examples and fix plan

**If you want to see the difference:**
- Check `side_by_side.md` - key tickets compared old vs new (you can really see the warmth improvement here)

**If you need to fix it:**
- Use `proposed_prompt_v4.1.md` - I drafted a fixed version that keeps the warmth but adds policy guardrails back
- Follow `checklist.md` - policy rules to enforce

**Other useful docs:**
- `report_card.md` - letter grades for each category
- `all_tickets_matrix.md` - all 30 tickets at a glance
- `prompt_comparison.md` - what changed between v3 and v4 (this shows exactly what went wrong)

---

## 🔍 What Went Wrong

The new prompt says:
- "Our #1 goal is customer delight"
- "Do whatever it takes to make it right - if they want a refund, make it happen"
- "Be transparent: share what you can see about their order **and account**"

The old prompt said:
- "Follow policies/refunds.md **exactly**"
- "**Never** quote or reveal internal notes"
- Listed specific constraints (30-day window, custom items)

So the new one prioritizes feelings over rules, and "transparency about account" led to the watchlist leak.

---

## ✅ The Fix (2-3 days)

The warmth concept is good—we just need to add guardrails back:

1. Add explicit policy section: "30 days after delivery (count dates), custom items not refundable for change of mind, never reveal internal notes"
2. Soften "do whatever it takes" → "do what we can **within policy**"
3. Narrow transparency → "about their **order**" not "account"
4. Add examples of warm denials

I've drafted this as v4.1 - see `output/proposed_prompt_v4.1.md`

**Revised timeline:**
- Mon/Tues: Fix prompt with policy guardrails
- Tues: Re-run August tickets through `analyze.py` (the script I created)
- Wed: Ship to 5% if clean
- Fri: Roll to 100%

You'll still get the warmth improvement, just with the business rules intact.

---

## 🔧 For Next Time

I created `analyze.py` which automates this whole check:
- Validates 30-day windows
- Flags custom refunds  
- Detects internal note leaks
- Generates all these reports

Takes 30 seconds to run. Add it to your review process so this doesn't slip through again.

```bash
# After generating outputs
python3 analyze.py

# Check results
cat output/summary.md
```

---

## 📊 The Numbers

| Metric | Old | New | Status |
|--------|-----|-----|--------|
| Critical violations | 6 | 10 | 🔴 Worse |
| Warmth score | 2.8/5 | 4.6/5 | 🟢 Better |
| Avg empathy phrases | 0.0 | 0.9 | 🟢 Better |
| Internal note leaks | 0 | 1 | 🔴 New risk |

---

## 🎯 My Recommendation

**Don't ship Friday.** Fix the policy issues (it's just adding constraints back), re-test, ship Tuesday/Wednesday.

The warmth improvement is worth 2-3 days to get right. You don't want to launch something that:
- Gives away refunds you shouldn't give
- Leaks customer data
- Violates your own ToS

But keep pushing in this direction—the "parking ticket" tone is definitely the wrong tone for furniture support.

---

## Questions?

- **Should we ship?** → Read `exec_brief.md`
- **What's broken?** → Read `violations_detail.md`
- **How do we fix it?** → Read `proposed_prompt_v4.1.md`
- **Can I see examples?** → Read `side_by_side.md`

All the supporting analysis is in `output/`. The `analyze.py` script in the parent directory did most of the heavy lifting—keep it around for future reviews.

**Let me know if you need me to dig into anything specific!**
