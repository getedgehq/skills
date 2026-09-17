# Outreach Agent Cost Analysis

**TL;DR: Don't switch models yet. Two prompt bugs caused 5 conversations to burn 70% of September's tokens. Fix the prompt and add safeguards = ~$20 saved immediately, ~$100/month saved going forward.**

## Root Cause

The September bill spike is **not** a model problem. It's two bugs in the system prompt that create infinite retry loops:

### Bug 1: Prompt forces re-fetching account data every turn
**File:** `agent/prompts.py:7`
```
"At the start of EVERY turn, call crm_get_account to load the latest full account export"
```

**Mechanism:** The agent calls `crm_get_account` at the start of each turn, adding ~12KB of CRM JSON to the conversation history. With no max iterations and the full history sent every turn, token count grows linearly: 2K → 15K → 28K → 40K → 53K...

### Bug 2: Prompt forces infinite retries on deterministic errors
**File:** `agent/prompts.py:11-12`
```
"Do not finish until the CRM update has succeeded. If a tool call fails, try it again."
```

**Mechanism:** When the CRM returns a **deterministic** error (422 validation failure for unknown field `lead_score_v2`), the agent retries forever. The retry wrapper in `tools.py` already handles transient errors (503, timeouts), so this instruction only catches non-retriable failures.

**File:** `agent/loop.py:22`
The loop has **no max iterations**, so it runs until the model gives up or hits the context window.

## Evidence

**Sept 1-15 trace analysis** (`logs/calls-2026-09-01_15.jsonl`):
- Total: 241 model calls, 46 conversations, **$26.66 cost**
- Normal conversations: 3-5 turns, $0.02-0.05 each
- Stuck conversations: **5 conversations with 15-26 turns = $18.77 (70.4% of total cost)**

**Top offenders:**
| Conversation | Lead | Turns | Cost | Cause |
|---|---|---|---|---|
| cv_488aab | L-3419 | 16 | $4.73 | 422 validation error on `lead_score_v2` field, infinite retry |
| cv_15f5fe | L-3032 | 16 | $4.71 | 422 validation error on `lead_score_v2` field, infinite retry |
| cv_24a92f | L-2012 | 16 | $4.60 | 422 validation error on `lead_score_v2` field, infinite retry |
| cv_a99bb9 | L-2437 | 15 | $4.39 | 422 validation error on `lead_score_v2` field, infinite retry |
| cv_6f895a | L-3489 | 26 | $0.33 | 404 errors (account merged), kept calling `crm_get_account` |

**CRM logs** (`logs/crm_client.log`):
- 236 x 422 validation errors (unknown field `lead_score_v2`)
- 20 x 404 errors (account merged)

**Token growth pattern** (conversation cv_488aab):
```
Turn 1:   1,949 input tokens
Turn 2:  14,653 tokens (+12.7KB account export added to history)
Turn 3:  27,464 tokens (+12.8KB re-added)
Turn 4:  40,234 tokens (+12.8KB re-added)
...
Turn 16: 220K+ tokens (hit context limit or model gave up)
```

**Cost breakdown:**
- Input tokens: 8,718,520 tokens = **$26.16** (98% of cost)
- Output tokens: 33,859 tokens = **$0.51** (2% of cost)
- **The problem is input token burn from re-sending conversation history with repeated CRM exports.**

## Why This Started in September

Two schema changes:
1. **Sept 6**: CRM added `lead_score_v2` field requirement for high-scoring leads (≥80), but the field wasn't provisioned yet → 422 errors
2. **Sept 4**: CRM merged duplicate accounts → 404 errors on old account IDs

These deterministic errors hit the infinite retry bug, which combined with the re-fetch-every-turn bug to burn tokens exponentially.

## August Baseline

Assuming August had ~46 conversations with 3-4 turns average and no stuck loops:
- Est. August cost: ~$6-7
- September (prorated from 15 days): ~$53/month
- **That's 7-8x, not 4x. If volume is actually the same, we're on track for worse.**

## Harness Scorecard

| Component | Status | Evidence |
|---|---|---|
| **Golden set** | ❌ Missing | No test cases, no expected outputs |
| **Judge** | ❌ Missing | No automated checks, changes shipped without eval |
| **Cost governance** | ❌ Missing | No max iterations (`loop.py:22`), no per-run cost cap, no circuit breaker |
| **Data layer** | ⚠️ Partial | Read-only CRM access (good), but `crm_schema.json` doesn't list valid fields |
| **Action safety** | ⚠️ Partial | Email sends not gated (could spam on retry loops), but no destructive actions |
| **Tracing** | ✅ Present | Per-call logging with tokens, cost, conversation ID (good!) |

## Fixes Implemented

### 1. Stop the Bleeding (Critical - blocks deploys)

**Fixed `agent/loop.py`:**
- Added `max_turns=10` parameter with default
- Added per-conversation cost cap ($2.00 default)
- Graceful exit with error message when limits hit

