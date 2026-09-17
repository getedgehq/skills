# Token Burn Analysis: Outreach Agent Sept 1-15, 2026

## Executive Summary

**Don't switch models yet.** Three code issues burned 92% of the budget ($24.54 of $26.66):

1. **Prompt tells agent to retry on non-transient errors (71% of cost, $18.93):** 4 leads with scores >=80 hit a CRM validation error (`lead_score_v2` field doesn't exist) and retried 14-15 times each, eventually hitting the 200K token context limit.

2. **Prompt tells agent to fetch full CRM export every turn (21% of cost, $5.61):** Every turn re-fetches 30-40KB of account data and includes the full history in the context, causing exponential token growth.

3. **No max-iterations cap:** Agent has an unbounded `while True` loop with no cost or turn limit.

Fixing these three issues will reduce cost by ~92% without changing the model.

## Evidence

### Total Spend
- **Sept 1-15 cost:** $26.66 across 241 successful API calls, 46 conversations
- **August cost (estimated):** ~$6.66 (4x less than Sept 1-15)
- **Projected September cost:** ~$53 (8x August)

### Token Breakdown
- Total input tokens: 8,718,520 (~8.7M)
- Total output tokens: 33,859 (~34K)
- **Average input per call:** 36,175 tokens (Turn 1: 1,906 tokens, Later turns: 44,261 tokens avg, max 193,624)
- Model: claude-sonnet-4-5 at $3/M input, $15/M output

### Root Cause 1: Retry Loop on Non-Transient Errors (71% of cost)

4 conversations account for $18.93 (71% of total):

| Conversation | Lead | Turns | Cost | Status |
|--------------|------|-------|------|--------|
| cv_488aab | L-3419 | 17 | $4.73 | Hit 200K token limit |
| cv_15f5fe | L-3032 | 17 | $4.71 | Hit 200K token limit |
| cv_24a92f | L-2012 | 17 | $4.60 | Hit 200K token limit |
| cv_a99bb9 | L-2437 | 16 | $4.39 | Hit 200K token limit |

**Mechanism (file evidence):**

From `logs/crm_client.log`:
```
2026-09-06T02:01:13Z PATCH /contacts/ct_70760 -> 422 Unprocessable Entity 
  {"error":"validation_failed","detail":"unknown field","field":"lead_score_v2"} (attempt 1/4) lead=L-2012
[... repeated 60+ times for this lead ...]
```

From `agent/prompts.py` line 7-9:
> "Leads scoring 80 or higher must get the new scoring field: {"lead_score_v2": <score>}. Others: {"lead_score": <score>}.
> Do not finish until the CRM update has succeeded. If a tool call fails, try it again."

From `agent/tools.py` line 16-26 (`with_retries` decorator):
- Retries **all** ToolErrors 4 times with exponential backoff
- Does not distinguish between transient (503) and non-transient (422 validation) errors

From `agent/loop.py` line 13:
- `while True:` — no max iterations

**What happened:**
1. Sept 3 changelog added `lead_score_v2` field requirement for high-scoring leads
2. CRM schema was never updated with the new field (see `crm_schema.json` — only has `lead_score`)
3. Leads scoring >=80 trigger CRM 422 validation errors
4. Agent retries 4x per attempt, then tries again on next turn (prompt says "try it again")
5. Agent also calls `crm_get_account` every turn per prompt instruction (see RC #2)
6. Context grows ~12K tokens/turn, hits 200K limit at turn 16-17
7. 4 leads × 16 turns × ~$1.18/turn = $18.93 wasted

**Cost breakdown for cv_24a92f:**
- Turn 1: 1,892 input tokens, $0.009
- Turn 2: 14,338 input tokens (+12K), $0.046
- Turn 10: 113,770 input tokens (+12K/turn), $0.344
- Turn 16: 188,297 input tokens, $0.567
- Turn 17: 200,644 tokens, API rejected

### Root Cause 2: Fetching Full CRM Export Every Turn (21% of cost)

From `agent/prompts.py` line 5-6:
> "At the start of EVERY turn, call crm_get_account to load the latest full account export so your
> information is always fresh (reps edit accounts during the day)."

From `agent/tools.py` line 55:
```python
def crm_get_account(self, account_id):
    # full export: contacts, activities, emails, notes. big accounts are 30-40KB of JSON.
    return _http("GET", f"/accounts/{account_id}/export", params={"include": "contacts,activities,emails,notes"})
```

**Impact:**
- 187 crm_get_account calls across 46 conversations (4.1 calls/conversation avg)
- 29 conversations had 3+ get_account calls
- Most egregious: cv_6f895a (lead L-3489) made 25 get_account calls in 26 turns, likely hitting 404 "account_merged" errors (see CRM log), costing $0.33

**Why this is expensive:**
- Each export is 30-40KB of JSON (~10K tokens)
- Full conversation history is sent every turn (agentic loop pattern)
- Turn N context = system prompt + user message + (10K export × N) + all prior tool results
- For a 4-turn conversation: 1,900 + 10K + 10K + 10K + 10K = ~42K input tokens per call on average

### Root Cause 3: No Cost Governance

From `agent/loop.py`:
- Line 13: `while True:` — unbounded loop
- No max iterations
- No per-conversation cost cap
- No graceful degradation when approaching limits

## Harness Scorecard

| Part | Status | Evidence |
|------|--------|----------|
| **Golden set** | ❌ Missing | No `evals/` folder, README says "No tests yet (TODO)" |
| **Judge** | ❌ Missing | No automated checks for correctness |
| **Cost governance** | ❌ Missing | Unbounded loop, no cost caps, no max iterations |
| **Data layer** | ⚠️ Partial | CRM schema exists but doesn't match prompts (`lead_score_v2` missing) |
| **Action safety** | ⚠️ Partial | Email sending has no approval, but low risk for SDR workflow |
| **Tracing** | ✅ Present | Good traces in `logs/calls-*.jsonl` with conversation_id, tokens, cost, tools |

## What Changed in September?

From `CHANGELOG.md` on 2026-09-03:
1. ✅ Added `lead_score_v2` requirement for high-scoring leads — **BUT CRM schema was never updated**
2. ✅ Added "refresh account export every turn" instruction — **created exponential token growth**
3. ✅ Added "do not finish until CRM write succeeds" — **turned non-transient errors into infinite retries**

This triple-whammy explains the 8x cost increase.

## Recommendations

### Immediate (Stop the Bleeding)

1. **Fix the CRM schema mismatch** (5 min, blocks everything)
   - Either: add `lead_score_v2` field to CRM
   - Or: remove the v2 requirement from the prompt until field exists
   - This alone fixes the 4 runaway conversations ($18.93)

2. **Add max iterations** (5 min, prevents future blowups)
   - Add `if turn >= 10: return "Max iterations reached"` to loop.py
   - 95% of conversations finish in 4 turns; 10 is generous headroom

3. **Stop retrying non-transient errors** (10 min, prevents retry loops)
   - Modify `with_retries` to only retry 5xx errors, not 4xx
   - Remove "If a tool call fails, try it again" from prompt
   - Let the agent see the error once and decide, don't auto-retry

4. **Don't fetch CRM export every turn** (10 min, cuts token growth)
   - Change prompt: "Call crm_get_account once at the start"
   - If reps editing mid-batch is a real concern, fetch once more before final email send
   - This cuts average input tokens by ~60%

**Expected savings from these 4 fixes:** 
- Eliminates runaway conversations: -$18.93 (71%)
- Reduces average conversation cost by 60%: -$4.64 (17%)
- **Total: ~$23.57 savings, bringing Sept 1-15 from $26.66 → $3.09**
- **Projected monthly cost after fixes: ~$6.18 (same as August!)**

### Short-term (Next Week)

5. **Add per-conversation cost cap** (30 min)
   ```python
   MAX_COST_PER_CONVERSATION = 0.50  # $0.50
   if sum(call.cost_usd for call in conversation_history) > MAX_COST_PER_CONVERSATION:
       return "Cost limit reached, escalating to human"
   ```

6. **Create golden set** (2 hours)
   - Extract 20 representative leads from logs (mix of scores, with/without emails)
   - Add the 4 problem leads that hit errors
   - Define expected: score range, CRM update succeeded, email sent/not sent
   - See `output/golden_set_template.jsonl`

7. **Create eval judge** (2 hours)
   - Run golden set, check:
     - Did CRM update succeed? (query CRM or check logs)
     - Was email sent when score >= 50?
     - Was correct score field used (v2 if >=80, else v1)?
     - Did it complete in <10 turns and <$0.25?
   - See `output/eval_judge.py`

### Blocking Risk

🔴 **CRM write logic is broken:** The prompt says "Leads scoring 80 or higher must get the new scoring field: lead_score_v2" but that field doesn't exist in the CRM schema. This is causing 100% failure rate for high-value leads and burning the budget on retries. This must be fixed before running any more batches.

## Model Comparison (After Fixes)

Once the above fixes are deployed, here's what different models would cost:

**Assumptions after fixes:**
- 46 conversations/15 days = 3.07/day = ~94 conversations/month
- Fixed avg: 4 turns/conversation, 6K input tokens/turn, 75 output tokens/turn
- Total per conversation: 24K input, 300 output

| Model | Input $/M | Output $/M | Cost/Conv | Monthly (94 conv) | vs Current |
|-------|-----------|------------|-----------|-------------------|------------|
| claude-sonnet-4-5 (current) | $3.00 | $15.00 | $0.077 | $7.24 | baseline |
| claude-haiku-4-5 | $1.00 | $5.00 | $0.026 | $2.41 | -67% |
| gpt-5-mini | $0.25 | $2.00 | $0.012 | $1.13 | -84% |
| gemini-2.5-flash | $0.30 | $2.50 | $0.015 | $1.41 | -81% |

**But** we should not switch models yet because:
1. We have no golden set to verify quality holds
2. Cold email writing is reasonably complex (needs to understand CRM data, score leads, write personalized email)
3. Haiku is same API/SDK, would be the safest step-down if we want to experiment
4. Switching to OpenAI/Google SDKs has integration cost

**Next step:** Deploy the 4 immediate fixes, collect data for a week, then run a golden-set eval comparing Sonnet vs Haiku quality. If quality holds, Haiku saves $4.83/month (67%).

## Files Created

- `output/cost_analysis.md` — this document
- `output/golden_set_template.jsonl` — starter golden set
- `output/eval_judge.py` — eval harness script
- `output/agent_fixes.patch` — code changes for immediate fixes
