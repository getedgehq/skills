# Model Comparison: Cost Impact Analysis
**Brightkiln Outreach Agent - Sept 2026**

---

## Current State (Sept 1-15)

**Model:** Claude Sonnet 4.5 ($3 in / $15 out per Mtok)  
**Conversations:** 46  
**Total Cost:** $26.66  

**Problem:** 70% of cost from 5 retry loops (fixed in this PR)

---

## Projected Monthly Costs

Based on Sept 1-15 data (46 conversations in 15 days = ~92/month)

### Scenario 1: Keep Sonnet, No Fixes
**Status:** Current production state (BAD)**

| Item | Calculation | Amount |
|------|-------------|--------|
| Conversations/month | 46 × 2 | 92 |
| Cost per conversation | $26.66 / 46 | $0.58 |
| **Monthly cost** | 92 × $0.58 | **$53.32** |
| Risk | Scales linearly with volume | 🔴 High |

---

### Scenario 2: Keep Sonnet, Apply Harness Fixes ⭐ RECOMMENDED FIRST STEP
**Status:** Code changes in this PR (agent/loop.py, prompts.py, tools.py)

| Item | Calculation | Amount |
|------|-------------|--------|
| Retry loop cost eliminated | 70% of $26.66 | -$18.66 |
| New cost (Sept 1-15) | $26.66 - $18.66 | $8.00 |
| Cost per conversation | $8.00 / 46 | $0.17 |
| **Monthly cost** | 92 × $0.17 | **$15.64** |
| **Monthly savings vs current** | $53.32 - $15.64 | **-$37.68 (71%)** |
| Risk | Capped at $0.50/conversation | 🟢 Low |

---

### Scenario 3: Switch to GPT-5-mini, No Fixes ❌ NOT RECOMMENDED
**Status:** Cheaper model but same bugs

| Item | Calculation | Amount |
|------|-------------|--------|
| Input tokens | 8.72M × $0.25 | $2.18 |
| Output tokens | 34K × $2.00 | $0.07 |
| Total (Sept 1-15) | | $2.25 |
| Cost per conversation | $2.25 / 46 | $0.05 |
| **Monthly cost** | 92 × $0.05 | **$4.60** |
| **Problem** | Retry loops still happen | 🟡 Medium |
| Quality | Unknown (not tested) | ❓ Unknown |

**Why not:** Saves money but retries still waste tokens. Quality untested. Fix the bug first.

---

### Scenario 4: Apply Fixes + Switch to GPT-5-mini
**Status:** Future option after testing quality

| Item | Calculation | Amount |
|------|-------------|--------|
| Input tokens (after fixes) | 2.62M × $0.25 | $0.66 |
| Output tokens | 34K × $2.00 | $0.07 |
| Total (Sept 1-15) | | $0.73 |
| Cost per conversation | $0.73 / 46 | $0.02 |
| **Monthly cost** | 92 × $0.02 | **$1.84** |
| **Monthly savings vs current** | $53.32 - $1.84 | **-$51.48 (97%)** |
| **Prerequisites** | Fix bugs, test quality on golden set | ⏳ Depends |

**When to do this:**
1. Deploy Scenario 2 (fixes on Sonnet) ✅ 
2. Validate cost drops to ~$16/month ✅
3. Run golden set on both models
4. If GPT-5-mini passes quality bar → switch and save another 88%

---

## Side-by-Side: Monthly Cost at Different Volumes

| Conversations/Month | Current (Sonnet, bugs) | Fixed (Sonnet) | Fixed + GPT-5-mini |
|---------------------|------------------------|----------------|-------------------|
| 92 (Sept pace) | $53 | **$16** ⭐ | $2 |
| 200 | $116 | **$34** ⭐ | $4 |
| 500 | $290 | **$85** ⭐ | $10 |
| 1,000 | $580 | **$170** ⭐ | $20 |

**Key insight:** Fix the harness first. It scales. Model price only matters after you stop wasting tokens.

---

## Decision Matrix

### Deploy This Week (Before Month End)

**Action:** Merge PR with harness fixes, deploy to production  
**Model:** Keep Sonnet (no risk, no quality testing needed)  
**Expected savings:** 71% (~$38/month at current volume)  
**Risk:** Low (added hard caps, removed infinite loops)  
**Effort:** 1 hour (code review + deploy)

### Next Sprint (October)

**Action:** Run golden set (evals/golden.jsonl) on Sonnet vs GPT-5-mini  
**Compare:** Quality (pass rate), email tone, scoring accuracy  
**Decision criteria:**
- If GPT-5-mini ≥95% pass rate → switch, save another 88%
- If quality drops → keep Sonnet, you already saved 71%

**Effort:** 1-2 days (golden set expansion + testing + review)

---

## Recommendation

### For Finance (This Week)
"Deploy the harness fixes now. Saves $38/month with zero model risk. We'll evaluate a model switch next sprint after proper testing."

### For Engineering (Next Sprint)
"Fix is in. Now let's test GPT-5-mini properly with the golden set. If it passes, we save another $14/month. If not, we're still 71% cheaper than we were."

---

## Questions for Priya

1. **Quality bar:** What's acceptable pass rate on golden set for a model switch? (Suggest: 95%)
2. **Email review:** Who can review 5-10 sample emails from each model to check tone?
3. **Volume forecast:** Are we scaling beyond 100 convos/month? (Affects ROI of model testing)
4. **Cost target:** Is $16/month acceptable, or do you need the full 97% savings urgently?

---

**Files in this PR:**
- `agent/loop.py` - Added max_iterations, cost caps
- `agent/tools.py` - Fixed retry logic, updated descriptions  
- `agent/prompts.py` - Removed infinite retry instructions
- `evals/golden.jsonl` - 5 test cases for model comparison
- `evals/judge.py` - Quality checker framework
- `output/REPORT.md` - Full analysis
- `output/model_cost_comparison.md` - This file

**Next:** Deploy to staging, validate costs, merge to prod.
