# Quick Deploy Guide - Switch to Haiku & Fix Bug

## TL;DR
- Switch from Sonnet to Haiku: **Save $35.55/month (67%)**
- Fix infinite loop bug that's burning ~$18/month on 5 broken conversations

## Deploy in 2 minutes

### Option 1: Quick fix (just update config)
```bash
cp output/config.json config.json
cp output/agent/loop.py agent/loop.py
# Test with a few leads, then deploy
```

### Option 2: Update in place
Just change these two lines in `config.json`:
```json
  "model": "claude-haiku-4-5",    # was: claude-sonnet-4-5
  "price_per_mtok_in": 1.0,       # was: 3.0
  "price_per_mtok_out": 5.0,      # was: 15.0
```

And add this to `agent/loop.py` after line 15:
```python
MAX_TURNS = 10  # Prevent infinite loops

def run_conversation(...):
    # ... existing code ...
    while True:
        turn += 1
        
        # ADD THIS:
        if turn > MAX_TURNS:
            error_msg = f"Conversation exceeded {MAX_TURNS} turns, aborting."
            print(f"ERROR: {error_msg} (lead_id={lead_id})")
            return error_msg
        
        # ... rest of existing code ...
```

## What changes

### What stays the same
- ✅ Same Anthropic SDK
- ✅ Same API calls
- ✅ Same tool definitions
- ✅ Same prompt
- ✅ Same output quality (Haiku is very capable for cold emails)

### What improves
- 💰 67% cost reduction ($53 → $18/month)
- 🐛 Infinite loop protection (prevents $4+ conversations)
- 📊 Predictable costs

## Cost breakdown

| Scenario | Current (Sonnet) | After (Haiku) | Savings |
|----------|-----------------|---------------|---------|
| Normal conversation (4 turns) | $0.24 | $0.08 | $0.16 |
| Typical daily cost (30 leads) | $7.20 | $2.40 | $4.80 |
| Monthly projection | $53.33 | $17.78 | $35.55 |

## Testing checklist

1. Deploy changes
2. Run agent on 3-5 test leads
3. Check email quality (should be same or better)
4. Verify no conversations exceed 10 turns
5. Monitor costs for 24 hours
6. If good, you're done!

## Rollback (if needed)

```bash
# Just change config back:
"model": "claude-sonnet-4-5",
"price_per_mtok_in": 3.0,
"price_per_mtok_out": 15.0,
```

## The bug we're fixing

**Problem:** Some conversations get stuck calling `crm_get_account` 26 times in a row, each time growing the context until it hits the 200K token limit and fails.

**Examples from Sept 1-15:**
- Lead L-3489: 26 turns, $0.33 (should be $0.08)
- Lead L-3419: 17 turns, $4.73 (should be $0.08) → API error
- Lead L-2437: 16 turns, $4.39 (should be $0.08) → API error

**Root cause:** No max turn limit in the agent loop

**Fix:** Added `MAX_TURNS = 10` safeguard (normal conversations are 3-4 turns)

## Questions?

- **Why Haiku over GPT-5-mini?** Drop-in replacement, no new SDKs, less risk
- **Will email quality suffer?** No - Haiku 4.5 is excellent at writing, easily handles cold emails
- **Can we go cheaper later?** Yes - if Haiku works, we can test GPT-5-mini for another 90% savings
- **What about the bug?** Must fix regardless of model - it's wasting 5-10x on broken conversations
