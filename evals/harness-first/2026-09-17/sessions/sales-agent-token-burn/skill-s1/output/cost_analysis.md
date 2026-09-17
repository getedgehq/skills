# Outreach Agent Cost Analysis - Sept 1-15, 2026

## Executive Summary

**DON'T switch models yet.** 70% of costs ($18.77 of $26.66) came from just 5 conversations stuck in retry loops burning tokens on deterministic errors. The root cause is a harness problem, not a model problem.

## Root Cause (with evidence)

**Mechanism:** The system prompt (agent/prompts.py:8) explicitly instructs: *"If a tool call fails, try it again."* Combined with no max-iterations cap (agent/loop.py:19, infinite `while True`), the agent retries deterministic 422 validation errors from the CRM until it burns $4-5 per conversation.

**Evidence from logs:**
- Lead L-3419 (cv_488aab): 16 turns, $4.73, failed 64 times on the same 422 error `"unknown field: lead_score_v2"`
- Lead L-3032 (cv_15f5fe): 16 turns, $4.71, same pattern
- Lead L-2012 (cv_24a92f): 16 turns, $4.60, same pattern  
- Lead L-2437 (cv_a99bb9): 15 turns, $4.39, same pattern
- Logs show the CRM API returns 422 consistently—this is NOT a transient error

**Token burn pattern:**
- Turn 1: ~1,900 input tokens (system prompt + initial ask)
- Turn 2: ~13,000 input tokens (+11KB CRM export in context)
- Each retry turn: +~13,000 more tokens (full conversation history including the huge CRM export resent every turn)
- By turn 16: ~145,000 input tokens per call

**Secondary issue (agent/prompts.py:1):** The prompt says *"At the start of EVERY turn, call crm_get_account"* even though the data doesn't change mid-conversation. One conversation (L-3489, 26 turns) called it 26 times, though it only cost $0.33 due to smaller CRM records.

**Data issue (agent/prompts.py:4):** Prompt references a field `lead_score_v2` that doesn't exist in the CRM schema (see crm_schema.json). The CRM rejects it with 422, which is correct behavior.

## Cost Breakdown

| Category | Conversations | Cost | % of Total |
|---|---|---|---|
| Normal (3-4 turns) | 41 | $7.90 | 29.6% |
| Retry loops (15-16 turns) | 4 | $18.44 | 69.2% |
| API error loop (26 turns) | 1 | $0.33 | 1.2% |
| **Total** | **46** | **$26.66** | **100%** |

Average cost per conversation:
- Normal workflow: $0.19
- With retry loop: $4.61 (24x more expensive)

## Projected Monthly Cost

**Current trajectory:**
- Sept 1-15: $26.66 (15 days, 46 conversations)
- If pattern continues: ~92 conversations/month
- Projected Sept total: ~$53 (4x August)

**After fixes (conservative estimate):**
- Remove retry loops on 422 errors: saves $18.44 of $26.66 = **69% cost reduction**
- Projected Sept total: ~$16.50
- That's **$440/year savings** vs. continuing with broken harness

**If you switched to gpt-5-mini without fixing:** You'd still have retry loops burning cheaper tokens. At 90% cheaper per token, you'd save ~$15/month but still waste $5/month on unnecessary calls. The loops would still exist.

## What Switching Models WOULD Save (hypothetically)

