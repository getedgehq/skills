# Anthropic Bill Cost Analysis - September 2026

## Executive Summary

**Recommendation: Switch to Claude Haiku 4.5**

- **Current Sept 1-15 cost:** $26.66 (projected $53.33 for full month, 4x August)
- **With Haiku 4.5:** $8.89 half-month ($17.78 full month)
- **Monthly savings:** ~$35.55/month (67% reduction)
- **Implementation:** Drop-in replacement, same API, zero code changes needed

## Problem Analysis

The cost spike is caused by two issues:

### 1. Massive Input Token Bloat (8.7M input vs 34K output)
The system prompt instructs the agent to call `crm_get_account` **at the start of EVERY turn**, which:
- Loads 30-40KB JSON account exports repeatedly into context
- Causes input tokens to balloon from ~2K (turn 1) to 10-16K (turns 2-4)
- Results in 99.6% of costs being input tokens

Sample conversation token growth:
```
Turn 1:  1,900 input tokens
Turn 2: 11,068 input tokens (+480%)
Turn 3: 11,297 input tokens  
Turn 4: 14,032 input tokens
```

### 2. Agent Hallucinations on Errors
When accounts return 404s (merged accounts), the agent hallucinates account IDs:
- Tries acc_4242, acc_4242-1, acc_4242-2, ... acc_4242-18
- Each failed attempt adds more context
- Some conversations have 17+ turns and cost $4.70 each!

**Top 5 Most Expensive Conversations (Sept 1-15):**
```
Lead L-3419: 17 turns, 1.56M input tokens, $4.73 → $1.58 with Haiku (67% savings)
Lead L-3032: 17 turns, 1.56M input tokens, $4.71 → $1.57 with Haiku (67% savings)
Lead L-2012: 17 turns, 1.52M input tokens, $4.60 → $1.53 with Haiku (67% savings)
Lead L-2437: 16 turns, 1.45M input tokens, $4.39 → $1.46 with Haiku (67% savings)
Lead L-3489: 26 turns,  101K input tokens, $0.33 → $0.11 with Haiku (67% savings)
```

These 5 conversations alone cost $18.76 (70% of total spend).

## Model Comparison

For September 1-15 actual usage (8.7M input / 34K output tokens):

| Model | Half-Month Cost | Full Month | Savings | Notes |
|-------|----------------|------------|---------|-------|
| **claude-sonnet-4-5** (current) | $26.66 | $53.33 | baseline | overkill for task |
| **claude-haiku-4-5** ⭐ | $8.89 | $17.78 | $35.55 (67%) | **recommended** |
| gpt-5-mini | $2.25 | $4.49 | $48.84 (92%) | needs OpenAI SDK |
| gemini-2.5-flash | $2.70 | $5.40 | $47.93 (90%) | needs Google SDK |

## Why Haiku 4.5?

1. **Drop-in replacement** - Same Anthropic API, zero migration work
2. **More than good enough** - Cold email qualification doesn't need Sonnet's reasoning
3. **67% cost reduction** - Still significant savings
4. **Low risk** - Can revert instantly if quality drops
5. **Quick deploy** - Change 1 line in config.json and restart

## Pricing Details (from Priya's sheet)

```
claude-sonnet-4-5: $3.00/M input, $15.00/M output
claude-haiku-4-5:  $1.00/M input, $5.00/M output
```

Input tokens drive 98%+ of cost, so 3x reduction on input = ~67% total savings.

## Implementation

See `updated_config.json` - just swap it in and restart the agent.

Files included:
- `cost_analysis.md` (this file)
- `updated_config.json` (ready to deploy)
- `sept_1-15_cost_breakdown.csv` (detailed per-conversation breakdown for finance)

## Optional Future Optimization

If you want even more savings later (could get to <$5/month):
- Remove "call crm_get_account at start of EVERY turn" from prompt
- Call it once per conversation instead of 2-4 times
- Add better error handling for merged accounts (stop retrying invalid IDs)
- Would cut costs by another 70-80%
- But requires testing the workflow and fixing the hallucination issue
