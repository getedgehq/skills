# Cost Blowup Analysis & Fixes
## Brightkiln Outreach Agent - September 2026

**Date:** 2026-09-16  
**Analyzed by:** Harness-First Methodology  
**Data:** logs/calls-2026-09-01_15.jsonl (Sept 1-15), logs/crm_client.log

---

## TL;DR - Don't Switch Models Yet

**Your question:** Should we switch from Sonnet to a cheaper model (GPT-5-mini, 90% cheaper)?

**Answer:** **Not yet.** 70% of your September cost ($18.77 of $26.66) came from 5 conversations stuck in retry loops on deterministic errors. Fix the harness first and you'll save 69% with no model change. *Then* eval both models on quality with real test cases.

---

## The Numbers

### Sept 1-15 Actual Costs
- **Total conversations:** 46  
- **Total API calls:** 245  
- **Total cost:** $26.66  
- **Total input tokens:** 8,718,520  
- **Total output tokens:** 33,859  

### The Problem: 5 Retry Loops Burned 70% of Budget

| Metric | Normal (41 convos) | Retry Loops (5 convos) |
|--------|-------------------|----------------------|
| Avg turns | 3.7 | 18.6 |
| Avg cost | $0.19 | $3.75 |
| Total cost | $7.90 (30%) | **$18.77 (70%)** |

**Top offenders:**
1. cv_488aab (L-3419): 17 turns, 1.56M input tokens, $4.73
2. cv_15f5fe (L-3032): 17 turns, 1.56M input tokens, $4.71
3. cv_24a92f (L-2012): 17 turns, 1.52M input tokens, $4.60

---

## Root Cause (With Evidence)

### The Death Spiral

**File:** `agent/prompts.py` line 8-9  
```python
"At the start of EVERY turn, call crm_get_account to load the latest full 
account export so your information is always fresh"
```

**Result:** Exponential context growth
- Turn 1: ~1,900 tokens
- Turn 2: ~14,000 tokens (prev history + 12KB account export)
- Turn 3: ~27,000 tokens (prev history + prev export + new export)
- Turn 4: ~40,000 tokens
- ...
- Turn 16: ~188,000 tokens

### The Infinite Retry

**File:** `agent/tools.py` line 16-25  
```python
@with_retries(attempts=4, backoff=1.5)
def crm_update_contact(...):
    # Retries ALL errors, including deterministic 422s
```

**File:** `agent/prompts.py` line 11-12  
```python
"Do not finish until the CRM update has succeeded. If a tool call fails, 
try it again."
```

**File:** `agent/loop.py` line 19  
```python
while True:  # No max iterations!
```

**Logs:** `logs/crm_client.log`  
236 instances of `422 Unprocessable Entity` for field `lead_score_v2` (CRM admin never created this custom field)

**Result:**  
When agent tries to write `{"lead_score_v2": 85}`:
1. CRM returns 422 "unknown field"
2. `@with_retries` retries 4 times (all fail - error is deterministic)
3. Agent sees error, calls crm_get_account again per prompt instruction
4. Context grows by 12KB
5. Agent retries crm_update_contact with same bad field
6. Loop repeats 15-17 times until... something gives up

---

## What Gets Fixed

### Code Changes (Already Applied)

#### 1. `agent/loop.py` - Stop the bleeding
- ✅ Added `max_iterations=8` (default) - hard stop after 8 turns
- ✅ Added `max_cost_usd=0.50` (default) - hard stop if cost exceeds $0.50
- ✅ Raise exceptions with clear errors when limits hit
- ✅ Log cost cap / iteration violations

#### 2. `agent/tools.py` - Fix retry logic
- ✅ Only retry transient errors (429, 5xx, timeouts)
- ✅ Fail fast on client errors (400, 404, 422) - these won't fix themselves
- ✅ Updated tool schema: "Call crm_get_account ONCE per conversation, not every turn"
- ✅ Updated tool schema: "Use 'lead_score' field. Field 'lead_score_v2' does not exist."

#### 3. `agent/prompts.py` - Remove bad instructions
- ✅ Changed "At the start of EVERY turn" → "Call crm_get_account ONCE"
- ✅ Changed "Do not finish until CRM update succeeded" → "If error you cannot resolve after one retry, report and finish"
- ✅ Removed reference to non-existent `lead_score_v2` field
- ✅ Added efficiency guidance: "Complete the task in 3-5 turns"

### Test Harness Created

