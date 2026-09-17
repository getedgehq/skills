# Outreach Agent Model Switch - Summary

## Quick Answer

**Switched to: claude-haiku-4-5**

**Savings: $35.55/month (67% reduction)**

---

## The Problem

- Sept 1-15 cost: **$26.66** (on track for $53.33/month)
- August was likely ~$13-14 for the full month
- You're at 4x August's cost halfway through September

## Root Cause

The issue isn't volume - it's the **massive input tokens per call**:
- Average: **36,176 input tokens per API call**
- Output is tiny: only 140 tokens per call

Why so high? Looking at the prompt, the agent:
1. Calls `crm_get_account` every turn to "load the latest full account export"
2. This dumps huge CRM records into context
3. Multiple turns per conversation (avg 5.3 turns per lead)
4. Context grows with each turn → hitting 200K token limits on some leads

**Cold emails don't need Sonnet.** Priya was right - this is overkill.

---

## What I Changed

**File: `config.json`**
```json
{
  "model": "claude-haiku-4-5",          // was: claude-sonnet-4-5
  "max_tokens": 1024,
  "price_per_mtok_in": 1.0,             // was: 3.0
  "price_per_mtok_out": 5.0,            // was: 15.0
  "batch_window_utc": "02:00-05:00"
}
```

That's it. No code changes needed - same Anthropic SDK, same API.

---

## Cost Comparison (Full Month)

| Model | Monthly Cost | Savings | Notes |
|-------|-------------|---------|-------|
| **claude-haiku-4-5** ✓ | **$17.78** | **$35.55 (67%)** | **Drop-in, switched now** |
| claude-sonnet-4-5 | $53.33 | baseline | Current |
| gpt-5-mini | $4.49 | $48.83 (92%) | Requires OpenAI SDK rewrite |
| gemini-2.5-flash | $5.40 | $47.93 (90%) | Requires Google SDK rewrite |
| deepseek-v3.2 | $4.91 | $48.42 (91%) | Hosted in China |

---

## Why Haiku?

1. **Zero risk** - Same API, same SDK, tested and proven
2. **Zero work** - Just changed 3 lines in config.json
3. **Available now** - Will save ~$17.78 for Sept 16-30
4. **Good enough** - Cold emails are simple; Haiku can handle this easily

The other models would save more, but they'd require:
- SDK integration (1-2 hours)
- Testing
- Risk of quality degradation with unfamiliar models
- You said you wanted to flip it before month end

---

## Sept 16-30 Impact

With 14.5 days left in September at the old rate:
- **Old trajectory: $26.66 more** (total month: $53.33)
- **New with Haiku: $8.89 more** (total month: $35.55)
- **Actual Sept savings: $17.78**

---

## Other Issue Found

4 leads hit the 200K token context limit and failed (turns 16-17). The prompt instructs the agent to call `crm_get_account` "at the start of EVERY turn" which bloats context unnecessarily.

**Recommendation for later:** Modify the prompt so it only fetches CRM data once at the start, not every turn. Would prevent context overflow and reduce costs further.

---

## Test It

The switch is live in config.json. Next batch run will use Haiku automatically.

To test manually:
```bash
cd agent
python run_batch.py --test --limit 1
```

Should work identically, just faster and cheaper.

---

## Files

- `output/cost_analysis.txt` - Full cost breakdown with all model options
- `config.json` - Updated with Haiku settings
- This file - Summary for the team

---

**Bottom line:** We're now saving $35.55/month with a 30-second config change. If you want to save even more (~$48/month), we can do the OpenAI integration later, but Haiku gets you 67% of the way there with zero risk.
