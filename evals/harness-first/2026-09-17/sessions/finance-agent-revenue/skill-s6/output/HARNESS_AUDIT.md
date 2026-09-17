# FinBot Harness Audit

Following the *Harness First* methodology to assess FinBot's reliability infrastructure.

## Overall Assessment: 🔴 CRITICAL GAPS

**Summary:** FinBot has NO harness. It's a model with a tool, no validation, no tracing, and dangerous permissions. The Q2 revenue error was inevitable.

---

## 1. Golden Set: ❌ MISSING

**Present means:** ~20+ cases with expected answers/constraints, drawn from real traffic, incidents, and edge cases.

**Status:** Missing entirely

**Evidence:**
- No `evals/` directory
- No test files
- No recorded expected answers

**Impact on Q2 incident:**
- The wrong-table error would have been caught immediately by a golden set including "Q2 revenue = $3.6M from revenue_recognized"
- No regression testing when prompt or model changes

**What exists:**
- 1 exported transcript (`transcripts/2026-09-11_board-deck.md`)
- Slack thread mention of the bot being "in use since March"
- No systematic collection of questions + correct answers

---

## 2. Judge: ❌ MISSING

**Present means:** Deterministic checks first (numbers, policy rules, forbidden content), LLM-rubric only for what code can't check; runs on every prompt/model/tool change.

**Status:** Missing entirely

**Evidence:**
- No eval script
- No CI/CD checks before deployment
- No automated comparison of outputs

**Impact on Q2 incident:**
- Prompt changes could be (and likely were) deployed without checking if they break existing queries
- No way to know if a model upgrade would improve or degrade answers

---

## 3. Cost Governance: 🔴 CRITICAL: NO LIMITS

**Present means:** Hard token/cost caps per user and per workflow, max iterations per run, graceful stop with a message.

**Status:** DANGEROUS - Infinite loop, no caps

**Evidence from `agent.py`:**
```python
while True:  # ← No max_iterations
    resp = chat(model=config.MODEL, system=system, messages=messages, tools=TOOLS, ...)
    # ... no token counting
    # ... no cost tracking
    # ... no iteration counter
```

**Risks:**
- **Token burn:** A syntax error in generated SQL causes infinite retry loop
- **No budget cap:** Single question could spend unlimited tokens
- **Deterministic retry:** `except Exception as e: out = {"error": str(e)}` sends errors back to model, which may retry the same bad query forever

**Max rows present:** `MAX_ROWS = 200` limits returned rows (partial mitigation)

**What's missing:**
- `max_iterations` (recommend: 5)
- Per-run token/cost cap
- Circuit breaker for repeated identical errors

---

## 4. Data Layer: ⚠️ PARTIAL / BROKEN

**Present means:** Read-only credentials for reads, a data dictionary that defines each metric/field the agent may use.

**Status:** Partially present but fundamentally broken

### Schema Documentation: ❌ Missing
No data dictionary. The prompt lists table names:
```markdown
Tables you can use:
- customers
- orders
- refunds
- revenue_recognized
- daily_kpis
```

But provides ZERO guidance on:
- When to use `orders` vs `revenue_recognized` for "revenue"
- What each table represents (operational vs financial)
- What "revenue" means (bookings, recognized, collected)

### Database Access: 🔴 UNSAFE - WRITE PERMISSIONS

From `agent.py` line 20-21:
```python
cur = conn.execute(query)  # ← executes whatever SQL the model generates
conn.commit()              # ← commits writes!
```

**CRITICAL SAFETY ISSUE:**
- Bot has WRITE access to the warehouse
- `run_sql` tool description says "Run a SQL query" (no mention of read-only)
- Model could generate `DELETE`, `UPDATE`, `DROP TABLE`, etc.
- `conn.commit()` on a SELECT query is unnecessary and signals write capability

**Proper config:**
- Use read-only SQLite connection: `uri=file:warehouse.db?mode=ro`
- Or: separate read-replica with read-only credentials
- Tool description should say "Run a **read-only** SQL query"

### Metric Definitions: ❌ Missing

The warehouse has multiple conflicting revenue numbers:

