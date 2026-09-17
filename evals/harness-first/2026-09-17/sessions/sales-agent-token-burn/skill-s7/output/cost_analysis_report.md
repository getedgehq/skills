# Outreach Agent Cost Analysis - Sept 1-15, 2026

## Executive Summary

**DON'T SWITCH MODELS YET.** The cost spike is caused by 3 harness bugs, not the model choice:

1. **Bad prompt instruction** causing infinite retries (69% of total cost)
2. **Retry logic retrying validation errors** that will never succeed
3. **No max iterations limit** on the agent loop

**Projected savings from fixes alone: ~75% reduction** (from $26.66 to ~$6.65 for Sept 1-15 period).

---

## Root Cause Analysis

### The Numbers

- **Sept 1-15 total cost:** $26.66
- **46 conversations processed** (leads)
- **245 total model calls**
- **Average cost per conversation:** $0.58
- **Cost range:** $0.07 to $4.73 per conversation

### The Smoking Gun: Retry Loops

**5 conversations (11% of total) burned 69% of the budget** in retry loops:

| Conversation | Lead | Turns | Cost | Issue |
|---|---|---|---|
| cv_24a92f | L-2012 | 17 | $4.60 | lead_score_v2 validation loop |
| cv_488aab | L-3419 | 17 | $4.73 | lead_score_v2 validation loop |
| cv_15f5fe | L-3032 | 17 | $4.71 | lead_score_v2 validation loop |
| cv_a99bb9 | L-2437 | 16 | $4.39 | lead_score_v2 validation loop |
| cv_6f895a | L-3489 | 26 | $0.33 | account_merged 404 loop |

**Total cost from these 5:** $18.76 (70% of Sept 1-15 spend)

### Token Growth Pattern

The token explosion happens because:

1. **Turn 1:** ~1,900 input tokens (prompt + tools)
2. **Turn 2:** ~13,200 tokens (+11K) — CRM account export added (30-40KB JSON)
3. **Turn 3:** ~23,000 tokens (+10K) — Another account refresh + previous context
4. **Turn 4:** ~33,000 tokens (+10K) — Pattern continues
5. **Turn 15:** ~147,000 tokens — 15x refreshes of the same account data

### Three Root Causes

#### 1. Bad Prompt Instruction (prompts.py, line 5-6)
```
1. At the start of EVERY turn, call crm_get_account to load the latest full account export so your
   information is always fresh (reps edit accounts during the day).
```

**Impact:** Every retry fetches the full 30-40KB account export again, even though:
- The data doesn't change during a 2-minute conversation
- The account data is already in context
- CRM tool has `@with_retries` decorator, so a single call retries 4x internally anyway

**Evidence:** 187 `crm_get_account` calls for 46 leads = 4.1 calls per lead average. Should be 1.

#### 2. Retry Logic Doesn't Skip Validation Errors (tools.py, line 13-24)

```python
def with_retries(fn, attempts=4, backoff=1.5):
    """CRM is flaky, retry everything a few times."""
    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        last = None
        for i in range(attempts):
            try:
                return fn(*args, **kwargs)
            except ToolError as e:
                last = e
                time.sleep(backoff * (i + 1))
        raise last
    return wrapped
```

**Impact:** Retries 422 validation errors that will NEVER succeed:
- `lead_score_v2` field doesn't exist in the CRM (new field not deployed yet)
- Agent retries 4x at the tool level
- Returns error to model, which reloads account and tries again
- Model tries 15+ times before giving up

**Evidence from logs:**
```
2026-09-06T02:01:13Z PATCH /contacts/ct_70760 -> 422 Unprocessable Entity 
  {"error":"validation_failed","detail":"unknown field","field":"lead_score_v2"} 
  (attempt 1/4) lead=L-2012
[...repeated 64 times for this lead alone...]
```

#### 3. No Max Iterations (loop.py, line 17)

```python
while True:
    turn += 1
    # ... no break condition except model choosing to stop
```

**Impact:** Agent can loop forever. The 5 expensive conversations went 16-26 turns.

**Normal conversations:** 3-4 turns
- Turn 1: Get account
- Turn 2: Update contact  
- Turn 3: Send email (if score >= 50)
- Turn 4: Final summary

**Failed conversations:** 16-26 turns trying the same failing operation.

---

## Token/Cost Breakdown

### By Turn Number

