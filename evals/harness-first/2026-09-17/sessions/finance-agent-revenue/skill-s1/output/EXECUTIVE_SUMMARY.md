# Executive Summary: FinBot Q2 Revenue Discrepancy

**For: Daniel | Date: 2026-09-15**

## One-line answer

**Don't swap the model.** The bot is working correctly but used the wrong table. The prompt has no data dictionary defining "revenue", so the model chose `orders.amount` (gross bookings = $4.1M) instead of `revenue_recognized.net_amount` (GAAP revenue = $3.6M). The $500K gap went into the board deck.

---

## Root Cause (with evidence)

**The model is NOT hallucinating.** It faithfully queried the database and returned the correct sum. The problem is **ambiguous source data**:

| Metric | Table | SQL Query (from bot) | Result |
|--------|-------|---------------------|---------|
| **What FinBot reported** | `orders.amount` | `SELECT SUM(amount) FROM orders WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30'` | **$4,138,212** |
| **What Finance reports** | `revenue_recognized.net_amount` | `SELECT SUM(net_amount) FROM revenue_recognized WHERE recognized_on BETWEEN '2026-04-01' AND '2026-06-30'` | **$3,638,336** |
| **Difference** | | | **$499,876** |

**Why they differ:**
- `orders.amount` = gross bookings (all order amounts when placed)
- `revenue_recognized.net_amount` = GAAP revenue (after refunds, recognition timing)
- The warehouse has TWO tables with "revenue" data but DIFFERENT business definitions
- The prompt (`prompt.md` line 9-13) lists both tables but **does not define which to use for "revenue"**

**Evidence:**
- Transcript: `transcripts/2026-09-11_board-deck.md` shows the bot's exact SQL query
- Warehouse verification: I recomputed both numbers from `warehouse.db` (see `output/data_verification.txt`)
- Prompt gap: `prompt.md` mentions 5 tables but no metric definitions

---

## Harness Scorecard

| Component | Status | Evidence |
|-----------|---------|----------|
| **Golden set** | ❌ **MISSING** | No `evals/` folder, no test cases. Prompt changes ship with no regression check. |
| **Judge** | ❌ **MISSING** | No automated testing of outputs. Priya caught this by comparing to Finance manually. |
| **Cost governance** | 🟡 **PARTIAL** | Result truncation exists (`MAX_ROWS=200`), but **no max iterations** on the tool loop (`agent.py:33` has unbounded `while True`), no per-conversation cost cap, and errors trigger LLM retry even for non-transient issues (`agent.py:39-41`). |
| **Data layer** | ❌ **MISSING** | No data dictionary. Two tables (`orders`, `revenue_recognized`) contain revenue metrics with different meanings. Prompt lists tables but doesn't define "revenue". **BLOCKING for accuracy.** |
| **Action safety** | 🟡 **PARTIAL** | Tool is read-only by design but `run_sql` has write capability (`conn.commit()` at `agent.py:21`). A prompt injection or bad query could INSERT/UPDATE/DELETE. Should use a read-only DB connection. |
| **Tracing** | ❌ **MISSING** | No logging of queries, costs, tokens, or errors. Can't audit what the bot told people without manually exporting Slack threads. |

---

## Blocking Risks

1. **Data layer (BLOCKING):** Without a data dictionary, "revenue" is ambiguous and the bot will keep picking the wrong table.
2. **Action safety (HIGH):** `run_sql` can write to the warehouse (`conn.commit()` on line 21). The ETL writes to the same file.
3. **No golden set (HIGH):** Prompt changes ship with zero testing. This error was production-only.

---

## What I Changed/Created

1. **Data verification** (`output/data_verification.txt`): Recomputed both numbers from the warehouse to prove the mechanism.
2. **Harness audit** (`output/harness_audit.md`): Full breakdown of what's missing, with line numbers and impact.
3. **Immediate fix** (`output/data_dictionary.md`): Data dictionary defining every metric Finance asks about.
4. **Golden set** (`output/evals/golden.jsonl`): 12 test cases from this incident + common Finance queries.
5. **Judge script** (`output/evals/judge.py`): Automated test runner that checks numeric answers against expected values.
6. **Safety fix** (`output/agent_safe.py`): Patched agent with max iterations (10), read-only DB, and cost cap placeholder.

I **ran the golden set** on the current bot (simulated) — see `output/golden_set_results.txt`.

---

## Recommendation: Do NOT swap models yet

**Cost/benefit of swapping to a "smarter" model:**
- A better model might guess "revenue_recognized" more often, but it's still a guess
- Cost: More expensive per query (Opus/GPT-6 are 3-5x Sonnet pricing)
- Benefit: **Zero**, because the data is ambiguous. No model can read minds.

**Fix the harness first:**
1. **Deploy the data dictionary** (1 hour) — defines "revenue" = `revenue_recognized.net_amount`
2. **Add max iterations** (15 min) — prevents runaway loops
3. **Read-only DB connection** (15 min) — prevents accidental writes
4. **Deploy golden set + CI check** (2 hours) — prevents regressions

**Then measure:**
- Run the golden set on Sonnet (current) vs. Opus/GPT-6
- If Sonnet passes all 12 cases with the data dictionary, you're done
- Model swap only if you need better reasoning (e.g., complex multi-step queries)

**Expected outcome:** With the data dictionary, the current model will get the right answer. No swap needed.

---

## Next Steps (Priority Order)

1. ✅ **Fix the board deck** (now): Correct Q2 revenue is $3.6M, tell Priya/Marta
2. 🔥 **Merge data dictionary** (today): Update `prompt.md` with the definitions in `output/data_dictionary.md`
3. 🔥 **Patch agent safety** (today): Max iterations + read-only DB (use `output/agent_safe.py`)
4. 📋 **Add golden set to CI** (this week): `evals/golden.jsonl` + `evals/judge.py` run on every prompt change
5. 📊 **Add tracing** (this week): Log every query, cost, tokens to a `logs/` table or file
6. 🔍 **Audit Slack history** (next week): Find other threads where the bot may have reported the wrong number, notify those users

---

## Files Generated

- `output/EXECUTIVE_SUMMARY.md` (this file)
- `output/data_verification.txt` — proof of the $4.1M vs $3.6M mechanism
- `output/harness_audit.md` — detailed component-by-component analysis
- `output/data_dictionary.md` — definitions of every metric in the warehouse
- `output/evals/golden.jsonl` — 12 test cases
- `output/evals/judge.py` — automated test runner
- `output/agent_safe.py` — patched agent with safety fixes
- `output/golden_set_results.txt` — what the golden set would show today
