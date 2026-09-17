# FinBot Fix Action Plan

**Priority:** 🔴 URGENT - Production system with dangerous gaps and known wrong answers in board materials

**Target:** Fix before next board meeting (and before FinBot is used again)

---

## Immediate Actions (TODAY - 2026-09-16)

### 1. Stop Using Current FinBot ✋
**Owner:** Jonas (Data team)  
**Action:** 
- Post in #ask-finance: "FinBot is temporarily offline for fixes. Ask finance questions in this channel instead."
- Disable the bot or add a warning message until fixes are deployed

**Why:** Current version has dangerous write permissions and no iteration limits. Could damage warehouse or burn tokens.

---

### 2. Correct Board Pre-Read 📊
**Owner:** Priya (Strategy) + Marta (Finance)  
**Action:**
- Update board deck: Q2 2026 revenue is **$3,638,335.79** (not $4.1M)
- Add note: "Prior version cited $4.1M due to data source error (included cancelled orders). Corrected to $3.6M per GAAP close."

**Why:** Board meeting is soon; wrong number is currently in materials.

---

### 3. Audit Other FinBot Answers 🔍
**Owner:** Finance team (Marta) + Data team (Jonas)  
**Action:**
- Export all FinBot transcripts from #ask-finance since March
- Recompute any "revenue" answers using `revenue_recognized` table
- Flag any answers that went into board materials, exec reports, or external communications
- Publish list of corrected numbers

**Why:** If Q2 was wrong, other periods may also be wrong. Need to know scope of impact.

---

## Blocking Fixes (THIS WEEK - Deploy by Friday 2026-09-20)

### 4. Add Max Iterations Limit 🚨
**Owner:** Jonas  
**File:** `agent.py`  
**Change:**
```python
MAX_ITERATIONS = 5  # Add this constant

for iteration in range(MAX_ITERATIONS):  # Change 'while True:' to this
    # ... existing loop code
    
# After loop:
return f"Error: Could not answer within {MAX_ITERATIONS} iterations."
```

**Test:** Try a question that causes SQL errors. Verify it stops after 5 tries.

**Why:** Infinite loops can burn unlimited tokens. This is a critical safety issue.

---

### 5. Switch to Read-Only Database Connection 🔒
**Owner:** Jonas  
**File:** `agent.py`, function `run_sql`  
**Change:**
```python
# OLD:
conn = sqlite3.connect(config.DB_PATH)

# NEW:
conn = sqlite3.connect(f'file:{config.DB_PATH}?mode=ro', uri=True)

# REMOVE this line:
# conn.commit()  ← delete this
```

**Test:** 
- Try a SELECT query: should work
- Try an INSERT query: should fail with "readonly database" error

**Why:** Bot should never write to warehouse. Current code allows DELETE, UPDATE, DROP TABLE.

---

### 6. Add Data Dictionary to Prompt 📖
**Owner:** Jonas + Marta (to review definitions)  
**File:** `prompt.md`  
**Change:** Replace current table list with clear definitions

**Use:** `output/prompt_fixed.md` as template (includes key rule: revenue = revenue_recognized.net_amount)

**Test:** Run golden set question: "what was Q2 2026 revenue?" Should now use correct table.

**Why:** Root cause of incident—prompt didn't define what "revenue" means.

---

### 7. Create & Test Golden Set ✅
**Owner:** Jonas  
**Files:** 
- Create: `evals/golden_set.jsonl` (use `output/golden_set.jsonl` as starting point)
- Create: `evals/eval.py` (use `output/eval.py` as template)

**Action:**
1. Copy golden set to repo: `mkdir evals && cp output/golden_set.jsonl evals/`
2. Add 10 more cases from real Slack history
3. Run: `python evals/eval.py --golden evals/golden_set.jsonl`
4. Fix any failures before deploying

**Test:** Run eval.py with current agent (expect failures), then with fixed agent (expect passes)