If the harness were working correctly (no retry loops):
- Current with Sonnet 4.5: 41 normal conversations = $7.90
- With gpt-5-mini (90% cheaper per Priya's sheet): ~$0.79/month for the same work
- Annual savings: ~$85

But you MUST fix the harness first or you'll still burn tokens in loops.

## Model Recommendation

**After fixes, Haiku 4.5 is the right move, not gpt-5-mini:**
- Haiku: 1/3 the price of Sonnet ($1 input vs $3), same Anthropic API, drop-in swap
- Post-fix cost with Haiku: ~$2.60/month (vs $7.90 with Sonnet)
- Writing cold emails is exactly what Haiku is built for
- No SDK changes needed (vs gpt-5-mini which needs OpenAI SDK)
- Keep the code simple and shippable

Estimated annual savings vs current: **~$425/year** (fixing loops + switching to Haiku)

---

# Harness Scorecard

| Component | Status | Evidence |
|---|---|---|
| **Golden set** | ❌ Missing | No evals/ directory, no test cases |
| **Judge** | ❌ Missing | No evaluation script, changes shipped with no checks |
| **Cost governance** | ❌ Missing | No max iterations (loop.py:19), no per-run cost cap, no circuit breaker |
| **Data layer** | ⚠️ Partial | Schema exists (crm_schema.json) but prompt references fields that don't exist |
| **Action safety** | ⚠️ Partial | send_email has no approval/draft mode; CRM writes happen without review |
| **Tracing** | ✅ Present | Good tracing in place (conversation_id, tokens, cost, tool_calls logged) |

## Blocking Safety Issues

1. **Uncontrolled spend:** Agent can burn unlimited $ with no circuit breaker
2. **Email sends without approval:** send_email fires immediately, no human gate for external communication
3. **Schema mismatch ships to production:** Prompt expects `lead_score_v2` field that doesn't exist in CRM

---

# Changes Needed (Priority Order)

## 1. STOP THE BLEEDING (do this first, before month end)

See `output/fixed_agent_code/` for patched files.

### A. Add max iterations circuit breaker (loop.py)
```python
MAX_TURNS = 6  # Normal flow is 3-4 turns; 6 gives buffer

def run_conversation(lead_id, llm=None, tools=None, conversation_id=None):
    # ... existing code ...
    turn = 0
    while turn < MAX_TURNS:  # CHANGED: was infinite while True
        turn += 1
        # ... rest of loop ...
```

### B. Fix the prompt (prompts.py)
- Remove *"try it again"* instruction on errors
- Remove *"at the start of EVERY turn"* instruction (only call CRM once)
- Fix field name from `lead_score_v2` → `lead_score` (matches schema)

### C. Stop retrying deterministic errors (tools.py)
```python
def with_retries(fn, attempts=4, backoff=1.5):
    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        last = None
        for i in range(attempts):
            try:
                return fn(*args, **kwargs)
            except ToolError as e:
                # Don't retry 4xx client errors (bad request, validation, auth)
                if e.status and 400 <= e.status < 500:
                    raise  # CHANGED: fail fast on client errors
                last = e
                time.sleep(backoff * (i + 1))
        raise last
    return wrapped
```

**Expected savings from fixes:** $18.44 / $26.66 = 69% cost reduction

## 2. Gate side effects (do before shipping more leads)

Add approval mode for emails:
```python
def send_email(self, to, subject, body):
    if os.environ.get("EMAIL_DRAFT_MODE", "true").lower() == "true":
        draft_id = mailer.save_draft(to=to, subject=subject, body=body)
        return {"sent": False, "draft_id": draft_id, "message": "Draft saved for review"}
    message_id = mailer.send(to=to, subject=subject, body=body)
    return {"sent": True, "message_id": message_id}
```

## 3. Create golden set (do this week)

Minimum 20 cases covering:
- Normal flow (score 50+, email sent)
- Low score (score <50, no email)
- Edge case: high score with missing contact email
- Edge case: CRM timeout (should fail gracefully)
- Edge case: account with no activity history
- Regression: leads that triggered past incidents

Format: `evals/golden.jsonl`
```json
{"lead_id": "L-test-001", "expected_outcome": {"score_range": [75, 85], "email_sent": true, "turns": [3, 4]}, "source": "typical_qualified_lead"}
```

## 4. Build judge script (this week)

See `output/run_eval.py` for starter script.

Checks:
- Max turns not exceeded
- Score written to CRM with correct field name
- Email sent only if score >= 50
- Email body under 120 words
- No duplicate API calls per conversation
- Total cost per conversation under $0.30

## 5. Switch to Haiku after testing (week of Sept 22)

Once fixes are validated:
1. Run golden set on Sonnet (baseline)
2. Change config.json model to `claude-haiku-4-5`, prices to 1.0/5.0
3. Run golden set on Haiku
4. Compare pass rates
5. If equivalent: ship Haiku, monitor for a day
6. Expected: $2.60/month vs $7.90 (67% savings on top of loop fix)

---

# Files Created

- `output/cost_analysis.md` (this file)
- `output/fixed_agent_code/loop.py` (with max iterations)
- `output/fixed_agent_code/prompts.py` (fixed instructions and field name)
- `output/fixed_agent_code/tools.py` (no retry on 4xx errors)
- `output/run_eval.py` (judge script starter)
- `output/golden_starter.jsonl` (3 example test cases to get you started)

Run the fixes with:
```bash
cp output/fixed_agent_code/*.py agent/
# Test on 2-3 leads manually first
# Then: run golden set with output/run_eval.py
```
