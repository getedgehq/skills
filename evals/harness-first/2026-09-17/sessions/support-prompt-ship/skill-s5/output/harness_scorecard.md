# Harness Scorecard - Support Bot Prompt Change

## 1. Golden Set
**Status: PARTIAL**

Evidence:
- ✓ Real traffic: 30 tickets from August (last month's actual tickets)
- ✓ Good coverage: includes refunds, custom items, legal threats, internal notes
- ✗ No expected outputs: tickets exist but no defined "correct answers"
- ✗ No edge case labeling: not marked which are policy tests vs tone tests
- ✗ No constraints defined: no checklist of "must include X" or "must not include Y"

**Grade: 4/10** - You have inputs but no test oracle.

---

## 2. Judge
**Status: MISSING**

Evidence:
- ✗ No automated checks run before the change
- ✗ Manual review only ("asked 5 people... 10 random replies")
- ✗ No deterministic policy checks (custom refund rules, 30-day window, internal notes)
- ✗ Sample size for manual review: 10/30 tickets (33%) - missed the violations in other 67%

**What exists:**
- PM's vibes ("night and day", "lovely")
- Warmth rating 2.8→4.6 on 10 tickets

**What's missing:**
- Automated policy violation detection
- Refund cost estimation
- Legal risk flagging
- Run-on-every-change pipeline

**Grade: 1/10** - No systematic quality gate.

---

## 3. Cost Governance
**Status: MISSING**

Evidence:
- ✗ No token/cost tracking visible in outputs
- ✗ No cost comparison old vs new prompt
- ✗ Unknown: model, temperature, token counts per ticket
- ✗ Unknown: total cost of replaying 30 tickets

**Cannot answer:**
- Does the longer "warm" prompt cost more per ticket?
- What's the monthly cost impact?
- Are there token/cost caps per ticket?

**Grade: 0/10** - No cost visibility at all.

---

## 4. Data Layer
**Status: PARTIAL**

Evidence:
- ✓ Structured ticket data (ticket_id, customer_name, order, message)
- ✓ Order data (order_id, sku, status, delivered_on)
- ✓ Internal notes field exists and is used
- ✗ No data dictionary defining fields
- ✗ No defined rules for parsing/using custom field (CUST- prefix)
- ✗ No validation that internal_notes are never shown to customer

**Grade: 5/10** - Data exists but no formal definitions or safety rules.

---

## 5. Action Safety
**Status: PARTIAL**

Evidence:
- ✓ Bot generates draft replies only (doesn't send directly to customers - assumed)
- ✗ No mention of human review/approval before sending
- ✗ No explicit gates for refund approvals (bot claims "I've arranged a refund")
- ✗ Unknown: Can the bot actually trigger refunds or just draft the message?

**Risk:**
If the bot CAN trigger refunds: custom item refunds would execute automatically.
If the bot CANNOT: the message tone implies it did ("I've arranged...") which creates customer expectation.

**Grade: 5/10** - Approval process unclear; message tone implies actions happened.

---

## 6. Tracing
**Status: MISSING**

Evidence:
- ✗ No conversation_id, workflow, model name in outputs
- ✗ No timestamps on outputs (don't know when replays ran)
- ✗ No token counts, costs, latency
- ✗ Can't trace back which prompt generated which reply without file name inference

**What exists:**
- ticket_id link
- prompt file name ("old_prompt.md" / "new_prompt.md")

**Grade: 2/10** - Minimal linkage, no operational metrics.

---

## Overall Harness Score: 17/60 (28%)

### Summary by part:
| Part | Score | Status |
|------|-------|--------|
| Golden set | 4/10 | PARTIAL - inputs only, no expected outputs |
| Judge | 1/10 | MISSING - manual spot checks only |
| Cost governance | 0/10 | MISSING - no visibility |
| Data layer | 5/10 | PARTIAL - data exists, no dictionary |
| Action safety | 5/10 | PARTIAL - approval process unclear |
| Tracing | 2/10 | MISSING - no operational metrics |

---

## What this means

The "warmth" improvement is real in the 10 tickets the PM manually checked.
But **there was no harness to catch the 4 critical policy violations** in the other tickets.

The prompt change is unsafe to ship because:
1. No automated judge caught custom item refunds being approved
2. No automated check caught internal notes leaking
3. Manual review sample was too small (10/30)

The good news: violations are deterministic and catchable with code.
