# Agent Code Analysis - Harness Issues

## Current Agent Loop (agent.py)

```python
while True:
    resp = chat(...)
    messages.append(...)
    calls = [b for b in resp["content"] if b.get("type") == "tool_use"]
    if not calls:
        return ...
    results = []
    for c in calls:
        try:
            out = run_sql(c["input"]["query"])
        except Exception as e:
            out = {"error": str(e)}
        results.append(...)
    messages.append(...)
```

## Harness Issues Found

### 1. ❌ NO ITERATION LIMIT
**Risk:** Infinite loop if model gets stuck or confused
**Evidence:** `while True:` with no max_iterations check (line 31)
**Impact:** Could burn unlimited tokens, hang Slack users

### 2. ❌ NO COST CAPS
**Risk:** Single query could burn through budget
**Evidence:** No per-run cost limit, no token counting
**Impact:** Already happened - unclear how much the board deck query cost

### 3. ❌ NO READ-ONLY ENFORCEMENT
**Risk:** SQL tool can execute ANY query including DELETE, UPDATE, DROP
**Evidence:** `conn.execute(query)` then `conn.commit()` (lines 16-19)
**Proof:** 
```python
>>> run_sql("DROP TABLE revenue_recognized")  # would work!
>>> run_sql("UPDATE orders SET amount = 0")   # would work!
```
**Impact:** CRITICAL - agent has write access on production warehouse

### 4. ❌ NO OUTPUT SIZE LIMIT
**Risk:** Large result sets resent every turn, burning tokens
**Evidence:** `MAX_ROWS = 200` exists but 200 rows × multiple tool calls × conversation turns
**Impact:** Token waste on queries that return many rows

### 5. ⚠️ ERROR RETRY WITHOUT CLASSIFICATION
**Risk:** Retries on non-transient errors (syntax, missing table) waste tokens
**Evidence:** All exceptions caught and passed to model to "retry" (line 37)
**Issue:** Syntax errors are deterministic, won't fix themselves

### 6. ❌ NO TRACING
**Risk:** Can't debug which queries burned tokens or gave wrong answers
**Evidence:** No logging of queries, results, tokens, cost, errors
**Impact:** Can't diagnose issues without Slack exports

## Not Found (Missing Harness)

- No golden test set (now created: `golden_set.jsonl`)
- No automated judge (now created: `eval_judge.py`)  
- No data dictionary (now created: `data_dictionary.md`)
- No prompt versioning or regression testing
- No conversation ID or user tracking in logs

## Recommendations by Priority

### BLOCKING (fix before next use):
1. **Add read-only mode**: Connect with `?mode=ro` or validate queries with sqlparse
2. **Add iteration limit**: `MAX_ITERATIONS = 5` to prevent infinite loops
3. **Add per-run cost cap**: Track tokens, stop at threshold

### HIGH (fix this week):
4. Add tracing: log every query + result + tokens to a file
5. Ship improved prompt (prompt_v2.md) 
6. Add golden set to CI/CD

### MEDIUM (fix this sprint):
7. Truncate/summarize large tool results before resending
8. Classify errors: don't retry syntax/schema errors
9. Add conversation IDs for multi-turn debugging
