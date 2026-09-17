# Outreach Agent Cost Investigation - Summary

**Date:** 2026-09-16  
**Period Analyzed:** Sept 1-15, 2026  
**Requested By:** Finance (Anthropic bill 4x August's cost)  
**Question:** Should we switch from Sonnet to a cheaper model?

---

## TL;DR - One-Liner Answer

**Don't switch models yet: 3 harness bugs (not the model) caused 69% of costs.** Fix the infinite retry loops and iteration cap first—saves $36-44/month. Then eval Haiku vs Sonnet on a golden set, which could save another $10-11/month if quality passes.

---

## Root Cause (with Evidence)

### The cost spike is NOT the model—it's a missing harness

**4 conversations (9% of volume) burned $18.44 (69% of total $26.66 cost)**

| Conversation | Lead | Turns | Cost | Problem |
|---|---|---|---|---|
| cv_24a92f | L-2012 | 17 | $4.60 | 64+ retries of 422 validation error "unknown field: lead_score_v2" |
| cv_488aab | L-3419 | 17 | $4.73 | Retry loop on validation error |
| cv_15f5fe | L-3032 | 17 | $4.71 | Retry loop on validation error |
| cv_a99bb9 | L-2437 | 16 | $4.39 | Retry loop on validation error |

**Files/Lines:**
- `agent/prompts.py:9` - "Do not finish until the CRM update has succeeded. If a tool call fails, try it again."
- `agent/tools.py:22-31` - `@with_retries` decorator retries ALL errors 4x, including permanent 422/404
- `agent/loop.py:16` - `while True` with no max iterations

**Mechanism:**
1. Prompt references CRM field "lead_score_v2" (for scores ≥80)
2. Field doesn't exist yet → CRM returns 422 "unknown field"
3. Decorator retries 4x
4. Model sees error, prompt says "try again" → model retries
5. Loop continues: each turn re-sends full 30-40KB CRM export in history
6. Tokens grow from 2K → 193K over 16 turns
7. No iteration cap or cost cap to stop it

Normal conversations (42/46): 3-4 turns, $0.08-0.27 each. These are fine.

---

## Harness Scorecard

| Part | Status | Impact |
|---|---|---|
| Golden set | ❌ MISSING | Can't test model changes safely |
| Judge | ❌ MISSING | No regression detection |
| Cost governance | ❌ MISSING | No iteration/cost caps → runaway costs |
| Data layer | ⚠️ PARTIAL | No data dictionary, referenced nonexistent field |
| Action safety | ⚠️ PARTIAL | Emails sent immediately, no approval |
| Tracing | ✅ PRESENT | Good logs enabled this diagnosis |

**Overall: 1/6 present, 2/6 partial, 3/6 missing**

---

## Cost Projections

### Current State (Broken)
- Sept 1-15: $26.66 for 46 leads
- Monthly projection: **$53-60** for ~100 leads
- **Unbounded if failure rate increases**

### After Harness Fixes (Same Model)
- Stop retry loops, add caps
- Monthly projection: **$16-18** for ~100 leads
- **Savings: $36-44/month (71% reduction)**

### After Haiku Switch (If Quality Passes)
- Input cost drops 67% ($3/MTok → $1/MTok)
- Normal 3-turn conversation: $0.143 → $0.048
- Monthly projection: **$5-6** for ~100 leads
- **Additional savings: $10-11/month**

**Total Potential Savings: $48-54/month vs current**

But harness first! A cheaper model in a broken loop still burns money.

---

## What Model to Switch To?

**Recommendation: claude-haiku-4-5**
- Drop-in replacement (same Anthropic API)
- Input: $1/MTok (67% cheaper), Output: $5/MTok (67% cheaper)
- Cold email writing ≠ complex reasoning, Haiku should handle it

**BUT: Test quality first with a golden set eval**
- Never recommend a model swap without eval evidence (per harness-first skill)
- "Likely fine" isn't good enough when sending to customers

---

## Deliverables Created

### Analysis
- `output/cost_analysis.md` - Full cost breakdown with evidence
- `output/harness_scorecard.md` - Six-part harness audit
- `output/token_burn_evidence.json` - Raw data on all 46 conversations
- `output/SUMMARY.md` - This file

### Fixes (Ready to Deploy)
- `output/fixes/loop.py` - Max 10 iterations, $1 cost cap per conversation
- `output/fixes/tools.py` - Only retry transient errors (429, 5xx, timeouts)
- `output/fixes/prompts.py` - Removed lead_score_v2, removed "try again" instruction
- `output/fixes/tracing.py` - Log errors properly
- `output/fixes/README.md` - Installation & testing guide

### Testing Foundation
- `output/evals/golden_set_starter.jsonl` - 10 test cases (normal, failures, edge cases)
  - Expand to 20-30 before running eval
  - Include cases from Sept 1-15 failures

---

## Action Plan (Prioritized)

### 1. URGENT (Today/Tomorrow) - Stop the Bleeding
- [ ] Review `output/fixes/` code changes
- [ ] Deploy to staging
- [ ] Test on 5-10 leads including known failures (L-2012, L-3489)
- [ ] Verify iteration cap works, cost cap works, retry loops stop
- [ ] Deploy to production
- **Expected Impact:** Save $36-44/month, prevent runaway costs

### 2. BLOCKING (This Week) - Fix Data Issue
- [ ] Either: Create "lead_score_v2" field in CRM
- [ ] Or: Keep using "lead_score" for all scores (simpler)
- [ ] Document in data dictionary (create one)
- **Expected Impact:** Eliminate 69% of failure cases

### 3. BEFORE MODEL CHANGE - Build Eval Harness
- [ ] Expand golden_set_starter.jsonl to 20-30 cases
- [ ] Build judge script with deterministic checks
- [ ] Run golden set on Sonnet (baseline)
- [ ] Run golden set on Haiku
- [ ] Compare quality + cost
- **Decision Point:** Only switch to Haiku if quality passes

### 4. OPTIONAL - Safety & Scale Prep
- [ ] Add draft mode for emails (stage for review)
- [ ] Separate read/write CRM tokens
- [ ] Log full email content in traces
- [ ] Add approval gate for high-value leads (score ≥90)

---

## Key Insights

1. **Always audit the harness before blaming the model**
   - The model followed instructions perfectly
   - The instructions were broken (retry forever, reference nonexistent field)

2. **A few outliers usually dominate costs**
   - 9% of conversations = 69% of costs
   - Fix the tail, not the average

3. **Tracing is worth its weight in gold**
   - Without structured logs, we'd be guessing
   - This diagnosis took 30 minutes because tracing existed

4. **Never ship a model/prompt change without a golden set**
   - The "lead_score_v2" prompt change had no tests
   - It burned $18.44 in 15 days and would have cost $36+/month

---

## Questions for You

1. **lead_score_v2 field:**
   - Was this supposed to exist in CRM? 
   - Should we create it, or revert to using lead_score for all scores?

2. **Deploy timeline:**
   - Can I/someone deploy the fixes in `output/fixes/` to staging today?
   - Who needs to review/approve code changes?

3. **Model switch timeline:**
   - When do you need a decision on Haiku?
   - Can we delay until we have golden set + eval results (1-2 weeks)?

4. **Access needed:**
   - Do you have staging environment where we can test fixes?
   - Who has CRM admin access to check if lead_score_v2 exists?

---

## Contact

If you want me to:
- Help deploy the fixes
- Build the full golden set + judge script
- Run the Haiku eval
- Review the code changes in detail

Just let me know. The fixes are ready to go and should ship ASAP to stop the bleeding.