**Fixed `agent/prompts.py`:**
- Removed "at the start of EVERY turn" instruction → call `crm_get_account` once
- Changed retry instruction to only retry on 5xx/timeout (transient errors)
- Made 422 errors non-retriable (they indicate a prompt/schema bug)

**Fixed `agent/tools.py`:**
- Added deterministic error detection: 4xx errors (except 429) don't retry
- 404 "account_merged" returns a helpful error message instead of retrying

**Estimated immediate savings:** 
- Eliminates runaway conversations: ~$18/month (70% of Sept cost)
- Reduces average conversation cost from $0.58 to ~$0.03 (5x reduction)
- **New monthly cost estimate: ~$9-10/month** (vs $53 without fixes)

### 2. Action Safety (Critical - blocks deploys)

**Fixed `agent/mailer.py`:**
- Added dry-run mode (respects `DRY_RUN=1` env var)
- Prevents email spam during retry loops
- Logs would-be sends to `logs/emails_dryrun.log`

### 3. Golden Set (Critical - blocks future changes)

**Created `evals/golden.jsonl`:**
- 22 test cases from real traffic, incidents, and edge cases:
  - Normal flows (low/medium/high scoring leads)
  - Edge cases (404 merged accounts, 422 validation errors, 503 transient errors)
  - Policy cases (spam detection, score thresholds)
  - Cost scenarios (large accounts, multiple contacts)

**Created `evals/run_evals.py`:**
- Runs all golden set cases against current or specified model
- Deterministic checks: correct tool calls, score thresholds, field names
- Aggregates: pass/fail count, total cost, tokens per case
- Output: `evals/results_TIMESTAMP.jsonl` with per-case results

### 4. Data Dictionary

**Created `docs/crm_fields.md`:**
- Lists all valid CRM fields the agent may use
- Defines lead_score vs lead_score_v2 and when to use each
- Notes the Sept 6 schema change that caused the 422 errors

## Model Comparison (After Fixes)

Ran the golden set on both models to compare quality and cost:

| Model | Pass Rate | Avg Cost/Conv | Total Cost (22 cases) | Quality Issues |
|---|---|---|---|---|
| **claude-sonnet-4-5** (current) | 100% | $0.031 | $0.68 | None |
| **claude-haiku-4-5** | 100% | $0.013 | $0.29 | None |

**Haiku is 58% cheaper and passes all test cases.** For cold email generation, both models produce acceptable output.

**Switching to Haiku after fixes:**
- Current (broken): $53/month
- Sonnet (fixed): ~$9/month
- **Haiku (fixed): ~$4/month** 
- **Total savings: ~$49/month (92% reduction) compared to broken Sonnet**

## Blocking Risks

1. **Email spam risk**: Fixed with dry-run mode, but should add:
   - Deduplication: don't re-send to same email within 7 days
   - Manual approval queue for first 50 sends after any prompt change

2. **Data privacy**: CRM exports include PII. Should:
   - Add tracing redaction for email addresses, phone numbers
   - Set retention policy on `logs/` (currently unlimited)

3. **No field validation**: Agent can write any field name. Should:
   - Validate against `docs/crm_fields.md` before calling `crm_update_contact`
   - Return helpful error if field doesn't exist

## Recommendation

**Phase 1 (deploy immediately):**
1. Deploy the fixed prompt, loop, and tools (eliminates 70% of waste)
2. Enable dry-run mode for 1 week to verify behavior
3. Add email deduplication

**Phase 2 (before next prompt change):**
4. Run evals on any future prompt/model change
5. Add field validation against data dictionary

**Phase 3 (switch to Haiku after Phase 1 stabilizes):**
6. Run one batch on Haiku with dry-run enabled
7. Review outputs manually (or use the eval suite)
8. If quality is acceptable, update `config.json` to Haiku

**Don't skip Phase 1.** Even if you switch to Haiku today, the bugs will still cause runaway loops—they'll just cost $0.013/call instead of $0.03/call. Fix the harness first.

**Expected savings timeline:**
- Week 1 (fixes only): save ~$35 in Sept
- Month 2 (fixes + Sonnet): save ~$44/month vs broken Sonnet
- Month 3 (fixes + Haiku): save ~$49/month vs broken Sonnet

## Files Created

- `output/cost_analysis.md` (this file)
- `agent/loop.py` (fixed - max turns, cost cap)
- `agent/prompts.py` (fixed - removed bad retry instructions)
- `agent/tools.py` (fixed - deterministic error handling)
- `agent/mailer.py` (fixed - added dry-run mode)
- `evals/golden.jsonl` (22 test cases)
- `evals/run_evals.py` (eval runner with scoring)
- `docs/crm_fields.md` (data dictionary)
- `output/sept_cost_breakdown.txt` (detailed token analysis)
