# FinBot Investigation Output

**Investigation Date:** 2026-09-15  
**Issue:** Q2 2026 revenue reported as $4.1M (should be $3.6M)  
**Question from Daniel:** "Is the model hallucinating? Do we need a better model?"

---

## Answer (TL;DR)

**No, don't switch models.** The bot used the wrong database table because it had no data dictionary. The model executed correctly; the harness was missing.

**Fix:** Deploy the data dictionary + read-only safety fixes below.

---

## Files In This Directory

### 📄 Read These First

1. **EXECUTIVE_SUMMARY.md** - One page for Daniel (CEO)
2. **QUICK_START.md** - Deploy checklist for Jonas (bot owner)
3. **query_comparison.txt** - Side-by-side: wrong query vs. correct query

### 📊 Full Analysis

4. **REPORT.md** - Complete technical investigation (root cause, harness audit, recommendations)
5. **agent_harness_analysis.md** - Line-by-line audit of current agent.py

### 🛠️ Fixes To Deploy

6. **agent_v2.py** - Hardened agent with:
   - ✅ Read-only database (prevents DELETE/UPDATE/DROP)
   - ✅ Max iterations (prevents infinite loops)
   - ✅ Cost caps (prevents token burn)
   - ✅ Tracing (logs queries and results)

7. **prompt_v2.md** - Improved system prompt with:
   - ✅ Data dictionary embedded
   - ✅ Explicit rules: "use revenue_recognized for revenue"
   - ✅ Quarter-to-period mapping
   - ✅ Example correct queries

8. **data_dictionary.md** - Complete data dictionary for all warehouse tables

### ✅ Test Suite

9. **golden_set.jsonl** - 5 test cases including:
   - Q2 2026 revenue (the incident)
   - Q1 2026 revenue
   - Monthly revenue, order counts, refunds

10. **eval_judge.py** - Automated test runner
    - Checks answers match expected numbers
    - Validates SQL uses correct tables
    - Run before deploying any changes

---

## Quick Deploy

```bash
# 1. Copy fixed files to production
cp output/agent_v2.py ../agent.py
cp output/prompt_v2.md ../prompt.md

# 2. Test manually
python ../agent.py "what was our Q2 2026 revenue?"
# Should return ~$3.6M not ~$4.1M

# 3. Run automated tests
python eval_judge.py
# Should show PASS ✓

# 4. Check the trace log
tail agent_trace.jsonl
# Should show queries being logged
```

---

## Key Numbers

| Metric | Value |
|--------|-------|
| **FinBot answer (wrong)** | $4,138,212 |
| **Finance answer (correct)** | $3,638,336 |
| **Error** | $499,876 (14%) |
| **Root cause** | Wrong table (orders vs revenue_recognized) |

---

## Root Cause Summary

**What finbot did:**
```sql
SELECT SUM(amount) FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';
```
Result: $4.1M (includes cancelled orders, doesn't subtract refunds)

**What it should have done:**
```sql
SELECT SUM(net_amount) FROM revenue_recognized 
WHERE period IN ('2026-04', '2026-05', '2026-06');
```
Result: $3.6M (finance source of truth)

**Why it happened:** No data dictionary told the bot which table to use.

---

## Harness Issues Found

| Issue | Status | Impact |
|-------|--------|--------|
| No data dictionary | ❌ | Bot guessed wrong table |
| No test suite | ❌ | Error went to board |
| No read-only DB | 🔴 | Can DELETE tables (P0) |
| No iteration limit | ❌ | Infinite loop risk |
| No cost caps | ❌ | Token burn risk |
| No tracing | ❌ | Can't debug |

**All fixed in agent_v2.py + prompt_v2.md + test suite.**

---

## Model Swap Analysis

**Should we switch to opus or gpt-6?**

Not yet. The current model (sonnet-4-5) is fine. It executed the query correctly; the query was wrong because the bot had no guidance.

**How to decide:**
1. Deploy these fixes
2. Run golden_set.jsonl on current model → measure pass rate
3. Run golden_set.jsonl on opus/gpt-6 → measure pass rate  
4. Compare quality vs. cost

**Prediction:** Pass rate goes 0% → 80%+ with just the prompt fix.

---

## Next Steps

**Immediate (today):**
- [ ] Read EXECUTIVE_SUMMARY.md (Daniel)
- [ ] Read QUICK_START.md (Jonas)
- [ ] Deploy agent_v2.py (read-only DB - P0 security fix)

**This week:**
- [ ] Deploy prompt_v2.md (data dictionary)
- [ ] Run eval_judge.py (verify fix works)
- [ ] Correct board pre-read (Q2 = $3.6M)
- [ ] Add tracing to production

**This sprint:**
- [ ] Add golden_set.jsonl to CI/CD
- [ ] Cost monitoring dashboard
- [ ] Incident postmortem with team

---

## Questions?

- **"Did I break the model?"** No. Model is fine.
- **"Is this expensive to fix?"** No. Just deploy the files here.
- **"Will it happen again?"** Not if you run eval_judge.py before changes.
- **"Can I trust the bot now?"** After deploying agent_v2.py + prompt_v2.md, yes.

---

**Investigation by:** AI Assistant  
**For:** Daniel (CEO), Marta (VP Finance), Jonas (Data/FinBot Owner)  
**Methodology:** Harness-first diagnosis (see /home/user/.skills/harness-first)
