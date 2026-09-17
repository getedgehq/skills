# Harness Scorecard - Support Bot

**Audit date:** 2026-09-15  
**Auditor:** AI Safety Review  
**Agent:** Brindle & Oak Support Bot

---

## Six-Part Harness Health Check

### 1. Golden Set: 🟡 PARTIAL (Now 2/5, was 0/5)

**Current state:**
- ✅ Created `golden_set.jsonl` with 8 cases drawn from real August tickets
- ✅ Covers critical policies: custom item refunds, internal notes, legal escalation, standard returns
- ⚠️ Need to expand to 20+ cases

**What's covered:**
- Custom item + change of mind (2 cases)
- Internal notes leak (1 case)
- Legal escalation (1 case)  
- Standard returns in window (1 case)
- Pre-shipment cancellation (1 case)
- Defect handling (1 case)

**Still missing:**
- 30+ day return requests (should decline)
- Warranty claims (2-year frame warranty)
- Store credit offers (when to offer vs not)
- Edge case: custom flag false but CUST- SKU
- Edge case: defect on custom item (should refund/remake)
- Multiple SKU patterns
- Tickets with no order found
- Tier 2 escalation paths beyond legal

**Next steps:**
- [ ] Add 12 more cases covering gaps above
- [ ] Review with PM for business-critical edge cases
- [ ] Include any past incidents that caused issues

**Score:** 2/5 (have 8, need 20+)

---

### 2. Judge: 🟢 PRESENT (Now 4/5, was 0/5)

**Current state:**
- ✅ Created `judge.py` with deterministic policy checks
- ✅ Checks custom item refund offers
- ✅ Checks internal notes leaks
- ✅ Checks legal escalation
- ✅ Checks standard refund paths
- ✅ Runs on both old and new outputs
- ✅ Exit code 1 when violations found (CI-ready)

**What it catches:**
- Refunds offered when policy says no
- Confidential info leaked to customers
- Legal mentions not escalated
- Missing remedy offers for valid requests

