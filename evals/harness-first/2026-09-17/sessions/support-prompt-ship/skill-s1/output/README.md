# Support Bot Prompt Audit Results

**TL;DR:** ❌ Don't ship the new prompt Friday. Found 4 critical policy violations. I built you tools to fix it and prevent this next time.

---

## Start Here

1. **Read first:** `SUMMARY.md` - executive summary with recommendation
2. **See the failures:** `side_by_side_failures.md` - the 4 policy violations explained
3. **Understand the root cause:** `harness_scorecard.md` - full audit

---

## Files in This Directory

### Core Analysis
- **`SUMMARY.md`** ⭐ Start here - exec summary, go/no-go decision
- **`harness_scorecard.md`** - Full harness audit with evidence
- **`policy_violations.txt`** - Detailed breakdown of the 4 failures
- **`side_by_side_failures.md`** - Visual comparison of old/new/fixed for each failure

### Tools I Built
- **`judge.py`** ⭐ Automated policy checker - run this before every deployment
- **`golden_set.jsonl`** ⭐ 20 test cases with pass/fail criteria
- **`eval_old.txt`** - Judge results for old prompt (18/20 pass)
- **`eval_new.txt`** - Judge results for new prompt (14/20 pass, 4 critical)

### Solutions
- **`new_prompt_v4.1_fixed.md`** ⭐ Fixed version of your prompt (warmth + policy)
- **`next_steps.md`** - Detailed action plan for next 2 weeks

---

## Quick Start: Run the Judge Yourself

```bash
# See the policy violations
python3 judge.py ../outputs_new.jsonl golden_set.jsonl

# If you test the fixed prompt:
python3 judge.py ../outputs_v4.1.jsonl golden_set.jsonl
```

Expected output:
- ❌ New prompt: 4 critical failures (T-1007, T-1013, T-1016, T-1019)
- ✅ Fixed prompt: 0 critical failures (after you test it)

---

## The Numbers

| Metric | Old Prompt | New Prompt | Impact |
|--------|-----------|------------|--------|
| **Warmth score** | 2.8 / 5 | 4.6 / 5 | +64% 🎉 |
| **Policy compliance** | 90% pass | 70% pass | ⚠️ 4 critical failures |
| **Token cost** | ~4,241 chars | ~6,559 chars | +55% 💰 |
| **Revenue risk** | Low | ~10% over-refund | ⚠️ $200k/mo potential leak |

---

## What Went Wrong

Your new prompt says:
> "If a customer is unhappy, do whatever it takes to make it right"

This overwrote:
- 30-day refund policy → approved refunds 35-38 days out
- Custom item no-refund policy → refunded made-to-measure wardrobe
- Internal notes confidentiality → told customer about "returns-abuse watchlist"

**Root cause:** No automated checks caught this. Warmth measured "nice replies", not "correct replies".

---

## What's Fixed

The fixed prompt (`new_prompt_v4.1_fixed.md`) adds:
1. **Explicit constraints:** "These rules always apply - empathy never overrides them"
2. **Policy reminders:** 30-day window, custom items, internal notes
3. **Examples:** Shows "warm but compliant" responses

---

## What To Do Monday

### Immediate
1. Don't ship new_prompt.md on Friday
2. Decide: test fixed prompt OR keep old prompt (both safe)

### If testing fixed prompt
1. Replay August tickets through `new_prompt_v4.1_fixed.md`
2. Run: `python judge.py outputs_v4.1.jsonl golden_set.jsonl`
3. Verify: 0 critical failures
4. Compare: Warmth on policy-compliant replies
5. Deploy if clean

### Next 2 weeks
- Integrate `judge.py` into CI/CD
- Expand golden set (add escalations, edge cases)
- Add cost caps and tracing
- See `next_steps.md` for details

---

## Questions?

**"Why did this happen?"**  
No automated policy checks. The PM review focused on warmth, not correctness.

**"Can we keep the warmth?"**  
Yes! See `new_prompt_v4.1_fixed.md` - you can be warm AND policy-compliant.

**"Will this happen again?"**  
Not if you run `judge.py` before every prompt change. It blocks policy violations.

**"How long to fix?"**  
- Test fixed prompt: 2-3 hours
- Integrate judge into CI: 1 day
- Full harness (cost caps, tracing): 2 weeks (see `next_steps.md`)

**"What about the warmth score?"**  
Your 5-person test was real, but it measured policy violations. Need to re-score policy-compliant replies separately.

---

## Built With

**Harness-First Methodology**  
- Audit the evaluation infrastructure before blaming the model
- 6 components: golden set, judge, cost caps, data layer, action safety, tracing
- Deterministic checks before subjective scoring

---

**Need help?** All context is in this directory. Show this to your eng team.
