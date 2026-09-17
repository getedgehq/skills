# FinBot Deployment Checklist

**Purpose:** Ensure safe deployment of Q2 revenue incident fix  
**Owner:** Jonas (Data team)  
**Stakeholders:** Marta (Finance), Daniel (CEO), Priya (Strategy)  
**Target:** Deploy after manual review complete

---

## Pre-Deployment (BLOCKING)

### [ ] 1. Manual Review of Recent Answers (Marta + Jonas)
**Timeline:** 1-2 days  
**Steps:**
1. Jonas: Export all #ask-finance Slack threads from past 30 days containing:
   - "revenue"
   - "ARR" or "annual recurring revenue"
   - "MRR" or "monthly recurring revenue"
   - "bookings"
   - "Q1", "Q2", "Q3", "Q4"
2. Marta: For each answer, verify against official finance numbers:
   - Q1 2026 revenue: $3,285,493.84
   - Q2 2026 revenue: $3,638,335.79
   - Apr 2026: $1,237,516.63
   - May 2026: $1,209,658.31
   - Jun 2026: $1,191,160.85
3. Document findings:
   - ✅ Correct answers
   - ❌ Wrong answers (like the Q2 incident)
   - ⚠️ Ambiguous/unclear answers
4. For wrong answers: Identify who received them, notify if used in materials
5. Create `review_results.md` with summary

**Exit criteria:** Marta signs off that all wrong answers have been identified and communicated.

---

## Deployment Steps

### [ ] 2. Backup Current System
```bash
cd /home/user/work
cp -r . ../finbot_backup_$(date +%Y%m%d)
```

### [ ] 3. Deploy Fixed Files
```bash
# Replace prompt
cp output/prompt_fixed.md prompt.md

# Replace agent code
cp output/agent_fixed.py agent.py

# Add data dictionary (new file)
cp output/data_dictionary.md ./

# Create logs directory for tracing
mkdir -p logs
```

### [ ] 4. Update Config (if needed)
```bash
# Verify config.py settings
cat config.py
# Should have:
# - DB_PATH = "warehouse.db"
# - MODEL = "claude-sonnet-4-5"  (no change needed)
# - MAX_ROWS = 200
# - TEMPERATURE = 0.2
```

### [ ] 5. Test on Golden Set
```bash
# Run eval script (requires FINBOT_GATEWAY_TOKEN)
export FINBOT_GATEWAY_TOKEN="<token>"
python output/evals/run_eval.py --live

# Expected: 10/10 tests pass (or document failures)
```

### [ ] 6. Smoke Test Critical Questions
Manually test via Slack or CLI:
```bash
python agent.py "what was our Q2 2026 revenue?"
# Expected: $3,638,335.79 (or ~$3.6M)

python agent.py "what was Q1 2026 revenue?"
# Expected: $3,285,493.84 (or ~$3.3M)

python agent.py "revenue in April 2026"
# Expected: $1,237,516.63 (or ~$1.2M)
```

### [ ] 7. Update Documentation
```bash
# Update README.md
cat >> README.md << 'EOF'

## Data Dictionary
See `data_dictionary.md` for definitions of all metrics (IMPORTANT!)

## Evaluation
Golden test set: `output/evals/golden.jsonl`
Run tests: `python output/evals/run_eval.py`

## Tracing
All conversations logged to `logs/finbot_trace.jsonl`
EOF
```

### [ ] 8. Deploy to Production Slack Bot
```bash
# Restart Slack bot service with new code
# (Exact steps depend on your deployment setup)
systemctl restart finbot  # or similar
```

---

## Post-Deployment

### [ ] 9. Monitor for 24 Hours
- Check `logs/finbot_trace.jsonl` for:
  - Any errors
  - Max iteration hits
  - Retry loops detected
  - Unexpected SQL queries
- Review first 10-20 answers in #ask-finance
- Compare answers to expected values

### [ ] 10. Communication
**Internal announcement in #ask-finance:**
```
📢 FinBot has been updated with improved accuracy for financial metrics.

What changed:
- More precise handling of revenue vs. bookings
- Better data validation
- All answers now logged for audit

If you used FinBot for revenue numbers in the past 30 days, please verify 
against official finance numbers (see pinned message).

Questions? Ask Jonas or Marta.
```

**Exec team update (Daniel, Marta, Priya):**
```
✅ FinBot Q2 revenue issue resolved
- Root cause: Data table ambiguity (not model)
- Fix: Data dictionary + clearer prompt + safety improvements
- Manual review: [X wrong answers found, Y teams notified]
- Status: Deployed and monitoring

Safe to use for internal analysis. 
For board/investor materials: still recommend finance team review.
```

### [ ] 11. Create Pre-Deployment Checklist for Future Changes
Add to `CONTRIBUTING.md` or similar:
```markdown
## Before Changing FinBot

Any changes to prompt, tools, or data access MUST:
1. Run golden set evaluation (`python output/evals/run_eval.py`)
2. Document expected behavior changes
3. Get Finance team sign-off for metric changes
4. Update data dictionary if new metrics added
```

---

## Rollback Plan

If issues found post-deployment:

### [ ] Rollback Steps
```bash
# Restore backup
cd /home/user
rm -rf work
cp -r finbot_backup_YYYYMMDD work
cd work

# Restart service
systemctl restart finbot

# Post in Slack
echo "⚠️ FinBot rolled back due to issue. Under investigation. 
Use finance team directly for numbers until resolved."
```

### [ ] Investigation
- Check `logs/finbot_trace.jsonl` for error patterns
- Export failing test cases to golden set
- Update fix and re-test before re-deploying

---

## Sign-Off

| Role | Name | Date | Status |
|------|------|------|--------|
| Manual Review Complete | Marta Oyelaran (Finance) | | [ ] |
| Code Review | Jonas Feld (Data) | | [ ] |
| Testing Complete | Jonas Feld (Data) | | [ ] |
| Deployment Complete | Jonas Feld (Data) | | [ ] |
| 24h Monitoring Complete | Jonas Feld (Data) | | [ ] |
| Approved for Exec Use | Marta Oyelaran (Finance) | | [ ] |

---

## Contact

- **Technical issues:** Jonas Feld (Data team owner)
- **Financial validation:** Marta Oyelaran (VP Finance)
- **Escalation:** Daniel Kurz (CEO)
