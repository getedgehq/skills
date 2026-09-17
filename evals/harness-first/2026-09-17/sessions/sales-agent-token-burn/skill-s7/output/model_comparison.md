# Model Comparison for Outreach Agent

## Current Situation (Sept 1-15)

**Model:** claude-sonnet-4-5
**Cost:** $26.66 for 46 conversations (leads)
**Problems:** Retry loops, not model choice

---

## After Applying Fixes (Same Model)

### Projected Performance: Sonnet with Fixes

**Assumptions:**
- No more validation error loops (prevents 4 conversations × $4.50 each)
- crm_get_account called 1x per lead instead of 4.1x average
- Max iterations prevents runaway costs
- Normal workflow: 3-4 turns per conversation

**Estimated token usage (Sept 1-15 equivalent, 46 leads):**

| Component | Tokens | Cost |
|---|---|---|
| Turn 1 (initial) | 46 × 1,900 = 87K | $0.26 |
| Turn 2 (account data) | 46 × 13,000 = 598K | $1.79 |
| Turn 3 (update/email) | 46 × 11,000 = 506K | $1.52 |
| Turn 4 (summary) | 30 × 500 = 15K | $0.05 |
| Output tokens | ~34K | $0.51 |
| **Total** | **~1.24M input** | **$4.13** |

**Savings: 84% reduction** ($26.66 → $4.13)

Note: This assumes normal execution. Edge cases (404s, transient errors) will add some cost, so realistic estimate is **~$5-6 for the period**.

---

## Model Options for Further Savings

### Option 1: Stay on Sonnet (RECOMMENDED)

✅ **Pros:**
- Already proven quality (when not looping)
- No integration work needed
- No risk to email quality
- Fixes alone save 84%

❌ **Cons:**
- Still the most expensive option per token
- Could save more with a cheaper model

**Cost after fixes:** ~$5-6 per 46 leads

---

### Option 2: Switch to Haiku (DROP-IN)

**Model:** claude-haiku-4-5  
**Pricing:** $1 input / $5 output (vs Sonnet $3/$15)

**Projected cost (Sept 1-15, after fixes applied):**
- Input: 1.24M × $1/M = $1.24
- Output: 34K × $5/M = $0.17
- **Total: ~$1.41** (75% cheaper than fixed Sonnet)

✅ **Pros:**
- Drop-in replacement (same API, just change model name)
- 3x cheaper on input, same quality tier (Anthropic family)
- Cold emails are not complex reasoning tasks
- Total savings: 95% from original ($26.66 → $1.41)

❌ **Cons:**
- **NO QUALITY DATA** - you don't know if Haiku writes worse emails
- Could hurt conversion rates (impossible to measure without testing)
- Premature optimization - fix works, why change more?

⚠️ **CRITICAL:** Do NOT switch without running golden set eval first.

**Estimated timeline to safely deploy:**
1. Build golden set: 1-2 days (20-30 real cases)
2. Run baseline on Sonnet: 1 hour
3. Run comparison on Haiku: 1 hour
4. Review quality differences: 2-4 hours
5. Get stakeholder approval: 1 day
**Total: 3-5 days**

---

### Option 3: Switch to GPT-5-mini (NEEDS INTEGRATION)

**Model:** gpt-5-mini (OpenAI)  
**Pricing:** $0.25 input / $2.00 output

**Projected cost (Sept 1-15, after fixes applied):**
- Input: 1.24M × $0.25/M = $0.31
- Output: 34K × $2/M = $0.07
- **Total: ~$0.38** (93% cheaper than fixed Sonnet, 73% cheaper than Haiku)

✅ **Pros:**
- Cheapest option
- Good quality for simple tasks (cold emails)
- Total savings: 98% from original ($26.66 → $0.38)

❌ **Cons:**
- **Requires code changes** (OpenAI SDK instead of Anthropic)
- Different tool calling format (function calling)
- Different prompting style may be needed
- Need to test quality extensively
- More testing/integration work

