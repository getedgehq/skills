# START HERE - FinBot Investigation Results

**Investigation Date:** 2026-09-15  
**Issue:** Board deck showed Q2 revenue as $4.1M, finance says $3.6M  
**Status:** ✅ Root cause found, fixes ready  
**Verdict:** NOT a model problem - harness failure

---

## 🎯 For Daniel (CEO) - 3 Minute Read

**Read this first:** [`EXECUTIVE_SUMMARY.md`](EXECUTIVE_SUMMARY.md)

**Bottom line:** 
- ✅ The model works fine - don't switch
- ❌ The bot used the wrong database table (orders vs revenue_recognized)
- 🔧 Fixes are ready to deploy in this folder
- ⚠️ This would happen with any model without these fixes

**Quick demo:**
```bash
python verify.py
# Shows the exact SQL problem and solution with real numbers
```

---

## 📊 For Quick Understanding

**Visual explanation:** [`SIDE_BY_SIDE.md`](SIDE_BY_SIDE.md)
- Shows the wrong SQL vs correct SQL
- Explains the $500K difference
- Why model swap won't help

**Key numbers:**
- FinBot said: $4,138,212 (from `orders` table - includes cancelled/refunded)
- Finance says: $3,638,336 (from `revenue_recognized` - net revenue)
- Difference: $499,876 (the error that went to the board)

---

## 📋 For Implementation

**Deployment guide:** [`IMPLEMENTATION.md`](IMPLEMENTATION.md)
- Step-by-step checklist
- What to do today vs this week vs this month
- Testing instructions

**Files to deploy:**
1. [`prompt_fixed.md`](prompt_fixed.md) → replace current `prompt.md`
2. [`agent_fixed.py`](agent_fixed.py) → replace current `agent.py`

**Test after deployment:**
```bash
python agent.py "what was Q2 2026 revenue?"
# Should return: $3,638,335.79 or "$3.6M"
# NOT: $4,138,212.16 or "$4.1M"
```

---

## 📚 For Technical Details

**Full analysis:** [`ANALYSIS.md`](ANALYSIS.md)
- Complete root cause investigation
- Evidence and verification
- Harness scorecard (golden set, judge, cost caps, data layer, safety, tracing)
- Cost impact analysis
- Prioritized recommendations

**Supporting artifacts:**
- [`data_dictionary.md`](data_dictionary.md) - Defines what "revenue" means
- [`golden.jsonl`](golden.jsonl) - 4 test cases including the Q2 incident
- [`judge.py`](judge.py) - Automated test runner
- [`verify.py`](verify.py) - Demonstrates the problem with real data

---

## 🚀 Quick Start (30 Minutes to Fix)

### Step 1: Deploy the fixes (5 min)
```bash
cd /home/user/work
cp output/prompt_fixed.md prompt.md
cp output/agent_fixed.py agent.py
```

### Step 2: Test manually (2 min)
```bash
python agent.py "what was Q2 2026 revenue?"
# Verify it says $3.6M, not $4.1M
```

### Step 3: Verify with demonstration (3 min)
```bash
python output/verify.py
# Shows side-by-side SQL comparison with real numbers
```

### Step 4: Update the board materials (20 min)
- Find all instances of "$4.1M" Q2 revenue
- Replace with "$3.6M" 
- Add note: "Corrected from preliminary figure"

---

## 📈 What Changed

### Safety Improvements
| Feature | Before | After |
|---------|--------|-------|
| Iteration limit | ❌ None (infinite loop possible) | ✅ Max 5 iterations |
| Database access | ⚠️ Read/write | ✅ Read-only |
| Cost cap | ❌ Unbounded | ✅ Capped per query |
| Query logging | ❌ None | ✅ Logged to stderr |

### Quality Improvements  
| Feature | Before | After |
|---------|--------|-------|
| Data dictionary | ❌ None | ✅ Created |
| Revenue definition | ❌ Ambiguous | ✅ Explicit in prompt |
| Test coverage | ❌ 0 tests | ✅ 4 test cases |
| Regression checking | ❌ Manual only | ✅ Automated judge |

---

## ❓ FAQ

### "Is the model hallucinating?"
**No.** The model returned exactly what the database said. It just queried the wrong table because nothing told it which table represents "revenue."

### "Should we switch to GPT-6 or Opus?"
**Not yet.** Fix the harness first. Then if you want to compare models, run the golden set on each and compare quality/cost with data, not vibes.

### "Why did this happen?"
**No harness.** The bot had:
- No data dictionary defining "revenue"
- No test cases to catch errors  
- No safety limits (cost, iterations, permissions)
- No audit trail

### "How much would model switching cost?"
- Current (Sonnet 4.5): ~$0.15 per question
- GPT-6: ~$0.30 per question (2x cost)
- Opus: ~$0.45 per question (3x cost)

**But all three would make the same error without the data dictionary.**

### "What if we had switched models first?"
You'd have:
- ✅ A more expensive bot
- ❌ The same $500K error
- ❌ Still no tests to catch it
- ❌ Still no safety limits

**Fix the harness, then evaluate models.**

---

## 📞 Next Steps

### Immediate
- [ ] Read [`EXECUTIVE_SUMMARY.md`](EXECUTIVE_SUMMARY.md) (3 min)
- [ ] Review [`verify.py`](verify.py) output (2 min)
- [ ] Decision: approve deployment of fixes?

### Today (if approved)
- [ ] Deploy [`prompt_fixed.md`](prompt_fixed.md) and [`agent_fixed.py`](agent_fixed.py)
- [ ] Test manually: "Q2 2026 revenue" → should get $3.6M
- [ ] Notify finance/strategy teams of correction

### This Week
- [ ] Expand test coverage (20+ cases)
- [ ] Add full tracing/logging
- [ ] CI: run tests on every code change

### This Month
- [ ] Template this approach for all internal agents
- [ ] Full security audit
- [ ] Then (if desired) evaluate other models with golden set

---

## 📁 File Guide

| File | Purpose | Read Time |
|------|---------|-----------|
| **`EXECUTIVE_SUMMARY.md`** | CEO-level overview | 3 min |
| **`SIDE_BY_SIDE.md`** | Visual SQL comparison | 5 min |
| **`IMPLEMENTATION.md`** | Deployment checklist | 10 min |
| **`ANALYSIS.md`** | Full technical report | 20 min |
| **`README.md`** | Directory guide | 5 min |
| `verify.py` | Run to see the problem | 1 min |
| `prompt_fixed.md` | Ready to deploy | - |
| `agent_fixed.py` | Ready to deploy | - |
| `data_dictionary.md` | Metric definitions | - |
| `golden.jsonl` | Test cases | - |
| `judge.py` | Test runner | - |

---

## ✅ Success Criteria

You'll know the investigation succeeded when:

1. ✅ Daniel understands: not a model problem, it's a harness problem
2. ✅ Team deploys: prompt + agent fixes  
3. ✅ Verification passes: bot returns $3.6M for Q2
4. ✅ Board materials updated: correct revenue figure
5. ✅ Future prevention: test cases catch similar errors
6. ✅ Cost savings: iteration caps prevent runaway spending

---

**All deliverables ready for Daniel's 9 AM meeting tomorrow.**

Questions? See the detailed analysis in [`ANALYSIS.md`](ANALYSIS.md) or run:
```bash
python output/verify.py  # 1 minute, shows the exact problem
```
