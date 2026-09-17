# 🚨 CRITICAL: Board Deck Contains TWO Wrong Numbers

**URGENT - Review Before Board Meeting**

---

## The Problem Is Bigger Than Q2

Both Q1 and Q2 revenue numbers from finbot are incorrect by ~$500K-$850K each.

| Quarter | Finbot Reported | Actual (Finance) | Difference | Status |
|---------|-----------------|------------------|------------|---------|
| **Q1 2026** | **$4,141,985.86** (~$4.1M) | **$3,285,493.84** (~$3.3M) | **-$856,492** ⚠️ | **WRONG** |
| **Q2 2026** | **$4,138,212.16** (~$4.1M) | **$3,638,335.79** (~$3.6M) | **-$499,876** ⚠️ | **WRONG** |
| **H1 2026** | **~$8.3M** | **$6,923,829.63** (~$6.9M) | **-$1.4M** ⚠️ | **WRONG** |

---

## Impact Assessment

### If the board deck shows:
- ✅ Q1 = ~$3.3M → Correct (unlikely, since Priya used finbot)
- ❌ Q1 = ~$4.1M → Wrong by $856K
- ❌ Q2 = ~$4.1M → Wrong by $500K  
- ❌ H1 = ~$8.3M → Wrong by $1.4M

### Potential consequences:
1. **Credibility damage** - Board sees 25% revenue overstatement
2. **Strategic implications** - QoQ growth narrative is wrong
3. **Financial reporting** - May conflict with actual financials
4. **Trust in data team** - Undermines confidence in analytics

---

## Correct Numbers (Use These)

### Q1 2026 Revenue by Month
| Month | Net Revenue |
|-------|-------------|
| January | $1,029,676.69 |
| February | $1,007,956.74 |
| March | $1,247,860.41 |
| **Q1 Total** | **$3,285,493.84** |

### Q2 2026 Revenue by Month
| Month | Net Revenue |
|-------|-------------|
| April | $1,237,516.63 |
| May | $1,209,658.31 |
| June | $1,191,160.85 |
| **Q2 Total** | **$3,638,335.79** |

### Half-Year Summary
| Period | Net Revenue | QoQ Growth |
|--------|-------------|------------|
| Q1 2026 | $3,285,493.84 | - |
| Q2 2026 | $3,638,335.79 | **+10.7%** ✅ |
| **H1 2026** | **$6,923,829.63** | - |

---

## The Real Story

**Finbot said:** Revenue was flat Q1 → Q2 (-0.1%)  
**Reality:** Revenue grew 10.7% Q1 → Q2 

This completely changes the narrative!

---

## Immediate Actions Required

### Priority 1: Board Deck Correction (ASAP)
- [ ] **Priya** - Check current board deck numbers
- [ ] **Marta** - Provide official Q1 and Q2 closes
- [ ] **Priya** - Update deck with correct numbers
- [ ] **Daniel** - Review before distribution

### Priority 2: Verify Impact
- [ ] Check if any other materials use finbot numbers
- [ ] Review investor updates, exec dashboards
- [ ] Check if numbers were shared in any email/Slack

### Priority 3: Fix Finbot (Today)
- [ ] **Jonas** - Deploy prompt fix immediately
- [ ] **Jonas** - Test with Q1 and Q2 questions
- [ ] **Jonas** - Post warning in #ask-finance about past numbers

---

## Communication Plan

### For the Board (if needed)
> "We identified a data processing error in our preliminary board materials. The numbers 
> have been corrected to reflect our official financial close. Q2 revenue was $3.6M, 
> representing 10.7% QoQ growth from Q1's $3.3M."

### For Internal Team
> "Finbot's revenue numbers were incorrect due to querying the wrong data table. 
> Q1 was ~$3.3M (not $4.1M) and Q2 was ~$3.6M (not $4.1M). We've fixed the bot 
> and are verifying all materials. Please check with Finance for any recent revenue 
> numbers you may have used."

---

## Why Both Quarters Are Wrong

Same root cause for both quarters:

**Finbot's query:** Sum ALL orders (including cancelled and refunded)
```sql
SELECT SUM(amount) FROM orders WHERE created_at BETWEEN ...
```

**Should be:** Sum net revenue (official finance close)
```sql
SELECT SUM(net_amount) FROM revenue_recognized WHERE period IN (...)
```

The error is consistent but the impact varies:
- Q1 had MORE refunds/cancellations → $856K difference
- Q2 had FEWER refunds/cancellations → $500K difference

---

## Root Cause (Same as Before)

The system prompt doesn't specify:
- Which table contains official revenue
- That `orders` includes cancelled/refunded transactions
- That `revenue_recognized` is finance's source of truth

**Fix:** Update prompt (5 minutes, already prepared in `output/prompt_FIXED.md`)

---

## Lessons Learned

1. **Always verify bot answers with source of truth** for board materials
2. **LLM outputs need validation** even when they look reasonable
3. **Prompts must encode business rules** explicitly
4. **Flat QoQ growth was the red flag** - should have triggered review

---

## Next Steps

1. **RIGHT NOW:** Check what's in the board deck
2. **Next hour:** Correct deck if needed, get Marta to verify
3. **Today:** Deploy prompt fix, notify team
4. **This week:** Review all recent materials for finbot-sourced numbers

---

## Contact for Questions

- **Finance numbers:** Marta Oyelaran (VP Finance)
- **Finbot fix:** Jonas Feld (Data team owner)
- **Board deck:** Priya Raman (Strategy)
- **Overall coordination:** Daniel Kurz (CEO)

---

## Attached Files

- `executive_summary.md` - One-page brief for Daniel
- `root_cause_analysis.md` - Full technical investigation
- `data_forensics.md` - Detailed data comparison
- `sql_comparison.md` - Correct queries to use
- `action_plan.md` - Implementation steps
- `prompt_FIXED.md` - Corrected prompt file

**Everything is ready to deploy. Just need approval to proceed.**
