# Harness Audit: FinBot

**Date:** 2026-09-15  
**Auditor:** Investigation following board deck incident (Q2 revenue discrepancy)  
**Agent:** FinBot (Slack finance Q&A bot)  
**Model:** claude-sonnet-4-5

---

## Executive Summary

FinBot is a **hackathon project promoted to production without a harness.** The Q2 revenue incident (reported $4.1M instead of $3.6M) was caused by ambiguous data definitions, not model quality. The harness scorecard shows 3 of 6 components missing, 2 partial, and only 1 present.

**Recommendation:** Fix the data layer and safety issues before considering a model upgrade. Current issues are harness problems, not model capability problems.

---

## Scorecard

| Component | Status | Score |
|-----------|---------|-------|
| Golden set | ❌ Missing | 0/10 |
| Judge | ❌ Missing | 0/10 |
| Cost governance | 🟡 Partial | 4/10 |
| Data layer | ❌ Missing | 0/10 |
| Action safety | 🟡 Partial | 5/10 |
| Tracing | ❌ Missing | 0/10 |
| **TOTAL** | | **9/60** |

---

## 1. Golden Set: ❌ MISSING (0/10)

### Definition
A collection of ~20+ real test cases with expected answers, drawn from production traffic, incidents, and edge cases.

### Status
**Does not exist.**

### Evidence
- No `evals/` folder in the repo
- No test cases in code or docs
- README says "Built in a hackathon in March, been in use since" — no mention of testing
- Priya's query went straight to the board deck with no validation

### Impact
- Prompt changes ship with **zero regression testing**
- The Q2 revenue error was production-only (no pre-deployment catch)
- Unknown how many other queries have returned wrong answers

### What's Missing
1. Test cases covering:
   - Revenue queries (incident source)
   - Multi-period comparisons (Q1 vs Q2)
   - Edge cases (invalid quarters, date ranges)
   - Different metric types (orders, refunds, customers)
2. Expected answers for each case (both exact values and constraints)
3. Source attribution (which Slack thread / incident each case came from)

### Recommendation
- **Created:** `output/evals/golden.jsonl` with 12 test cases
- **Priority:** HIGH (prevents future incidents)
- **Effort:** 2 hours to integrate into CI

---

## 2. Judge: ❌ MISSING (0/10)

### Definition
Automated validation that runs the golden set and checks outputs against expected answers. Runs on every prompt/model/tool change.

### Status
**Does not exist.**

### Evidence
- No test runner in repo
- No CI/CD checks (no `.github/workflows`, no `.gitlab-ci.yml`)
- Manual testing only: Priya asked the bot, copied answer to deck, Finance caught error later

### Impact
- Changes are tested by hand (if at all)
- Regression risk on every change
- No visibility into which queries work/fail

### What's Missing
1. Test runner that:
   - Loads golden set
   - Runs agent on each case
   - Extracts SQL queries and validates table/column usage
   - Extracts numeric answers and validates against expected values
   - Reports pass/fail per case
2. CI integration
3. Deterministic checks before LLM-as-judge (table names, numeric ranges)

### Recommendation
- **Created:** `output/evals/judge.py` (deterministic validation)
- **Priority:** HIGH (blocks safe prompt changes)
- **Effort:** 1 hour to add to CI

---

## 3. Cost Governance: 🟡 PARTIAL (4/10)

### Definition
Hard caps on tokens/cost per user and per workflow, max iterations, graceful failure messages.

### Status
**Partially implemented.** Has result truncation but missing critical controls.

### Evidence

#### ✅ Present:
- **Result truncation:** `config.py` line 3: `MAX_ROWS = 200`
  - Limits SQL results to 200 rows
  - Prevents huge tables from burning tokens in context

#### ❌ Missing:
1. **No max iterations:** `agent.py` line 33: `while True:`
   - Unbounded loop — could run indefinitely
   - If SQL errors cause retry loops, cost spirals
   - **Risk:** Deterministic SQL error → model retries forever → $$$

2. **No per-conversation cost cap:**
   - No `MAX_COST` or budget tracking
   - User could trigger expensive multi-step queries
   - **Risk:** Complex questions burn tokens with no limit

3. **Retry on non-transient errors:** `agent.py` line 39-41:
   ```python
   except Exception as e:  # let the model see the error and retry
       out = {"error": str(e)}
   ```
   - Catches ALL exceptions, lets model retry
   - Syntax errors, missing tables, etc. are not transient
   - **Risk:** Model tries same bad query 10+ times

4. **No graceful degradation:**
   - No message when hitting limits
   - No "query too complex, try simplifying" guidance

### Impact
- **Runaway cost risk:** Unbounded loop could burn hundreds of dollars on one query
- **Poor UX:** Errors silently retry, slow responses, no user feedback

