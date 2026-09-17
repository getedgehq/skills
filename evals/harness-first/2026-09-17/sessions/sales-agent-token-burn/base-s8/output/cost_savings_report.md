# Outreach Agent Cost Savings Analysis
**Date:** 2026-09-16  
**Analysis Period:** Sept 1-15, 2026 (15 days)

## Current Situation

You're absolutely right - the costs are way higher than they should be for cold email generation.

**Current Model:** Claude Sonnet 4.5
- **Cost for Sept 1-15:** $26.66 (half month)
- **Projected full September cost:** $53.33
- **241 successful API calls** (4 errors due to context overflow)
- **Average tokens per call:** 36,176 input / 141 output

### The Problem

The agent is making multi-turn conversations with large CRM data dumps that get re-sent every turn. This is ballooning the context size and burning through expensive Sonnet tokens for a simple task (qualifying leads and writing short cold emails).

---

## Recommendation: Switch to Claude Haiku 4.5

**Why Haiku:**
✅ **Drop-in replacement** - Same Anthropic API, zero code changes needed  
✅ **67% cost reduction** - From $3/$15 per MTok to $1/$5 per MTok  
✅ **More than capable** - Haiku 4.5 handles tool calling and structured tasks perfectly  
✅ **No new integrations** - Uses your existing Anthropic setup

### Cost Comparison

| Model | 15-Day Cost | Monthly Cost | Monthly Savings | Savings % |
|-------|-------------|--------------|-----------------|-----------|
| **Current (Sonnet 4.5)** | $26.66 | $53.33 | - | - |
| **Haiku 4.5** ⭐ | $8.89 | $17.78 | **$35.55** | **67%** |
| gpt-5-mini | $2.25 | $4.49 | $48.83 | 92% |
| gemini-2.5-flash | $2.70 | $5.40 | $47.93 | 90% |

### Why Not The Others?

**gpt-5-mini** and **gemini-2.5-flash** would save even more (~90%), but they require:
- New SDK integration (OpenAI or Google client libraries)
- Rewriting tool/function calling code
- Testing and validation
- Risk of behavioral changes in email output

For a pre-month-end fix, Haiku is the clear choice.

---

## Bonus Issues Found

Looking at your logs, I found **4 API errors** where conversations hit the 200K token context limit (turns 16-17). This happens because the prompt keeps growing with tool results. The agent is also doing unnecessary work - it's calling `crm_get_account` on EVERY turn per the system prompt, even though the data rarely changes mid-conversation.

### Quick Win Fixes:
1. **Remove the "at the start of EVERY turn" requirement** from the system prompt - only fetch CRM data once
2. **Add conversation length limits** - conversations shouldn't need 17 turns for a cold email
3. These fixes will cut token usage significantly on top of the model switch

---

## Action Items

I've updated `config.json` to use Haiku 4.5. To deploy:

```bash
# The code already supports this via config.json
# Just restart your agent service
systemctl restart outreach-agent  # or whatever your deployment uses
```

**Expected monthly cost after switch:** ~$18 (down from $53)

Let me know if you want me to also fix the system prompt to reduce the token bloat!