**Still missing:**
- LLM-as-judge for tone/empathy (deterministic checks can't measure "warmth")
- Character count checks (replies shouldn't be >500 words)
- Profanity/inappropriate language detection
- Check for broken links or fake order IDs
- Response time tracking (not in scope of this review)

**Next steps:**
- [ ] Add tone scoring (optional: use LLM to rate warmth 1-5)
- [ ] Add length checks
- [ ] Add profanity filter
- [ ] Integrate into CI/CD pipeline

**Score:** 4/5 (deterministic checks present, LLM-judge for subjective quality missing)

---

### 3. Cost Governance: ⚫ UNKNOWN (0/5)

**Current state:**
- ❌ No evidence in provided files
- ❌ No token usage logs
- ❌ No cost-per-ticket metrics
- ❌ No max iterations or timeout configs
- ❌ No per-customer cost caps

**What's needed:**
- Hard token limit per ticket (suggest 2000 tokens)
- Cost cap per ticket (suggest $0.10 with gpt-4 pricing)
- Max retries on errors (should be 1-2, not infinite)
- Monitoring dashboard showing:
  - Average tokens per ticket
  - 95th percentile cost
  - Outliers (tickets that burned >$1)
- Alerts when costs spike

**Risk:**
- If bot enters a loop or gets a huge context, costs could spike
- No visibility into whether new prompt costs more than old
- Can't prove ROI of prompt changes

**Next steps:**
- [ ] Instrument bot to log tokens/cost per ticket
- [ ] Set hard caps in bot config
- [ ] Build cost dashboard
- [ ] Review past month's token usage

**Score:** 0/5 (no evidence of cost tracking or caps)

---

### 4. Data Layer: ⚫ UNKNOWN (0/5)

**Current state:**
- ❌ No DB schema provided
- ❌ No data dictionary defining fields
- ❌ Don't know if bot has read-only vs read-write DB access
- ❌ Can't verify if `internal_notes` can be accidentally written to customer-visible fields

**What's needed:**
- Data dictionary defining each field the bot can access:
  - `order.sku` - product SKU, format: XXX-0000 or CUST-0000
  - `order.custom` - boolean, true if made-to-measure
  - `order.delivered_on` - ISO date, null if not yet delivered
  - `internal_notes` - CONFIDENTIAL, staff only, never customer-facing
  - Etc.
- Read-only DB credentials for the bot
- Separate write permission only for approved actions (if any)
- Schema validation on inputs

**Risk:**
- Bot could misinterpret field meanings
- Bot could overwrite data if it has write access
- Ambiguous fields (e.g., is `order.custom` always set? What if null?)

**Next steps:**
- [ ] Document all fields the bot reads
- [ ] Verify bot has read-only access (no UPDATE/DELETE)
- [ ] Add field validation to bot code
- [ ] Clarify edge cases (what if custom is null? what if SKU is missing?)

**Score:** 0/5 (no data layer documentation)

---

### 5. Action Safety: 🔴 MISSING (0/5)

**Current state:**
- ⚠️ Bot appears to **directly commit refunds/cancellations** based on outputs like "I've arranged a full refund"
- ❌ No evidence of approval gate
- ❌ No evidence of draft mode
- ❌ Don't know if bot actually triggers refund API or just drafts a message

**What's needed:**

**Option A: Draft + Approve workflow (recommended)**
- Bot drafts reply
- Human agent reviews and clicks "Approve & Send"
- Irreversible actions (refunds, cancellations) require approval
- Low-risk actions (tracking updates, general info) can auto-send

**Option B: Read-only mode**
- Bot drafts replies, never sends
- Always requires human review
- Safest but highest ops load

**Option C: Action caps**
- Bot can auto-send replies but NOT trigger financial actions
- Refund/cancel buttons disabled, requires separate agent action
- Bot says "I've started the refund process" but doesn't execute it

**Risk:**
- Current violations show bot offering refunds it shouldn't
- If bot actually executes these refunds, company loses $1000s
- If bot just drafts text, risk is lower but still damages customer expectation

**Next steps:**
- [ ] **URGENT:** Clarify if bot auto-executes refunds or just drafts text
- [ ] If auto-executes: add approval gate immediately
- [ ] If just drafts: add "draft mode" labeling so customers know
- [ ] Define which actions require approval (refunds >$X, cancellations, account changes)

**Score:** 0/5 (no action safety gates visible, critical blocker)

---

### 6. Tracing: ⚫ UNKNOWN (0/5)

**Current state:**
- ❌ No trace logs provided in review files
- ❌ Can't see token usage, latency, or error rates
- ❌ Can't debug which tickets failed or why
- ❌ Can't compare old vs new prompt performance

**What's needed:**
- Log every bot interaction with:
  - `conversation_id` / `ticket_id`
  - `prompt_version` (old_prompt.md, new_prompt.md)
  - `model` (gpt-4, gpt-3.5-turbo, etc)
  - `input_tokens`, `output_tokens`, `total_cost`
  - `latency_ms`
  - `timestamp`
  - `error` (if any)
  - `output` (the actual reply generated)
- Aggregate views:
  - Token usage by prompt version
  - Error rate by ticket type
  - P50/P95 latency
  - Outliers (tickets with >5000 tokens)

**Risk:**
- Can't debug production issues
- Can't prove new prompt is cheaper/faster
- Can't find the 1% of tickets that burn 50% of tokens

**Next steps:**
- [ ] Add structured logging to bot
- [ ] Send logs to centralized system (Datadog, CloudWatch, etc)
- [ ] Build dashboard for daily review
- [ ] Set up alerts for anomalies

**Score:** 0/5 (no tracing infrastructure visible)

---

## Overall Harness Score: 1.2 / 5.0

| Component | Score | Status |
|-----------|-------|--------|
| Golden set | 2/5 | 🟡 Partial - have 8, need 20+ |
| Judge | 4/5 | 🟢 Present - deterministic checks working |
| Cost governance | 0/5 | ⚫ Unknown - no evidence |
| Data layer | 0/5 | ⚫ Unknown - no docs |
| Action safety | 0/5 | 🔴 Missing - URGENT |
| Tracing | 0/5 | ⚫ Unknown - no logs |

---

## Critical Next Steps (Priority Order)

### 🔴 URGENT (blocking for ANY production use)

1. **Clarify action execution model**
   - Does bot auto-execute refunds? If yes, add approval gate NOW
   - If no, label all bot output as "draft" mode
   
2. **Fix new prompt policy violations**
   - Use `prompt_v4.1_FIXED.md` or revert to old prompt
   - Run `judge.py` to verify 0 violations before ship

### 🟡 HIGH (needed for safe iteration)

3. **Expand golden set to 20+ cases**
   - Cover all refund edge cases
   - Include past incidents
   
4. **Document data layer**
   - What fields exist?
   - What do they mean?
   - Is bot read-only?

### 🟢 MEDIUM (needed for scale)

5. **Add cost tracking**
   - Log tokens per ticket
   - Set hard caps
   - Alert on spikes
   
6. **Add tracing**
   - Log every interaction
   - Build performance dashboard

---

## Questions to Answer Before Next Prompt Change

1. **Does the bot have write access to any databases?** If yes, revoke it.
2. **Does the bot execute refunds/cancellations or just draft text?** If executes, add approval.
3. **What's the average token usage per ticket?** Need baseline to detect regressions.
4. **What's the error rate?** Are 1% of tickets failing silently?
5. **Who reviews bot outputs before they go to customers?** If no one, high risk.

---

## How to Use This Scorecard

- Re-run this audit quarterly or when changing agents
- Track score over time (goal: all 4-5/5 within 6 months)
- Block production changes if Action Safety < 3/5
- Block scale-up if Cost Governance < 3/5

**Last updated:** 2026-09-15
