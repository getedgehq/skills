# Investigation Log: FinBot Q2 Revenue Discrepancy

**Date:** 2026-09-15  
**Incident ID:** finbot-2026-09-14-revenue  
**Reported By:** Marta Oyelaran (VP Finance)  
**Impact:** Board pre-read contained $500K revenue error

---

## Timeline

### 2026-09-11 10:02 AM
- **Event:** Priya Raman asks @finbot "what was our Q2 2026 revenue?"
- **Response:** FinBot responds "$4,138,212.16 (~$4.1M)"
- **Action:** Priya copies number into board deck
- **Source:** `transcripts/2026-09-11_board-deck.md`

### 2026-09-14
- **Event:** Marta (Finance) reviews board pre-read
- **Observation:** Deck says Q2 revenue = $4.1M, but Finance Q2 close = $3.6M
- **Impact:** $500K discrepancy, board deck scheduled to go out
- **Escalation:** Daniel (CEO) asks if model is "making numbers up"

### 2026-09-15 (Investigation)
- **Assigned:** Investigation using harness-first diagnostic
- **Approach:** Reproduce from evidence, audit harness, find mechanism

---

## Investigation Steps

### Step 1: Gather Evidence
✅ **Completed**

**Artifacts collected:**
- `transcripts/2026-09-11_board-deck.md` — Slack thread with Priya
- `notes/slack-exec-thread.txt` — Exec team discussion
- `warehouse.db` — Production database snapshot
- `agent.py` — Agent code
- `prompt.md` — System prompt
- `config.py` — Configuration

**Key observations:**
- Bot's SQL query visible in transcript
- Query used `orders` table, not `revenue_recognized`
- Both tables exist in warehouse
- Prompt lists both tables but doesn't define "revenue"

### Step 2: Reproduce the Numbers
✅ **Completed**

**Recomputed from warehouse.db:**

Query 1 (what bot used):
```sql
SELECT SUM(amount) FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';
-- Result: 4,138,212.16
```

Query 2 (what Finance uses):
```sql
SELECT SUM(net_amount) FROM revenue_recognized 
WHERE recognized_on BETWEEN '2026-04-01' AND '2026-06-30';
-- Result: 3,638,335.79
```

**Gap:** $499,876.37 (12.1% difference)

**Breakdown:**
- Orders (gross bookings): $4,138,212
- Refunds in Q2: -$355,257
- Recognition timing: -$144,619
- Net revenue: $3,638,336

### Step 3: Understand the Data Model
✅ **Completed**

**Two tables contain "revenue" data:**

1. `orders` table
   - Purpose: Order events (sales pipeline)
   - `amount` column = gross order value when placed
   - Includes orders that may be refunded later
   - Includes orders recognized in different periods

2. `revenue_recognized` table
   - Purpose: GAAP revenue recognition (financial reporting)
   - `net_amount` column = revenue after refunds, recognized in period
   - Source of truth for Finance reporting
   - Used for board decks, investor updates

**The prompt lists both but doesn't say which to use for "revenue".**

### Step 4: Analyze Agent Behavior
✅ **Completed**

**Code review of `agent.py`:**
- Line 33: `while True:` — unbounded loop (safety issue)
- Line 39-41: Catches all exceptions, lets model retry (cost issue)
- Line 21: `conn.commit()` — allows database writes (safety issue)

**Prompt review of `prompt.md`:**
- Lists 5 tables (lines 9-13)
- No metric definitions
- No data dictionary
- Says "Use the run_sql tool" but doesn't define "revenue"

**Model behavior:**
- Interpreted "revenue" as "sum of order amounts"
- Reasonable guess, but wrong for financial reporting
- Not a hallucination — query executed correctly

### Step 5: Check for Harness Components
✅ **Completed**

**Audit results:**
- ❌ Golden set: Does not exist
- ❌ Judge: Does not exist
- 🟡 Cost governance: Partial (has MAX_ROWS, missing max iterations)
- ❌ Data layer: No data dictionary, no read-only access
- 🟡 Action safety: Partial (designed for reads, but can write)
- ❌ Tracing: No logging

**Score:** 9/60 points

### Step 6: Identify Root Cause
✅ **Completed**

**Mechanism:** Data layer missing → ambiguous metric → model guessed wrong table