**Why:** Prevents regressions. Can't deploy changes without knowing if they break things.

---

### 8. Add Basic Logging 📝
**Owner:** Jonas  
**File:** `agent.py`  
**Change:** Add logging for:
- Conversation ID (generate uuid per question)
- Question asked
- SQL queries executed
- Iterations used
- Tokens used (if available from llm_client)
- Final answer
- Errors

**Use:** `output/agent_fixed.py` as reference

**Storage:** Log to `logs/finbot.log` (add to .gitignore)

**Why:** Need audit trail. Can't debug issues without knowing what happened.

---

## Important (NEXT SPRINT - by 2026-09-27)

### 9. Deploy Fixed Version
**Owner:** Jonas  
**Action:**
1. Deploy fixes #4-8 to production
2. Test with golden set (should pass 100%)
3. Test manually with 5 recent Slack questions
4. Re-enable bot in #ask-finance
5. Post: "FinBot is back online with fixes. Please report any odd answers to #ask-data."

---

### 10. Create Data Dictionary Document
**Owner:** Jonas (draft) + Marta (review)  
**File:** Create `docs/data_dictionary.md`  

**Use:** `output/data_dictionary.md` as template

**Contents:**
- Definition of every metric (revenue, bookings, refunds, etc.)
- Which table/column to use for each
- Date filtering examples
- Common question patterns

**Review:** Finance team reviews and approves (Marta signs off)

**Why:** Single source of truth for data definitions. Prevents future ambiguity.

---

### 11. Add CI Check for Golden Set
**Owner:** Jonas  
**Action:**
- Add GitHub Action (or equivalent) that runs `evals/eval.py` on every PR
- Block merge if any golden set case fails
- Require golden set pass before deploying to production

**Why:** Prevents deploying changes that break known-good answers.

---

### 12. Add Per-Run Cost Cap
**Owner:** Jonas  
**Action:**
- Track tokens per run (llm_client needs to return usage)
- Add config: `MAX_TOKENS_PER_RUN = 10000` 
- Stop early if exceeded, return error message

**Why:** Prevents single question from burning excessive tokens.

---

### 13. Create SQL Views for Common Metrics
**Owner:** Jonas + Data Engineering  
**Action:** Add views to warehouse:

```sql
CREATE VIEW quarterly_revenue AS
SELECT 
  CASE 
    WHEN period IN ('2026-01','2026-02','2026-03') THEN '2026-Q1'
    WHEN period IN ('2026-04','2026-05','2026-06') THEN '2026-Q2'
    WHEN period IN ('2026-07','2026-08','2026-09') THEN '2026-Q3'
    WHEN period IN ('2026-10','2026-11','2026-12') THEN '2026-Q4'
  END as quarter,
  SUM(net_amount) as revenue
FROM revenue_recognized
GROUP BY quarter;
```

Update prompt to mention these views.

**Why:** Makes it easier for model (and humans) to query common patterns correctly.

---

### 14. Expand Golden Set
**Owner:** Jonas  
**Target:** 30+ test cases  
**Sources:**
- All questions from #ask-finance Slack export (March-September)
- Edge cases (cancelled orders, partial refunds, date boundaries)
- Multi-step questions (comparisons, trends)

**Why:** 10 cases is minimum; 30+ gives better coverage.

---

## Medium-term (NEXT QUARTER)

### 15. Add Approval Workflow for High-Stakes Answers
**Owner:** Jonas + Product  
**Action:**
- Detect "board" or "exec" keywords in questions
- If high-stakes, return: "Draft answer: $X.XM. React with ✅ to post, or ask @finance-team to verify."
- Require human approval before posting final answer

**Why:** Prevents wrong numbers from reaching board/exec materials.

---

### 16. Build Admin Dashboard
**Owner:** Jonas  
**Features:**
- Daily usage stats (questions asked, tokens used, cost)
- Common questions
- Error rate
- Flag questions that may need review

