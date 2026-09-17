# FinBot Q2 Revenue Investigation - Output Files

**Investigation Date:** September 16, 2026  
**Issue:** FinBot reported Q2 revenue as $4.1M, Finance close is $3.6M  
**Root Cause:** Bot queried wrong table (orders vs revenue_recognized)  
**Solution:** Update system prompt (not model upgrade)

---

## 📁 Files in This Directory

### Start Here 👇

**1. TLDR.md**  
One-page summary for Daniel. Read this first.
- What happened
- Why it happened  
- Do we need a smarter model? (No)
- The fix (5 minutes)
- What to tell the board

### For Deployment 🚀

**2. fixed_prompt.md**  
Drop-in replacement for `prompt.md`. This is the fix.
- Explicitly tells the bot to use revenue_recognized for revenue questions
- Zero code changes required
- Ready to deploy immediately

**3. test_queries.py**  
Verification script to test the fix works.
- Shows expected correct answers
- Compares old vs new table results
- Run after deploying to verify

### Deep Analysis 📊

**4. investigation_report.md**  
Complete technical investigation (8+ pages).
- Full root cause analysis
- Database schema exploration
- Query comparisons
- Why model upgrade won't help
- Long-term recommendations

**5. data_appendix.md**  
All the numbers in one place.
- Official Q2 revenue breakdown
- Monthly trends
- Refund analysis
- SQL query reference
- Board talking points

### Additional Context 📝

**6. executive_brief.md**  
Simplified version of the investigation for exec team.
- Less technical than investigation_report.md
- Focuses on business impact
- Clear recommendations

**7. before_after_comparison.md**  
Shows exactly what changes with the prompt fix.
- Side-by-side comparison
- Same question, different results
- Why the fix works

---

## ⚡ Quick Start (for Daniel)

### 1. Read This (2 minutes)
```bash
cat TLDR.md
```

### 2. Deploy the Fix (5 minutes)
```bash
# Backup current prompt
cp prompt.md prompt.md.backup

# Deploy fix
cp output/fixed_prompt.md prompt.md

# Verify it works
python agent.py "what was our Q2 2026 revenue?"
# Should return: ~$3.6M (not $4.1M)
```

### 3. Update Board Deck (1 minute)
Replace: "Q2 Revenue: $4.1M"  
With: "Q2 Revenue: $3.6M"

Done. ✅

---

## 🎯 Key Findings

| Question | Answer |
|----------|--------|
| Is the bot hallucinating? | ❌ No - it's querying real data |
| Is the model too dumb? | ❌ No - current model is fine |
| Do we need Opus/GPT-6? | ❌ No - would be wasting money |
| What's the real problem? | ✅ Vague prompt, bot picked wrong table |
| How do we fix it? | ✅ Update prompt (5 min, $0) |
| What's the correct Q2 revenue? | ✅ $3,638,335.79 ($3.6M) |

---

## 📊 The Numbers

| Metric | FinBot Said | Finance Says | Error |
|--------|-------------|--------------|-------|
| Q2 Revenue | $4,138,212 | $3,638,336 | +$500K (+13.7%) |
| Table Used | orders | revenue_recognized | - |
| Includes cancelled | Yes ❌ | No ✅ | - |
| Nets out refunds | No ❌ | Yes ✅ | - |
| Board-ready | No ❌ | Yes ✅ | - |

---

## 🔧 What Changed

**Prompt Changes:**
- Added explicit guidance: "For revenue, use revenue_recognized.net_amount"
- Explained what each table is for
- Provided examples of correct queries

**Code Changes:**
- None (0 lines changed)

**Model Changes:**
- None (still Claude Sonnet 4.5)

**Cost Changes:**
- $0

**Deployment Time:**
- 5 minutes

---

## ✅ Verification Steps

After deploying fixed_prompt.md, test these:

```bash
# Should return ~$3.6M (was $4.1M before)
python agent.py "what was our Q2 2026 revenue?"

# Should return ~$3.3M
python agent.py "what was our Q1 2026 revenue?"

# Should return ~$1.2M
python agent.py "what was august 2026 revenue?"
```

Run the test suite:
```bash
python output/test_queries.py
```

---

## 📞 Questions?

- **High-level explanation:** Read `TLDR.md` or `executive_brief.md`
- **Technical details:** Read `investigation_report.md`
- **All the data:** Read `data_appendix.md`
- **Before/after comparison:** Read `before_after_comparison.md`

---

## 🎓 Lessons Learned

1. **LLM clarity:** Models need explicit guidance about domain-specific tables
2. **Not all errors are hallucinations:** Check data sources first
3. **Prompt engineering > Model upgrades:** Often the cheapest fix
4. **Testing is critical:** Need automated tests for finance queries
5. **Documentation matters:** Schema docs would have prevented this

---

## 📌 Action Items

### Immediate (Today)
- [ ] Deploy fixed_prompt.md
- [ ] Verify with test queries
- [ ] Correct board deck: Q2 = $3.6M

### This Week  
- [ ] Review other board deck numbers from FinBot
- [ ] Add integration tests for key queries
- [ ] Document revenue_recognized as source of truth

### Next Sprint
- [ ] Add query validation layer
- [ ] Create finance metrics glossary
- [ ] Add schema documentation to prompt

---

**Bottom line:** Prompt fix, not model upgrade. Deploy today, verify tonight, board deck is ready.
