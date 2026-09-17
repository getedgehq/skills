# Outreach Agent Cost Analysis - Sept 1-15, 2026

## Executive Summary

**DO NOT switch models yet.** The cost spike is caused by 3 critical harness bugs, not the model:

1. **Infinite retry loops on validation errors** (69% of total cost)
2. **No iteration limit** in the agent loop
3. **Full conversation history resent every turn** causing exponential token growth

### By the Numbers (Sept 1-15)
- **Total cost:** $26.66
- **46 conversations, 245 API calls**
- **4 conversations (9%) burned $18.44 (69% of total cost)**
  - Each ran 16-17 turns retrying a deterministic CRM validation error
  - Token counts grew from ~2K to 193K per call due to unbounded history
- **Normal conversations:** $0.08-0.27 per lead (3-4 turns)
- **Broken conversations:** $4.40-4.73 per lead (16-17 turns)

## Root Causes (with evidence)

### Issue #1: Retrying deterministic errors (BLOCKING)
**File:** `agent/tools.py:22-31`, `agent/prompts.py:9`

The prompt instructs: "Do not finish until the CRM update has succeeded. If a tool call fails, try it again."

The `@with_retries` decorator retries ALL errors 4 times, including:
- **422 validation errors** (unknown field `lead_score_v2` - permanent)
- **404 account_merged** (permanent)

**Evidence from logs/crm_client.log:**
- Lead L-2012 (conv cv_24a92f): 64+ failed PATCH attempts for unknown field "lead_score_v2"
  - Each failed attempt → model retries → full history resent → 13K more tokens
  - Cost: $4.60 over 17 turns
- Lead L-3489 (conv cv_6f895a): 26 failed GET attempts for merged accounts
  - Cost: $0.33 over 26 turns (smaller account data, so less token growth)

**Mechanism:**
1. Model tries to write `lead_score_v2` (score ≥80, per prompt)
2. CRM returns 422 "unknown field" (the field doesn't exist yet)
3. Decorator retries 4x
4. Tool returns error to model
5. Prompt says "try again" → model retries
6. Loop continues until rate limit or manual stop

### Issue #2: No max iterations (BLOCKING)
**File:** `agent/loop.py:16-35`

The `while True` loop has no iteration limit. Combined with issue #1, this allows 16-26 turn conversations.

### Issue #3: Unbounded history accumulation (BLOCKING)
**File:** `agent/loop.py:25`

Every turn, the full `messages` list (including all tool results) is resent to the API. CRM account exports are 30-40KB JSON.

**Token growth in failed conversations:**
| Conversation | Turn 1 | Turn 10 | Turn 16 | Growth/turn |
|---|---|---|---|---|
| cv_488aab (L-3419) | 1,949 | 116,933 | 193,624 | +12,778 |
| cv_15f5fe (L-3032) | 1,915 | 116,550 | 192,988 | +12,738 |
| cv_24a92f (L-2012) | 1,892 | 113,770 | 188,297 | +12,427 |

Each turn adds:
- System prompt (constant ~300 tokens)
- All previous messages
- Large CRM export result (12-14K tokens) from turn 2 onwards

### Issue #4: CRM tool called every turn (INEFFICIENCY)
**File:** `agent/prompts.py:7-8`

The prompt mandates: "At the start of EVERY turn, call crm_get_account to load the latest full account export..."

For a 3-turn conversation (normal case):
- Turn 1: ~1,900 tokens
- Turn 2: ~15,000 tokens (system + CRM export)
- Turn 3: ~28,000 tokens (system + CRM + previous)
- Cost: $0.08-0.10 per lead

This is wasteful but tolerable for normal conversations. It becomes catastrophic in retry loops.

## Cost Projection

### Current state (broken harness):
- Sept 1-15: $26.66 for 46 leads
- Failure rate: ~9% (4/46 conversations hit retry loops)
- **Projected monthly:** ~$53-60 for ~100 leads/month
- **If failure rate increases:** unbounded (no cost cap)

### After harness fixes (same model):
Assuming fixes stop retry loops:
- 46 leads, 42 succeed normally (avg $0.18), 4 fail gracefully (1-2 turns, ~$0.02)
- **Projected cost:** $7.56 + $0.08 = **$7.64** (71% reduction from current)
- **Projected monthly:** ~$16 for ~100 leads/month

### If switching to claude-haiku-4-5 (after fixes):
- Normal conversation input cost: $1/MTok vs $3/MTok (67% cheaper)
- 3-turn conversation: 1.9K + 15K + 28K = 44.9K input, ~0.5K output
  - Sonnet: $0.135 + $0.0075 = **$0.143**
  - Haiku: $0.045 + $0.0025 = **$0.048** (66% cheaper)
- **Projected monthly (Haiku, after fixes):** ~$5-6 for ~100 leads/month

**Bottom line:** Fix the harness first. That alone saves ~$36-44/month. Model swap saves another $10-11/month (but requires testing quality first).

## What Model Would I Choose?

**After harness fixes, run a golden set eval on Haiku vs Sonnet.** Cold email writing is not complex reasoning, so Haiku will likely perform fine. But "likely" isn't good enough - test it.

If Haiku quality passes, switch and save another 66% on input tokens. But fix the harness FIRST - a cheaper model in a broken loop still burns money.

## Files Created in This Analysis
- `output/cost_analysis.md` - This report
- `output/harness_scorecard.md` - Six-part harness audit
- `output/token_burn_evidence.json` - Raw data on worst conversations
- `output/fixes/` - Code fixes with max iterations, error classification, cost caps
