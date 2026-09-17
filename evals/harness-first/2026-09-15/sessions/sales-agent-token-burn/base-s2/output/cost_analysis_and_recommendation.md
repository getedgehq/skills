# Anthropic Bill Analysis & Model Switch Recommendation

**Date:** September 15, 2026  
**Prepared for:** Finance escalation on Sept 1-15 costs

---

## Executive Summary

**Current situation:**
- Sept 1-15 (half month): **$26.66**
- Projected full month: **$53.33**
- This is ~4x August costs with no volume change ✅ Matches finance report

**Root cause:** The agent is using Claude Sonnet 4.5 ($3/$15 per Mtok) for simple cold email generation, and the prompt has a bug causing massive context bloat.

**Recommendation:** Switch to **Claude Haiku 4.5** immediately
- Drop-in replacement (same Anthropic API, no code changes needed)
- **67% cost savings: $53.33 → $17.78/month**
- **Save ~$35/month ($425/year)**

---

## Cost Breakdown

### Sept 1-15 Usage
- **Total conversations:** 46 leads processed
- **Total API calls:** 245
- **Total input tokens:** 8,718,520 (8.7M)
- **Total output tokens:** 33,859 (34K)
- **Total cost:** $26.66

### The Problem: Context Bloat

**70% of costs come from just 5 conversations** (10.9% of volume) that got stuck in long loops:

| Conversation | Turns | Input Tokens | Cost | Status |
|--------------|-------|--------------|------|--------|
| cv_488aab | 17 | 1,564,200 | $4.73 | ❌ API error (context limit) |
| cv_15f5fe | 17 | 1,558,994 | $4.71 | ❌ API error (context limit) |
| cv_24a92f | 17 | 1,521,943 | $4.60 | ❌ API error (context limit) |
| cv_a99bb9 | 16 | 1,454,091 | $4.39 | ❌ API error (context limit) |
| cv_6f895a | 26 | 100,687 | $0.33 | Completed but inefficient |

**Why this happens:**
1. Prompt tells agent to call `crm_get_account` at the start of EVERY turn
2. Each CRM export is 30-40KB of JSON (contacts, activities, emails, notes)
3. Context grows: Turn 1 = 2K tokens → Turn 17 = 200K+ tokens (API limit!)
4. 4 conversations failed completely after burning ~$4.70 each
5. Average conversation: 5.3 turns (should be 3-4 max for this task)

---

## Model Comparison

Based on Sept 1-15 actual usage (projected to full month):

| Model | Monthly Cost | Savings | Notes |
|-------|--------------|---------|-------|
| **Claude Sonnet 4.5** (current) | **$53.33** | baseline | Overkill for cold emails |
| **Claude Haiku 4.5** ⭐ | **$17.78** | **$35.55/mo** | Same API, drop-in replacement |
| GPT-5 Mini | $4.49 | $48.83/mo | Requires OpenAI SDK rewrite |
| Gemini 2.5 Flash | $5.40 | $47.93/mo | Requires Google SDK rewrite |
| DeepSeek v3.2 | $4.91 | $48.42/mo | Hosted in China |

### Why Claude Haiku 4.5?

✅ **Drop-in replacement** - no code changes, just update config.json  
✅ **Same Anthropic API** - same reliability, same tool use  
✅ **67% cost savings** - $35/month savings with zero dev work  
✅ **Still plenty smart** - cold emails aren't rocket science  
✅ **Can deploy today** - change config, restart agent  

The other options save more (~90%) but require:
- Rewriting the LLM client to use different SDKs
- Testing tool use with different providers
- Risk of quality/reliability issues
- 1-2 days of dev work

---

## What I'm Delivering

### 1. Updated config (output/config.json)
- Switched to `claude-haiku-4-5`
- Updated pricing: $1/$5 per Mtok
- Ready to deploy

### 2. Fixed prompt (output/prompts.py)
- Removed "at the start of EVERY turn" instruction
- Agent now loads CRM data once per conversation
- Should reduce average turns from 5.3 → 3-4
- Eliminates context overflow failures

### 3. This analysis (output/cost_analysis_and_recommendation.md)

---

## Deployment Plan

**Option A: Quick fix (recommended for end-of-month)**
1. Copy `output/config.json` to project root
2. Restart the agent
3. Saves 67% immediately

**Option B: Full fix (do this too, but can wait)**
1. Also update `agent/prompts.py` with the fixed version
2. Eliminates the context bloat bug
3. Will reduce costs further + fix the 4 failing conversations

---

## Expected Savings

**With model switch only:**
- Sept 16-30: Save ~$17 vs current trajectory
- October onward: Save ~$35/month ($425/year)

**With model switch + prompt fix:**
- Eliminate the 70% cost spike from long conversations
- Expect total monthly costs to drop to ~$12-15
- **Total savings: ~75-80% vs current**

---

## Questions?

The logs show this is purely a model-overkill + prompt-bug issue. Volume hasn't changed. Haiku will work fine for "qualify lead, write cold email" - it's the same Anthropic model family, just more efficient.

Want me to deploy this before month-end? I can push the config change now.
