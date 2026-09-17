# Harness Scorecard: Brightkiln Outreach Agent

Audit performed: 2026-09-16
Period examined: Sept 1-15, 2026 logs

## Summary

| Part | Status | Evidence |
|---|---|---|
| Golden set | ❌ **MISSING** | No evals/ directory, no test cases |
| Judge | ❌ **MISSING** | No scoring script |
| Cost governance | ❌ **MISSING** | No iteration limit, no per-run cap, no graceful degradation |
| Data layer | ⚠️ **PARTIAL** | CRM schema exists but no data dictionary; uses write-capable token |
| Action safety | ⚠️ **PARTIAL** | Emails sent directly (no draft mode), but mailer module exists (could add approval) |
| Tracing | ✅ **PRESENT** | All calls logged with conv_id, tokens, cost (agent/tracing.py) |

**Overall: 1/6 present, 2/6 partial, 3/6 missing**

## Detailed Assessment

### 1. Golden set - MISSING ❌

**What's there:**
- Nothing. No `evals/` directory, no test cases file, no documented expected behaviors.

**What's needed:**
- ~20-30 test cases covering:
  - Normal flow (qualify, score, send email)
  - Edge cases (merged accounts, missing fields, low scores that shouldn't email)
  - Recent failures (L-2012, L-3419, L-3032, L-3489)
  - Policy constraints (email length, score thresholds, required fields)

**Impact:**
- Prompt change that added "lead_score_v2" field was shipped with no regression testing
- The field doesn't exist in CRM yet, causing 69% of current costs
- No way to validate quality before/after model changes

**Blocking:** YES - cannot safely change model or prompt without this

---

### 2. Judge - MISSING ❌

**What's there:**
- Nothing. No automated scoring of outputs.

**What's needed:**
- Script that runs golden set through agent and checks:
  - **Deterministic checks first:**
    - Email sent only if score ≥ 50
    - Email length ≤ 120 words
    - CRM updated with correct score field
    - No emails to unsubscribed contacts
  - **LLM judge (optional) for:**
    - Email tone/professionalism
    - Relevance to lead's business

**Impact:**
- No way to catch regressions before production
- No comparison data for model swap decision

**Blocking:** YES - cannot safely ship changes without this

---

### 3. Cost governance - MISSING ❌

**What's there:**
- `max_tokens: 1024` in config (limits single response, not conversation)
- Tracing records costs but doesn't enforce limits

**What's needed:**
- **Hard cap:** max 10 iterations per conversation (add to `loop.py:16`)
- **Per-run cost cap:** Fail gracefully if conversation exceeds $1
- **Graceful degradation:** Return summary message instead of crashing

**Current risk:**
- 4 conversations exceeded $4 each (no stop condition)
- No protection against runaway costs
- Finance has no predictable budget

**Impact of fix:**
- Would have capped Sept 1-15 at ~$10 instead of $26.66
- Saves ~$36-44/month vs current broken state

**Blocking:** YES - financial risk, must fix before month-end

---

### 4. Data layer - PARTIAL ⚠️

**What's there:**
- `crm_schema.json` exists (field types, constraints)
- CRM API client with structured requests

**What's missing:**
- **Data dictionary:** No definition of what "lead_score" vs "lead_score_v2" means, when to use each
- **Read-only access:** Agent uses write-capable CRM token (tools.py:13, env var BK_CRM_TOKEN)
- **Field validation:** No check that score field exists before writing

**Impact:**
- Prompt referenced a field that doesn't exist yet → 64 failed API calls for L-2012
- Agent could accidentally corrupt CRM data (has write access)

**Recommendation:**
- Create data dictionary: each field's definition, when it was added, which version of agent uses it
- Separate read token for CRM queries (get_account) from write token (update_contact, send_email)

**Blocking:** Partial - write access is a safety risk but not causing the immediate cost spike

---

### 5. Action safety - PARTIAL ⚠️

**What's there:**
- Emails sent via `mailer.send()` (agent/mailer.py)
- Tool schema documents what emails do

**What's missing:**
- **No draft mode:** Emails sent immediately, no human review
- **No approval gate:** High-stakes actions (sending to CEO, large companies) have no special handling
- **No rollback:** Once sent, cannot be unsent

**Current risk:**
- In retry loops, agent might send duplicate emails
- No review for emails to high-value prospects
- Logs show emails were sent, but no content captured for audit

**Recommendation:**
- Add `draft: true` mode that stages emails for rep approval
- For scores ≥ 90 or company size > 100 employees, require approval
- Log full email content in traces (currently only metadata)

**Blocking:** No - not causing cost issue, but safety gap exists

---

### 6. Tracing - PRESENT ✅

**What's there:**
- `agent/tracing.py` logs every call with:
  - conversation_id, lead_id, turn number
  - input_tokens, output_tokens, cost_usd
  - model, stop_reason
- Structured JSONL format (`logs/calls-2026-09-01_15.jsonl`)
- CRM client logs all HTTP calls (`logs/crm_client.log`)

**What could improve:**
- Add workflow/batch_id to trace calls from same batch job
- Log full email content sent (for audit/debugging)
- Add latency/duration per call
- Add error flag for failed conversations

**Impact:**
- Tracing enabled this diagnosis! Without it, we'd be guessing.
- Good foundation, minor improvements would help

**Blocking:** No - already good enough

---

## Priority Fixes (in order)

1. **Stop the bleeding (TODAY):**
   - Add max 10 iterations to loop.py
   - Classify errors as retryable/non-retryable in tools.py
   - Add per-conversation $1 cost cap
   - **Expected savings:** $36-44/month

2. **Data issue (THIS WEEK):**
   - Remove "lead_score_v2" from prompt until CRM field exists
   - OR create the field in CRM
   - Document in data dictionary

3. **Golden set (BEFORE MODEL CHANGE):**
   - Extract 20 cases from logs (including 4 failures)
   - Document expected score, email sent Y/N, key phrases
   - Build judge script with deterministic checks

4. **Run eval (BEFORE MODEL CHANGE):**
   - Run golden set on Sonnet (baseline)
   - Run golden set on Haiku
   - Compare quality + cost
   - If Haiku passes, switch and save another 66% on input

5. **Safety (BEFORE SCALING):**
   - Add draft mode for emails
   - Separate read/write CRM tokens
   - Log full email content

---

## Recommendation to Leadership

**Don't switch models yet.** The harness is missing or broken in 5 of 6 areas, causing:
- 69% of costs from retry loops (easily preventable)
- No way to test model changes safely
- Unpredictable budget (no cost caps)

Fix the harness (1-2 days of work), which saves 71% of current costs. THEN run a proper eval and consider Haiku, which could save another 66% on top of that.

**Total potential savings vs today:**
- Harness fixes alone: ~$36-44/month
- Harness + model switch: ~$48-54/month (if Haiku quality passes)

But a cheaper model in a broken harness still burns money. Fix the loop first.
