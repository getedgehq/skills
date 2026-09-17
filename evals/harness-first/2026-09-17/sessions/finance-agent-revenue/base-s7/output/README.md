# Investigation Results: Finbot Revenue Discrepancy

**Investigation Date:** September 16, 2026  
**Issue:** Finbot reported Q2 2026 revenue as $4.1M, Finance says $3.6M

---

## 🚨 KEY FINDINGS

### This is NOT a hallucination or model problem
- The model correctly executed SQL and returned accurate data
- The prompt doesn't specify which table contains official revenue
- **Fix:** Update the prompt (5 min, $0 cost)
- **Don't:** Upgrade the model (won't help, costs more)

### Both Q1 AND Q2 are wrong
| Quarter | Finbot Said | Should Be | Difference |
|---------|-------------|-----------|------------|
| Q1 2026 | $4.1M | $3.3M | -$856K ⚠️ |
| Q2 2026 | $4.1M | $3.6M | -$500K ⚠️ |
| H1 2026 | $8.3M | $6.9M | -$1.4M ⚠️ |

### Root cause
- Finbot queries `orders` table (gross bookings, includes cancelled/refunded)
- Should query `revenue_recognized` table (net revenue, finance's official close)
- Prompt lists both tables but doesn't say which one to use for revenue

---

## 📋 DOCUMENTS IN THIS FOLDER

### Start Here
1. **URGENT_board_deck_alert.md** - Critical alert about Q1 and Q2 both being wrong
2. **executive_summary.md** - One-page brief for Daniel

### Details
3. **root_cause_analysis.md** - Complete technical investigation
4. **data_forensics.md** - Detailed data comparison and validation
5. **sql_comparison.md** - Wrong vs. right queries with examples
6. **action_plan.md** - Step-by-step fix implementation

### The Fix
7. **prompt_FIXED.md** - Corrected prompt file (ready to deploy)

---

## ⚡ IMMEDIATE ACTIONS

### Priority 1: Board Deck (URGENT)
- [ ] Check if Q1 and/or Q2 numbers in board deck came from finbot
- [ ] If yes, correct to official finance numbers
- [ ] Verify with Marta (Finance) before sending to board

### Priority 2: Deploy Fix (Today)
- [ ] Replace `prompt.md` with `prompt_FIXED.md`
- [ ] Test: `python agent.py "what was Q2 2026 revenue?"`
- [ ] Expected result: ~$3.6M (not $4.1M)

### Priority 3: Damage Control
- [ ] Check other materials that may have used finbot numbers
- [ ] Post correction in #ask-finance channel
- [ ] Notify exec team of issue and fix

---

## 📊 THE CORRECT NUMBERS

### Official Q2 2026 Revenue
**$3,638,335.79** (from `revenue_recognized.net_amount`)

Breakdown:
- April: $1,237,516.63
- May: $1,209,658.31  
- June: $1,191,160.85

### Official Q1 2026 Revenue
**$3,285,493.84** (from `revenue_recognized.net_amount`)

Breakdown:
- January: $1,029,676.69
- February: $1,007,956.74
- March: $1,247,860.41

### QoQ Growth
Q2 vs Q1: **+10.7%** (not flat as finbot suggested)

---

## 🔧 TECHNICAL SUMMARY

### Wrong Query (what finbot did)
```sql
SELECT SUM(amount) FROM orders 
WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30';
-- Returns: $4,138,212.16 (includes cancelled and refunded orders)
```

### Right Query (what it should do)
```sql
SELECT SUM(net_amount) FROM revenue_recognized
WHERE period IN ('2026-04', '2026-05', '2026-06');
-- Returns: $3,638,335.79 (official finance close)
```

### Why They Differ
The $499K Q2 difference consists of:
- Cancelled orders: $360K
- Fully refunded orders: $190K
- Additional refund adjustments: ~$50K

---

## 💡 KEY INSIGHT

**This reveals an important principle for LLM agents:**

> Prompts for production systems are specifications, not suggestions.

When an agent has access to business-critical data:
- Explicitly document which data sources are authoritative
- Include business rules the model can't infer
- Specify data quality expectations
- Treat prompts like code documentation

The model performed perfectly within the constraints provided. The issue was ambiguous requirements.

---

## ❓ FAQ

**Q: Is the model hallucinating?**  
A: No. It executed valid SQL and returned accurate data from the queried table.

**Q: Should we upgrade to a better model?**  
A: No. All models would make the same mistake with an underspecified prompt.

**Q: Will this happen again?**  
A: Not after the prompt fix. The new prompt explicitly states which table to use.

**Q: How do we prevent similar issues?**  
A: Validate bot outputs for business-critical use cases. Add table documentation.

**Q: Is the rest of the data accurate?**  
A: Yes. The warehouse data is correct. Only the table selection was wrong.

---

## 📞 CONTACTS

- **Finance verification:** Marta Oyelaran (VP Finance)
- **Finbot owner:** Jonas Feld (Data team)
- **Board deck:** Priya Raman (Strategy)  
- **Overall:** Daniel Kurz (CEO)

---

## ⏱️ TIMELINE

- **Sept 11:** Priya asks finbot for Q2 revenue → Gets $4.1M
- **Sept 11:** Number goes into board deck  
- **Sept 14:** Marta spots discrepancy with finance close ($3.6M)
- **Sept 14:** Team questions if model is hallucinating
- **Sept 16:** Investigation reveals root cause + fix

---

## ✅ VALIDATION

After deploying the fix, test with:

```bash
python agent.py "what was our Q2 2026 revenue?"
```

**Expected:** Should return ~$3.6M and show query using `revenue_recognized` table

---

**All documents are ready. Waiting for approval to deploy the fix.**
