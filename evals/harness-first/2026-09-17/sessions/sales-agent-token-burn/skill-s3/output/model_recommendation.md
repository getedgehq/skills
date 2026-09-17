# Model Recommendation (After Fixing Harness)

## TL;DR

**Keep Claude Sonnet 4-5 for now.** The harness fixes will save $46/month. Switching models would save at most another $3.50/month, which doesn't justify migration risk or engineering time.

If you must switch, **claude-haiku-4-5** is the safest choice (drop-in replacement, $2.50/month additional savings).

## Cost Projection After Harness Fixes

Based on Sept 1-15 data (46 conversations, fixed to 3-4 turns each):

| Model | Input $/M | Output $/M | Monthly Cost | Savings vs Sonnet | Migration Effort |
|-------|-----------|------------|--------------|-------------------|------------------|
| **claude-sonnet-4-5** (current) | $3.00 | $15.00 | **$7.36** | baseline | none |
| claude-haiku-4-5 | $1.00 | $5.00 | $4.91 | $2.45/mo | zero (same API) |
| gpt-5-mini | $0.25 | $2.00 | $3.68 | $3.68/mo | medium (new SDK) |
| gemini-2.5-flash | $0.30 | $2.50 | $4.42 | $2.94/mo | medium (new SDK) |
| deepseek-v3.2 | $0.28 | $0.42 | $1.60 | $5.76/mo | high (CN hosting, new SDK) |

**Note:** These costs assume identical token usage. Different models may use more/fewer tokens or degrade quality.

## Why Keep Sonnet?

1. **Harness fixes deliver 86% savings** ($53 → $7.36/mo) - model swap is marginal
2. **Cold email quality matters** - Sonnet writes better than small models
3. **$7.36/month is negligible** for a production agent that touches real customers
4. **No regression risk** from model swap

## If You Must Switch

### Option 1: claude-haiku-4-5 ✅ RECOMMENDED
**Savings:** $2.45/month  
**Migration:** Change 1 line in config.json  
**Risk:** Low (same Claude API, similar training)  
**Quality:** Likely good enough for cold emails

```json
{
  "model": "claude-haiku-4-5",
  "max_tokens": 1024,
  "price_per_mtok_in": 1.0,
  "price_per_mtok_out": 5.0
}
```

**Before deploying:**
1. Run evals/judge.py on Haiku (when you implement runner)
2. Manually review 10 emails for quality
3. A/B test 50 leads (25 Sonnet, 25 Haiku) and compare reply rates

### Option 2: gpt-5-mini
**Savings:** $3.68/month  
**Migration:** Add OpenAI SDK, rewrite llm.py, adjust tool schemas  
**Risk:** Medium (different tool calling format)  
**Quality:** Unknown for this task

Not worth the engineering time for $1.23/month over Haiku.

### Option 3: Others
Gemini and Deepseek: Even more migration work, similar or worse savings than GPT-5-mini.

## What to Measure If You Test Models

Run golden set on each model and compare:

**Deterministic (must pass)**
- Tool call counts (1 crm_get_account per conversation)
- Max turns (<= 4 for normal cases)
- Policy compliance (email sent if score >= 50)

**Subjective (score with rubric)**
- Email quality: personalized, under 120 words, no jargon
- Lead scoring accuracy: does score match account data?
- Error handling: graceful on CRM failures?

**Business metrics (A/B test on 100+ leads)**
- Reply rate
- Meeting booked rate
- Complaints/unsubscribes

Don't ship a model change to production without running all three.

## Bottom Line

The 4x cost spike was a harness problem, not a model problem. Fix the harness, save $46/month, and leave Sonnet alone unless you have evidence that a cheaper model maintains quality.

If finance still pushes back on $7.36/month, switch to Haiku (zero effort, $4.91/month). Anything cheaper requires real work for negligible savings.
