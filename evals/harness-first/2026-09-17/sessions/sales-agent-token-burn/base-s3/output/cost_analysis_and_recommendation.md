# Outreach Agent Cost Analysis & Model Recommendation
**Date:** 2026-09-15  
**Prepared for:** Finance review of Anthropic bill spike

## Executive Summary

**Current Situation:**
- Sept 1-15 (halfway through month): **$26.66**
- Projected full September: **$53.33**
- Using: `claude-sonnet-4-5` @ $3/M input, $15/M output

**Recommendation:** Switch to `claude-haiku-4-5`
- **Savings: 67%** ($35.55/month)
- **Full September projected cost:** $17.78 (vs $53.33)
- **Zero code changes required** - drop-in replacement, same API

---

## Detailed Analysis

### September 1-15 Usage
- **Total cost:** $26.66
- **Input tokens:** 8,718,520 (~8.7M)
- **Output tokens:** 33,859 (~34K)
- **Conversations:** 46
- **Unique leads:** 45

### Cost Breakdown Pattern
The agent runs 4-turn conversations on average:
1. **Turn 1:** Initial CRM fetch (~1.9K tokens in, ~130 tokens out)
2. **Turn 2:** Multi-tool calls with large context (~12-15K tokens in, ~120 tokens out)
3. **Turn 3:** Email composition (~12-16K tokens in, ~300 tokens out)
4. **Turn 4:** Final summary (~13-17K tokens in, ~50 tokens out)

**Problem:** The agent repeatedly calls `crm_get_account` per the system prompt, causing massive context growth. Some conversations balloon to 40K+ input tokens due to repeated large CRM dumps.

---

## Model Comparison

| Model | Input $/M | Output $/M | Sept 1-15 | Full Month | Monthly Savings | % Saved | Implementation |
|-------|-----------|------------|-----------|------------|-----------------|---------|----------------|
| **claude-sonnet-4-5** (current) | $3.00 | $15.00 | $26.66 | **$53.33** | - | - | Current |
| **claude-haiku-4-5** ⭐ | $1.00 | $5.00 | $8.89 | **$17.78** | **$35.55** | **67%** | Zero code changes |
| gpt-5-mini | $0.25 | $2.00 | $2.25 | $4.49 | $48.83 | 92% | Need OpenAI SDK |
| gemini-2.5-flash | $0.30 | $2.50 | $2.70 | $5.40 | $47.93 | 90% | Need Google SDK |

---

## Why Claude Haiku 4-5?

### ✅ Pros:
1. **Zero friction deployment** - Change one line in `config.json`, no code changes
2. **Same API, same SDK** - Uses existing Anthropic integration
3. **Same tool-calling format** - No compatibility issues
4. **67% cost reduction** - Saves $35.55/month
5. **Appropriate for the task** - Cold email generation doesn't need Sonnet's capabilities
6. **Deploy today** - Can flip before month end as requested

### 🤔 Alternative Considerations:
- **gpt-5-mini** or **gemini-2.5-flash** save more (90%+) but require:
  - New SDK integration
  - Testing tool-calling format differences
  - Potential quality validation
  - 1-2 days of development work

### Task Complexity Assessment:
The agent workflow is:
1. Query CRM for lead data
2. Score the lead (simple heuristic)
3. Write score back to CRM
4. Generate a <120 word cold email

**This is NOT rocket science** (per Priya's note). Haiku is more than capable for this task.

---

## Recommendation

### Primary: Switch to claude-haiku-4-5 NOW
- **Action:** Update `config.json` (see updated file)
- **Timeline:** Deploy immediately, saves money for rest of September
- **Risk:** Very low - same API, proven model
- **Expected quality:** Equivalent for this simple use case

### Future: Consider gpt-5-mini for additional savings
- **Timing:** Q4 project if you want to squeeze more savings
- **Additional savings:** ~$13/month over Haiku (another 75% reduction)
- **Effort:** 1-2 days engineering work

---

## Config Change Required

Update `config.json`:
```json
{
  "model": "claude-haiku-4-5",
  "max_tokens": 1024,
  "price_per_mtok_in": 1.0,
  "price_per_mtok_out": 5.0,
  "batch_window_utc": "02:00-05:00"
}
```

That's it. Redeploy and you're saving 67%.

---

## Additional Optimization Opportunity

**Context bloat issue:** The system prompt requires calling `crm_get_account` at the start of EVERY turn, causing context to grow from ~2K to 40K+ tokens across 4 turns. 

**Potential fix:** Modify prompt to only fetch CRM data once per conversation, could reduce token usage by 50%+. This would amplify savings further.

**Estimated additional savings:** Another $8-10/month with current model, $3-4/month with Haiku.

Not urgent, but worth considering if you want to optimize further.

---

## Questions?

- **Quality concerns?** Haiku handles tool calling and short-form email generation perfectly
- **Rollback plan?** Change config back, takes 30 seconds
- **Testing?** Run a few leads manually to verify output quality if desired

**Bottom line:** Switch to Haiku today, save $35/month, done before month end. ✅
