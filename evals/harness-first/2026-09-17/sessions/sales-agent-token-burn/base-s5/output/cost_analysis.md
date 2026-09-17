# Outreach Agent Cost Analysis & Recommendation

**Date:** 2026-09-16  
**Analysis Period:** Sept 1-15, 2026 (15 days)

## Current Situation

- **Current Model:** claude-sonnet-4-5 ($3/MTok input, $15/MTok output)
- **Sept 1-15 Actual Cost:** $26.66
- **Projected Full September Cost:** $53.33
- **Total API Calls (Sept 1-15):** 245 calls
- **Average tokens per call:** 35,586 input / 138 output

## The Problem

At current rate, September will cost ~$53, which is **4x the August cost**. The volume hasn't changed, so Sonnet-4-5 is simply too expensive for this use case.

## Model Comparison

| Model | Cost/Call | Sept Projected | Savings/Mo | Savings % | Notes |
|-------|-----------|----------------|------------|-----------|-------|
| **claude-sonnet-4-5** (current) | $0.109 | $53.33 | - | - | Overkill for cold emails |
| **claude-haiku-4-5** ⭐ | $0.036 | $17.78 | **$35.55** | **66.7%** | Drop-in replacement, same API |
| gpt-5-mini | $0.009 | $4.49 | $48.83 | 91.6% | Requires OpenAI SDK integration |
| gemini-2.5-flash | $0.011 | $5.40 | $47.93 | 89.9% | Requires Google SDK integration |
| deepseek-v3.2 | $0.010 | $4.91 | $48.42 | 90.8% | Cheapest, but CN-hosted |

## Recommendation: Switch to Claude Haiku 4-5

**Why Haiku:**
1. **Drop-in replacement** - Same Anthropic API, zero code changes needed (just config update)
2. **Saves $35.55/month (67% reduction)** - Gets costs under control without the risk of switching providers
3. **Perfect for the task** - Cold email qualification doesn't need Sonnet's advanced reasoning
4. **Same safety/quality guarantees** - Stays within Anthropic's model family

**Why not the cheaper options:**
- GPT-5-mini/Gemini would save more (~$48-49/mo) BUT require:
  - SDK integration work
  - Testing on a different model architecture
  - New API key management
  - Risk of quality degradation
- For a task as simple as cold email qualification, the extra engineering risk isn't worth the $12-13 additional savings

## Updated Configuration

I've updated `config.json` to use Haiku. The change is live - just restart the agent.

**Estimated remaining Sept cost with Haiku (Sept 16-30):**
- 15 days remaining × $1.19/day = **~$17.78 total** for Sept
- You'll save ~$26 just in the second half of September

## Next Steps

1. ✅ Updated config.json to claude-haiku-4-5
2. Restart the outreach agent when ready
3. Monitor quality for 2-3 days (check email output, scoring accuracy)
4. If all looks good, you're saving $426/year on this agent alone

---

*Note: If Haiku quality isn't sufficient (unlikely for this task), we can test GPT-5-mini next. But I'd be shocked if Haiku can't handle lead qualification and cold emails.*
