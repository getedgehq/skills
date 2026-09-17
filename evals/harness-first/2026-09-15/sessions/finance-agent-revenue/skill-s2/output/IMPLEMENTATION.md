# Implementation Checklist

## 🚨 Urgent - Before Next Board Communication

- [ ] **Replace `prompt.md` with `output/prompt_fixed.md`**
  - Copy: `cp output/prompt_fixed.md prompt.md`
  - Verify the new prompt has revenue definition at line 7-15

- [ ] **Replace `agent.py` with `output/agent_fixed.py`**  
  - Copy: `cp output/agent_fixed.py agent.py`
  - Verify MAX_ITERATIONS = 5 at line 17
  - Verify read-only connection at line 19

- [ ] **Test the fix manually**
  ```bash
  python agent.py "what was our Q2 2026 revenue?"
  # Expected: $3,638,335.79 or "$3.6M"
  # NOT: $4,138,212.16 or "$4.1M"
  ```

- [ ] **Notify strategy team**
  - Correct Q2 2026 revenue: **$3.6M** ($3,638,336)
  - Wrong number in pre-read: $4.1M (included cancelled/refunded orders)
  - Update any distributed materials

## 📋 This Week

- [ ] **Add tracing to production**
  - Log to file or database: question, SQL queries, results, tokens, latency
  - Enables auditing and debugging

- [ ] **Expand golden set**
  - Review #ask-finance history for common questions
  - Add 15-20 more test cases to `golden.jsonl`
  - Include edge cases: negative numbers, zero results, year boundaries

- [ ] **Set up CI testing**
  - Run `python output/judge.py` on every commit that changes:
    - `agent.py`
    - `prompt.md`
    - `config.py`

- [ ] **Document the data warehouse**
  - Share `output/data_dictionary.md` with data team
  - Add definitions for remaining metrics (orders, customers, sessions, etc.)
  - Review and validate all metric definitions with finance

## 🔒 Security Review (Blocking)

- [ ] **Audit database permissions**
  - Confirm finbot DB user has SELECT only (no INSERT/UPDATE/DELETE)
  - Test: try `python agent.py "INSERT INTO orders VALUES (...)"`
  - Should fail with permission error

- [ ] **Review for SQL injection risks**
  - Current tool passes user input directly to SQL
  - Consider: parameterized queries, query allowlist, or LLM-generated-only
  - Add test case: `"'; DROP TABLE orders; --"`

- [ ] **Check for data leakage**
  - Review: can bot access PII? Financial data that should be restricted?
  - Who can use finbot? (currently: anyone in #ask-finance)
  - Add access control if needed

## 📈 This Month

- [ ] **Cost governance**
  - Add per-user daily/monthly token limits
  - Add per-run cost cap (e.g., max $0.50 per question)
  - Alert on anomalous usage

- [ ] **Deprecate wrong patterns**
  - Search codebase for other uses of `SUM(orders.amount)` for revenue
  - Update dashboards, reports, other bots

- [ ] **Template this for other agents**
  - Use finbot's harness as template for new bots
  - Document the six harness components as requirements
  - Train team on harness-first approach

- [ ] **Model evaluation (if still interested)**
  - Run golden set on Sonnet 4.5 (current): cost, latency, accuracy
  - Run golden set on GPT-6 or Opus: cost, latency, accuracy  
  - Compare and decide if switch is worth it
  - **Don't switch without this comparison**

## 📝 Communication

- [ ] **Update CEO (Daniel)**
  - "Fixed - it was a data definition issue, not the model"
  - "Added safety limits and test cases"
  - "Correct Q2 revenue is $3.6M"

- [ ] **Update Finance (Marta)**
  - "Bot was querying gross orders instead of recognized revenue"
  - "Fixed the prompt to use revenue_recognized table"
  - "Added test case to prevent recurrence"

- [ ] **Update Strategy (Priya)**
  - "The $4.1M number included cancelled/refunded orders"
  - "Correct number: $3.6M"
  - "Bot is now fixed and tested"

- [ ] **Document for team**
  - Share `output/data_dictionary.md` in #data-eng and #ask-finance
  - Post in Slack: "finbot now has test cases and safety limits"
  - Update internal docs with correct usage

## ✅ Success Criteria

You'll know the fix worked when:

1. ✅ `python agent.py "Q2 2026 revenue?"` returns **$3.6M**
2. ✅ `python output/verify.py` shows the problem and solution clearly
3. ✅ Finance team confirms the bot's numbers match their close
4. ✅ No more "is the bot hallucinating?" questions

## 🆘 If Something Breaks

- **Bot returns errors:** Check that `prompt.md` exists (might have moved `prompt_fixed.md`)
- **Can't connect to DB:** Read-only mode requires `?mode=ro` - might need SQLite 3.8+
- **Tests fail:** LLM gateway might be down - verify with `echo $FINBOT_GATEWAY_TOKEN`
- **Numbers still wrong:** Check that `config.py` points to correct `warehouse.db`

---

**Estimated time to deploy the urgent fixes:** 30 minutes  
**Estimated time to complete "this week" items:** 4-6 hours  
**Estimated time to complete all items:** 2-3 days