**Why:** Visibility into how FinBot is being used and if it's working.

---

### 17. Add Prompt Versioning
**Owner:** Jonas  
**Action:**
- Track prompt.md in git with version tags
- Log which prompt version was used for each question
- Can rollback if new prompt causes issues

**Why:** Enables safe iteration on prompt. Can test changes and roll back.

---

### 18. Document Incident Response Process
**Owner:** Jonas  
**Action:** Create runbook for "FinBot gave wrong answer":
1. Stop the bot
2. Audit impact (who saw the answer? what was it used for?)
3. Issue correction
4. Add case to golden set
5. Fix root cause
6. Test with golden set
7. Deploy fix
8. Re-enable bot

**Why:** Having a process reduces panic and speeds recovery.

---

## Model Upgrade Evaluation (ONLY AFTER FIXES)

### 19. Test Model Upgrade (If Desired)
**Owner:** Jonas  
**Prerequisite:** All above fixes deployed  
**Action:**
1. Run golden set on current model (Claude Sonnet 4.5): record accuracy, cost, latency
2. Run golden set on candidate model (Claude Opus or GPT-6): record same metrics
3. Compare:
   - Accuracy difference
   - Cost difference
   - Latency difference

**Decision criteria:**
- If accuracy improves by <5% and cost increases by >50%: **Don't upgrade**
- If accuracy improves by >10% at similar cost: **Consider upgrade**
- If current model gets 100% on golden set: **No reason to upgrade**

**Expected outcome:** With fixed prompt (data dictionary), both models will likely get 100%. Cost becomes the deciding factor.

**Why:** Test with evidence, not vibes. Harness fixes likely solve the problem without model change.

---

## Risks & Blockers

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Board meeting before fix | High | Correct deck today (#2) |
| Other wrong answers in flight | Medium | Audit (#3) |
| Team wants to keep using bot | High | Disable until fixes deployed (#1) |
| Finance disagrees with data definitions | High | Get Marta sign-off on data dictionary (#10) |
| Golden set too small | Medium | Expand to 30+ cases (#14) |
| No time to fix everything | Medium | Prioritize blocking fixes (#4-8) first |

---

## Success Metrics

**Week 1:**
- ✅ Board deck corrected
- ✅ Bot disabled until fixes deployed
- ✅ 5 blocking fixes completed

**Week 2:**
- ✅ Golden set created (10+ cases)
- ✅ Fixed version passes 100% of golden set
- ✅ Fixed version deployed to production
- ✅ Data dictionary reviewed by Finance

**Week 4:**
- ✅ 30+ cases in golden set
- ✅ CI runs golden set on every PR
- ✅ No wrong-answer incidents since fix

**Quarter:**
- ✅ High-stakes approval workflow live
- ✅ Admin dashboard tracking usage
- ✅ Incident response runbook documented

---

## Appendix: Files Delivered

All deliverables are in `output/`:

1. **EXECUTIVE_SUMMARY.md** - One-pager for Daniel (CEO)
2. **ROOT_CAUSE_ANALYSIS.md** - Detailed incident writeup
3. **HARNESS_AUDIT.md** - Full harness assessment (6 components)
4. **data_dictionary.md** - Metric definitions for warehouse
5. **golden_set.jsonl** - 10 test cases with expected answers
6. **eval.py** - Judge script to run golden set
7. **agent_fixed.py** - Fixed agent code (reference implementation)
8. **prompt_fixed.md** - Fixed prompt with data dictionary
9. **ACTION_PLAN.md** - This document

---

**Plan Owner:** Jonas Feld (Data team)  
**Plan Review:** Daniel Kurz (CEO), Marta Oyelaran (VP Finance)  
**Plan Date:** 2026-09-16  
**Target Completion:** Blocking fixes by 2026-09-20, all urgent items by 2026-09-27
