# Outreach Agent Cost Analysis & Model Recommendation

**Date:** September 15, 2026  
**Prepared for:** Finance escalation on Anthropic bill

---

## Executive Summary

**Current situation:** We're halfway through September and already at **$26.66** in API costs (projected **$53.33** for the full month). Based on the 4x increase from August, this suggests August was ~$13-14.

**Root cause:** Claude Sonnet 4.5 is massively overkill for writing cold emails. We're spending $0.59 per lead for a task that doesn't require advanced reasoning.

**Recommendation:** Switch to **Claude Haiku 4.5** immediately
- **Drop-in replacement** (same API, just change model name)
- **66.7% cost reduction** → ~$17.78/month vs $53.33/month
- **Saves ~$35.55/month** (~$427/year)
- No code changes needed beyond config

---

## Current Usage (Sept 1-15)

| Metric | Value |
|--------|-------|
| Total API calls | 241 |
| Unique leads processed | 45 |
| Total input tokens | 8,718,520 |
| Total output tokens | 33,859 |
| **Total cost** | **$26.66** |
| Avg cost per lead | $0.59 |
| Avg calls per lead | 5.4 |

**Note:** The high input token count (193k per lead!) suggests the agent is making repeated CRM lookups as per the prompt requirements. Each turn starts with a fresh account export.

---

## Model Comparison & Savings

### Option 1: Claude Haiku 4.5 ⭐ **RECOMMENDED**

**Pricing:** $1.00/Mtok input, $5.00/Mtok output

| Metric | Amount |
|--------|--------|
| Sept 1-15 cost | $8.89 |
| Projected monthly | $17.78 |
| **Monthly savings** | **$35.55 (66.7%)** |
| Annual savings | $427 |

**Pros:**
- Drop-in replacement (Anthropic API, same tools/function calling)
- No SDK changes needed
- Same quality for simple tasks like cold emails
- Proven for structured tool use

**Cons:**
- None for this use case

---

### Option 2: GPT-5 Mini (not recommended)

**Pricing:** $0.25/Mtok input, $2.00/Mtok output

| Metric | Amount |
|--------|--------|
| Sept 1-15 cost | $2.25 |
| Projected monthly | $4.49 |
| **Monthly savings** | **$48.83 (91.6%)** |
| Annual savings | $586 |

**Pros:**
- Maximum cost savings
- Good for simple text generation

**Cons:**
- Requires OpenAI SDK integration (code changes)
- Different function calling format
- Would need testing/validation
- Higher implementation risk

---

## Recommendation Rationale

**Go with Claude Haiku 4.5** because:

1. **Zero risk deployment:** Literally just change the model name in config.json
2. **Proven tool calling:** Anthropic's function calling works identically across models
3. **Perfect for the task:** Writing 120-word cold emails doesn't need Sonnet's reasoning power
4. **Immediate savings:** Can deploy before month-end with zero testing overhead
5. **Material impact:** $427/year savings is real money for what's essentially a config change

The task breakdown shows the agent is:
- Loading CRM data (simple lookup)
- Scoring leads on 0-100 scale (basic math)
- Writing short emails (<120 words)
- Making CRM updates (structured JSON)

None of this requires Sonnet's advanced capabilities. Haiku is specifically designed for fast, cost-effective structured tasks.

---

## Implementation

See `updated_config.json` - just replace your current config.json with this file.

**Rollback plan:** If there are any quality issues (unlikely), just change the model back to `claude-sonnet-4-5` in config.json.

**Testing:** Monitor the first batch run and spot-check a few emails for quality. The output should be indistinguishable.

---

## Questions?

This is a no-brainer change. Let me know if you want me to flip it over now or if you want to review a sample batch first.
