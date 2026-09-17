# ⚡ Quick Start Guide

**You asked:** Can you sanity check the new warmth prompt and give me a go/no-go for Friday?

**Answer:** 🚫 **NO-GO** - but fixable quickly!

---

## 📍 Where to Start (5 minutes)

1. **Read this:** `EXECUTIVE_SUMMARY.txt` (1 page, has everything)
2. **See examples:** `SIDE_BY_SIDE_EXAMPLES.md` (see the warmth + the violations)
3. **Decision time:** `GO_NO_GO_DECISION.md` (3 options for you)

---

## 🔥 The Bottom Line

### What's Wrong:
- ❌ T-1013: Refunded custom wardrobe (policy violation)
- ❌ T-1016: Told customer they're on "returns-abuse watchlist" (CRITICAL leak)
- ❌ T-1026: Refunded custom bookshelf (policy violation)
- ⚠️  2+ more refunds outside 30-day window

### What's Right:
- ✅ Warmth is REAL (4.6/5 vs 2.8/5)
- ✅ 100% first name usage
- ✅ 70% empathy phrases
- ✅ Your favorite examples are genuinely better

### Why It Happened:
New prompt says "do whatever it takes - if they want a refund, make it happen" which overrides ALL policies.

---

## 🎯 Your 3 Options

### Option A: Fix & Ship Monday ⭐ RECOMMENDED
1. Use `proposed_v4_fixed.md` (keeps warmth + adds guardrails)
2. Test on 30 tickets
3. Run `python3 judge.py tickets.jsonl outputs_fixed.jsonl`
4. Must pass 30/30 to ship

**Time:** 30 min fix + 5 min test = ship Monday

---

### Option B: Hybrid Ship Friday
- New prompt for safe tickets (order status, care tips)
- Old prompt for refunds/money
- Full rollout next week

**Time:** Can ship Friday

---

### Option C: Wait for Approval Workflow
- Build human approval for refund decisions
- Ship warmth + approval together

**Time:** 2-3 weeks

---

## 🛠️ Tools We Built for You

### `judge.py` ⭐ MOST IMPORTANT
Run before EVERY prompt change:
```bash
python3 output/judge.py tickets.jsonl outputs_new.jsonl
```

- Exit 0 = pass (ship it)
- Exit 1 = fail (fix violations first)

### `proposed_v4_fixed.md`
Fixed prompt that keeps the warmth + adds safety.

### `golden_set_template.jsonl`
Template for expected answers (expand to 30 cases).

---

## 💰 Financial Impact

| Issue | Impact |
|-------|--------|
| Token cost increase | +£1-5/month (negligible) |
| Policy violations | £167k/month (CRITICAL) |

**The problem isn't the tokens - it's the wrongly-approved refunds.**

---

## ❓ FAQ

**Q: Can I ship anything Friday?**  
A: Only if you route non-refund tickets to new prompt (Option B)

**Q: Is the warmth worth the wait?**  
A: YES! The warmth is real and valuable. Just needs guardrails.

**Q: How long to fix?**  
A: 30 min prompt edit + 5 min test = Monday ship

**Q: Will judge.py catch everything?**  
A: It catches the critical policy violations we found. Expand checks as you find new edge cases.

---

## 📞 Next Action

**Lena:** Pick an option from `GO_NO_GO_DECISION.md`

**Engineering:** Add `judge.py` to CI/CD

**Future:** Run judge on every prompt change

---

Built with ❤️ using harness-first methodology.

**Remember:** The warmth is good. The policies matter. Both can win.
