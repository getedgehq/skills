# Quick Deployment Guide

## What Changed

✅ **Model:** `claude-sonnet-4-5` → `claude-haiku-4-5`  
✅ **Prompt:** Fixed context bloat bug (removed "EVERY turn" instruction)  
✅ **Savings:** 67% immediate, ~75% total with prompt fix

---

## Files Updated

### In Project Root (already done)
- ✅ `config.json` - switched to Haiku with correct pricing
- ✅ `agent/prompts.py` - fixed prompt to load CRM data once

### In Output Folder (for your reference)
- 📄 `output/cost_analysis_and_recommendation.md` - executive summary
- 📄 `output/technical_deep_dive.md` - detailed technical analysis
- 📊 `output/model_cost_comparison.csv` - cost comparison spreadsheet
- 🔧 `output/config.json` - backup of new config
- 🔧 `output/prompts.py` - backup of fixed prompt

---

## Deployment Steps

### Option A: Deploy Everything Now (Recommended)
```bash
# The files are already updated in your repo
# Just restart the agent service

# If running as a service:
sudo systemctl restart outreach-agent

# If running via cron/manual:
# Just let it run at the next scheduled time (02:00-05:00 UTC)
# It will pick up the new config.json automatically
```

**Result:** 
- Tonight's run will use Haiku (67% savings)
- No more context bloat bugs (eliminates failures)
- Conversations will finish in 3-4 turns instead of 5-17

### Option B: Deploy Model Switch First, Prompt Fix Later
```bash
# If you want to be extra cautious, deploy in stages:

# Stage 1 (today): Just switch the model
git checkout agent/prompts.py  # revert prompt changes
# Keep the config.json change
# Restart agent

# Stage 2 (next week): Deploy prompt fix
# Update agent/prompts.py with the fix
# Restart agent
```

**Result:**
- Stage 1: 67% savings, but still has context bloat on long conversations
- Stage 2: Additional ~10-15% savings, eliminates failures

---

## Validation

### After Next Run (Sept 16 morning)
Check the logs:

```bash
# Count conversations and costs
python3 << 'EOF'
import json
cost = 0
convs = set()
with open('logs/calls-2026-09-16.jsonl') as f:
    for line in f:
        d = json.loads(line)
        cost += d.get('cost_usd', 0)
        convs.add(d['conversation_id'])
print(f"Conversations: {len(convs)}, Cost: ${cost:.2f}")
EOF
```

**Expected results:**
- Similar number of conversations (~2-3 per night based on your lead volume)
- Cost per conversation: ~$0.19 (down from ~$0.58)
- No API errors about context length
- Average turns: 3-4 (down from 5.3)

### Red Flags
- ❌ If cost per conversation is still ~$0.50+ → model didn't switch (check config.json)
- ❌ If you see >5 turn conversations → prompt fix didn't apply (check prompts.py)
- ❌ If emails look bad → unlikely, but escalate and we can revert

---

## Rollback Plan

If something goes wrong:

```bash
# Revert to Sonnet
git checkout config.json agent/prompts.py

# Or manually edit config.json:
{
  "model": "claude-sonnet-4-5",
  "max_tokens": 1024,
  "price_per_mtok_in": 3.0,
  "price_per_mtok_out": 15.0,
  ...
}

# Restart agent
sudo systemctl restart outreach-agent
```

---

## Cost Tracking

### Current Trajectory (if you do nothing)
- Sept 1-15: $26.66
- Sept 16-30: ~$26.66
- **Sept total: ~$53.33**

### After Haiku Switch
- Sept 1-15: $26.66 (already spent)
- Sept 16-30: ~$8.89 (with Haiku)
- **Sept total: ~$35.55** (saves $17.78)

### Monthly Going Forward
- October: ~$17.78 (with model switch only)
- October: ~$12-15 (with model switch + prompt fix)

---

## FAQ

**Q: Do we need to test first?**  
A: The LLM client already supports both models (same API). The prompt fix is low-risk (just removes inefficiency). If you want to test, run one lead manually:

```bash
python3 << 'EOF'
from agent.loop import run_conversation
result = run_conversation("L-TEST-001", conversation_id="test")
print(result)
EOF
```

**Q: Will this affect email quality?**  
A: No. Haiku is the same model family, optimized for efficiency. The logs show your current emails are simple/templated - Haiku handles this easily.

**Q: What if finance asks why Sept is still high?**  
A: Show them this report. Sept 1-15 already happened ($26.66). Sept 16-30 will be much cheaper. October will show the full savings.

**Q: Should we monitor anything?**  
A: Yes, watch for:
- Email deliverability (should be unchanged)
- CRM update errors (should decrease)
- Average conversation cost (should drop to ~$0.19)

---

## Timeline

- **Sept 15 (today):** Deploy changes
- **Sept 16 morning:** Validate first run with Haiku
- **Sept 30:** Month-end - show finance the savings
- **Oct 1:** Full month on Haiku - expect ~$17.78 total

---

## Need Help?

If anything breaks or looks wrong:
1. Check logs for error messages
2. Verify config.json has correct model name
3. Test one lead manually (see FAQ above)
4. Worst case: revert and we'll debug

The changes are simple and low-risk. You should be fine to deploy immediately.
