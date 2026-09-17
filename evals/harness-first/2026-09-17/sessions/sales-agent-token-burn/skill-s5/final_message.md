Perfect! Now let me create a final summary for you:

---

## Summary for You

**Don't switch models yet.** Three harness bugs caused your 4x cost spike, not Sonnet being "overkill."

### The Three Bugs (I Fixed Them)

1. **Prompt bug** (`agent/prompts.py`): "Call crm_get_account at the start of EVERY turn" → re-fetched 30-40KB account data on every turn, wasting 6.4M tokens
2. **No iteration limit** (`agent/loop.py`): `while True:` with no max → 5 conversations (11% of volume) looped 16-26 turns and burned $18.77 of your $26.66 (70% of cost)
3. **Retry on permanent errors** (`agent/tools.py`): Retried ALL errors 4x including 404 "account_merged" and 422 "unknown field: lead_score_v2"

### Cost Comparison

| Option | Monthly Cost | Savings |
|--------|--------------|---------|
| Current (Sonnet, bugs) | **$53.32** | baseline |
| Switch to Haiku (no fixes) | $17.78 | 67% |
| **Fix harness (keep Sonnet)** | **$14.82** | **72%** ← DO THIS |
| Fix harness + Haiku | $4.94 | 91% ← THEN THIS |

**Key insight:** Harness fixes save MORE than switching to Haiku without fixes ($14.82 vs $17.78/month).

### What I Delivered

**Code fixes (ready to deploy):**
- ✅ `agent/prompts.py` - Changed "EVERY turn" to "ONCE at the start"
- ✅ `agent/loop.py` - Added `max_iterations=10`
- ✅ `agent/tools.py` - Only retry transient errors (429, 502-504)

**Harness components:**
- ✅ `output/golden_set.jsonl` - 5 test cases from incidents
- ✅ `output/judge.py` - Automated quality validator
- ✅ `output/cost_calculator.py` - Cost comparison tool
- ✅ `output/HARNESS_AUDIT_REPORT.md` - Full analysis with file:line evidence
- ✅ `output/EXECUTIVE_SUMMARY.md` - One-page overview
- ✅ `output/ANSWER.txt` - Complete answer

### Recommendation

1. **This week:** Deploy the 3 fixed files from `agent/`, test on 2-3 leads
2. **Check with CRM admin:** Does `lead_score_v2` field exist? (It's causing 422 errors that triggered 4 of the 5 expensive loops)
3. **Next week:** Run `judge.py` on new traces to validate fixes worked
4. **After validation:** Consider Haiku for additional 67% savings, but validate quality first with the golden set

**About Haiku:** Yes, it makes sense for cold emails (not reasoning-heavy), but only AFTER fixing the bugs. Otherwise you're paying Haiku prices for infinite loops.

### Files to Read

Start with `output/EXECUTIVE_SUMMARY.md` (5 min read), then run `python3 output/cost_calculator.py` to see the numbers.