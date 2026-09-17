# Support Bot v4 Analysis - Output Directory

This directory contains the complete analysis of the new "Warmth" prompt (v4) compared to the current prompt (v3).

## 📋 Files & What They're For

### **Start Here**
- **`exec_brief.md`** - One-pager for leadership (5 min read)
- **`report_card.md`** - Detailed grades and scoring (10 min read)

### **Deep Dives**
- **`recommendation.md`** - Full go/no-go analysis with rationale (15 min read)
- **`summary.md`** - Statistical summary + violations count
- **`violations_detail.md`** - Every policy violation with excerpts

### **Examples & Context**
- **`side_by_side.md`** - Key tickets compared old vs new (great for seeing the tone improvement)
- **`all_tickets_matrix.md`** - All 30 tickets at a glance with pass/fail status

### **For Next Time**
- **`checklist.md`** - Quick reference for policy rules + test cases
- **`proposed_prompt_v4.1.md`** - Fixed version ready to test

---

## 🎯 The Bottom Line

**NO-GO on Friday launch**

- ✅ Warmth/tone is genuinely better (2.8 → 4.6 rating)
- ❌ 10 critical policy violations (vs 6 in old prompt)
- 🚨 1 severe issue: internal notes leaked to customer

**Recommended action:** Fix policy issues (2-3 days), re-test, ship Tuesday/Wednesday

---

## 📊 Key Numbers

| Metric | Old | New | Status |
|--------|-----|-----|--------|
| Critical violations | 6 | 10 | 🔴 +67% |
| Warmth rating | 2.8/5 | 4.6/5 | 🟢 +64% |
| Avg empathy phrases | 0.0 | 0.9 | 🟢 +0.9 |
| Reply length (words) | 25 | 41 | 🟢 +64% |

---

## 🚨 The 3 Critical Issues

1. **Custom items refunded** (2 cases) - Made-to-measure items being refunded for change of mind, violating policy. Potential $3k+ loss in sample.

2. **30-day window violated** (7 cases) - Refunds approved 37-66 days after delivery, sometimes claiming "you're within the window" when false.

3. **Internal notes leaked** (1 case) - Customer told about "returns-abuse watchlist" status. Legal/reputational risk.

---

## 🔧 How to Use This Analysis

### If you're a PM/Decision Maker:
1. Read `exec_brief.md` first
2. Check `side_by_side.md` for examples (especially T-1007, T-1013, T-1016)
3. Review `recommendation.md` for full rationale
4. Use `proposed_prompt_v4.1.md` as starting point for fixes

### If you're implementing the fix:
1. Read `checklist.md` for policy rules
2. Use `proposed_prompt_v4.1.md` as template
3. Re-run `../analyze.py` on new outputs
4. Verify zero critical violations before shipping

### If you're reviewing future prompts:
1. Keep `checklist.md` handy
2. Run `../analyze.py` on every change
3. Look for these patterns in `all_tickets_matrix.md`:
   - ❌ next to custom items
   - ❌ next to 30d+ deliveries
   - 🚨 anywhere (internal leaks)

---

## 📈 What We Learned

**The warmth concept works.** Customers will respond better to:
- Leading with empathy ("I'm so sorry", "I understand")
- Using their first name
- Longer, more contextual replies
- The "Oakley" persona

**But "customer delight" can't override policy.** The directive "do whatever it takes to make it right" caused the model to:
- Approve refunds it shouldn't
- Share information it shouldn't
- Prioritize feelings over business rules

**The fix is straightforward:** Add explicit policy constraints back while keeping the warm tone. See v4.1 proposal.

---

## 🔄 For the Next Prompt Review

We've created `analyze.py` in the parent directory that:
- Checks 30-day windows automatically
- Flags custom refunds
- Detects internal note leaks
- Generates all these reports

**Make it part of your process:**
```bash
# After generating outputs from old and new prompts
python3 analyze.py

# Check output/ for go/no-go recommendation
cat output/summary.md
```

Run time: ~30 seconds  
Catches issues we caught manually: ✅  

---

## 📞 Questions?

- **Policy questions:** See `checklist.md` or `violations_detail.md`
- **Why specific tickets failed:** See `side_by_side.md`
- **What to fix:** See `proposed_prompt_v4.1.md`
- **Should we ship:** See `exec_brief.md` (spoiler: not yet)

---

**Analysis Date:** September 15, 2026  
**Prompt Versions:** v3 (old) → v4 "Warmth" (new) → v4.1 (proposed fix)  
**Verdict:** Fix and ship next week, don't ship Friday
