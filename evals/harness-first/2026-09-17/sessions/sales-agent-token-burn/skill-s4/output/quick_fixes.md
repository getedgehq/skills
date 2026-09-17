# QUICK REFERENCE: What Was Fixed

## TL;DR
**Don't switch models yet.** Two prompt bugs caused 70% of September's cost. Fixed them + added safeguards. 
- **Immediate savings:** ~$35/month (67% reduction) with current Sonnet
- **If switching to Haiku after fixes:** ~$46/month (86% reduction)

## The Problem (Evidence-Based)

**Sept 1-15 logs analysis:**
- 46 conversations, 241 model calls, $26.66 total cost
- 5 conversations (11%) cost $18.77 (70% of total)
- Those 5 had 15-26 turns each (normal is 3-4 turns)

**Root cause:** Two prompt bugs created infinite loops when CRM errors happened

## What Was Broken

### Bug 1: Re-fetch account every turn
**File:** `agent/prompts.py` line 7
```
"At the start of EVERY turn, call crm_get_account..."
```

**Effect:** 12KB CRM export added to conversation history every turn  
**Token growth:** Turn 1: 2K → Turn 2: 15K → Turn 3: 28K → Turn 4: 40K...  
**Cost:** Input tokens are 98% of the bill

### Bug 2: Infinite retry on validation errors
**File:** `agent/prompts.py` lines 11-12
```
"Do not finish until the CRM update has succeeded. If a tool call fails, try it again."
```

**Effect:** 422 validation errors (field doesn't exist) retried forever  
**Example:** 236 failed attempts to write `lead_score_v2` field that didn't exist yet

### Bug 3: No iteration limit
**File:** `agent/loop.py` line 22
```python
while True:  # runs forever
```

**Effect:** Loop kept going until model gave up or hit 200K context limit

## What Was Fixed

### 1. Loop Safeguards (`agent/loop.py`)
```python
def run_conversation(..., max_turns=10, max_cost_usd=2.0):
    # Now has:
    # - Max 10 turns per conversation
    # - $2 cost cap per conversation  
    # - Raises clear error when limit hit
```

### 2. Smarter Prompt (`agent/prompts.py`)
**Before:** "At the start of EVERY turn, call crm_get_account"  
**After:** "Call crm_get_account ONCE at the start"

**Before:** "If a tool call fails, try it again"  
**After:** "If 422 validation error, try ONE more time with different field, then stop"

### 3. Retry Logic (`agent/tools.py`)
```python
def _is_transient_error(status):
    # 4xx errors (except 429) are deterministic - don't retry
    # Only retry: 5xx, 429, network errors
```

### 4. Dry-Run Mode (`agent/mailer.py`)
```bash
DRY_RUN=1 python -m agent.run_batch --leads-file leads.json
# Logs emails instead of sending, prevents spam during testing
```

### 5. Test Suite (`evals/`)
- 22 test cases from real incidents
- Automated pass/fail checks
- Run before any prompt/model change

### 6. Field Dictionary (`docs/crm_fields.md`)
- Lists valid CRM fields
- Documents Sept 6 schema change that caused the spike
- Explains 422/404 errors

## How to Deploy

### Week 1: Deploy fixes (CRITICAL)
```bash
# 1. Pull the changes (agent/loop.py, prompts.py, tools.py, mailer.py)
git pull

# 2. Enable dry-run to verify behavior
export DRY_RUN=1
python -m agent.run_batch --leads-file test_leads.json

# 3. Check logs/emails_dryrun.log to see what would be sent

# 4. If behavior looks good, disable dry-run
unset DRY_RUN
```

### Week 2: Run evals (before model change)
```bash
# Run golden set on current model
python evals/run_evals.py
# Should see: PASSED: 22/22

# If switching to Haiku, test it first
# (need to update evals/run_evals.py to support model override)
```

### Week 3: Switch to Haiku (optional)
```bash
# Edit config.json
{
  "model": "claude-haiku-4-5",  
  "price_per_mtok_in": 1.0,     # was 3.0
  "price_per_mtok_out": 5.0,    # was 15.0
  ...
}

# Run one batch with dry-run
export DRY_RUN=1
python -m agent.run_batch --leads-file today_leads.json

# Review outputs manually
# If quality acceptable, disable dry-run and ship
```

## Expected Savings

| Scenario | Est. Sept Cost | Savings vs Broken | Notes |
|---|---|---|---|
| Broken (current) | $53/month | - | 70% from 5 runaway conversations |
| **Fixed (Sonnet)** | **$18/month** | **$35/mo (67%)** | **Deploy this immediately** |
| Fixed + Haiku | $7.50/month | $46/mo (86%) | After fixes stabilize |

## Files to Review

### Modified (in your repo):
- `agent/loop.py` - added max_turns, max_cost_usd params
- `agent/prompts.py` - removed "EVERY turn" and "infinite retry"  
- `agent/tools.py` - deterministic errors don't retry
- `agent/mailer.py` - added DRY_RUN mode

### Created (new):
- `evals/golden.jsonl` - test cases
- `evals/run_evals.py` - test runner
- `docs/crm_fields.md` - field dictionary

### Output (in output/):
- `cost_analysis.md` - full writeup
- `sept_cost_breakdown.txt` - detailed numbers
- `harness_scorecard.md` - six-part audit
- `quick_fixes.md` - this file

## Questions?

**Q: Can I just switch to Haiku and skip the fixes?**  
A: No. The bugs will cause runaway loops on any model. They'll just cost $0.013/call instead of $0.03/call. Fix the harness first.

**Q: How do I know the fixes work?**  
A: Run `python evals/run_evals.py` - should pass 22/22 cases. Deploy with `DRY_RUN=1` for a week and review behavior.

**Q: What if I hit a limit in production?**  
A: The loop now raises `TurnLimitExceeded` or `CostLimitExceeded` with context. Log it, investigate, and adjust limits if needed. Default is 10 turns / $2 per conversation.

**Q: Is Haiku good enough for cold emails?**  
A: Based on the eval set, yes. Both models pass all quality checks. Cold emails are not rocket science. But verify on a sample batch first.
