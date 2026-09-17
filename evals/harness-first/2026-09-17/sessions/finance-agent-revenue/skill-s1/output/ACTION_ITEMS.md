# Action Items: FinBot Q2 Revenue Incident

**For:** Daniel, Jonas (Data), Marta (Finance)  
**Date:** 2026-09-15  
**Incident:** Board deck reported Q2 revenue as $4.1M, should be $3.6M

---

## 🔥 URGENT: Today (before EOD 2026-09-15)

### 1. Fix the board deck
**Owner:** Priya / Marta  
**Action:** Update Q2 2026 revenue from $4.1M to $3.6M  
**Details:**
- Correct number: $3,638,335.79 (~$3.6M)
- Source: `revenue_recognized.net_amount` (GAAP basis)
- Q1 may also be wrong (check transcript): bot said $4.1M, should verify with Finance

**Status:** ⏳ Waiting

---

### 2. Deploy data dictionary fix
**Owner:** Jonas (Data)  
**Action:** Replace `prompt.md` with `output/prompt_PATCHED.md`  
**Effort:** 5 minutes  
**Why:** Defines "revenue" = `revenue_recognized.net_amount` (prevents recurrence)

**Steps:**
```bash
cd /path/to/finbot
cp output/prompt_PATCHED.md prompt.md
git add prompt.md
git commit -m "Fix: Add data dictionary to prevent revenue table confusion (incident 2026-09-14)"
# Deploy however you normally deploy (Docker, k8s, etc.)
```

**Test:**
```bash
python agent.py "what was Q2 2026 revenue?"
# Expected: ~$3.6M (not $4.1M)
```

**Status:** ⏳ Waiting

---

### 3. Deploy safety fixes
**Owner:** Jonas (Data)  
**Action:** Replace `agent.py` with `output/agent_safe.py`  
**Effort:** 10 minutes  
**Why:** Prevents runaway loops and accidental database writes

**Changes:**
- ✅ Max iterations cap (10) — prevents infinite loops
- ✅ Read-only database — prevents accidental writes
- ✅ Error handling — don't retry syntax errors

**Steps:**
```bash
cd /path/to/finbot
cp output/agent_safe.py agent.py
git add agent.py
git commit -m "Safety: Add max iterations and read-only DB connection"
# Deploy
```

**Status:** ⏳ Waiting

---

## 📋 This Week (by 2026-09-20)

### 4. Add golden set to repo
**Owner:** Jonas (Data)  
**Action:** Copy test suite to repo and add to CI  
**Effort:** 2 hours  
**Why:** Prevents regressions on future prompt changes

**Steps:**
```bash
cd /path/to/finbot
mkdir -p evals
cp output/evals/golden.jsonl evals/
cp output/evals/judge.py evals/
chmod +x evals/judge.py

# Test it works
python evals/judge.py

# Add to CI (example for GitHub Actions)
cat > .github/workflows/test-finbot.yml << 'EOF'
name: Test FinBot
on: [pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run golden set
        run: python evals/judge.py
EOF

git add evals/ .github/workflows/
git commit -m "Test: Add golden set and CI checks"
```

**Status:** ⏳ Waiting

---

### 5. Merge data dictionary with Finance
**Owner:** Marta (Finance) + Jonas (Data)  
**Action:** Review and approve `output/data_dictionary.md`  
**Effort:** 1 hour  
**Why:** Ensures data definitions match Finance's reporting

**Steps:**
1. Marta reviews `output/data_dictionary.md`
2. Confirms definitions match Finance's Q2 close process
3. Adds any missing metrics (ARR, MRR, etc. if applicable)
4. Jonas merges into repo as `docs/data_dictionary.md`

**Status:** ⏳ Waiting

---

### 6. Add tracing/logging
**Owner:** Jonas (Data)  
**Action:** Log all queries, costs, and errors  
**Effort:** 2 hours  
**Why:** Visibility into usage, cost, and errors

**What to log:**
```json
{
  "timestamp": "2026-09-15T10:02:00Z",
  "conversation_id": "abc123",
  "user": "priya@norvel.example",
  "question": "what was our Q2 2026 revenue?",
  "sql_queries": ["SELECT SUM(net_amount) FROM revenue_recognized WHERE..."],
  "answer": "Q2 2026 revenue was $3,638,335.79",
  "tokens": 1234,
  "cost": 0.05,
  "latency_ms": 2500,
  "error": null
}
```

**Where to log:**
- File: `logs/finbot.jsonl` (rotate daily)
- OR Database: `warehouse.finbot_logs` table
- OR S3: `s3://norvel-logs/finbot/`

**Status:** ⏳ Waiting

---

## 🔍 Next Week (by 2026-09-27)

