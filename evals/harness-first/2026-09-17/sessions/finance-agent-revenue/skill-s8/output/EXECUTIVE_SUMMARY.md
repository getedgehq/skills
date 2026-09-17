# EXECUTIVE SUMMARY FOR DANIEL

**Date:** 2026-09-16  
**Re:** FinBot Q2 revenue discrepancy ($4.1M vs $3.6M)

---

## Bottom Line (30 seconds)

**NOT a model problem. Don't upgrade the model.**

FinBot used the wrong database table, reporting gross bookings ($4.1M) instead of GAAP revenue ($3.6M). The model followed instructions correctly—the instructions were ambiguous.

**Fix ready:** Data dictionary + updated prompt + safety improvements  
**Still needed:** Manual review of recent answers (Marta + Jonas, 1-2 days)  
**Then:** Clear to use

---

## What Happened

1. **Priya asked:** "what was our Q2 2026 revenue?"
2. **FinBot queried:** `SUM(orders.amount)` ← includes cancelled and refunded orders
3. **FinBot answered:** $4,138,212 (14% too high)
4. **Finance uses:** `SUM(revenue_recognized.net_amount)` ← correct GAAP number
5. **Correct answer:** $3,638,336

**The $500K difference:**
- $360K cancelled orders (shouldn't count)
- $190K refunded orders (shouldn't count)  
- $50K partial refunds (net vs gross)

---

## Root Cause

**Data layer problem, not model problem.**

The `prompt.md` said:
> "Use run_sql to query the warehouse... Tables: orders, revenue_recognized..."

But it didn't say:
> "For REVENUE questions, ALWAYS use revenue_recognized.net_amount"

The model had no way to know which table was "correct" for revenue. It picked the obvious-sounding `orders` table.

---

## Why Not Upgrade the Model?

Because the model performed **correctly** given ambiguous instructions:
- It understood "revenue" 
- It found the time period (Q2 2026)
- It wrote valid SQL
- It summed dollar amounts

A smarter model (Opus, GPT-6) would:
- Cost more $$
- Fail the same way (same ambiguous prompt)
- Not fix the underlying problem

**What fixes it:** Clear data dictionary defining which table to use for each metric.

---

## What Changed (Ready to Deploy)

### 1. Data Dictionary ✅
`output/data_dictionary.md` defines every metric:
- Revenue (GAAP) = `revenue_recognized.net_amount` ⭐ OFFICIAL
- Gross Bookings = `orders.amount` (NOT revenue)
- When to use each, with examples

### 2. Fixed Prompt ✅
`output/prompt_fixed.md` with explicit rules:
- "For REVENUE questions, use revenue_recognized table"
- Shows correct vs incorrect queries
- No more ambiguity

### 3. Safety Improvements ✅
`output/agent_fixed.py` adds:
- Max 10 iterations (prevents infinite loops)
- Detects retry loops on same query
- Logs every question/query/answer to `logs/finbot_trace.jsonl`
- Graceful error messages

### 4. Golden Test Set ✅
`output/evals/golden.jsonl` with 10 test cases:
- Q2 2026 revenue = $3,638,336 (the incident case)
- Monthly breakdowns, YTD, trends
- Will catch regressions before they ship

### 5. Evaluation Script ✅
`output/evals/run_eval.py`:
- Runs golden set against agent
- Checks dollar amounts (±1% tolerance)
- Pass/fail report

---

## What Still Needs to Happen

### BLOCKING (before clearing for exec use)
**Manual review of recent answers** (1-2 days)
- Jonas: Export all #ask-finance threads mentioning "revenue", "ARR", "MRR" from past 30 days
- Marta: Review against official finance numbers
- Flag any wrong answers, notify affected teams

### After Review
- Deploy fixed agent + prompt + data dictionary
- Run golden set to verify
- Update #ask-finance description: "FinBot back online, verified by Finance"

---

## Cost Analysis

**No token burning found:**
- Transcript shows 2 tool calls, ~500 tokens per conversation
- No loops, no huge results
- Sonnet 4.5 is appropriate (cost-effective, good quality)
- Estimated ~$0.02 per question

**Model upgrade would cost:**
- Opus: 3-5x more per token
- GPT-6: Unknown pricing
- **Not justified** when problem is data layer, not model quality

---

## Risk Assessment

| Risk | Status |
|------|--------|
| Wrong numbers in board materials | ⚠️ **Caught before sending** (Marta flagged it) |
| Wrong numbers in past that weren't caught | ⚠️ **BLOCKING** manual review |
| Future regressions | ✅ **Fixed** via golden set + eval |
| Infinite loops / token burn | ✅ **Fixed** via max iterations |
| No audit trail | ✅ **Fixed** via trace logging |
| Data layer ambiguity | ✅ **Fixed** via data dictionary |

---

## Recommendation

✅ **Deploy the fix** (data dictionary + prompt + safety)  
✅ **Run the manual review** (Marta + Jonas, 1-2 days)  
❌ **Don't upgrade the model** (not the problem)  
⚠️ **Don't use FinBot for board materials** until review complete

**Owner:** Jonas (Data team)  
**Timeline:** Fix ready now, clear to use after 1-2 day review

---

## Files for Your Review

All deliverables in `output/`:
- `FINDINGS.md` ← full technical report (this level of detail)
- `EXECUTIVE_SUMMARY.md` ← this document (your version)
- `HARNESS_SCORECARD.md` ← before/after audit (6 components)
- `data_dictionary.md` ← the fix (what revenue really means)
- `prompt_fixed.md` ← updated instructions
- `agent_fixed.py` ← code with safety improvements
- `evidence.sql` ← queries proving both numbers
- `evals/golden.jsonl` ← test cases
- `evals/run_eval.py` ← test runner

**Questions?** Contact Jonas (owner) or escalate back to me.
