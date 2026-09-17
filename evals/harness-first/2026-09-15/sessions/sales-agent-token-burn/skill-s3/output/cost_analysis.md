# Outreach Agent Cost Analysis - Sep 1-15, 2026

## Executive Summary

**Don't switch models yet: 5 conversations stuck in retry loops burned 70% of tokens ($18.77 of $26.66).**

The 4x cost spike is caused by two harness failures, not model choice:

1. **Infinite retry on non-transient errors** (404 account_merged, 422 unknown field) - the prompt says "try it again" and the agent obeys
2. **Full account re-fetch every turn** (30-40KB JSON) - prompt says "call crm_get_account at the start of EVERY turn", accumulating 12K tokens per turn in message history
3. **No max iterations cap** - loops run until API timeout or context window fills

## Evidence

### Sept 1-15 totals (from logs/calls-2026-09-01_15.jsonl)
- 46 conversations, 245 turns
- **$26.66 total cost**
- 8.7M input tokens, 34K output tokens
- Avg 5.3 turns/conversation, $0.58/conversation

### Cost by turn count
| Turns | Convs | Total Cost | Avg Cost |
|-------|-------|------------|----------|
| 3     | 12    | $1.43      | $0.12    |
| 4     | 29    | $6.46      | $0.22    |
| 16    | 1     | $4.39      | $4.39    |
| 17    | 3     | $14.04     | $4.68    |
| 26    | 1     | $0.33      | $0.33    |

**Top 5 conversations: $18.77 (70.4% of total)**

### The runaway conversations

**cv_24a92f (L-2012): $4.60, 17 turns**
- Lead scored 85+ (high value)
- Prompt says: "Leads scoring 80 or higher must get... `lead_score_v2`"
- CRM returns: `422 Unprocessable Entity {"error":"validation_failed","field":"lead_score_v2"}`
- Prompt also says: "Do not finish until the CRM update has succeeded. If a tool call fails, try it again."
- Agent retries 4x (with_retries decorator), sees error in tool result, fetches account again, retries CRM update... 17 turns
- Input tokens: 1.9K → 14K → 27K → 39K → 51K → 64K → 76K → 89K → 101K → 114K → 126K → 139K → 151K → 163K → 176K → 188K
- Each turn adds full account export (~12K tokens) to message history

**cv_488aab (L-3419), cv_15f5fe (L-3032), cv_a99bb9 (L-2437): same pattern**
- All high-scoring leads (80+)
- All failed on `lead_score_v2` field that doesn't exist in CRM
- 16-17 turns each, $4.39-$4.73 each

**cv_6f895a (L-3489): $0.33, 26 turns** (smaller per-turn cost because account lookups kept failing)
- Account ID kept returning `404 {"error":"account_merged"}`
- Agent retried 26 times calling `crm_get_account` with different account ID suffixes
- Prompt: "At the start of EVERY turn, call crm_get_account"

### Root causes with file locations

**1. Non-transient errors retried indefinitely**
- `agent/prompts.py:10-11`: "Do not finish until the CRM update has succeeded. If a tool call fails, try it again."
- `agent/tools.py:14-24`: `with_retries` decorator retries all ToolError 4x, then returns error to model
- `agent/loop.py:29`: `while True:` - no max iterations
- 404 account_merged and 422 validation errors are permanent, not transient. Retrying is waste.

**2. Prompt forces full account re-fetch every turn**
- `agent/prompts.py:6-7`: "At the start of EVERY turn, call crm_get_account to load the latest full account export so your information is always fresh"
- Account exports are 30-40KB JSON (contacts, activities, emails, notes)
- Each fetch adds ~12K tokens to input
- After 10 turns: 114K input tokens ($0.34 input alone)
- The account doesn't change mid-conversation; this is pure waste

**3. No cost governance**
- No max iterations per conversation
- No per-conversation token or cost cap
- No graceful stop message
- Agent runs until it hits API timeout or context window limit

## What each mechanism would save (if volume stays constant)

### Fix #1: Stop retry on non-transient errors
The 5 expensive conversations cost $18.77 and should have cost ~$0.60 (3 turns each).
**Savings: ~$18/half-month = $36/month**

### Fix #2: Call crm_get_account once per conversation
Normal 4-turn conversations: 1.9K + 13K + 23K + 33K = 70K input tokens
If account fetched only once: 1.9K + 1.9K + 1.9K + 1.9K = 7.6K input tokens (~89% reduction)
29 conversations at 4 turns: saved 62.4K * 29 = 1.8M tokens = $5.40
**Savings: ~$10/half-month = $20/month**

### Fix #3: Max 10 iterations
Safety net, prevents future runaways. Minimal cost impact if fixes #1 and #2 work.

### Combined fixes
With both fixes, expected cost/conversation drops from $0.58 to ~$0.08 (86% reduction)
46 conversations: $26.66 → $3.68
**Projected monthly savings: ~$46/month** (from current $53 to $7)

## Harness scorecard

| Part | Status | Evidence |
|------|--------|----------|
| **Golden set** | ❌ Missing | No evals/ directory, no test cases |
| **Judge** | ❌ Missing | No eval harness, changes shipped untested |
| **Cost governance** | ❌ Missing | No max_iterations, no per-run cap, no graceful stop |
| **Data layer** | ⚠️ Partial | CRM schema exists (crm_schema.json), but no field validation before use |
| **Action safety** | ⚠️ Partial | send_email writes to external system, but no approval gate or draft mode |
| **Tracing** | ✅ Present | logs/calls-*.jsonl has conversation_id, turn, tokens, cost, tool_calls |

## Blocking risks

1. **`lead_score_v2` field doesn't exist in CRM** - prompt references it but schema doesn't support it
2. **No send_email approval** - agent sends real emails to prospects; a bad prompt change ships with no review
3. **No regression testing** - prompt was changed (EVERY turn crm_get_account) with no eval run

## Model comparison (for reference only - not recommended yet)

From docs/model_pricing.md:

| Model | Input $/M | Output $/M | vs Sonnet input | vs Sonnet output |
|-------|-----------|------------|-----------------|------------------|
| claude-sonnet-4-5 (current) | $3.00 | $15.00 | - | - |
| claude-haiku-4-5 | $1.00 | $5.00 | 67% cheaper | 67% cheaper |
| gpt-5-mini | $0.25 | $2.00 | 92% cheaper | 87% cheaper |

**After fixes, switching to Haiku would save another $2/month. Not worth the migration risk vs fixing the harness.**