| Source | Q2 2026 Value | Meaning |
|--------|--------------|---------|
| `orders.amount` | $4.1M | Gross bookings (incl. cancelled/refunded) |
| `revenue_recognized.net_amount` | $3.6M | GAAP recognized revenue |
| `daily_kpis.revenue` | (incomplete) | Unknown definition, data only through May |

**No document defines which to use when.** This is why the incident happened.

---

## 5. Action Safety: ⚠️ READ PATH, BUT WRITE-CAPABLE

**Present means:** Irreversible or external actions (send, pay, delete, write, refund) are reversible or gated by human approval.

**Status:** No side-effecting tools defined, but write access present

**Current tools:**
- `run_sql` - intended as read-only, but has write capability (see Data Layer)

**Risks:**
- If model generates `DELETE FROM orders`, it will execute
- No approval workflow for "high-stakes" answers (e.g., board materials)
- Results copy-pasted directly into external documents without review flag

**Recommendations:**
- Remove write permissions (blocking)
- Add "draft mode" for questions tagged as high-stakes
- Log all queries for audit (currently not logged)

---

## 6. Tracing: ❌ MISSING

**Present means:** Every model and tool call logged with conversation id, workflow, input, output, tokens, cost, latency, error.

**Status:** No logging whatsoever

**Evidence:**
- No log files in repo
- `agent.py` has no logging statements
- No way to reconstruct what queries were run or what they cost

**What's missing:**
- Conversation ID (to link multi-turn threads)
- Timestamp
- User ID (who asked)
- Input question
- Generated SQL
- Query result (or result size)
- Model tokens (prompt + completion)
- Model cost
- Latency (model call + DB query)
- Error tracking

