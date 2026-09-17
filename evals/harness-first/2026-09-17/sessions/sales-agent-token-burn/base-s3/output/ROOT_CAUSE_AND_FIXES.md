## 🔥 ROOT CAUSE IDENTIFIED: TWO BUGS CAUSING 70% OF COSTS

### The Problem
5 conversations accounting for **$18.77 (70% of September costs)** are stuck in retry loops due to **TWO DISTINCT BUGS**:

---

## Bug #1: Unknown Field `lead_score_v2` (3 conversations, $14.06)
**Leads affected:** L-2012, L-3032, L-3419

### Error
```
422 Unprocessable Entity 
{"error":"validation_failed","detail":"unknown field","field":"lead_score_v2"}
```

### Root Cause
The system prompt says:
> "Leads scoring 80 or higher must get the new scoring field: {"lead_score_v2": <score>}"

**But this field doesn't exist in the CRM schema yet!**

### Impact
- Agent scores lead ≥80
- Tries to write `lead_score_v2` field
- CRM rejects it (422 error)
- Agent retries 15-17 times
- Costs $4.60-4.71 per conversation (vs $0.19 average)

### Fix
**Option A (Quick):** Remove the `lead_score_v2` logic from `agent/prompts.py`
```python
# OLD:
# 3. Write the score to the contact with crm_update_contact. Leads scoring 80 or higher must get the new
#    scoring field: {"lead_score_v2": <score>}. Others: {"lead_score": <score>}.

# NEW:
3. Write the score to the contact with crm_update_contact: {"lead_score": <score>}.
```

**Option B (Complete):** Add `lead_score_v2` field to CRM schema first, then deploy prompt

**Cost savings:** $14.06 → $0.57 (95% reduction on these 3 conversations)

---

## Bug #2: Merged Accounts (2 conversations, $4.71)
**Leads affected:** L-3489, L-2437

### Error
```
404 Not Found 
{"error":"account_merged"}
```

### Root Cause
- Agent tries to fetch account data
- Account was merged (common in CRM deduplication)
- CRM returns 404
- Agent doesn't understand "account_merged" error
- Tries different account IDs (acc_4242-1, acc_4242-2, etc.)
- Eventually hits rate limits (429 Too Many Requests)
- 26 turns before giving up

### Impact
- L-3489: 26 turns, $0.33 cost
- L-2437: 16 turns, $4.39 cost
- Total: $4.71 (vs $0.38 for normal handling)

### Fix
Update `agent/tools.py` CRM client to:
1. Detect "account_merged" errors
2. Return clear error message to agent
3. Tell agent to skip to next lead (don't retry)

OR

Update system prompt to handle merged accounts:
```python
If you encounter an "account_merged" error, skip this lead and report: 
"Lead {id}: account merged, cannot process."
```

**Cost savings:** $4.71 → $0.38 (92% reduction)

---

## Summary of Fixes

| Issue | Affected Leads | Current Cost | Fixed Cost | Savings | Priority |
|-------|----------------|--------------|------------|---------|----------|
| Bug #1: lead_score_v2 field | 3 | $14.06 | $0.57 | $13.49 (96%) | 🔴 URGENT |
| Bug #2: Merged accounts | 2 | $4.71 | $0.38 | $4.33 (92%) | 🟡 HIGH |
| Normal operations | 41 | $7.89 | $7.89 | $0 | - |
| **TOTAL** | **46** | **$26.66** | **$8.84** | **$17.82 (67%)** | - |

---

## Complete Action Plan

### 1. Deploy Haiku (Today - 5 minutes)
✅ `config.json` already updated in repo
- **Immediate savings:** 67% on all costs
- **Sept 1-15:** $26.66 → $8.89
- **Projected full month:** $53.33 → $17.78

### 2. Fix lead_score_v2 Bug (Today - 10 minutes)
Edit `agent/prompts.py` line 8:
```diff
- 3. Write the score to the contact with crm_update_contact. Leads scoring 80 or higher must get the new
-    scoring field: {"lead_score_v2": <score>}. Others: {"lead_score": <score>}.
+ 3. Write the score to the contact with crm_update_contact: {"lead_score": <score>}.
```

**Impact:** Eliminates the most expensive failures

### 3. Fix Merged Account Handling (This Week - 30 minutes)
Update `agent/tools.py` to handle account_merged errors gracefully

**Impact:** Prevents 16-26 turn conversations

### 4. Add Turn Limit Safety (This Week - 15 minutes)
Edit `agent/loop.py`:
```python
def run_conversation(lead_id, llm=None, tools=None, conversation_id=None, max_turns=10):
    ...
    while turn < max_turns:
        ...
```

**Impact:** Safety net against future runaway costs

---

## Cost Projections After Fixes

| Scenario | Sept 1-15 | Full Month | Savings vs Current |
|----------|-----------|------------|-------------------|
| Current (Sonnet, bugs) | $26.66 | $53.33 | - |
| **Haiku only** | $8.89 | $17.78 | 67% ($35.55) |
| **Haiku + Bug #1 fixed** | $4.40 | $8.80 | 84% ($44.53) |
| **Haiku + Both bugs fixed** | $2.95 | $5.90 | 89% ($47.43) |

---

## Files to Edit

1. ✅ `/home/user/work/config.json` - Already updated to Haiku
2. 📝 `/home/user/work/agent/prompts.py` - Remove lead_score_v2 logic
3. 📝 `/home/user/work/agent/loop.py` - Add max_turns parameter
4. 📝 `/home/user/work/agent/tools.py` - Handle account_merged errors

---

## Recommendation

**Deploy ALL fixes together:**
1. Haiku (67% savings) ✅ Ready now
2. Remove lead_score_v2 (eliminates 3 most expensive conversations) ← 10 min fix
3. Add turn limit (safety net) ← 15 min fix
4. Handle merged accounts (eliminates remaining issues) ← 30 min fix

**Total effort:** ~1 hour
**Total savings:** 89% ($47/month)
**Deploy by end of day, save money for rest of September**
