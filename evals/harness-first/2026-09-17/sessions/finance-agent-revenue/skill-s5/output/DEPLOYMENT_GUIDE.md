# FinBot Fix - Deployment Guide

**Issue:** Q2 revenue reported as $4.1M (wrong table), Finance close is $3.6M  
**Root Cause:** Missing data dictionary  
**Fix:** Add definitions, safety checks, and test suite  
**Deploy Time:** ~30 minutes  
**Risk:** LOW (read-only changes, adds safety)

---

## Pre-Deployment Checklist

- [ ] Read `EXEC_BRIEF.md` or `INCIDENT_REPORT.md` to understand the issue
- [ ] Backup current production files
- [ ] Have access to finbot deployment environment
- [ ] Can restart the Slack bot

---

## Deployment Steps

### 1. Backup Current Files (2 min)

```bash
cd /home/user/work
cp agent.py agent.py.backup.2026-09-16
cp prompt.md prompt.md.backup.2026-09-16
echo "Backed up to *.backup.2026-09-16"
```

### 2. Deploy Fixed Agent (5 min)

```bash
# Deploy agent with safety fixes:
# - Read-only DB connection
# - Max 10 iterations per question
# - Graceful failure message
cp output/fixes/agent.py agent.py

# Verify the changes
grep "mode=ro" agent.py  # Should find read-only connection
grep "MAX_TURNS" agent.py  # Should find iteration limit
```

**What changed:**
- Line 13: Added `MAX_TURNS = 10` constant
- Line 17: DB opens in read-only mode: `sqlite3.connect(f"file:{config.DB_PATH}?mode=ro", uri=True)`
- Line 23: Removed `conn.commit()` (not needed for reads)
- Lines 33-35: Loop now has iteration counter
- Lines 52-53: Graceful failure message after max turns

**Risk:** LOW - makes the agent safer, no behavior change for normal queries

### 3. Deploy Data Dictionary (10 min)

```bash
# Deploy prompt with metric definitions
cp output/fixes/prompt.md prompt.md

# Show what was added
diff prompt.md.backup.2026-09-16 prompt.md
```

**What changed:**
- Added full data dictionary section
- Defined "revenue" = `revenue_recognized.net_amount` (GAAP net)
- Documented all 5 tables with column descriptions
- Added query guidelines (when to use each table)

**Risk:** LOW - adds clarity, doesn't remove anything

### 4. Add Evaluation Suite (5 min)

```bash
# Copy eval files
cp -r output/fixes/evals ./

# Verify
ls -la evals/
# Should see: golden.jsonl, run_evals.py
```

### 5. Test the Fix (5 min)

```bash
# Option A: Run eval script (if agent environment is available)
cd evals
python run_evals.py

# Expected output:
# ✅ q2-2026-revenue: Expected $3,638,335.79
# ✅ q1-2026-revenue: Expected $3,285,493.84
# ... (6 tests)
# Results: 6/6 passed
```

```bash
# Option B: Manual test
cd ..
python agent.py "what was Q2 2026 revenue?"

# Expected: should mention ~$3.6M (from revenue_recognized table)
# If it says ~$4.1M, the fix didn't apply correctly
```

### 6. Deploy to Slack Bot (3 min)

```bash
# Your deployment process here, e.g.:
# - Restart the bot service
# - Push to repo and deploy via CI/CD
# - Copy files to production server

# Example (adjust for your setup):
# systemctl restart finbot
# or
# supervisorctl restart finbot
```

### 7. Verify in Slack (2 min)

In #ask-finance:
```
@finbot what was Q2 2026 revenue?
```

**Expected answer:** ~$3.6M or ~$3,638,336  
**If you get ~$4.1M:** The old prompt is still in use, check deployment

---

## Post-Deployment Checklist

- [ ] Verify Slack bot responds to test question with $3.6M
- [ ] Check that logs don't show SQL errors
- [ ] Run full eval suite: `cd evals && python run_evals.py`
- [ ] Monitor #ask-finance for any user reports of issues
- [ ] Update team: post in #data that fix is deployed

---

## Rollback Plan (if needed)

If the bot breaks or gives worse answers:

```bash
# Restore backups
cd /home/user/work
cp agent.py.backup.2026-09-16 agent.py
cp prompt.md.backup.2026-09-16 prompt.md

# Restart bot
# (your restart command)

# Report issue to data team
```

**When to rollback:**
- Bot crashes on normal questions
- Eval script shows <80% pass rate
- Users report widespread wrong answers

**When NOT to rollback:**
- One edge case fails (fix forward instead)
- Answers are different but still reasonable (investigate first)

---

## Testing Scenarios

After deployment, test these questions:

### Should Work (Expected Behavior)

| Question | Expected Answer | Table Used |
|----------|----------------|------------|
| "what was Q2 2026 revenue?" | ~$3.6M | revenue_recognized |
| "what was Q1 revenue?" | ~$3.3M | revenue_recognized |
| "how many Q2 orders were cancelled?" | 202 | orders |
| "how many orders in Q2?" | 2213 | orders |
| "how much did we refund in Q2?" | ~$355K | refunds |

### Edge Cases to Watch

| Question | Notes |
|----------|-------|
| "Q2 gross revenue" | Should clarify gross vs. net, or ask user |
| "orders revenue Q2" | Might be ambiguous - should use revenue_recognized |
| "total order value Q2" | Could use orders table (GMV), distinct from revenue |

---

## Monitoring After Deployment

### Week 1
- [ ] Check #ask-finance daily for user feedback
- [ ] Review any "I couldn't answer" messages (hit max turns)
- [ ] Run eval suite if prompt changes

### Week 2
- [ ] Collect new questions from Slack
- [ ] Add to golden set (expand to 20+ cases)
- [ ] Audit old Slack threads for similar issues

### Month 1
- [ ] Add structured logging (conversation ID, tokens, cost)
- [ ] Create cost dashboard
- [ ] Document runbook for "wrong answer" incidents

---

## FAQ

**Q: Will this change existing Slack threads?**  
A: No, past messages stay the same. Only new questions use the new prompt.

**Q: Do we need to tell users?**  
A: Optional. Could post: "FinBot now has clearer definitions for revenue and other metrics. Let us know if you see any issues!"

**Q: What if someone asks about the $4.1M in the board deck?**  
A: Explain: "That was gross order value. The correct GAAP net revenue is $3.6M. We've updated the bot's definitions."

**Q: Will this make the bot slower?**  
A: No, same speed. The data dictionary is just text in the prompt.

**Q: Can this break other questions?**  
A: Unlikely. The data dictionary only adds clarity. Old queries should still work or work better.

**Q: When can we add more features?**  
A: After running the eval suite on your changes. Don't deploy without passing tests.

---

## Success Criteria

Deployment is successful if:
- ✅ Eval script passes (6/6 tests)
- ✅ "Q2 revenue" question returns ~$3.6M
- ✅ Bot doesn't crash or show SQL errors
- ✅ Users don't report regressions

If all ✅, proceed to post-deployment monitoring.

---

## Contact

**Fix prepared by:** AI Investigation Team  
**Owner:** Jonas (Data Team)  
**Questions:** #data Slack channel

**Files:**
- `output/fixes/agent.py` - safe agent
- `output/fixes/prompt.md` - data dictionary
- `output/fixes/evals/` - test suite
