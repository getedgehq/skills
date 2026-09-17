# Implementation Guide

## Quick Deploy (Stop the Bleeding)

To fix the immediate issue and prevent recurrence:

### 1. Update the Prompt (5 minutes)
```bash
cp output/prompt_fixed.md prompt.md
```

This adds explicit guidance on which table to use for revenue questions.

### 2. Deploy Data Dictionary (5 minutes)
```bash
cp output/data_dictionary.md .
```

Place where the data team can maintain it. Update the prompt to reference it.

### 3. Update Agent Code (10 minutes)
```bash
cp output/agent_fixed.py agent.py
cp output/config_fixed.py config.py
mkdir -p logs
```

This adds:
- Max iterations (10) to prevent infinite loops
- Read-only database connection
- Basic tracing to `logs/` directory
- Better error handling

### 4. Test with the Golden Set (5 minutes)
```bash
python output/run_eval.py --priority critical
```

This demonstrates the fix on the incident case.

---

## Full Harness (This Week)

### Phase 1: Validation (Day 1-2)

1. **Deploy the fixes above**
2. **Announce in #ask-finance:**
   > "We fixed the Q2 revenue issue. FinBot now uses the same revenue table as Finance. If you see any weird numbers, please flag the message with 🚩"

3. **Monitor logs:**
   ```bash
   tail -f logs/conversations.jsonl | jq '.question, .answer, .tokens'
   ```

### Phase 2: Continuous Testing (Day 3-4)

1. **Set up eval runs:**
   - Create a cronjob or GitHub Action to run `run_eval.py` nightly
   - Alert on failures

2. **Expand golden set:**
   - Add flagged questions to `output/evals/golden.jsonl`
   - Target 50+ cases within 2 weeks

3. **Build answer recorder:**
   - Log actual bot answers alongside queries
   - This enables regression testing when you change prompts/models

### Phase 3: Governance (Day 5+)

1. **Change control:**
   - Require golden set pass (95%+) before deploying prompt changes
   - Document in CONTRIBUTING.md

2. **Cost caps:**
   - Add per-user budget tracking
   - Add per-conversation token limit
   - Alert when approaching limits

3. **Approval flow for actions:**
   - If you add write operations (create drafts, send emails), gate with human approval
   - See agent_fixed.py for structure

---

## Testing Different Models

If you want to compare Sonnet vs Opus vs GPT-6:

```python
# Create a test script
for model in ["claude-sonnet-4-5", "claude-opus-4", "gpt-6-turbo"]:
    results = []
    for case in golden_cases:
        answer = agent.answer(case["question"], model=model)
        passed = check_answer(case, answer)
        cost = calculate_cost(answer.tokens, model)
        results.append({"case": case["id"], "passed": passed, "cost": cost})
    
    print(f"{model}: {pass_rate}% pass, ${total_cost} total")
```

Compare pass rate AND cost before switching.

---

## Database: Read-Only Connection

The fixed agent uses `sqlite3.connect(uri=True, mode=ro)` for safety.

If your production DB is Postgres/MySQL:
```python
# Use a read-only user
conn = psycopg2.connect(
    host=DB_HOST,
    user="finbot_readonly",  # Create this user with SELECT-only grants
    password=DB_PASS,
    database=DB_NAME
)
```

---

## Monitoring Dashboard

Create a simple dashboard to track:
- Questions per day
- Most common queries
- Error rate
- Token cost per day
- Average latency

Can use the `logs/conversations.jsonl` as source.

---

## When to Add More Test Cases

Add to golden set when:
1. Someone flags a wrong answer
2. An incident occurs
3. You add a new table to the warehouse
4. A new metric definition is created (e.g., "ARR", "NRR")
5. You notice a pattern of similar questions

Aim for 20+ cases in the first week, 50+ within a month.

---

## FAQ

**Q: Do we need to re-test every time we add data?**  
A: No. Test when you change:
- The prompt
- The model
- The tool definitions
- Table schemas that affect metric definitions

**Q: What if a test starts failing after it was passing?**  
A: Investigate immediately. Could be:
- Data quality issue in ETL
- Prompt was changed without testing
- Model behavior changed (rare but happens)

**Q: Can we auto-fix wrong answers?**  
A: No. Auto-correction is risky. Instead:
1. Log the error
2. Add to golden set
3. Fix root cause (prompt/data)
4. Verify fix passes the test

---

## Success Metrics

After 2 weeks, you should see:
- ✅ Zero financial reporting errors in Slack
- ✅ Golden set has 50+ cases
- ✅ 95%+ pass rate on golden set
- ✅ All prompt changes require eval before deploy
- ✅ Basic cost and usage visibility

After 1 month:
- ✅ Users trust the bot enough to paste answers directly in decks
- ✅ Finance team validates bot against quarter-close
- ✅ Token cost is predictable and capped
- ✅ You have data to make informed model upgrade decisions
