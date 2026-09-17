# Next Steps: Support Bot Prompt Update

**Status:** ❌ Current new prompt (v4) not safe to ship  
**Priority:** Fix policy violations, then re-evaluate warmth

---

## Immediate Actions (Before Friday)

### 1. DO NOT SHIP current new_prompt.md ⛔
- 4 critical policy violations found (13% error rate on policy tests)
- 3 unauthorized refunds (outside window + custom item) = direct revenue loss
- 1 internal information leak = customer dispute risk

### 2. Use fixed prompt (v4.1) or revert to old
Two options:
- **Option A (recommended):** Use `output/new_prompt_v4.1_fixed.md` 
  - Keeps warmth improvements
  - Restores explicit policy constraints
  - Adds examples of "warm but within policy" responses
  
- **Option B (safe fallback):** Keep old_prompt.md until fixed version is tested
  - No revenue risk
  - Boring but correct

### 3. Test fixed prompt before ANY deployment
```bash
# Run judge on fixed prompt outputs
python3 output/judge.py outputs_v4.1.jsonl output/golden_set.jsonl
```
Must achieve: ✅ All 4 critical policy tests pass

---

## Build the Harness (Next 2 Weeks)

### Week 1: Stop the bleeding
1. **Golden set expansion** (output/golden_set.jsonl is a start)
   - Add 10 more edge cases from support team: escalations, warranty boundaries, promo abuse
   - Document expected behavior for each: "MUST deny because...", "MAY offer..."
   
2. **Deterministic judge** (output/judge.py is ready)
   - Integrate into CI/CD: block merges if critical tests fail
   - Add cost check: fail if >25% token increase without explicit approval
   
3. **Action safety audit**
   - List every action bot can commit: refund, cancel, ship, discount, escalate
   - For refunds/cancellations: require order metadata validation (date, SKU, status)
   - Consider: approval queue for edge cases vs auto-deny

### Week 2: Ongoing quality
4. **Warmth evaluation (optional, after policy pass)**
   - LLM-as-judge rubric for empathy/tone (only run on policy-compliant replies)
   - OR: sample 20 random tickets weekly, human CSAT from real customers
   
5. **Cost governance**
   - Set hard cap: 2000 tokens/ticket, fail gracefully if exceeded
   - Monitor: token cost per ticket category (returns cost more than balance checks)
   
6. **Tracing in production**
   - Log every bot reply: ticket_id, prompt_version, tokens, cost, policy_violations_detected
   - Alert: if >1% of daily tickets hit a policy rule

---

## How to Make Future Prompt Updates Less Painful

### Every prompt change must include:
1. **Run the golden set first**
   ```bash
   # Replay all tickets with new prompt
   python replay_tickets.py --prompt new_v5.md --output outputs_v5.jsonl
   # Run judge
   python output/judge.py outputs_v5.jsonl output/golden_set.jsonl
   ```

2. **Document what changed and why**
   - Example: "Added 'acknowledge emotion first' to improve CSAT; kept all policy constraints"

3. **Side-by-side comparison** of 5-10 key tickets (like your PM notes, but AFTER policy check)

4. **Cost impact:** Compare token usage old vs new

### Golden set maintenance:
- Add new case whenever:
  - Customer support escalates a bot error
  - New policy is introduced
  - Edge case discovered (e.g., "What if delivery date is missing from order record?")

---

## What This Fixes

| Problem | Solution |
|---------|----------|
| "Warmth" measured policy violations | Deterministic judge checks policy first, warmth second |
| No shared definition of "correct" | Golden set with pass/fail criteria |
| Prompt tweaks every 2 weeks break things | Judge in CI blocks bad changes |
| Over-refunds costing revenue | Action safety checks + golden set catches them |
| No way to compare costs | Judge reports token diff, sets threshold |

---

## Cost-Benefit of This Work

**Time investment:**
- Initial: ~4 hours (golden set + judge + fixed prompt)
- Ongoing: ~30 min per prompt update (run judge, review failures)

**Value:**
- Prevented: 3 unauthorized refunds in 30-ticket sample = ~10% over-refund rate
  - If 10k tickets/month, that's 1,000 erroneous refunds
  - At avg $200 furniture order = $200k/month revenue leak ⚠️
- Token cost transparency: 55% increase now visible and capped
- CSAT improvements now measurable independently of policy compliance

---

## Questions for PM / Leadership

1. **Approval for v4.1 testing?**
   - Need to replay August tickets through fixed prompt
   - Target: pass all 4 critical policy tests, compare warmth scores

2. **Action approval workflow?**
   - Should bot auto-approve refunds at all, or always draft for human review?
   - Threshold: refunds <$50 auto-approve, >$50 require human?

3. **Golden set ownership?**
   - Who maintains golden_set.jsonl? (Suggest: support team lead + eng)
   - Monthly review to add new cases?

4. **Cost budget?**
   - What's acceptable cost/ticket? Current: old prompt ~140 chars, new ~220 chars
   - Alert threshold?

---

## Files Created

- `output/harness_scorecard.md` - Full audit with evidence
- `output/policy_violations.txt` - Detailed breakdown of 4 failures
- `output/golden_set.jsonl` - 20 test cases with pass/fail criteria
- `output/judge.py` - Automated evaluation script
- `output/new_prompt_v4.1_fixed.md` - Fixed prompt (warmth + policy)
- `output/eval_old.txt` - Old prompt evaluation results
- `output/eval_new.txt` - New prompt evaluation results (with failures)
- `output/next_steps.md` - This file

**To run:** `python3 output/judge.py outputs_new.jsonl output/golden_set.jsonl`
