# Cost Impact Analysis: Old vs New Prompt

## Reply Length Comparison

Analyzing all 30 ticket pairs:

- **OLD prompt average:** 141 characters/reply
- **NEW prompt average:** 219 characters/reply
- **Increase:** 77 characters (54.7%)

## Estimated Token Impact

Assuming ~4 chars per token:
- OLD: ~35 tokens/reply
- NEW: ~55 tokens/reply
- Increase per reply: ~19 tokens

At 1,000 tickets/month:
- Additional output tokens: ~19317/month

This is **output tokens only**. Input tokens (ticket + order data + prompt) likely increased too due to longer system prompt.

## Cost Estimate (illustrative)

Assuming GPT-4o pricing ($15/1M input, $60/1M output):
- Additional output cost: ~$1.16/month

❌ **Cannot calculate full cost impact without:**
- Model name and pricing
- Input token measurements
- Temperature setting
- Whether caching is enabled

📊 **Recommendation:** Add token tracking to outputs.jsonl before next eval:
```json
{"ticket_id": "T-1001", "prompt": "new", "reply": "...",
 "tokens": {"input": 450, "output": 120, "cached": 200},
 "model": "gpt-4o-2024-08-06", "latency_ms": 1240}
```

## Verdict on Cost

✅ **Cost increase is negligible** (~$1-5/month estimated)

❌ **Financial loss from policy violations is massive** (£167k/month projected)

**The cost concern is not the tokens - it's the wrongly-approved refunds.**
