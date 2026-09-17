# FinBot Incident Analysis: Q2 Revenue Discrepancy
**Date:** 2026-09-15  
**Analyst:** AI Assistant  
**For:** Daniel Kurz (CEO)

## Executive Summary

**Don't switch models yet.** The model did exactly what it was told - it faithfully queried the wrong table. This is a data layer problem, not a model problem.

**Root Cause:** FinBot used the `orders` table instead of `revenue_recognized`, counting $4.1M in gross orders (including $550K in cancelled/refunded transactions) instead of $3.6M in net recognized revenue.

**The model didn't hallucinate** - it returned exactly what the database said. The database has two tables with different revenue definitions, and nothing in the system tells the bot which one is correct for "revenue."

## The Numbers

| Metric | Amount | Source |
|--------|--------|--------|
| **FinBot's answer** | $4,138,212 | `orders` table (all statuses) |
| **Finance close** | $3,638,336 | `revenue_recognized` table (net) |
| **Discrepancy** | $499,876 | Cancelled + refunded orders included |

### What FinBot Counted (Q2 2026 orders table)
- Completed orders: $3,269,511
- Partially refunded: $318,719
- **❌ Cancelled orders: $360,039** (should not count)
- **❌ Fully refunded: $189,943** (should not count)
- **Total: $4,138,212** ← This went to the board

### What Finance Counted (Q2 2026 revenue_recognized table)
- Net revenue (gross - refunds): **$3,638,336** ← The correct number

## Evidence

### The Transcript
From `transcripts/2026-09-11_board-deck.md`:

```
Priya: @finbot what was our Q2 2026 revenue?

finbot: > SELECT SUM(amount) FROM orders 
        > WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30'
Q2 2026 revenue was $4,138,212.16 (~$4.1M)
```

### Verification in the Warehouse
```python
# What finbot ran
SELECT SUM(amount) FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30'
→ $4,138,212  # includes cancelled and refunded

# What it should have run
SELECT SUM(net_amount) FROM revenue_recognized 
WHERE period IN ('2026-04', '2026-05', '2026-06')  
→ $3,638,336  # net recognized revenue (matches finance)
```

### The Problem: Two "Revenue" Tables

The warehouse has:
1. **`orders`** - gross order amounts (includes cancelled/refunded)
2. **`revenue_recognized`** - GAAP net revenue (what finance reports)

The prompt says "use the run_sql tool" and lists both tables, but never says:
- Revenue questions should use `revenue_recognized`, not `orders`
- The `orders` table is gross/dirty data
- Which table is authoritative for which metrics

## Root Cause Mechanism

**File:** `agent.py:32` - the tool loop  
**File:** `prompt.md:8-13` - the system prompt lists tables but no definitions

The bot:
1. Saw "revenue" in the question
2. Saw `orders.amount` looks revenue-ish  
3. Wrote a reasonable SQL query
4. Returned the wrong number faithfully

The model worked correctly. **The harness failed** - there's no data dictionary, no validation that revenue must come from `revenue_recognized`, and no golden set to catch this before it shipped.

## Harness Scorecard

| Component | Status | Evidence |
|-----------|--------|----------|
| **Golden set** | ❌ Missing | No test cases, no regression suite |
| **Judge** | ❌ Missing | No automated checks on outputs |
| **Cost governance** | ❌ Missing | Infinite `while True` loop, no max iterations, no per-run cap |
| **Data layer** | ❌ Missing | No data dictionary defining what "revenue" means, no query validation |
| **Action safety** | ⚠️ Partial | Tool has write access (`conn.commit()` on line 20), but read-only queries only so far |
| **Tracing** | ❌ Missing | No logging of questions, SQL, results, tokens, or costs |

### Critical Gaps