**Estimated timeline to safely deploy:**
1. Integrate OpenAI SDK: 2-4 hours
2. Adapt tool schemas: 1-2 hours
3. Test integration: 2 hours
4. Build golden set: 1-2 days
5. Run evals on both models: 2-4 hours
6. Review quality: 2-4 hours
7. Get approval: 1 day
**Total: 4-7 days**

---

### Option 4: Switch to Gemini Flash (NEEDS INTEGRATION)

**Model:** gemini-2.5-flash (Google)  
**Pricing:** $0.30 input / $2.50 output

**Projected cost (Sept 1-15, after fixes applied):**
- Input: 1.24M × $0.30/M = $0.37
- Output: 34K × $2.50/M = $0.09
- **Total: ~$0.46** (92% cheaper than fixed Sonnet)

Similar pros/cons to GPT-5-mini. Not recommended unless you're already using Google's stack.

---

## Recommendation

### Ship This Week: Fixes Only (Stay on Sonnet)

**Why:**
1. Fixes alone save 84% ($26.66 → $5-6)
2. Zero risk to quality
3. Can deploy today
4. Solves the immediate budget crisis

**What to deploy:**
- ✅ Max iterations limit (8)
- ✅ Cost cap per run ($0.50)
- ✅ Smart retry logic (fail fast on 4xx)
- ✅ Fixed prompt (call account once, remove lead_score_v2)

---

### Next Month: Evaluate Haiku Switch (If You Want More Savings)

**Why consider it:**
- Additional 75% savings over fixed Sonnet ($5 → $1.40)
- Drop-in replacement (low risk)
- Monthly savings at scale: $5 → $1.40 per 46 leads
  - If you do 1,000 leads/month: $109/mo → $30/mo (saves $79/mo)
  - If you do 5,000 leads/month: $543/mo → $152/mo (saves $391/mo)

**Why NOT immediately:**
- You need quality validation first
- The pain is already solved with fixes
- Rushing a model change is how you ship bad emails

**Timeline if you do this:**
1. This week: Ship fixes, monitor for issues
2. Next week: Build golden set (20-30 cases)
3. Week after: Run Sonnet vs Haiku evals
4. If Haiku passes quality bar: Switch with monitoring
5. If Haiku fails: Stay on Sonnet or try GPT-5-mini

---

## Cost Comparison Table

| Scenario | Sept 1-15 Cost (46 leads) | Monthly (1K leads) | Monthly (5K leads) |
|---|---|---|---|
| **Current (broken)** | $26.66 | $580 | $2,898 |
| **Sonnet + fixes** | $5.00 | $109 | $543 |
| **Haiku + fixes** | $1.40 | $30 | $152 |
| **GPT-5-mini + fixes** | $0.38 | $8 | $41 |

**Key insight:** At your current scale, even Sonnet with fixes is probably fine. The absolute dollars saved by switching to Haiku ($79/mo) or GPT-5-mini ($101/mo) may not be worth the testing effort unless you're scaling to thousands of leads per week.

---

## What Finance Should Know

**Current month-to-date (Sept 1-15):** $26.66  
**Projected for full month (at current broken rate):** ~$53  
**After fixes deployed:** ~$10-12 for full month (assuming similar volume)

**The 4x cost spike is from a bug, not volume.** We identified 5 conversations that hit retry loops and consumed 70% of the budget. The fixes prevent this.

**No model change needed** to get back to reasonable costs. The model choice was never the problem.

---

## Decision Matrix

| If your priority is... | Do this |
|---|---|
| **Stop the bleeding NOW** | Deploy fixes, keep Sonnet |
| **Maximum savings, don't care about timeline** | Fixes + eval Haiku/GPT-5-mini over 2 weeks |
| **Absolute cheapest, high volume** | Fixes + integrate GPT-5-mini (4-7 days) |
| **Balance of safety and savings** | Fixes now, eval Haiku next sprint if volume increases |

---

## Files to Review

- `/home/user/work/agent/loop.py` - Max iterations and cost caps
- `/home/user/work/agent/tools.py` - Smart retry logic
- `/home/user/work/agent/prompts.py` - Fixed prompt instructions
- `/home/user/work/output/cost_analysis_report.md` - Full analysis with evidence
- `/home/user/work/output/golden_set_starter.jsonl` - Eval cases to start with
