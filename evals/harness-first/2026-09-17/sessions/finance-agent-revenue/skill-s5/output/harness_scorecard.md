# FinBot Harness Scorecard

**Audit Date:** 2026-09-16  
**Auditor:** AI Assistant  
**Agent:** FinBot (finance Q&A Slack bot)  
**Codebase:** /home/user/work (agent.py, prompt.md, config.py)

---

## Overview

| Component | Status | Score |
|-----------|--------|-------|
| Golden set | ❌ Missing | 0/10 |
| Judge | ❌ Missing | 0/10 |
| Cost governance | ⚠️ Partial | 3/10 |
| Data layer | ❌ Missing | 1/10 |
| Action safety | ⚠️ Unsafe | 2/10 |
| Tracing | ❌ Missing | 0/10 |
| **TOTAL** | **6/60** | **10%** |

**Assessment:** Critical harness gaps. Not production-ready by standard safety criteria.

---

## 1. Golden Set (0/10) - ❌ MISSING

**What exists:**
- One manually exported Slack transcript (`transcripts/2026-09-11_board-deck.md`)
- No test cases with expected answers
- No regression suite

**What's missing:**
- No `evals/` directory
- No test cases covering:
  - Different time periods (Q1, Q2, months, years)
  - Different metrics (revenue, orders, refunds, customers)
  - Edge cases (zero results, date boundaries, ambiguous questions)
  - Known past incidents
- No mechanism to run tests before deploying changes

**Evidence:**
```bash
$ find /home/user/work -name "*eval*" -o -name "*test*"
# (no results)
```

**Impact:** 
- Prompt changes are deployed with no validation
- Model swaps have no quality comparison
- Regressions are discovered by users (like this incident)

**Fix created:** `output/fixes/evals/golden.jsonl` (6 test cases from actual data)

---

## 2. Judge (0/10) - ❌ MISSING

**What exists:**
- Nothing. No automated checks.

**What's missing:**
- No script to run golden set and check answers
- No deterministic checks (e.g., "revenue queries must use revenue_recognized")
- No LLM-based grading for subjective quality
- No CI/CD gate to block bad deployments

**Evidence:**
- No evaluation code in repository
- README says "Built in a hackathon in March, been in use since" - suggests no formal testing process

**Impact:**
- The Q2 revenue bug could have been caught by a single test case
- No way to prove a model upgrade is worth the cost
- Every change is a manual spot-check at best

**Fix created:** `output/fixes/evals/run_evals.py` (basic judge script, needs extension)

---

## 3. Cost Governance (3/10) - ⚠️ PARTIAL

**What exists:**
- `MAX_ROWS = 200` caps query result size (config.py)
- `temperature = 0.2` reduces randomness (config.py)

**What's missing:**
- **No max iterations:** Loop is `while True:` (agent.py:30), runs until model stops or timeout
- **No per-run cost cap:** No token budget or cost limit per question
- **No graceful failure:** If model never stops calling tools, agent hangs until timeout
- **No retry logic for transient errors:** All errors returned to model (agent.py:25-26), even non-transient ones
- **No cost monitoring:** No alerts if cost spikes

**Evidence:**
```python
# agent.py line 30
while True:
    resp = chat(...)  # No iteration counter, no break condition
```

**Specific risks:**
- User asks a question that triggers 50 tool calls → expensive, slow, bad UX
- Deterministic SQL error (e.g., column typo) → model retries indefinitely → token burn

**Example scenario:**
```
User: "compare revenue by region for every customer"
Model: runs query, gets 10k rows (truncated to 200)
Model: "I need more data" → queries again
Model: still truncated → queries again
... (repeats until timeout)
```

**Fix created:** 
- `output/fixes/agent.py` adds `MAX_TURNS = 10` with graceful failure message
- Would also recommend: per-user daily cost cap, alert if any single query costs >$X

---

## 4. Data Layer (1/10) - ❌ MISSING

**What exists:**
- Five tables listed in prompt: customers, orders, refunds, revenue_recognized, daily_kpis
- Warehouse.db file with those tables

**What's missing:**
- **No data dictionary:** No definition of "revenue" or other metrics
- **Ambiguous column names:** Both `orders.amount` and `revenue_recognized.net_amount` could be "revenue"
- **No guidance on which table to use:** Model must guess intent
- **No field descriptions:** What's the difference between `created_at` and `recognized_on`?
- **No exclusion rules:** Should cancelled orders be counted?

**Evidence (the incident):**
```markdown
# prompt.md lines 7-12
Tables you can use:
- customers
- orders
- refunds
- revenue_recognized
- daily_kpis

If a question is about money, always give a single headline number with a dollar sign.
```

No definitions. Model saw "revenue" and reasonably picked `orders` (simpler, more obvious).

**Root cause of incident:**
- Finance means: `revenue_recognized.net_amount` (GAAP, net of refunds)
- FinBot computed: `SUM(orders.amount)` (gross, includes cancelled)
- Difference: $499,876 (12% error)

