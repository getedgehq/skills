# FinBot Quick Fix - DO THIS FIRST

## 🔴 CRITICAL: The bot can delete data

Current bot can execute DELETE/UPDATE/DROP on the warehouse.

**Fix now:** Use `agent_v2.py` which connects read-only.

---

## ⚠️ The Q2 Board Deck Error

**What happened:** FinBot said Q2 revenue was $4.1M. Finance says $3.6M.

**Why:** Bot used `orders` table (includes cancelled orders) instead of `revenue_recognized` table.

**Fix:** Use `prompt_v2.md` which tells bot to use `revenue_recognized` for revenue questions.

---

## ✅ Quick Deploy Checklist

1. **Replace prompt:**
   ```bash
   cp output/prompt_v2.md prompt.md
   ```

2. **Replace agent (or merge changes):**
   ```bash
   cp output/agent_v2.py agent.py
   # OR: merge the read-only connection + max iterations changes
   ```

3. **Test it works:**
   ```bash
   python agent.py "what was our Q2 2026 revenue?"
   # Should return ~$3.6M not $4.1M
   ```

4. **Run regression test:**
   ```bash
   cd output && python3 eval_judge.py
   # Should show PASS ✓
   ```

---

## 📊 Verify The Fix

The correct Q2 2026 revenue query is:

```sql
SELECT SUM(net_amount) 
FROM revenue_recognized 
WHERE period IN ('2026-04', '2026-05', '2026-06')
```

Result: **$3,638,335.79** (~$3.6M)

The old wrong query was:

```sql
SELECT SUM(amount) 
FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30'
```

Result: $4,138,212.16 (~$4.1M) ❌

---

## 🛡️ What The Fixes Do

### agent_v2.py
- ✅ Read-only database (can't DELETE/UPDATE/DROP)
- ✅ Max 5 iterations (prevents infinite loops)
- ✅ 50k token cap per question (prevents cost explosions)
- ✅ Logs all queries to agent_trace.jsonl (for debugging)

### prompt_v2.md
- ✅ Explicitly tells bot: "use revenue_recognized for revenue"
- ✅ Maps Q2 → periods '2026-04', '2026-05', '2026-06'
- ✅ Shows example correct queries

### golden_set.jsonl + eval_judge.py
- ✅ 5 test cases including the Q2 revenue question
- ✅ Run before deploying any changes
- ✅ Prevents regression

---

## 📞 Questions?

- **"Is the model bad?"** No. Model executed the query correctly. Query was wrong because bot had no data dictionary.
- **"Should we switch models?"** Not yet. Fix the harness first, then test both models with the golden set.
- **"Can I use the bot now?"** Only after deploying agent_v2.py (read-only) and prompt_v2.md (data dictionary).

---

See `REPORT.md` for full analysis.
