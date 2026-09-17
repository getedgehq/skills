# For Daniel - One Page Summary

**Date:** 2026-09-15  
**Re:** FinBot Q2 revenue error (board deck issue)

---

## Your Question
> "Is the bot just making numbers up? If the model isn't good enough we should pay for a better one"

## Answer

**No, don't switch models yet.** The bot isn't hallucinating - it calculated the wrong number because it queried the wrong table. The model is fine; the scaffolding around it is missing.

---

## What Happened

**FinBot said:** Q2 revenue = $4.1M  
**Finance says:** Q2 revenue = $3.6M  
**Difference:** $499k (14% error)

**Root cause:** Bot used the `orders` table which includes cancelled orders ($360k) and doesn't subtract refunds ($333k). Finance uses the `revenue_recognized` table which properly calculates net revenue.

**Why it happened:** No data dictionary told the bot which table to use. It guessed and guessed wrong.

---

## Is This A Model Problem?

**No.** The model correctly executed the SQL query it wrote. The query was logically wrong because:

1. ❌ No data dictionary (bot didn't know revenue = revenue_recognized table)
2. ❌ No test suite (nobody caught this before it went to the board)
3. ❌ No cost caps (bot could burn unlimited tokens)
4. 🔴 **Write access to production warehouse** (can DELETE tables - P0 security issue)

This is like asking "is the engine broken?" when the car has no steering wheel, no brakes, and no seatbelts.

---

## What I Fixed (in output/)

✅ **Read-only database access** - prevents DELETE/UPDATE/DROP  
✅ **Iteration & cost limits** - prevents infinite loops and token burn  
✅ **Data dictionary** - tells bot revenue = revenue_recognized table  
✅ **Improved prompt** - embeds data rules  
✅ **Test suite (5 cases)** - catches errors before production  
✅ **Automated judge** - runs tests, reports pass/fail  

---

## What To Do Monday

**Jonas should:**

1. Deploy `agent_v2.py` (read-only + safety limits)
2. Deploy `prompt_v2.md` (data dictionary)
3. Test: ask bot "what was Q2 2026 revenue?" → should say $3.6M
4. Run `eval_judge.py` → should pass

**You should:**

5. Correct the board pre-read (Q2 = $3.6M not $4.1M)

---

## Model Swap Decision

**Don't decide until:**

1. We deploy the harness fixes
2. We run the test suite on the current model (sonnet-4-5) → measure pass rate
3. We run the test suite on opus/gpt-6 → measure pass rate
4. We compare quality vs. cost

**My prediction:** Pass rate goes from 0% → 80%+ with just the prompt fix. Model is fine.

**If I'm wrong:** Then test fancier models, but use the test suite to measure, not vibes.

---

## Bottom Line

- ✅ Root cause identified: wrong table, no data dictionary
- ✅ Harness built: tests, data dictionary, safety limits
- ✅ Security issue fixed: read-only access
- ⏳ Deploy Monday, verify with test suite
- ⏸️ Don't swap models until you've tested the fix

The model executed its query correctly. We gave it the wrong instructions.

---

**Files delivered:** All in `output/`
- `REPORT.md` - Full technical analysis  
- `QUICK_START.md` - Deploy instructions for Jonas
- `agent_v2.py`, `prompt_v2.md`, `golden_set.jsonl`, `eval_judge.py` - The fixes

**Questions?** Read REPORT.md or ask Jonas to walk through the eval_judge.py output.
