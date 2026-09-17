# DON'T SWITCH MODELS YET — Fix the Harness First

**TL;DR:** Three bugs caused the 4x cost spike. I fixed them. Deploy the changes in `agent/`, save $38/month (72%), THEN consider Haiku.

---

## The 4x Cost Spike: Root Cause

**Current Sept 1-15 cost:** $26.66 (projected $53/month)  
**Normal expected cost:** ~$7-8 per half-month

### Bug #1: Prompt forces redundant API calls (19% waste)
```python
# agent/prompts.py line 7 (BEFORE):
"At the start of EVERY turn, call crm_get_account..."
```
This re-fetches the 30-40KB account export on every turn even though the data never changes. By turn 15, we're sending 146K tokens per call.

**Fixed:** Changed to "Call crm_get_account ONCE at the start"

### Bug #2: No max iterations (67% waste) 
```python
# agent/loop.py line 20 (BEFORE):
while True:  # <-- infinite loop
```
5 conversations (11% of volume) hit CRM validation errors and looped 16-26 turns trying to retry. They burned $18.77 of the $26.66 total (70%).

**Fixed:** Added `max_iterations=10` parameter

### Bug #3: Retry on permanent errors (6% waste)
The retry decorator retries ALL errors 4x, including:
- 422 Unprocessable Entity (validation error—field doesn't exist)
- 404 Not Found "account_merged" (account was deleted)

**Fixed:** Only retry transient errors (429, 502, 503, 504)

---

## Cost Comparison

| Option | Sept 1-15 | Monthly | vs. Current |
|--------|-----------|---------|-------------|
| **Current (Sonnet, no fixes)** | $26.66 | $53.32 | baseline |
| Switch to Haiku (no fixes) | $8.89 | $17.78 | 67% savings |
| **Fix harness (keep Sonnet)** | **$7.41** | **$14.82** | **72% savings** |
| Fix harness + Haiku | $2.47 | $4.94 | 91% savings |

**Key insight:** Fixing the harness saves MORE than switching to Haiku without fixes ($14.82 vs. $17.78/month).

---

## What I Did

### 1. Fixed the code (ready to deploy)
- ✅ `agent/prompts.py` — removed "every turn" instruction
- ✅ `agent/loop.py` — added max_iterations=10
- ✅ `agent/tools.py` — only retry transient errors

### 2. Created harness components
- ✅ `output/golden_set.jsonl` — 5 test cases from real incidents
- ✅ `output/judge.py` — automated quality checks
- ✅ `output/cost_calculator.py` — compare all options
- ✅ `output/HARNESS_AUDIT_REPORT.md` — full analysis with evidence

### 3. Identified blocking risks
- ⚠️ **No approval gate on send_email** — agent sends to real prospects without review
- ⚠️ **Unknown CRM field** — `lead_score_v2` causes 422 errors (check with CRM admin)

---

## Recommendation

### This week (before month-end):
1. **Deploy the fixes** — Test on 2-3 leads, then roll out
2. **Check the lead_score_v2 field** — Talk to CRM admin (it's causing 4 of the 5 expensive loops)

### Next week:
3. **Run judge.py** on new traces to validate the fixes worked
4. **Add per-conversation cost cap** — stop if cost exceeds $0.50

### After validation:
5. **Consider Haiku** — Run golden set on both models, A/B test quality
6. **Add email approval workflow** — Draft mode for safety

---

## Model Recommendation

**Haiku makes sense for this workload** (after fixing the bugs):
- Cold email generation is not reasoning-heavy
- Same API, zero migration effort
- Additional 67% savings on top of the fixes

**But validate first:**
- Run golden set on both Sonnet and Haiku
- Score email quality, CRM field accuracy
- A/B test with 20% traffic for 2 weeks
- Monitor response rates

**Don't switch without eval evidence.** Even switching to GPT-5-mini saves 92%, but:
- Requires porting to OpenAI SDK
- Harness fixes alone get you 72% savings with zero code changes
- Then Haiku gets you to 91% with a one-line config change

---

## Files to Review

1. **`output/HARNESS_AUDIT_REPORT.md`** — Full analysis with evidence and file:line citations
2. **`output/cost_calculator.py`** — Run this to see the numbers
3. **`output/judge.py`** — Run on new traces after deploying fixes
4. **`output/golden_set.jsonl`** — Expand with 15-20 more cases

## Judge Baseline (Current Traces)

Ran `judge.py` on Sept 1-15 traces:
```
Max turns (<=10):           41 / 46 (89.1%)
crm_get_account once:        7 / 46 (15.2%)  ❌
No retry patterns:           7 / 46 (15.2%)  ❌
Cost reasonable (<$0.50):   42 / 46 (91.3%)

Overall: 52.7% pass rate — FAIL
```

After fixes, expect >90% pass rate.

---

**Questions?** Run the judge or cost_calculator scripts, or ping with new traces after deploying the fixes.
