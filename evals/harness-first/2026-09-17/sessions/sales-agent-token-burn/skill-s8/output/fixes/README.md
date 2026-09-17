# Agent Fixes - Cost Governance & Error Handling

## What's Fixed

### 1. Cost Caps (loop.py)
- **Max iterations:** 10 turns per conversation (was infinite)
- **Max cost:** $1.00 per conversation (was unbounded)
- **Graceful degradation:** Returns error message instead of crashing
- **Impact:** Would have saved $16.66 on Sept 1-15 (capped at ~$10 vs $26.66)

### 2. Smart Error Handling (tools.py)
- **Only retry transient errors:** 429, 500, 502, 503, 504, timeouts
- **Don't retry permanent errors:** 400, 404, 422, 401
- **Reduced retry attempts:** 3 instead of 4
- **Mark retryability:** Model can see if error is worth retrying
- **Impact:** Stops infinite loops on validation errors (69% of Sept 1-15 costs)

### 3. Fixed Prompt (prompts.py)
- **Removed lead_score_v2:** Field doesn't exist in CRM yet (caused 64 failed API calls)
- **Removed "try again" instruction:** Was causing model to retry forever
- **Removed "call crm_get_account EVERY turn":** Wasteful, only needed once
- **Impact:** Eliminates root cause of 3 of 4 expensive conversations

### 4. Better Tracing (tracing.py)
- **Log errors:** Now captures conversations that hit limits
- **Handle None response:** Don't crash when logging errors

## Installation

```bash
# Backup originals
cp agent/loop.py agent/loop.py.backup
cp agent/tools.py agent/tools.py.backup
cp agent/prompts.py agent/prompts.py.backup
cp agent/tracing.py agent/tracing.py.backup

# Install fixes
cp output/fixes/loop.py agent/
cp output/fixes/tools.py agent/
cp output/fixes/prompts.py agent/
cp output/fixes/tracing.py agent/

# Test on a single lead first
python -c "
from agent.loop import run_conversation
result = run_conversation('L-TEST-001', conversation_id='test_001')
print(result)
"
```

## Testing Checklist

- [ ] Normal lead (score 50-79): qualifies, scores, sends email
- [ ] High-scoring lead (score 80+): qualifies, scores, sends email
- [ ] Low-scoring lead (score <50): qualifies, scores, no email sent
- [ ] Merged account: stops gracefully after 1-2 attempts, doesn't burn 26 turns
- [ ] Validation error: stops after 3 retries, doesn't loop forever
- [ ] Cost cap: conversation stops at $1.00, returns error message

## Expected Cost Reduction

| Scenario | Before | After | Savings |
|---|---|---|---|
| Normal conversation (3-4 turns) | $0.08-0.27 | $0.08-0.27 | $0 (already efficient) |
| Retry loop (16-17 turns) | $4.40-4.73 | $0.02-0.05 | $4.35-4.68 per failure |
| **Sept 1-15 actual** | **$26.66** | **~$10** | **$16.66 (62%)** |
| **Monthly projection (100 leads)** | **$53-60** | **$16-18** | **$36-44 (71%)** |

## What's Still Needed

### Before Switching Models:
1. **Golden set:** 20-30 test cases with expected outputs (see `evals/golden_set_starter.jsonl`)
2. **Judge script:** Automated scoring of golden set outputs
3. **Eval run:** Compare Sonnet vs Haiku on golden set
4. **Quality check:** Ensure Haiku emails are professional, not spammy

### Before Scaling:
5. **Data dictionary:** Document what each CRM field means, when to use it
6. **Draft mode:** Stage emails for review instead of sending immediately
7. **Separate tokens:** Read-only token for CRM queries, write token for updates
8. **Email content logging:** Capture full email text in traces for audit

## Model Recommendation

**After these fixes are tested, run an eval comparing:**
- claude-sonnet-4-5 (current): $3/MTok input, $15/MTok output
- claude-haiku-4-5 (recommended): $1/MTok input, $5/MTok output (same API, drop-in)

Expected additional savings with Haiku: 66% on input tokens
- Normal 3-turn conversation: $0.143 → $0.048 (67% cheaper)
- Monthly projection: $16-18 → $5-6 (saves another $10-11/month)

**Total potential savings:** $36-44/month from fixes + $10-11/month from model = **$48-54/month vs current**

But test Haiku quality first! "Likely fine" isn't good enough when you're sending to customers.