#### `evals/golden.jsonl` - 5 test cases
Based on real incidents and edge cases:
1. **normal_high_score:** Happy path, score ≥50, send email
2. **high_score_422_field_error:** Would have hit 17-turn loop, now should use correct field
3. **low_score_no_email:** Score <50, no email (validates conditional logic)
4. **unknown_field_graceful_fail:** 422 error handling (stop, don't infinite loop)
5. **account_merged_404:** 404 error handling (the 26-turn case)

#### `evals/judge.py` - Constraint checker
Ready to run when you have CRM test environment. Checks:
- Turn count limits
- Required tools called
- No repeated calls to expensive tools
- No infinite retry patterns
- Completion status

---

## Projected Savings

### Option A: Fix Harness Only (Same Model - Sonnet)
**Eliminates the 5 retry loops**

- Input tokens: 8.72M → 2.62M (remove 6.1M retry waste)
- Cost: $26.66 → **$8.37** 
- **Savings: 69% ($18.29)**

### Option B: Fix Harness + Switch to GPT-5-mini
**Applies fix, then uses cheaper model**

Current pricing:
- Sonnet: $3/Mtok in, $15/Mtok out
- GPT-5-mini: $0.25/Mtok in, $2/Mtok out

With harness fixes:
- Input: 2.62M × $0.25 = $0.66
- Output: 34K × $2 = $0.07
- **Total: $0.73**
- **Savings: 97% ($25.93)**

### Why Fix First?

**Without the fix, even on GPT-5-mini:**
- Same 5 retry loops would happen
- 8.72M tokens × $0.25 = $2.18 (91% cheaper but still wasteful)
- As volume scales, you still burn budget on exponential retries
- You'd debug the same infinite loops on a different model

**With the fix, on any model:**
- Retry loops eliminated
- Cost proportional to actual work
- Can scale volume without fear
- *Then* compare model quality/cost with real data

---

## Harness Scorecard

| Component | Status | Notes |
|-----------|--------|-------|
| **Golden set** | ⚠️ PARTIAL | Created 5 cases in `evals/golden.jsonl`. Need 15-20 more from production traffic. |
| **Judge** | ⚠️ PARTIAL | Framework in `evals/judge.py`. Needs CRM test env to run. |
| **Cost governance** | ✅ FIXED | Max iterations (8), max cost ($0.50), graceful failures with logging. |
| **Data layer** | ⚠️ PARTIAL | Fixed `lead_score_v2` bug. Need data dictionary defining scoring criteria. |
| **Action safety** | ❌ BLOCKED | `send_email` still has no approval gate - one bad prompt = spam to all leads. |
| **Tracing** | ✅ PRESENT | Already excellent (enabled this diagnosis). |

---

## Blocking Safety Issues

### 🔴 Critical: Emails Sent Without Approval

**File:** `agent/tools.py` `send_email()`  
**Risk:** One bad prompt change or prompt injection → spam sent to all leads

**Fix needed:** Add approval workflow or draft mode:
```python
def send_email(to, subject, body):
    # Option 1: Return draft for human approval
    draft_id = mailer.create_draft(to=to, subject=subject, body=body)
    return {"draft_created": True, "draft_id": draft_id, 
            "message": "Email draft ready for review"}
    
    # Option 2: Staging flag
    if os.environ.get("AGENT_ENV") != "production":
        return {"preview": True, "to": to, "subject": subject}
```

### 🟡 Medium: Write Credentials on Read-Heavy Path

**Issue:** Agent has full CRM write access but primarily needs read  
**Risk:** Compromised token or prompt injection could corrupt customer data

**Fix needed:** Read-only CRM credentials, separate write token with approval gate

---

## Next Steps (Prioritized)

### Before End of Month (Your Timeline)

1. ✅ **DONE:** Fixed retry loops, added cost caps (code changes above)
2. ✅ **DONE:** Created golden test set (5 cases in `evals/golden.jsonl`)
3. **TODO:** Test fixed agent on staging CRM with golden cases
4. **TODO:** Measure new cost per conversation (expect ~$0.19 avg)
5. **TODO:** Deploy to production with monitoring
6. **Expected savings:** 69% ($18/month on current volume)

### Before Model Switch

1. Add 15 more golden cases from real Sept traffic (aim for 20 total)
2. Run golden set on both Sonnet and GPT-5-mini
3. Compare: quality (pass rate), cost per case, email tone/length
4. If GPT-5-mini passes all cases: switch and save another 91%
5. If quality drops: keep Sonnet, you already saved 69%

### Before Scaling Volume

1. **Gate send_email:** Add draft mode or approval workflow
2. **Read-only CRM:** Separate read/write credentials
3. Expand golden set to 30+ cases covering all scoring scenarios
4. Automate judge runs on every prompt change (CI/CD gate)
5. Add alerting on cost spikes (>$1/conversation = investigate)

---

## Files Created

All outputs in `/home/user/work/output/` and `/home/user/work/evals/`:

- ✅ `output/cost_analysis.txt` - Detailed trace analysis with numbers
- ✅ `output/harness_scorecard.md` - Six-part harness assessment
- ✅ `output/REPORT.md` - This file (comprehensive summary)
- ✅ `agent/loop.py` - Fixed with max_iterations and cost caps
- ✅ `agent/tools.py` - Fixed retry logic, updated tool descriptions
- ✅ `agent/prompts.py` - Removed infinite retry instructions
- ✅ `evals/golden.jsonl` - 5 test cases from real incidents
- ✅ `evals/judge.py` - Constraint checking framework

---

## Summary

**You asked:** Should we switch to a cheaper model?

**Answer:** Not without fixing the harness first. You're not paying for expensive model quality - you're paying for infinite retry loops. Fix those (already done in the code) and you'll save 69% with no model change. Then run real quality tests on both models and decide with data, not vibes.

**Action:** Test the fixed code on staging, deploy before month end, monitor cost per conversation. You should see avg $0.19 instead of $0.58. That's your first win. Model comparison comes after.