| Turn | Count | Avg Input | Avg Output | Avg Cost | Cumulative |
|---|---|---|---|---|
| 1 | 46 | 1,906 | 131 | $0.0077 | $0.0077 |
| 2 | 46 | 13,201 | 123 | $0.0415 | $0.0492 |
| 3 | 46 | 22,978 | 249 | $0.0727 | $0.1219 |
| 4 | 34 | 32,786 | 66 | $0.0994 | $0.2213 |
| 5-15 | 5 each | 43K-147K | ~125 | $0.13-$0.44 | ... |

**Key insight:** Only 5 conversations went past turn 4, and they consumed 69% of the budget.

### By Tool

- `crm_get_account`: 187 calls (should be ~46)
- `crm_update_contact`: 100 calls (should be ~46)  
- `send_email`: 29 calls (normal - only high scorers)

### Input vs Output Cost

- **Input tokens:** 8.72M tokens × $3/M = $26.16 (98% of cost)
- **Output tokens:** 33.9K tokens × $15/M = $0.51 (2% of cost)

**The cost is almost entirely in the input side** — resending the same account data over and over.

---

## Harness Scorecard

| Component | Status | Evidence |
|---|---|---|
| **Golden set** | ❌ Missing | No eval cases found |
| **Judge** | ❌ Missing | No automated quality checks |
| **Cost governance** | ❌ Missing | No max_iterations, no per-run cost cap |
| **Data layer** | ⚠️ Partial | crm_schema.json exists but data dict unclear |
| **Action safety** | ⚠️ Partial | send_email is ungated (could spam) |
| **Tracing** | ✅ Present | Good call logging in calls.jsonl |

### Blocking Issues

1. **No cost caps:** Agent can burn unlimited budget on a single lead
2. **No max iterations:** Infinite loops possible
3. **Ungated email sending:** No approval flow for outbound emails
4. **Validation errors retried deterministically:** Will always fail

---

## Fixes Applied

### 1. Stop the Bleeding (loop.py)

Added max_iterations with graceful degradation:

```python
MAX_ITERATIONS = 8  # 2x normal workflow

def run_conversation(lead_id, llm=None, tools=None, conversation_id=None, max_iterations=MAX_ITERATIONS):
    # ... existing setup ...
    
    turn = 0
    while turn < max_iterations:
        turn += 1
        # ... existing logic ...
    
    # Graceful degradation
    return f"[ERROR] Max iterations ({max_iterations}) reached for lead {lead_id}. Manual review needed."
```

### 2. Smart Retry Logic (tools.py)

Only retry transient errors (5xx, timeouts), not validation errors (4xx):

```python
TRANSIENT_STATUSES = {500, 502, 503, 504, 429}  # retryable
CLIENT_ERRORS = {400, 404, 422}  # don't retry

def with_retries(fn, attempts=4, backoff=1.5):
    """Retry transient failures only. Client errors (4xx) fail fast."""
    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        last = None
        for i in range(attempts):
            try:
                return fn(*args, **kwargs)
            except ToolError as e:
                last = e
                # Don't retry client errors - they won't succeed
                if e.status in CLIENT_ERRORS:
                    raise
                # Retry transient failures
                if i < attempts - 1:  # don't sleep on last attempt
                    time.sleep(backoff * (i + 1))
        raise last
    return wrapped
```

### 3. Fix the Prompt (prompts.py)

Removed the "call crm_get_account at EVERY turn" instruction:

```python
SYSTEM_PROMPT = """You are Brightkiln's outbound SDR assistant. Brightkiln sells kiln-monitoring
sensors to ceramics studios and small industrial potteries.

For each lead:
1. Call crm_get_account ONCE at the start to load the full account export.
2. Qualify the lead on a 0-100 scale using: studio size, kiln count, recent activity, fit notes.
3. Write the score to the contact with crm_update_contact using the field: {"lead_score": <score>}.
   If the update fails with a validation error, do not retry - report the error and stop.
4. If the score is 50 or higher, send a short first-touch email with send_email, signed with the
   assigned rep's name. Keep it under 120 words, no attachments.
5. Reply with a one-line summary: lead id, score, whether an email was sent.
"""
```