**Fix created:** `output/fixes/prompt.md` with full data dictionary

---

## 5. Action Safety (2/10) - ⚠️ UNSAFE

**What exists:**
- Tool description says "read-only" in comments
- Tool returns data, doesn't confirm writes

**What's missing / BLOCKING RISKS:**

### Risk 1: Write access on a read path
**Evidence:** agent.py lines 16-21
```python
def run_sql(query):
    conn = sqlite3.connect(config.DB_PATH)  # ← Opens with write access
    try:
        cur = conn.execute(query)
        rows = cur.fetchall() if cur.description else []
        cols = [d[0] for d in cur.description] if cur.description else []
        conn.commit()  # ← Commits every query (unnecessary for reads)
```

**Impact:**
- Any SQL statement executes: `DROP TABLE orders`, `UPDATE orders SET amount=0`, etc.
- No approval, no confirmation, no undo
- Tool description says "run a query and return rows" but code allows writes
- User could accidentally ask "update Q2 revenue to match budget" and FinBot would try to execute it

**Mitigation needed:**
1. Open connection in read-only mode: `sqlite3.connect(f"file:{path}?mode=ro", uri=True)`
2. Remove `conn.commit()` line (not needed for reads)
3. Consider: separate DB user with SELECT-only grants (if using Postgres/MySQL)

### Risk 2: No approval for irreversible actions
Currently no write actions are exposed via tools, but if they were (e.g., "file a refund", "update customer segment"), there's no approval workflow.

**Fix created:** `output/fixes/agent.py` opens DB in read-only mode, removes commit

---

## 6. Tracing (0/10) - ❌ MISSING

**What exists:**
- Slack threads (manual exports)
- No structured logs

**What's missing:**
- **No conversation IDs:** Can't link a question to its full execution trace
- **No LLM call logs:** No record of tokens, latency, cost per call
- **No tool call logs:** No record of which SQL queries were run
- **No error tracking:** If agent fails, no way to debug without asking user what happened
- **No cost attribution:** Can't answer "which users/questions cost the most?"
- **No performance tracking:** Can't see if response time is degrading

**Evidence:**
- No logging code in agent.py
- README says transcripts are "exported Slack threads people flagged" (manual, reactive)

**Impact:**
- This incident required manual investigation (reading Slack, rerunning queries)
- No way to audit all Q2 questions to see if others got wrong data
- No way to know if a model change increases cost by 2x until the bill arrives

**Recommended structure:**
```json
{
  "conversation_id": "slack-C123-thread-456",
  "user": "priya.raman",
  "timestamp": "2026-09-11T10:02:00Z",
  "question": "what was Q2 revenue?",
  "llm_calls": [
    {"model": "claude-sonnet-4-5", "tokens_in": 234, "tokens_out": 89, "cost": 0.0023, "latency_ms": 450}
  ],
  "tool_calls": [
    {"tool": "run_sql", "query": "SELECT ...", "rows": 1, "latency_ms": 12}
  ],
  "answer": "Q2 2026 revenue was $4,138,212.16",
  "total_cost": 0.0023,
  "total_latency_ms": 462
}
```

**Fix:** Not implemented (would require integration with corp logging system or new JSON log file)

---

## Summary & Prioritization

### Blocking (deploy immediately):
1. **Read-only DB connection** (5 min) - prevents data corruption
2. **Max iterations** (5 min) - prevents runaway costs

### High (deploy this week):
3. **Data dictionary** (30 min) - fixes this incident class
4. **Golden set** (1 hour) - prevents regressions
5. **Judge script** (30 min) - gates future deployments

### Medium (deploy this month):
6. **Tracing** (1-2 days) - visibility for debugging and cost control
7. **Cost caps** (4 hours) - per-user and per-query limits

### Long-term (quarter):
8. **Approval workflow** for any future write tools
9. **Expanded golden set** (50+ cases from Slack history and finance FAQs)
10. **LLM-based judge** for answer quality beyond exact number matches

---

## Comparison: Current State vs. Production-Ready

| Aspect | Current | Production-Ready |
|--------|---------|------------------|
| Testing | None | 50+ golden cases, run on every change |
| Safety | Write access, no limits | Read-only, cost caps, max iterations |
| Definitions | "Tables you can use" | Full data dictionary with examples |
| Monitoring | Manual Slack exports | Structured logs, cost/error dashboards |
| Deployment | No checks | Judge must pass, diff review |
| Error handling | Retry forever | Max 10 turns, graceful failure |

**Maturity level:** Prototype (appropriate for March hackathon, not for board materials)

**To reach production:** ~2-3 days of eng work to implement fixes 1-6

---

## Files Created

All fixes are in `output/fixes/`:
- `agent.py` - read-only DB, max iterations
- `prompt.md` - data dictionary
- `evals/golden.jsonl` - 6 test cases
- `evals/run_evals.py` - basic judge script

Deploy these files to fix the incident and prevent future regressions.
