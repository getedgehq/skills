# Action Plan: Fix Finbot Revenue Issue

**Status:** Ready to implement  
**Estimated time to fix:** 5 minutes  
**Risk level:** Very low

---

## Immediate Actions (Do Today)

### 1. Update the System Prompt ⚡ CRITICAL
**File:** `prompt.md`  
**What to do:** Replace with the corrected version (see `output/prompt_FIXED.md`)

**Key changes:**
- Add descriptions for each table indicating their purpose
- Clearly mark `revenue_recognized` as the source for revenue questions
- Add explicit instructions to use `net_amount`, not `orders.amount`
- Explain WHY (orders table includes cancelled/refunded transactions)

**Test command after updating:**
```bash
python agent.py "what was our Q2 2026 revenue?"
```

**Expected result:** Should now return ~$3.6M instead of $4.1M

---

### 2. Verify Q1 Number in Board Deck 📊
**Owner:** Priya (Strategy) / Marta (Finance)

The same issue affects Q1:
- Finbot reported Q1 as $4.1M (from orders table)
- Finance's actual Q1 close is likely ~$3.6M

**Action:** 
- Check what Q1 number is in the board pre-read
- If it came from finbot, update it to match finance's official close
- Run this query to get correct Q1:
  ```sql
  SELECT SUM(net_amount) FROM revenue_recognized
  WHERE period IN ('2026-01', '2026-02', '2026-03');
  ```

---

### 3. Notify Stakeholders 📢
**Who to tell:**
- Daniel (CEO) - Root cause identified, not a model issue
- Priya (Strategy) - Board deck numbers need correction
- Marta (Finance) - Confirm fix addresses the issue
- Jonas (Data team) - Owner of finbot, needs to deploy fix

**Message template:**
> Found the issue with finbot's revenue numbers. This is NOT a model problem - the bot correctly executed SQL but didn't know which table to use. The prompt didn't specify that revenue_recognized is the source of truth. 
>
> Fix is simple: update the prompt to clarify table usage. No model upgrade needed.
>
> Q1 numbers in the board deck may also need correction (same issue).

---

## This Week

### 4. Add Documentation to Warehouse Schema
**Owner:** Jonas / Data team

Add comments to the warehouse explaining:
```sql
-- orders table: Contains ALL orders including cancelled and refunded.
-- Use for: Order-level analysis, not revenue totals.

-- revenue_recognized table: Official financial ledger with net revenue.
-- Use for: All revenue reporting and financial analysis.
-- This is the source of truth that matches finance's closed books.
```

---

### 5. Create Finbot Usage Guidelines
**Owner:** Jonas / Data team

Quick guide for internal users:
- When to trust finbot answers directly
- When to verify with finance
- Which questions finbot is good at vs. should be escalated

Post in #ask-finance channel as pinned message.

---

### 6. Review Recent Finbot Usage
**Action:** Check Slack for other questions that might have used the wrong table

Common risky queries:
- "How much revenue..." 
- "What were sales..."
- "Total bookings for..."

If any of these were used in important documents, flag for review.

---

## Next Sprint (Nice to Have)

### 7. Add Schema Documentation Tool
Enhance finbot to have access to table metadata:
- Add a `describe_tables` tool
- Include business context in table descriptions
- Let the model see relationships between tables

### 8. Add Validation Rules
Before returning revenue numbers, sanity check:
- Q2 revenue should be $2M-$5M (based on historical data)
- If result is outside range, flag for human review
- Log all queries to a Slack channel for spot-checking

### 9. Create Data Dictionary
Comprehensive documentation:
- Table purposes and relationships
- Column definitions
- Business rules (e.g., "net_amount = gross - refunds")
- Common queries and their correct table usage

---

## Testing Plan

After implementing the fix, test with:

### Revenue questions (should use revenue_recognized):
- ✅ "What was Q2 2026 revenue?" → $3,638,335.79
- ✅ "Revenue in June 2026?" → $1,191,160.85
- ✅ "How much did we make in Q1?" → Check against finance close
- ✅ "What was revenue in April, May, and June 2026?" → Sum of Q2 months

### Order questions (should use orders table):
- ✅ "How many orders in Q2?" → 2,213 orders
- ✅ "What's the average order value in Q2?" → ~$1,870
- ✅ "How many cancelled orders in Q2?" → 202 orders

### Edge cases:
- ✅ "What were our bookings in Q2?" → Clarify if they mean gross or net
- ✅ "Total sales for Q2" → Should use net revenue

---

## Rollback Plan

If the prompt change causes issues:

1. Revert to original `prompt.md`
2. Add a manual review step: "For revenue questions, check with @finance"
3. Investigate specific failure cases
4. Refine the prompt based on failures

**Risk assessment:** Very low. The change is additive (more context) not restrictive.

---

## Success Metrics

After deploying the fix, monitor:
- Revenue query accuracy (should match finance reports)
- User satisfaction in #ask-finance
- Number of questions escalated to finance team
- Reduction in "hey this number looks wrong" messages

---

## Cost Analysis

### Option A: Fix the Prompt (RECOMMENDED)
- **Time:** 5 minutes
- **Cost:** $0
- **Ongoing cost:** No change
- **Effectiveness:** Solves the root cause

### Option B: Upgrade Model (NOT RECOMMENDED)
- **Time:** 5 minutes  
- **Cost:** $0 upfront
- **Ongoing cost:** 2-3x per query ($$$)
- **Effectiveness:** Won't fix the issue (model isn't the problem)

**Recommendation:** Option A - Fix the prompt

---

## Key Takeaway

This incident reveals an important principle for LLM agents:

> **Prompts for production agents are specifications, not suggestions.**

When an LLM agent has access to business-critical data:
- Document business rules explicitly
- Specify which data sources are authoritative
- Include domain knowledge the model can't infer
- Treat the prompt like you would treat code comments

The model performed perfectly within the constraints it was given. The issue was ambiguous requirements, not model capability.