1. **No data dictionary** - "Revenue" is ambiguous (orders vs revenue_recognized)
2. **No golden set** - This error would have been caught by a single test case
3. **No iteration limit** - Loop could run forever burning tokens
4. **Write access on read path** - `conn.commit()` on line 20 means SQL injection could write data
5. **No tracing** - Can't audit what questions were asked or what SQL ran

## What I Built

### 1. Data Dictionary (`output/data_dictionary.md`)
Defines every metric the bot can report:
- **Revenue** = `revenue_recognized.net_amount` (NOT `orders.amount`)
- Shows correct vs incorrect queries
- Documents all tables and their purposes

### 2. Golden Set (`output/golden.jsonl`)
4 test cases including:
- Q2 2026 revenue (the incident): expects $3,638,336 from `revenue_recognized`
- Q1 2026 revenue: expects $3,285,494
- Q2 order count: 1,907 orders
- Total customers: 420

### 3. Judge Script (`output/judge.py`)
Automated test runner:
- Runs each golden case
- Extracts numbers from bot responses
- Checks against expected values
- Reports pass/fail

### 4. Fixed Prompt (`output/prompt_fixed.md`)
Updated system prompt that:
- Links to the data dictionary
- Explicitly says revenue = `revenue_recognized.net_amount`
- Warns not to use `orders.amount` for revenue

### 5. Fixed Agent (`output/agent_fixed.py`)
Safety improvements:
- Max 5 iterations (prevents runaway loops)
- Read-only database connection (prevents writes)
- Better error handling
- Logs all SQL queries (for future tracing)

## Cost Savings from Fixes

The iteration limit alone prevents runaway token burn. Example: if a bot gets stuck in a retry loop:
- Without limit: 50+ iterations × 1000 tokens = 50K+ tokens (~$1.50 per stuck run)
- With limit: max 5 iterations × 1000 tokens = 5K tokens (~$0.15 cap)

**Estimated savings:** 90% reduction in worst-case costs, plus elimination of $500K revenue errors.

## What Should Happen Next

### Immediate (before next board deck)
1. ✅ **Update the prompt** with the data dictionary (use `output/prompt_fixed.md`)
2. ✅ **Deploy the fixed agent** with iteration limits and read-only DB
3. ✅ **Run the golden set** to verify the fix (`python output/judge.py`)
4. ✅ **Manual verification:** Ask finbot "what was Q2 2026 revenue" and confirm $3.6M

### This week
5. **Add tracing** - log every question, SQL query, result, and token count to a file or DB
6. **Expand golden set** - add 15-20 more cases from real Slack history
7. **CI integration** - run judge.py on every prompt or code change

### This month
8. **Audit write access** - confirm no SQL injection risk, consider parameterized queries
9. **Cost caps** - add per-user and per-run token limits
10. **Data governance** - make `revenue_recognized` the single source of truth, deprecate `orders.amount` for revenue queries

## Recommendation

**Do NOT switch models.** Claude Sonnet 4.5 is not the problem. The agent has:
- No definition of what "revenue" means
- No tests to catch wrong answers
- No safety limits

Switching to GPT-6 or Opus would give you a more expensive bot with the same $500K error.

**Fix the harness first:** Deploy the updated prompt and agent, run the golden set, and confirm it returns $3.6M for Q2 revenue. Then evaluate if you need a different model (you probably don't).

## Blocking Risk

⚠️ **Write access on a read path** (`agent.py:20` - `conn.commit()`)

While the bot currently only runs SELECT queries, the database connection has write permissions. If someone asks "delete all test orders" or a SQL injection occurs, the bot could modify the warehouse.

**Fix:** Use a read-only connection. Changed in `output/agent_fixed.py` line 18.

---

**Files delivered:**
- `output/ANALYSIS.md` (this file)
- `output/data_dictionary.md` - metric definitions
- `output/golden.jsonl` - test cases
- `output/judge.py` - automated test runner
- `output/prompt_fixed.md` - updated system prompt
- `output/agent_fixed.py` - safety fixes

**Ready for Daniel's review tomorrow morning.**