**Impact on Q2 incident:**
- Only have 1 exported transcript because someone manually saved it
- No systematic record of what FinBot has been asked
- No way to audit for other wrong answers
- No cost analysis (don't know if model is expensive or cheap)

**Recommendation:**
- Log every invocation to `logs/YYYY-MM-DD.jsonl`
- Fields: `timestamp, conversation_id, user, question, sql_queries, result_summary, tokens, cost_usd, latency_ms, error`

---

## Scorecard Summary

| Harness Component | Status | Blocker? |
|-------------------|--------|----------|
| **Golden Set** | ❌ Missing | No (but urgent) |
| **Judge** | ❌ Missing | No (but urgent) |
| **Cost Governance** | 🔴 Critical: infinite loop | **YES** |
| **Data Layer** | ⚠️ Broken: write access + no definitions | **YES (safety)** |
| **Action Safety** | ⚠️ Write-capable on read path | **YES (safety)** |
| **Tracing** | ❌ Missing | No (but needed for audit) |

**Overall:** 🔴 FinBot is not production-ready. It has dangerous permissions, no iteration limits, and no validation.

---

## How This Caused the Q2 Incident

1. **No data dictionary** → Model guessed which table meant "revenue"
2. **No golden set** → Error not caught before Priya used the answer
3. **No tracing** → Don't know if other answers are also wrong
4. **No judge** → Prompt/model deployed without regression testing

The model performed correctly given what it knew. The harness failed.

---

## Evidence: What Tests Would Have Caught This

A minimal golden set would include:

```json
{
  "question": "what was our Q2 2026 revenue?",
  "expected_table": "revenue_recognized",
  "expected_column": "net_amount",
  "expected_period_filter": "period IN ('2026-04', '2026-05', '2026-06')",
  "expected_answer_approx": 3638335.79,
  "tolerance_pct": 1.0
}
```

A deterministic judge could check:
- ✓ Did query use `revenue_recognized` table? (not `orders`)
- ✓ Did query use `net_amount` column? (not `amount`)
- ✓ Did query filter by period correctly?
- ✓ Is result within 1% of expected? ($3.6M ± $36k)

This test would **fail** on the current implementation, flagging the issue before it reached the board deck.

---

## Token Burn Analysis

We don't have logs, so this is estimated:

**Current config:**
- Model: `claude-sonnet-4-5`
- Temperature: 0.2
- No max_iterations

**Potential burn scenarios:**

1. **Syntax error loop:**
   - User asks complex question
   - Model generates SQL with syntax error
   - Error sent back: `{"error": "near \"FROM\": syntax error"}`
   - Model retries similar query → same error
   - Loop continues indefinitely
   - **Estimated cost:** Could hit thousands of tokens/dollars on a single question

2. **Large result resent every turn:**
   - Query returns 200 rows (MAX_ROWS limit)
   - Full result re-sent in conversation history every tool turn
   - Multi-turn conversation balloons message history
   - **Mitigation:** MAX_ROWS limits this somewhat, but no context summarization

3. **No caching:**
   - System prompt (`prompt.md`) re-sent every call
   - No prompt caching enabled
   - **Cost:** ~120 tokens per request unnecessarily

**Without logs, we can't prove if these are happening.** But the infinite loop is a critical risk.

---

## Recommended Fixes (Prioritized)

### 🔴 BLOCKING (fix before next use):

1. **Add max_iterations = 5** to the while loop
2. **Switch to read-only DB connection:**
   ```python
   conn = sqlite3.connect(f'file:{config.DB_PATH}?mode=ro', uri=True)
   ```
3. **Remove `conn.commit()`** (unnecessary for SELECT)

### 🟡 URGENT (fix this week):

4. **Create data_dictionary.md** defining:
   - Revenue = `revenue_recognized.net_amount` (GAAP recognized revenue, net of refunds)
   - Bookings = `orders.amount` where status = 'completed' (gross order value)
   - When to use each table

5. **Update prompt.md** to reference data dictionary

6. **Create golden set** with 10 questions from real Slack history:
   - Q1 revenue → expected $X from revenue_recognized
   - Q2 revenue → expected $3,638,335.79 from revenue_recognized
   - July revenue → expected $Y
   - etc.

7. **Add basic tracing:**
   ```python
   import logging
   logging.basicConfig(filename='logs/finbot.jsonl', ...)
   ```

### 🟢 IMPORTANT (next sprint):

8. **Build judge script:**
   ```bash
   python eval.py --golden evals/golden.jsonl --prompt prompt.md
   ```
   - Runs all golden set questions
   - Checks SQL uses correct table/column
   - Checks numeric answers are within tolerance
   - Prints pass/fail report

9. **Add cost tracking:**
   - Parse token counts from llm_client response
   - Log per-question cost
   - Add per-run budget cap (e.g., $1 max)

10. **Audit all Slack uses since March:**
    - Export all FinBot questions from #ask-finance
    - Recompute answers with fixed logic
    - Flag any wrong answers for correction

---

## Model Upgrade Decision

**Should we upgrade from Claude Sonnet 4.5 to Opus or GPT-6?**

### Current Evidence: NO

**Reason:** The incident was caused by harness gaps, not model capability:
- Model understood the question correctly
- Model generated valid SQL correctly  
- Model chose wrong table because prompt doesn't define "revenue"

**Any model would fail the same way** without a data dictionary.

### How to Decide Properly

1. Fix the harness (items 1-7 above)
2. Run golden set on:
   - Current model (Sonnet 4.5)
   - Candidate upgrade (Opus or GPT-6)
3. Compare:
   - Accuracy (% correct on golden set)
   - Cost per query
   - Latency

4. Upgrade only if:
   - Accuracy improvement > 10%
   - Cost increase justified by accuracy gain
   - Current model consistently fails cases that matter

**Prediction:** With data dictionary in prompt, both models will get 100% on golden set. Cost may be the only differentiator.

---

## Conclusion

FinBot's architecture is:
```
[User Question] → [Model + Tool] → [Answer]
                       ↓
                  No validation
                  No limits
                  No logging
                  No definitions
```

This is not a production system. It's a prototype that escaped the lab.

**The Q2 revenue error is not an anomaly—it's the expected outcome of a system with no harness.**

Fix the harness before considering model changes. The model is fine; the system is not.

---

**Audit Date:** 2026-09-16  
**Auditor:** Data Engineering  
**Methodology:** Harness First (expert system reliability audit)  
**Files Examined:**
- `agent.py` (tool loop)
- `config.py` (settings)
- `prompt.md` (system prompt)
- `warehouse.db` (data source)
- `transcripts/` (incident evidence)
- `notes/` (stakeholder discussion)