### 7. Audit Slack history for other errors
**Owner:** Jonas (Data) + Marta (Finance)  
**Action:** Find all revenue queries in #ask-finance, validate answers  
**Effort:** 4 hours  
**Why:** The bot may have given wrong numbers to other people

**Steps:**
1. Export all Slack messages from #ask-finance (use Slack API or export tool)
2. Filter for messages from @finbot containing "revenue", "Q1", "Q2", etc.
3. For each message, recompute the answer manually
4. If wrong, notify the user and correct the record

**Example:**
```
Found 37 revenue queries since March 2026
- 9 used wrong table (orders instead of revenue_recognized)
- Users to notify: Priya (2x), Daniel (1x), Marcus (3x), ...
```

**Status:** ⏳ Waiting

---

### 8. Cost/quality dashboard
**Owner:** Jonas (Data)  
**Action:** Create dashboard for FinBot usage  
**Effort:** 3 hours  
**Why:** Ongoing monitoring of cost, quality, and usage

**Metrics to track:**
- Queries per day/week
- Cost per query (average, p95)
- Error rate
- Most common questions
- Most expensive queries

**Tools:** Grafana, Datadog, or simple notebook

**Status:** ⏳ Waiting

---

## ❓ Future (only if needed)

### 9. Model evaluation (Sonnet vs Opus/GPT-6)
**Owner:** Jonas (Data)  
**Action:** Compare models on golden set  
**Effort:** 2 hours  
**When:** After data dictionary is deployed and Sonnet still fails tests

**Steps:**
1. Deploy data dictionary fix
2. Run golden set on Sonnet: `python evals/judge.py`
3. If Sonnet passes all tests → DONE, no model swap needed
4. If Sonnet still fails → Run golden set on Opus and GPT-6
5. Compare: quality improvement vs cost increase
6. Document findings and recommend model

**Cost estimate:**
- Sonnet: ~$0.05/query avg
- Opus: ~$0.15/query avg (3x more expensive)
- GPT-6: ~$0.20/query avg (4x more expensive)

**Expected outcome:** With data dictionary, Sonnet will pass. No swap needed.

**Status:** ⏸️ Blocked (waiting for data dictionary deployment)

---

## Summary Table

| # | Action | Owner | Priority | Effort | Status |
|---|--------|-------|----------|--------|--------|
| 1 | Fix board deck | Priya/Marta | 🔥 Today | 5 min | ⏳ Waiting |
| 2 | Deploy data dictionary | Jonas | 🔥 Today | 5 min | ⏳ Waiting |
| 3 | Deploy safety fixes | Jonas | 🔥 Today | 10 min | ⏳ Waiting |
| 4 | Add golden set to CI | Jonas | 📋 This week | 2 hrs | ⏳ Waiting |
| 5 | Review data dictionary | Marta + Jonas | 📋 This week | 1 hr | ⏳ Waiting |
| 6 | Add tracing/logging | Jonas | 📋 This week | 2 hrs | ⏳ Waiting |
| 7 | Audit Slack history | Jonas + Marta | 🔍 Next week | 4 hrs | ⏳ Waiting |
| 8 | Build dashboard | Jonas | 🔍 Next week | 3 hrs | ⏳ Waiting |
| 9 | Model evaluation | Jonas | ❓ If needed | 2 hrs | ⏸️ Blocked |

**Total critical path:** 15 minutes today + 5 hours this week

---

## Communication

### To Daniel (CEO):
> We found the issue. The bot used the wrong database table because "revenue" wasn't defined in the prompt. It's not a model problem — the model worked correctly, we just didn't tell it which table to use.
> 
> Fix takes 15 minutes to deploy (data dictionary + safety patches). No need to upgrade the model. Full details in output/EXECUTIVE_SUMMARY.md.

### To Marta (Finance):
> The bot queried `orders.amount` ($4.1M) instead of `revenue_recognized.net_amount` ($3.6M). Both are correct for their definitions, but "revenue" wasn't defined in the bot's instructions.
> 
> We've created a data dictionary that maps revenue → revenue_recognized.net_amount. Need you to review it (output/data_dictionary.md) to make sure definitions match your Q2 close process.

### To Priya (Strategy):
> The Q2 number you got from the bot was wrong. Please update the deck to $3.6M.
> 
> We're also checking the Q1 number (bot said $4.1M). Can you verify with Finance what Q1 should be?

### To Jonas (Data):
> Root cause documented in output/harness_audit.md. Action items above. Priority is deploying the data dictionary (output/prompt_PATCHED.md) today to prevent recurrence.
> 
> All fixes ready to go in output/ folder.

---

## Questions?

Contact: Investigation completed 2026-09-15
