# FinBot Incident Analysis - Deliverables

**Date:** 2026-09-15  
**Issue:** FinBot reported Q2 revenue as $4.1M, finance says $3.6M  
**Root Cause:** Bot queried wrong table (orders vs revenue_recognized)  
**Verdict:** NOT a model problem - the harness failed

## Quick Start

```bash
# See the problem demonstrated with real data
python verify.py

# View the full analysis
cat ANALYSIS.md
```

## Files in This Directory

### 📊 Analysis & Evidence
- **`ANALYSIS.md`** - Complete incident report with root cause, evidence, and recommendations
- **`verify.py`** - Demonstrates the exact SQL discrepancy with warehouse data

### 🛠️ Fixes (Ready to Deploy)
- **`prompt_fixed.md`** - Updated system prompt with explicit revenue definition
- **`agent_fixed.py`** - Agent with safety limits (max iterations, read-only DB)

### ✅ Testing Infrastructure  
- **`golden.jsonl`** - 4 test cases including the Q2 revenue incident
- **`judge.py`** - Automated test runner (requires LLM gateway to run)
- **`data_dictionary.md`** - Authoritative metric definitions

## The Problem in 30 Seconds

1. **What happened:** FinBot told the board Q2 revenue was $4.1M
2. **The truth:** Finance closed Q2 at $3.6M
3. **The gap:** $500K in cancelled and refunded orders
4. **Root cause:** Bot queried `orders.amount` (gross) instead of `revenue_recognized.net_amount` (net)
5. **Why:** No data dictionary, no test cases, prompt didn't specify which table for revenue

## The Fix

Replace `prompt.md` with `prompt_fixed.md` which explicitly states:
```
For any question about "revenue":
- Use revenue_recognized table, NOT orders table  
- Sum the net_amount column
```

Deploy `agent_fixed.py` which adds:
- Max 5 iterations (stops runaway loops)
- Read-only database (prevents accidental writes)
- Query logging (for future tracing)

## Harness Scorecard

| Component | Before | After | Notes |
|-----------|--------|-------|-------|
| Golden set | ❌ Missing | ✅ Created | 4 cases in `golden.jsonl` |
| Judge | ❌ Missing | ✅ Created | `judge.py` runs tests |
| Cost governance | ❌ Missing | ✅ Fixed | Max 5 iterations in agent |
| Data layer | ❌ Missing | ✅ Created | `data_dictionary.md` |
| Action safety | ⚠️ Write access | ✅ Fixed | Read-only connection |
| Tracing | ❌ Missing | ⚠️ Partial | Logs queries to stderr |

## Key Numbers

| Metric | Value | Source |
|--------|-------|--------|
| Q2 2026 (wrong) | $4,138,212 | `orders` table - what finbot used |
| Q2 2026 (correct) | $3,638,336 | `revenue_recognized` - what finance uses |
| Discrepancy | $499,876 | Cancelled ($360K) + Refunded ($190K) orders |

## Recommendations

### Immediate (Before Next Board Deck)
1. Deploy `prompt_fixed.md` and `agent_fixed.py`
2. Test manually: ask "what was Q2 2026 revenue?" → should get $3.6M
3. Add note to any existing board decks with the correction

### This Week
4. Expand golden set to 20+ cases from real Slack history
5. Add full tracing (log every question, SQL, result to DB)
6. Run judge.py on every prompt change

### This Month  
7. Make this the template for all internal agents
8. Add per-user and per-run token caps
9. Audit all bots for similar data layer issues

## Do NOT Switch Models

Claude Sonnet 4.5 is not the problem. The bot had:
- No definition of "revenue"
- No test cases to catch errors
- No safety limits

Upgrading to GPT-6 or Opus would cost more and still give wrong answers.

**Fix the harness first, then evaluate models with the golden set.**

---

**For Daniel (CEO):** Read `ANALYSIS.md` - it has everything you need for tomorrow's discussion.

**For Jonas (Data):** Deploy `prompt_fixed.md` and `agent_fixed.py`, then test with verify.py

**For Finance:** The correct Q2 number is $3,638,336 (from revenue_recognized table)