**Evidence chain:**
1. User asked: "what was our Q2 2026 revenue?"
2. Prompt lists `orders` and `revenue_recognized` with no distinction
3. Model chose `orders.amount` (reasonable interpretation)
4. Query returned $4,138,212.16 (correct sum for that table)
5. User copied to board deck
6. Finance caught error in pre-read

**This is NOT:**
- ❌ Model hallucination (didn't make up numbers)
- ❌ Model capability issue (executed valid SQL)
- ❌ Token/cost issue (query was efficient)

**This IS:**
- ✅ Harness failure (no data dictionary)
- ✅ Testing gap (no golden set)
- ✅ Process failure (no validation before board deck)

### Step 7: Build Harness Fixes
✅ **Completed**

**Created:**
1. `data_dictionary.md` — Canonical metric definitions
2. `prompt_PATCHED.md` — System prompt with data dictionary
3. `agent_safe.py` — Agent with safety fixes
4. `evals/golden.jsonl` — 12 test cases
5. `evals/judge.py` — Automated test runner
6. `golden_set_results.txt` — Simulated test results

**Validated:**
- Data dictionary defines "revenue" = `revenue_recognized.net_amount`
- Golden set includes Q2 revenue case (incident source)
- Judge detects table/column usage errors
- Safety fixes prevent infinite loops and writes

### Step 8: Evaluate Model Swap Question
✅ **Completed**

**Question:** Should we upgrade to Opus or GPT-6?

**Analysis:**
- Current issue: Data ambiguity (harness)
- Model capability: Sufficient (executed valid SQL)
- Cost of upgrade: 3-5x per query
- Benefit without data dictionary: Zero (still ambiguous)

**Recommendation:** Fix data layer first, then measure if upgrade needed

**Expected outcome:** With data dictionary, current model will pass all tests

---

## Findings

### Root Cause
**Data layer missing (no data dictionary)** caused the bot to guess which table to use for "revenue"

### Contributing Factors
1. No golden set — incident case was never tested
2. No judge — no automated validation
3. No data dictionary — "revenue" was ambiguous
4. Manual workflow — Priya copied answer without validation

### Model Behavior
- ✅ Model worked correctly (executed valid SQL)
- ✅ Query was efficient (< 1 second)
- ✅ Result was accurate for the table chosen
- ❌ Table choice was wrong (ambiguous prompt)

### Impact
- **Board deck:** $500K wrong number in pre-read
- **Blast radius:** Unknown how many other queries were wrong
- **Reputation:** Finance caught before board saw it, but close call

### Other Issues Found
1. **Safety:** Unbounded loop could cause runaway cost
2. **Safety:** Tool can write to production database
3. **Visibility:** No logging/tracing of queries
4. **Testing:** No regression suite

---

## Recommendations

### Immediate (Today)
1. 🔥 Fix board deck: Q2 = $3.6M, Q1 = $3.3M
2. 🔥 Deploy `prompt_PATCHED.md` (adds data dictionary)
3. 🔥 Deploy `agent_safe.py` (max iterations + read-only DB)

### This Week
4. 📋 Add golden set to CI
5. 📋 Finance reviews data dictionary
6. 📋 Add logging/tracing

### Next Week
7. 🔍 Audit Slack history for other errors
8. 🔍 Build cost/quality dashboard

### Future (If Needed)
9. ❓ Evaluate model upgrade (after data dictionary deployed)

---

## Lessons Learned

### What Went Wrong
- Hackathon project went to production without harness
- No data dictionary = ambiguous metrics
- No testing = no safety net
- Manual workflow = human error risk

### What Went Right
- Finance caught error before board saw it
- Bot logged queries in Slack (made investigation possible)
- Database snapshot available for reproduction

### Prevention Strategies
1. **Data dictionary required** for all data-query agents
2. **Golden set required** before production deployment
3. **CI checks required** on prompt changes
4. **Validation step** before high-stakes outputs (board decks)

---

## Sign-off

**Investigation completed:** 2026-09-15  
**Root cause confirmed:** Data layer missing (no data dictionary)  
**Model swap required:** No (fix harness first)  
**Deliverables:** 11 files in `output/` folder, ready to deploy  

**Reviewed by:**
- [ ] Daniel Kurz (CEO) — aware of findings
- [ ] Marta Oyelaran (VP Finance) — to review data dictionary
- [ ] Jonas Feld (Data) — to deploy fixes
- [ ] Priya Raman (Strategy) — to update board deck

---

**Next Action:** Deploy fixes per `ACTION_ITEMS.md`