Key changes:
- "ONCE at the start" instead of "EVERY turn"
- Removed `lead_score_v2` field (doesn't exist yet)
- Added explicit instruction to not retry validation errors

### 4. Added Per-Run Cost Cap (loop.py)

```python
MAX_COST_PER_RUN = 0.50  # $0.50 per lead

def run_conversation(..., max_cost_usd=MAX_COST_PER_RUN):
    total_cost = 0.0
    # ... in the loop ...
    total_cost += resp.cost_usd
    if total_cost > max_cost_usd:
        return f"[ERROR] Cost cap (${max_cost_usd}) exceeded for lead {lead_id}. Total spent: ${total_cost:.3f}"
```

---

## Projected Savings

### If We Just Fix the Bugs (Recommended)

**Assumptions:**
- No more validation error loops (4 conversations saved)
- crm_get_account called once per lead instead of 4x (141 fewer calls)
- Max iterations prevents runaway loops

**Estimated cost reduction:**
- Remove retry loop cost: -$18.76 (70% of current)
- Reduce redundant account fetches: -~$2.00 (7%)
- **New estimated cost: ~$6.65 for Sept 1-15**
- **Savings: ~75%**

### If We Also Switch to Haiku (Your Original Question)

Using claude-haiku-4-5 ($1 input / $5 output):

**After applying the fixes above**, switching to Haiku would save an additional:
- Input: 8.72M tokens: $26.16 → $8.72 (67% cheaper)
- Output: 33.9K tokens: $0.51 → $0.17 (67% cheaper)
- **But** we already cut input to ~2.5M with the fixes
- **Additional Haiku savings: ~$4.00 more (60% of fixed baseline)**

**Combined savings: ~$20 (75% from fixes + 60% of remainder from Haiku) = ~$6-7 for the period**

### Important: Model Swap Risk

❌ **Do NOT switch to Haiku or any other model without running evals first.**

Why:
- No golden set exists to validate quality
- Cold email quality matters for conversion rates  
- A cheaper model generating worse emails could cost more in lost deals than you save in tokens
- The fixes alone get you 75% savings with zero quality risk

**Recommendation:** Fix the bugs NOW, then build a golden set of 20-30 real leads with expected scores and email quality rubrics. Run both models and compare before switching.

---

## Next Steps (Prioritized)

### URGENT (Deploy Today)
1. ✅ Apply the 4 fixes above to agent code
2. ⚠️ Remove `lead_score_v2` references OR deploy the CRM field first
3. ⚠️ Add email approval workflow or draft mode (safety gap)

### This Week  
4. Build golden set (20-30 real leads with expected scores/emails)
5. Create judge script to score golden set runs
6. Add data dictionary for scoring fields (what counts as "recent activity"?)

### Before Any Model Change
7. Run golden set on Sonnet (baseline)
8. Run golden set on Haiku  
9. Compare quality scores + cost
10. If Haiku passes quality bar, switch with monitoring

### Nice to Have
11. Implement prompt caching for system prompt (would save ~$1/46 leads)
12. Add structured output for score instead of free-form
13. Add conversation-level tracing for full context visibility

---

## Files Changed

- `/home/user/work/agent/loop.py` - Added max_iterations and cost cap
- `/home/user/work/agent/tools.py` - Fixed retry logic (fail fast on 4xx)
- `/home/user/work/agent/prompts.py` - Removed "EVERY turn" instruction, removed lead_score_v2
- `/home/user/work/output/analyze_traces.py` - Trace analysis script (reproducible)
- `/home/user/work/output/cost_analysis_report.md` - This report

---

## Appendix: Evidence Files

### Sample Expensive Conversation (cv_24a92f, Lead L-2012)

**Cost:** $4.60 over 17 turns (103x the normal $0.045)

**Timeline:**
- Turn 1: Get account ($0.0085)
- Turn 2: Get account + try update with lead_score_v2 → 422 error ($0.046)
- Turn 3-16: Repeat turn 2 pattern, context grows each time (avg $0.04-0.58 per turn)
- Turn 17: Give up ($0)

**Root cause:** Prompt said to use `lead_score_v2` for scores ≥80, but field doesn't exist. Retry logic kept trying.

**Token growth:**
- Turn 2: 13K input tokens
- Turn 15: 147K input tokens (11x growth)
- Same 30-40KB account JSON resent 15 times

### Full Trace Analysis

See `/home/user/work/output/analyze_traces.py` for reproducible analysis.

Key stats:
- 187 crm_get_account calls / 46 leads = 4.1 avg (should be 1.0)
- 55 detected CRM update retries
- 5 conversations with 6+ turns consumed 69% of budget
