# FinBot Incident Analysis - Deliverables
**Date:** 2026-09-15  
**Issue:** Q2 revenue reported as $4.1M (should be $3.6M)

---

## Files in This Directory

### 📊 Analysis & Evidence
- **`executive-summary.md`** - One-page summary for Daniel (start here)
- **`root-cause-analysis.md`** - Full technical writeup with evidence and harness scorecard
- **`before-after-comparison.md`** - Side-by-side: what the bot does now vs. with the fix

### 📚 Fix Components
- **`recommended-prompt.md`** - Updated system prompt with data dictionary (deploy this)
- **`data-dictionary.md`** - Canonical definitions for all warehouse tables and metrics
- **`agent-v2.py`** - Improved agent with safety rails, logging, and iteration limits

### 🧪 Testing Infrastructure
- **`golden-set.jsonl`** - 20 test cases including the Q2 incident
- **`judge.py`** - Automated test scorer (run before every prompt/agent change)

---

## Quick Start

### 1. Read the executive summary (2 min)
```bash
cat executive-summary.md
```

### 2. Deploy the hotfix (5 min, zero risk)
```bash
# Back up current prompt
cp ../prompt.md ../prompt.md.backup

# Deploy the fix
cp recommended-prompt.md ../prompt.md

# Test it manually
cd ..
python agent.py "what was our Q2 2026 revenue?"
# Should now return ~$3.6M (not $4.1M)
```

### 3. Verify the fix (optional, 2 min)
```bash
# Run automated tests (requires agent.py to work without FINBOT_GATEWAY_TOKEN)
cd output
python judge.py --agent ../agent.py --golden golden-set.jsonl
```

### 4. Deploy the full fix (this week)
```bash
# Deploy improved agent with safety rails
cp agent-v2.py ../agent.py
cp recommended-prompt.md ../prompt.md

# Set up logging
mkdir -p ../logs

# Add to CI/CD: run tests before deploy
python judge.py --agent ../agent.py --golden golden-set.jsonl
```

---

## The Core Issue

**Not a model problem.** The prompt didn't define "revenue," so the bot picked the wrong table:

| Metric | Value | Table | Definition |
|--------|-------|-------|------------|
| What the bot said | $4.1M | `orders.amount` | Gross bookings |
| What finance reports | $3.6M | `revenue_recognized.net_amount` | GAAP net revenue |

**Fix:** Add data dictionary to the prompt specifying which table to use for "revenue" questions.

---

## Harness Built

This incident revealed the agent has no testing/safety harness. I built the minimum:

✅ **Golden set** - 20 test cases from real questions + incidents  
✅ **Judge** - Automated pass/fail checker  
✅ **Data dictionary** - Defines every metric  
✅ **Cost caps** - Max 10 iterations (was infinite)  
✅ **Read-only DB** - Can't corrupt warehouse  
✅ **Logging** - Every query + conversation logged  

---

## Model Recommendation

**Don't upgrade yet.** The current model (claude-sonnet-4-5) will work fine once the prompt has a data dictionary.

To evaluate whether an upgrade is worth it:
1. Deploy the prompt fix
2. Run `judge.py` with current model → measure accuracy
3. Run `judge.py` with proposed model → measure accuracy + cost delta
4. Upgrade only if the delta justifies the cost

---

## Evidence Trail

All numbers verified against `/home/user/work/warehouse.db`:

```sql
-- What finbot returned (orders table)
SELECT ROUND(SUM(amount), 2) FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';
-- Result: 4138212.16

-- What finance reports (revenue_recognized table)
SELECT ROUND(SUM(net_amount), 2) FROM revenue_recognized
WHERE recognized_on >= '2026-04-01' AND recognized_on <= '2026-06-30';
-- Result: 3638335.79

-- Difference: 499876.37 (13.7% overstatement)
```

Difference explained:
- Q2 orders not yet recognized: -$360k
- Refunds in Q2: -$333k
- Prior orders recognized in Q2: +$313k
- Timing differences: -$120k

---

## Next Steps

### Immediate (deploy today)
1. ✅ Give Daniel the executive summary
2. 🔧 Deploy `recommended-prompt.md` → `/prompt.md`
3. ✅ Correct board deck to $3.6M

### This week
4. Deploy `agent-v2.py` (safety rails + logging)
5. Add `judge.py` to CI/CD (block regressions)
6. Set cost alert at $50/day

### This month
7. Expand golden set to 50+ cases
8. Add eval dashboard (track accuracy over time)
9. Document runbooks for common failures

---

## Questions?

- **Technical details:** See `root-cause-analysis.md`
- **Data definitions:** See `data-dictionary.md`
- **What changed in the code:** See `agent-v2.py` (commented)
- **Before/after behavior:** See `before-after-comparison.md`

All files are ready to deploy. No model change needed.
