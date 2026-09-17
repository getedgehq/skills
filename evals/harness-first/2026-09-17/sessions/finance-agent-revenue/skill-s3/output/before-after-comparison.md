# Before vs After: The Q2 Revenue Question

## The Question
**Priya:** "what was our Q2 2026 revenue?"

---

## Current Agent (with original prompt.md)

### What the agent does:
1. Reads prompt: "use the `run_sql` tool to query the warehouse"
2. Lists available tables: customers, orders, refunds, revenue_recognized, daily_kpis
3. Prompt says "If a question is about money, always give a single headline number with a dollar sign"
4. Model picks `orders` table (reasonable: it's listed, has `amount` column, dates match)
5. Generates query:
```sql
SELECT ROUND(SUM(amount), 2) AS revenue 
FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';
```
6. Result: `{"columns": ["revenue"], "rows": [[4138212.16]]}`
7. Answers: "Q2 2026 revenue was **$4,138,212.16** (~$4.1M)."

### Why this is wrong:
- This is **gross bookings** (orders placed), not **GAAP revenue** (revenue recognized)
- Finance reports $3.6M to the board (from `revenue_recognized.net_amount`)
- **$500k error** (13.7% overstatement)
- Goes into board deck → embarrassment + credibility loss

---

## Fixed Agent (with recommended-prompt.md)

### What the agent does:
1. Reads prompt: "When someone asks about 'revenue,' they mean GAAP recognized revenue (net of refunds). Always use `revenue_recognized.net_amount`"
2. Sees explicit instruction: "Filter by `recognized_on` (NOT `orders.created_at`)"
3. Sees warning: "Never use `orders.amount` for revenue questions"
4. Generates query:
```sql
SELECT ROUND(SUM(net_amount), 2) AS revenue
FROM revenue_recognized
WHERE recognized_on >= '2026-04-01' AND recognized_on <= '2026-06-30';
```
5. Result: `{"columns": ["revenue"], "rows": [[3638335.79]]}`
6. Answers: "Q2 2026 revenue was **$3,638,335.79** (~$3.6M)."

### Why this is correct:
- Matches finance's official Q2 close ($3.6M)
- Uses the same table finance uses for board reporting
- Net of refunds, with proper revenue recognition timing
- Safe to put in board deck

---

## Side-by-Side Comparison

| Aspect | Current Agent | Fixed Agent |
|--------|---------------|-------------|
| **Answer** | $4,138,212.16 | $3,638,335.79 |
| **Table used** | `orders` | `revenue_recognized` |
| **What it measures** | Gross bookings | GAAP net revenue |
| **Matches finance?** | ❌ Off by $500k | ✅ Matches $3.6M |
| **Safe for board deck?** | ❌ No | ✅ Yes |
| **Root cause** | Ambiguous prompt | Clear data dictionary |

---

## The Model Did Nothing Wrong

- Both answers are **factually accurate** for the table queried
- The model followed instructions correctly in both cases
- The problem is **ambiguous source data with no definition**
- Switching models won't fix this—GPT-6 or Opus would make the same mistake

---

## What Changed (Technically)

### Prompt additions:
1. **Data dictionary section** defining revenue
2. **Explicit table selection rule** for "revenue" questions
3. **Warning about orders.amount** to prevent the wrong table
4. **Query examples** showing correct vs incorrect patterns

### Agent code changes (agent-v2.py):
1. **Read-only database connection** (`mode=ro`)
2. **Max iteration limit** (10 turns, not infinite)
3. **Query logging** (every SQL query → `logs/queries.jsonl`)
4. **Conversation logging** (every Q&A → `logs/conversations.jsonl`)
5. **Dangerous keyword blocking** (no INSERT/UPDATE/DELETE)

### New harness components:
1. **Golden set** (20 test cases including this incident)
2. **Judge script** (automated pass/fail checker)
3. **Data dictionary** (canonical definitions for all metrics)

---

## Deployment Plan

### Option A: Hotfix (deploy today, before board meeting)
1. Replace `prompt.md` with `output/recommended-prompt.md`
2. Test with the Q2 question manually
3. Post correction in #exec-staff
4. Update board deck with correct $3.6M

### Option B: Full fix (deploy this week)
1. Deploy `agent-v2.py` (with safety rails)
2. Deploy new prompt
3. Set up `logs/` directory for query logging
4. Add golden set to CI/CD (run on every change)

### Option C: Both (recommended)
1. Today: Hotfix prompt only (test manually)
2. This week: Deploy agent-v2.py + golden set + judge
3. This month: Expand golden set, add cost caps, set up eval dashboard

---

## Cost Impact

### Current burn (estimated from vibes, no tracing):
- ~500 questions/week in #ask-finance
- Some hit infinite retry loops (no max iterations)
- No logging, so we don't know actual cost

### After fix:
- Same 500 questions/week
- Max 10 iterations each (capped)
- Query logging shows exactly which questions are expensive
- Can optimize or add caching based on real data

**Bottom line:** Fix the harness first, measure actual cost, *then* decide if a cheaper model makes sense. Right now we're flying blind.
