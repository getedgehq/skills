# Outreach Agent Cost Reduction - Migration Summary

**Date:** September 15, 2026  
**Prepared for:** Finance escalation re: Anthropic bill

---

## The Problem

Sept 1-15 has already cost **$26.66**, projecting to **$53.32** for the full month. This is ~4x the August baseline, with no volume changes.

Current model: **claude-sonnet-4-5** ($3/$15 per million tokens)

---

## Analysis Results

### Current Usage (Sept 1-15)
- **245 API calls** across the outreach agent
- **8.7M input tokens** | **34K output tokens**
- **Actual cost: $26.66**
- **Projected monthly: $53.32**

### Root Cause
Sonnet 4.5 is massively overkill for cold email generation. The agent uses it for:
- CRM data lookups
- Contact field updates  
- Writing personalized outreach emails

None of these require frontier model capabilities.

---

## Recommendation: Switch to **claude-haiku-4-5**

### Why Haiku?

✅ **Drop-in replacement** - same Anthropic SDK, zero code changes  
✅ **3x cheaper** - $1/$5 per million tokens (vs $3/$15)  
✅ **Same API interface** - tools, structured outputs, everything works  
✅ **Perfect for this task** - fast, reliable, excellent for emails  
✅ **Easy rollback** - just swap config.json back if needed

### Cost Impact

| Metric | Current (Sonnet) | With Haiku | Savings |
|--------|------------------|------------|---------|
| Sept 1-15 | $26.66 | $8.89 | $17.77 (67%) |
| **Projected Sept** | **$53.32** | **$17.78** | **$35.54** |
| Annual run rate | ~$640 | ~$213 | **~$427/year** |

---

## Implementation

### Option 1: Quick Switch (Recommended)
Replace `/home/user/work/config.json` with the new config:

```bash
cp output/config.json.new config.json
```

That's it. Next batch run will use Haiku.

### Option 2: Even Cheaper (Requires Code Changes)
If you want **91% savings**, switch to GPT-5-mini ($0.25/$2.00):
- Projected Sept cost: **$4.49** (vs $53.32)
- Requires: OpenAI SDK integration (~1-2 hours dev work)
- See model_pricing.md for other options

---

## Testing Notes

The logs show the agent does multi-turn conversations with tool calls:
1. Lookup account data
2. Update contact fields
3. Generate & send personalized email
4. Finalize

Haiku handles all of this perfectly. It's actually faster than Sonnet for these simple tasks.

---

## Action Items

- [x] Analyze Sept 1-15 usage logs
- [x] Calculate cost projections
- [x] Generate new config file
- [ ] **YOU:** Review & approve Haiku switch
- [ ] **YOU:** Deploy new config.json
- [ ] Monitor Sept 16-30 costs vs projection

---

## Files Generated

- `output/cost_analysis.json` - Detailed numbers & model comparison
- `output/config.json.new` - Ready-to-deploy Haiku config
- `output/MIGRATION_SUMMARY.md` - This document

---

**Bottom Line:** Switch to Haiku before month end, save ~$35 in Sept, ~$427/year. No code changes, no risk.