### Recommendation
- **Created:** `output/agent_safe.py` with:
  - `MAX_ITERATIONS = 10`
  - Deterministic error detection (don't retry syntax errors)
  - Cost cap placeholder (needs gateway integration)
  - Graceful failure messages
- **Priority:** HIGH (cost risk)
- **Effort:** 1 hour to deploy

---

## 4. Data Layer: ❌ MISSING (0/10)

### Definition
- Read-only credentials for read-only operations
- Data dictionary defining every metric/field the agent uses
- Canonical metric definitions shared with data producers

### Status
**Does not exist.** This is the root cause of the Q2 revenue incident.

### Evidence

#### ❌ No data dictionary:
- `prompt.md` line 9-13 lists tables but **no metric definitions**:
  ```
  Tables you can use:
  - customers
  - orders
  - refunds
  - revenue_recognized
  - daily_kpis
  ```
- No explanation of what "revenue" means
- Two tables have revenue data with different meanings:
  - `orders.amount` = gross bookings = $4.1M
  - `revenue_recognized.net_amount` = GAAP revenue = $3.6M
- **The model had to guess.** It guessed wrong.

#### ❌ No read-only enforcement:
- `agent.py` line 21: `conn.commit()`
- Database is opened in read-write mode
- Tool could execute `INSERT`, `UPDATE`, `DELETE`
- `warehouse.db` is the **live ETL target** (per `config.py` comment)
- **Risk:** A bad query could corrupt production data

### Impact
- **High-severity incident:** $500K wrong number in board deck
- **Blast radius unknown:** How many other queries returned wrong numbers?
- **Data corruption risk:** Tool can write to the warehouse

### What's Missing
1. **Data dictionary** defining:
   - "Revenue" = `revenue_recognized.net_amount`
   - "Bookings" = `orders.amount`
   - Every other metric users ask about
2. **Read-only DB connection** (SQLite URI mode: `file:warehouse.db?mode=ro`)
3. **Metric ownership:** Finance team should own definitions

### Recommendation
- **Created:** `output/data_dictionary.md` with:
  - Canonical definitions for revenue, bookings, refunds, etc.
  - Table/column mappings
  - Examples of correct queries
  - Ownership (Finance team)
- **Priority:** 🔥 **BLOCKING** (prevents recurrence)
- **Effort:** 1 hour to merge into prompt

---

## 5. Action Safety: 🟡 PARTIAL (5/10)

### Definition
Irreversible actions (send, pay, delete, write) are gated by human approval or run in draft mode.

### Status
**Partially safe.** Tool is read-only by design, but implementation allows writes.

### Evidence

#### ✅ Intent is read-only:
- Tool description: "Run a SQL query... and return the rows"
- No explicit write operations in tool logic
- Use case is answering questions (read-only)

#### ❌ Implementation allows writes:
- `agent.py` line 21: `conn.commit()`
- No SQL query validation (no whitelist/blacklist)
- A model mistake or prompt injection could execute:
  ```sql
  DELETE FROM orders WHERE 1=1;
  ```
- Database is opened in read-write mode

#### ❌ No approval gate:
- Tool executes immediately
- No "are you sure?" for dangerous operations
- No draft mode

### Impact
- **Data corruption risk:** Tool can write to production warehouse
- **Compliance risk:** If warehouse has PII, tool could exfiltrate it
- **Incident history:** No evidence this has happened yet, but it's possible

### Recommendation
- **Created:** `output/agent_safe.py` with:
  - Read-only connection: `file:warehouse.db?mode=ro`
  - Query validation: block INSERT/UPDATE/DELETE/DROP
  - Error message: "Permission denied: this tool is read-only"
- **Priority:** HIGH (data safety)
- **Effort:** 15 minutes to deploy

---

## 6. Tracing: ❌ MISSING (0/10)

### Definition
Every model and tool call logged with:
- Conversation ID
- Workflow/feature
- Input/output
- Tokens, cost, latency
- Errors

### Status
**Does not exist.**

### Evidence
- No logging in `agent.py`
- No logging in `llm_client.py`
- No logs directory
- Only trace is manual Slack exports (e.g., `transcripts/2026-09-11_board-deck.md`)

### Impact
- **No cost visibility:** Can't see which queries are expensive
- **No error tracking:** Can't see which queries fail
- **No audit trail:** Can't see who asked what or what answers were given
- **Slow incident response:** Had to manually export Slack thread to investigate

### What's Missing
1. Structured logging (JSON lines)
2. Fields to log:
   - `timestamp`, `conversation_id`, `user`, `question`
   - `model`, `system_prompt_version`, `tool_calls`
   - `sql_queries`, `sql_results`
   - `final_answer`, `tokens_used`, `cost`, `latency_ms`
   - `error` (if any)
3. Log storage (S3, database, file)
4. Dashboards (cost per week, top queries, error rate)

### Recommendation
- Add logging to `agent.py`:
  ```python
  import logging
  import json
  
  logger = logging.getLogger("finbot")
  logger.info(json.dumps({
      "conversation_id": generate_id(),
      "question": question,
      "queries": queries,
      "answer": answer,
      "cost": cost
  }))
  ```
- Store in `logs/finbot.jsonl`
- **Priority:** MEDIUM (needed for ongoing operations)
- **Effort:** 2 hours

---

## Root Cause of Q2 Revenue Incident

**Mechanism:** Data layer missing → ambiguous metric definition → model guessed wrong table

**Evidence chain:**
1. User asked: "what was our Q2 2026 revenue?"
2. Prompt lists two tables with revenue data but no definitions
3. Model chose `orders.amount` (reasonable guess for "revenue")
4. Query returned $4,138,212.16 (correct sum of orders.amount)
5. User put "$4.1M" in board deck
6. Finance Q2 close is $3,638,335.79 (from `revenue_recognized.net_amount`)
7. $500K gap discovered in pre-read

**This is NOT a model hallucination.** The model:
- Did not make up numbers
- Executed valid SQL
- Returned correct results from the chosen table
- Made a reasonable interpretation of "revenue"

**This IS a harness failure.** The system:
- Had no data dictionary
- Had no golden set to catch this in testing
- Had no judge to validate answers
- Had no tracing to detect the error before it reached the board

---

## Risk Assessment

### 🔥 Blocking Risks (Deploy fixes today)

1. **Data layer missing:** "Revenue" will remain ambiguous until data dictionary is added
2. **Action safety:** Tool can write to warehouse (data corruption risk)
3. **No max iterations:** Unbounded loop could cause runaway costs

### 🟡 High Risks (Deploy this week)

4. **No golden set:** Prompt changes ship without testing
5. **No tracing:** Can't audit what the bot told people, no cost visibility

### 📋 Medium Risks (Deploy this month)

6. **No judge automation:** Manual testing is slow and incomplete

---

## Effort Estimates

| Fix | Priority | Effort | Impact |
|-----|----------|--------|--------|
| Merge data dictionary into prompt | 🔥 Blocking | 1 hour | Fixes revenue queries |
| Deploy read-only DB connection | 🔥 Blocking | 15 min | Prevents data corruption |
| Add max iterations | 🔥 Blocking | 15 min | Prevents runaway cost |
| Add golden set | 🟡 High | 1 hour | Enables regression testing |
| Add judge to CI | 🟡 High | 1 hour | Automates testing |
| Add tracing | 🟡 High | 2 hours | Visibility into usage/cost |
| **Total** | | **6 hours** | All 6 harness components |

---

## Next Actions

### Immediate (today):
1. ✅ Correct board deck: Q2 revenue is $3.6M
2. 🔥 Merge `output/data_dictionary.md` into `prompt.md`
3. 🔥 Deploy `output/agent_safe.py` (max iterations + read-only DB)

### This week:
4. 📋 Add `output/evals/golden.jsonl` and `output/evals/judge.py` to repo
5. 📋 Run golden set as CI check on prompt changes
6. 📊 Add structured logging

### Next week:
7. 🔍 Audit Slack history: find other threads with revenue queries, check for errors
8. 📊 Dashboard: cost per week, query volume, error rate

---

## Model Swap Decision

**Question:** Should we upgrade to Opus or GPT-6?

**Answer:** **Not yet.** Fix the harness first.

**Reasoning:**
- Current issue is **data ambiguity**, not model capability
- A smarter model might guess "revenue_recognized" more often, but it's still a guess
- Cost: Opus/GPT-6 are 3-5x more expensive per query
- Benefit: Zero, until data dictionary is added

**Decision framework:**
1. ✅ Deploy data dictionary (defines "revenue")
2. ✅ Run golden set on current model (Sonnet)
3. ❓ If Sonnet still fails cases, run golden set on Opus/GPT-6
4. ❓ Compare: quality improvement vs cost increase
5. ❓ Decide based on cost/quality tradeoff

**Expected outcome:** With data dictionary, Sonnet will pass all tests. No upgrade needed.

---

## Summary

FinBot has **9/60 points on the harness scorecard.** The Q2 revenue incident was caused by:
- ❌ Missing data dictionary (the root cause)
- ❌ No golden set (would have caught this)
- ❌ No judge (would have blocked deployment)

**The model is not at fault.** It did its job (query the database, return results). The harness failed to define what "revenue" means.

**Recommendation:** Don't swap models. Fix the harness (6 hours of work), then re-evaluate if needed.
