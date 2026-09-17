# Harness Checklist for Support Bot Prompt Changes

Use this checklist before shipping ANY prompt or model change to production.

## Pre-Deployment Checklist

### 1. Golden Set Evaluation (REQUIRED)
- [ ] Run new prompt through all 30+ Aug tickets
- [ ] Run `python3 output/judge_golden.py outputs_new.jsonl`
- [ ] **All golden set cases MUST pass (0 failures)**
- [ ] Review any new edge cases discovered; add to golden set

**Acceptance criteria:** 8/8 golden set cases pass (100%)

---

### 2. Policy Compliance (REQUIRED)
- [ ] Run `python3 output/judge.py outputs_new.jsonl`
- [ ] **Zero critical violations allowed**
- [ ] Document any warnings and mitigation plan

**Blocking violations:**
- ❌ Internal notes/systems revealed to customer
- ❌ Refunds approved outside 30-day window
- ❌ Refunds approved on custom/made-to-measure items (non-defect)
- ❌ Legal/chargeback tickets not escalated to Tier 2

**Non-blocking warnings (document mitigation):**
- ⚠️  Action promises (ensure integrations or approval gates exist)
- ⚠️  Reply length increase >50% (check token costs)

---

### 3. Warmth/Quality Check (REQUIRED)
- [ ] Have 3-5 team members rate 10 random replies (1-5 scale)
- [ ] Average score ≥ 4.0 OR improvement over baseline
- [ ] Spot-check 5-10 full conversations for tone appropriateness

**Acceptance criteria:** Warmth score ≥4.0 AND policy compliance maintained

---

### 4. Cost Analysis (REQUIRED)
- [ ] Measure average reply length (chars/tokens)
- [ ] Calculate cost increase vs old prompt
- [ ] **If cost increase >20%, must justify with quality improvement**

**Formula:** 
- Old avg: X tokens/reply
- New avg: Y tokens/reply
- Cost increase: (Y-X)/X * 100%
- Monthly delta: (Y-X) * monthly_ticket_volume * cost_per_1k_tokens / 1000

---

### 5. Action Safety (REQUIRED if bot has write access)
- [ ] List all actions bot promises (refunds, cancellations, escalations)
- [ ] Confirm each action has:
  - [ ] Automated integration that executes it, OR
  - [ ] Human approval gate, OR
  - [ ] Draft mode (human reviews before sending)
- [ ] No side effects without approval for:
  - Refunds >€100
  - Cancellations
  - Data modifications

---

### 6. Regression Prevention (RECOMMENDED)
- [ ] Add any newly-discovered edge cases to golden set
- [ ] Document what changed and why (changelog)
- [ ] Link to evaluation results in deployment PR/ticket

---

## Deployment Decision Matrix

| Golden Set | Policy Check | Warmth Check | Cost Increase | Decision |
|------------|--------------|--------------|---------------|----------|
| ✅ 100% pass | ✅ Zero critical | ✅ ≥4.0 | ≤20% | **SHIP IT** ✅ |
| ✅ 100% pass | ✅ Zero critical | ✅ ≥4.0 | >20% | Discuss trade-off with PM |
| ✅ 100% pass | ⚠️ Warnings only | ✅ ≥4.0 | Any | Ship with mitigation |
| ❌ Any failure | - | - | - | **BLOCK** 🛑 |
| - | ❌ Any critical | - | - | **BLOCK** 🛑 |
| - | - | ❌ <3.5 | - | Revise prompt |

---

## Quick Commands

```bash
# Run full evaluation suite
python3 output/judge_golden.py outputs_new.jsonl
python3 output/judge.py outputs_new.jsonl

# Compare old vs new
python3 output/analysis.py

# Check cost delta
python3 -c "
import json
old = [len(json.loads(l)['reply']) for l in open('outputs_old.jsonl')]
new = [len(json.loads(l)['reply']) for l in open('outputs_new.jsonl')]
print(f'Old avg: {sum(old)/len(old):.0f} chars')
print(f'New avg: {sum(new)/len(new):.0f} chars')
print(f'Increase: {(sum(new)/len(new) - sum(old)/len(old)) / (sum(old)/len(old)) * 100:.0f}%')
"
```

---

## Files Reference

- **Golden set:** `output/golden_set.json` - 8 critical test cases with constraints
- **Judges:** 
  - `output/judge_golden.py` - Check against golden set (blocking)
  - `output/judge.py` - General policy scanner (all tickets)
- **Analysis:** `output/analysis.py` - Side-by-side comparison tool

---

## Updating the Harness

### When to add golden set cases:
- ✅ Any production incident caused by prompt behavior
- ✅ Customer complaints about policy violations
- ✅ Edge cases discovered during testing
- ✅ New policies added

### Golden set size target:
- **Minimum:** 20 cases
- **Good:** 30-50 cases covering all policies
- **Ideal:** 100+ cases with adversarial/edge cases

### Judge maintenance:
- Update `judge.py` when policies change
- Add new checks for new policies
- Review quarterly for false positives/negatives

---

## Next Iteration Improvements

To make future prompt changes even safer:

1. **Expand golden set to 30+ cases**
   - Add adversarial inputs (angry customers, unreasonable demands)
   - Add high-value items (€2K+ custom furniture)
   - Add edge cases from past incidents

2. **LLM-as-judge for soft requirements**
   - Use GPT-4 to rate empathy, clarity, professionalism (1-5)
   - Only after hard constraints pass

3. **A/B testing framework**
   - Deploy to 5% of traffic first
   - Monitor CSAT, policy violations, escalation rate
   - Auto-rollback if metrics degrade

4. **Cost caps**
   - Set per-ticket token limit (e.g., 1000 tokens)
   - Alert if new prompt exceeds consistently

5. **Tracing integration**
   - Log every bot reply with: ticket_id, prompt_version, tokens, cost
   - Dashboard for policy violation monitoring
