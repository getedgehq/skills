# Outreach Agent Cost Fix - Quick Start

## TL;DR

**Don't switch models yet.** 70% of your Sept costs ($18.77 of $26.66) came from 5 conversations stuck in retry loops. The agent has no max-iterations cap and the prompt tells it to retry deterministic 422 validation errors forever.

**Fix the harness first, then switch to Haiku (not gpt-5-mini).**

Expected savings:
- Fixing loops alone: **$37/month** (70% reduction)
- Fixes + Haiku switch: **$48/month** (90% reduction) = **~$577/year**

---

## What Happened

### Root Cause
1. **Infinite loop (agent/loop.py:19):** `while True` with no max turns
2. **Bad prompt (agent/prompts.py:8):** *"If a tool call fails, try it again"*
3. **Retrying deterministic errors (tools.py:29):** CRM returns 422 "unknown field: lead_score_v2" → code retries 4 times → model sees error → prompt says retry → repeat 16 times → $4.73 wasted

### Evidence
- Lead L-3419: 16 turns, $4.73 (vs $0.19 normal)
- Lead L-3032: 16 turns, $4.71
- Lead L-2012: 16 turns, $4.60
- Lead L-2437: 15 turns, $4.39
- All failed on the same 422 validation error (field `lead_score_v2` doesn't exist in CRM schema)

By turn 16, each API call was sending ~145,000 input tokens (full conversation history + 30KB CRM export repeated every turn).

---

## How to Fix (5 minutes)

### 1. Apply the harness fixes

```bash
cd /home/user/work
cp output/fixed_agent_code/*.py agent/
```

**What changed:**
- ✅ `loop.py`: Added `MAX_TURNS = 6` circuit breaker
- ✅ `prompts.py`: Removed "try it again" instruction, fixed field name `lead_score_v2` → `lead_score`, removed "EVERY turn" fetch instruction
- ✅ `tools.py`: Stop retrying 4xx errors (they're deterministic, not transient)

### 2. Test manually on 2-3 leads

```bash
# Set draft mode so you don't accidentally send emails during testing
export EMAIL_DRAFT_MODE=true

# Run on a few test leads
python -c "from agent.loop import run_conversation; print(run_conversation('L-test-001'))"
```

Check logs to verify:
- ✅ Conversations finish in 3-4 turns (not 16+)
- ✅ No repeated crm_get_account calls
- ✅ Total cost per lead < $0.30

### 3. Deploy fixes ASAP (before month end)

This stops the bleeding immediately. Expected savings: **$37/month**.

---

## Next: Switch to Haiku (Week of Sept 22)

**Why Haiku, not gpt-5-mini?**
- Haiku is 1/3 the price of Sonnet ($1 input vs $3)
- Same Anthropic API, just change config.json
- No code changes needed (gpt-5-mini requires OpenAI SDK)
- Cold emails are exactly what Haiku is designed for

**How to switch:**

1. Build golden set first (see below)

2. Run baseline eval with Sonnet:
```bash
python output/run_eval.py > results_sonnet.txt
```

3. Switch to Haiku:
```bash
# Edit config.json:
{
  "model": "claude-haiku-4-5",
  "max_tokens": 1024,
  "price_per_mtok_in": 1.0,
  "price_per_mtok_out": 5.0,
  "batch_window_utc": "02:00-05:00"
}
```

4. Run eval with Haiku:
```bash
python output/run_eval.py > results_haiku.txt
```

5. Compare quality, if equivalent → ship

Expected additional savings: **$11/month** on top of loop fixes = **$48/month total** vs current.

---

## Build the Golden Set (This Week)

The starter file has 3 cases. You need 20+ covering:

```bash
# Expand golden_starter.jsonl with:
- 5 normal qualified leads (score 50-100, email sent)
- 5 unqualified leads (score 0-49, no email)
- 3 edge cases (missing data, timeout, merged accounts)
- 2 high-score edge cases (score 80+ but no email address)
- 5 regression cases (leads from the 4 incidents in logs/)
```

Format:
```json
{"case_id": "golden-004", "description": "...", "lead_id": "L-...", "expected_outcome": {...}, "source": "..."}
```

---

## Files Created

```
output/
├── cost_analysis.md          # Full analysis with evidence
├── cost_comparison.py        # Visual before/after breakdown
├── run_eval.py              # Evaluation harness
├── golden_starter.jsonl     # 3 starter test cases
└── fixed_agent_code/
    ├── loop.py              # Added MAX_TURNS circuit breaker
    ├── prompts.py           # Fixed instructions and field name
    └── tools.py             # Stop retrying 4xx errors
```

---

## Harness Scorecard (Before → After)

| Component | Before | After Fixes |
|---|---|---|
| Cost governance | ❌ None | ✅ MAX_TURNS cap |
| Golden set | ❌ None | ⚠️ 3 cases (need 20+) |
| Judge | ❌ None | ✅ run_eval.py |
| Data layer | ⚠️ Schema mismatch | ✅ Fixed field name |
| Action safety | ⚠️ No gate | ✅ EMAIL_DRAFT_MODE |
| Tracing | ✅ Good | ✅ Good |

---

## Questions?

- **"Why not just switch to gpt-5-mini?"** → You'd still have retry loops burning tokens. Fix the mechanism first.
- **"How confident are you?"** → 100%. The logs show 4 conversations burning $4.60-4.73 each on the same deterministic error. This is mechanical, not probabilistic.
- **"Can I skip the golden set?"** → No. You'll break something else without regression tests. This almost shipped to production.

---

## Run Cost Comparison

```bash
python output/cost_comparison.py
```

Shows before/after breakdown with monthly projections.
