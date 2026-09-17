# Token Burn Mechanism - Detailed Trace

This shows exactly how 1 conversation burned $4.73 in 5 minutes.

## Lead L-3419 (conversation cv_488aab)
**Sept 9, 2026 - 02:10 UTC**

---

### Turn 1: Normal start (1,949 input tokens)
**Cost: $0.006**

```
System prompt (1,800 tokens) + "Work lead L-3419: qualify it..." (150 tokens)
→ Model calls: crm_get_account("acc_4242")
→ Result: 30KB JSON export
```

---

### Turn 2: Model sees CRM data, tries to update (14,653 input tokens)
**Cost: $0.044**

```
Previous turn (1,949 tokens) 
+ CRM export in tool result (11,000 tokens)
+ Model output (113 tokens)
+ New request (1,591 tokens)
→ Model calls: crm_get_account("acc_4242") [AGAIN - prompt says "EVERY turn"]
              crm_update_contact("ct_75842", {"lead_score_v2": 85})
→ CRM returns: 422 Unprocessable Entity {"error": "unknown field: lead_score_v2"}
```

**The retry wrapper tries 4 times:**
```
logs/crm_client.log:
2026-09-09T02:10:23Z PATCH /contacts/ct_75842 -> 422 (attempt 1/4)
2026-09-09T02:10:25Z PATCH /contacts/ct_75842 -> 422 (attempt 2/4)
2026-09-09T02:10:27Z PATCH /contacts/ct_75842 -> 422 (attempt 3/4)
2026-09-09T02:10:29Z PATCH /contacts/ct_75842 -> 422 (attempt 4/4)
```

After 4 attempts, tool returns: `{"error": "422 Unprocessable Entity...", "status": 422}`

---

### Turn 3: Model sees error, prompt says "try it again" (27,464 input tokens)
**Cost: $0.082**

```
Full history so far (14,766 tokens)
+ CRM export AGAIN because model called crm_get_account again (11,000 tokens)
+ Tool error message (100 tokens)
+ New request (1,598 tokens)
→ Model tries SAME calls again: crm_get_account, crm_update_contact with lead_score_v2
→ SAME 422 error, retry wrapper runs 4 more times
→ Tool returns same error
```

---

### Turn 4-16: Identical pattern, growing input every turn

Each turn:
1. Resends entire conversation history
2. Resends the 30KB CRM export (called fresh each turn per prompt instruction)
3. Model sees error
4. Prompt says "try it again"
5. Makes same invalid API call
6. Retry wrapper burns 4 attempts
7. Returns same error
8. +~13,000 tokens per turn

**Turn 16: 144,792 input tokens, $0.434 per call**

By the end:
- 16 turns
- 64 failed CRM API calls (16 turns × 4 retry attempts)
- 1,564,200 total input tokens
- **$4.73 total cost**
- Zero useful work done

---

## Why the Loop Didn't Break

### Problem 1: No max turns (loop.py:19)
```python
while True:  # ← Infinite loop
    turn += 1
    # ...
```

**Fix:**
```python
MAX_TURNS = 6  # Normal is 3-4, gives buffer
while turn < MAX_TURNS:
    # ...
```

### Problem 2: Prompt encourages retries (prompts.py:8)
```
"Do not finish until the CRM update has succeeded. 
If a tool call fails, try it again."
```

**Fix:**
```
"If the CRM update returns an error, report it and stop—do NOT retry."
```

### Problem 3: Retry wrapper doesn't distinguish errors (tools.py:29)
```python
def with_retries(fn, attempts=4, backoff=1.5):
    for i in range(attempts):
        try:
            return fn(*args, **kwargs)
        except ToolError as e:
            last = e  # ← Retries ALL errors
            time.sleep(backoff * (i + 1))
    raise last
```

**Fix:**
```python
def with_retries(fn, attempts=4, backoff=1.5):
    for i in range(attempts):
        try:
            return fn(*args, **kwargs)
        except ToolError as e:
            # Don't retry 4xx client errors - they're deterministic
            if e.status and 400 <= e.status < 500:
                raise  # Fail fast
            last = e
            time.sleep(backoff * (i + 1))
    raise last
```

### Problem 4: Prompt says fetch EVERY turn (prompts.py:1)
```
"At the start of EVERY turn, call crm_get_account"
```

This is wasteful even when the loop terminates normally. Accounts don't change mid-workflow.

**Fix:**
```
"Call crm_get_account ONCE at the start"
```

---

## 4 Other Conversations, Same Pattern

| Lead | Turns | Cost | Failed Field |
|---|---|---|---|
| L-3419 (cv_488aab) | 16 | $4.73 | lead_score_v2 |
| L-3032 (cv_15f5fe) | 16 | $4.71 | lead_score_v2 |
| L-2012 (cv_24a92f) | 16 | $4.60 | lead_score_v2 |
| L-2437 (cv_a99bb9) | 15 | $4.39 | lead_score_v2 |
| **Total** | | **$18.43** | |

All hit the same bug: CRM schema doesn't have `lead_score_v2`, prompt asks for it, 422 error, infinite retry.

One more (L-3489) hit a different loop (26 turns, $0.33) retrying `crm_get_account` on merged accounts returning 404.

---

## Cost Impact

**Sept 1-15 actual:**
- 46 conversations
- $26.66 total
- $18.77 (70%) from 5 broken conversations

**What normal should be:**
- 46 conversations
- $7.90 total (41 working conversations extrapolated)
- $0.17 per conversation average

**Savings from fixes:**
- $18.77 eliminated
- $37.54/month ongoing
- $450/year

---

## Why Model Choice Doesn't Matter Yet

Even at 1/10 the price, broken loops still waste money:
- gpt-5-mini: 16 turns × 140K tokens = still expensive
- The mechanism is the problem, not the token price

**Fix the harness, THEN pick the cheapest model that passes quality bar.**

After fixes, Haiku is perfect for this (cold emails, simple task, 1/3 Sonnet price).
