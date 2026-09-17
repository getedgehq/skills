# Anthropic Bill Analysis & Recommendation

**Date:** 2026-09-16  
**Analyzed by:** AI Assistant  
**Period:** Sept 1-15, 2026

## Executive Summary

**Current monthly projection: $53.33** (up from ~$13 in August, a 4x increase)

**Recommendation: Switch to Claude Haiku 4.5**
- **Monthly savings: $35.55 (67% reduction)**
- **New monthly cost: ~$17.78**
- Drop-in replacement (same API, no code changes needed)
- More than adequate for cold email generation

## Detailed Analysis

### Current Usage (Sept 1-15)

| Metric | Value |
|--------|-------|
| Model | claude-sonnet-4-5 |
| Total API calls | 245 |
| Unique leads processed | 46 |
| Total cost | $26.66 |
| Input tokens | 8,718,520 |
| Output tokens | 33,859 |
| Average cost/lead | $0.58 |
| Average turns/lead | 5.3 |

### The Problem

1. **Sonnet is overkill for this task** - Cold email generation and simple lead scoring doesn't need the most powerful model
2. **No turn limit exists** - 5 conversations got stuck in loops (16-26 turns), 4 hit API errors from exceeding 200K token context limit
3. **Massive context growth** - Average 189K input tokens per conversation due to repeated CRM data loading

### Cost Comparison

| Model | Sept 1-15 | Monthly Projection | Monthly Savings | Reduction |
|-------|-----------|-------------------|----------------|-----------|
| **claude-sonnet-4-5** (current) | $26.66 | **$53.33** | - | - |
| **claude-haiku-4-5** ⭐ | $8.89 | **$17.78** | **$35.55** | **67%** |
| gpt-5-mini | $2.25 | $4.49 | $48.83 | 92% |
| gemini-2.5-flash | $2.70 | $5.40 | $47.93 | 90% |
| deepseek-v3.2 | $2.46 | $4.91 | $48.42 | 91% |

### Why Claude Haiku 4.5?

✅ **Drop-in replacement** - Same Anthropic API, zero code changes  
✅ **Proven quality** - Haiku 4.5 easily handles cold emails and basic reasoning  
✅ **67% cost reduction** - Saves ~$425/year without switching vendors  
✅ **No integration risk** - Keep existing SDK, auth, error handling  

While GPT-5-mini and others are cheaper, they require:
- New SDK dependencies (OpenAI/Google)
- Different API patterns and error handling
- Testing and validation
- Potential differences in tool calling behavior

**For a before-month-end change with minimal risk, Haiku is the clear choice.**

## Critical Bug Found

**Issue:** Some conversations get stuck in infinite loops calling `crm_get_account` repeatedly (one hit 26 turns!)

**Root cause:** No max turn limit in `agent/loop.py`

**Impact:** 
- Top 5 most expensive conversations: $4.39-$4.73 each (vs $0.58 average)
- 4 API errors from exceeding 200K token context limit
- ~$18 wasted on these 5 leads alone in 15 days

**Fix:** Added max turn limit of 10 in updated code (see `agent/loop.py`)

## Files Generated

1. `output/cost_analysis.md` - This analysis
2. `output/agent/loop.py` - Fixed loop with turn limit
3. `output/config.json` - Updated config for Haiku 4.5
4. `output/agent/llm.py` - Optional: Added turn limit support

## Action Items

1. ✅ **Switch to Haiku** - Replace config.json with `output/config.json`
2. ✅ **Fix infinite loop bug** - Replace `agent/loop.py` with `output/agent/loop.py`  
3. Test with a few leads to verify email quality
4. Monitor costs for 2-3 days
5. If Haiku quality is acceptable (it should be), you're done. If not, try GPT-5-mini next.

## Expected Results

- **Monthly bill drops from $53 to ~$18**
- No more infinite loop conversations
- Same or better email quality (Haiku is very capable for this task)
- Changes deployed in <5 minutes
