# 👋 START HERE

## Quick Answer

**🟡 CONDITIONAL GO** - Ship the new "Warmth" prompt Friday IF you fix the data layer by Thursday.

---

## What You Asked

> "can you sanity check it and give me a go/no-go? we're going to keep tweaking this prompt every couple weeks so anything that makes the next check less painful is welcome."

---

## What You Get

### 1. The Decision (2 min read)
📄 **[EXEC_SUMMARY.txt](EXEC_SUMMARY.txt)** - Visual summary with checklist

### 2. Quick Reference (5 min read)
📄 **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Everything you need to know

### 3. Full Analysis (15 min read)
📄 **[GO_NO_GO_REPORT.md](GO_NO_GO_REPORT.md)** - Complete audit with evidence

### 4. Examples (5 min read)
📄 **[SIDE_BY_SIDE_EXAMPLES.md](SIDE_BY_SIDE_EXAMPLES.md)** - See the actual reply differences

### 5. How to Use This (2 min read)
📄 **[README.md](README.md)** - File guide and next steps

---

## The Bottom Line

### ✅ What's Good
- **Fixed** critical legal escalation bug (T-1011)
- **Warmer** tone (2.8/5 → 4.6/5 team rating)
- **Better** policy compliance (3/8 → 4/8)
- **Safe** "do whatever it takes" language (not causing problems)

### ❌ What's Blocking
- **4 tickets** offered refunds outside 30-day window
- **Both prompts** have this bug (model calculates dates wrong)
- **Fix needed:** Add `refund_eligible` computed field

### 🔧 What to Do
1. **Thursday EOD:** Eng adds `refund_eligible`, `days_since_delivery` fields
2. **Re-run:** `python output/judge.py` → expect 7/8 pass
3. **Friday 9am:** Ship to 10%, monitor 2 hours
4. **Friday 2pm:** If clean → 100%

---

## For Future Prompt Changes

You now have an **automated test harness**:

```bash
# Run evaluation
python output/judge.py new_outputs.jsonl

# Check for regressions
# - Any new failures?
# - Any violations introduced?
# - Ship only if same or better
```

**Golden set:** 8 test cases with policy constraints  
**Judge:** Automated pass/fail checker  
**Expand:** Add edge cases, incidents, CSAT=1 tickets

This makes biweekly prompt tweaks **fast and safe**.

---

## Key Files

| File | Purpose | Read This If... |
|------|---------|-----------------|
| **EXEC_SUMMARY.txt** | One-page decision | You need to brief someone quickly |
| **QUICK_REFERENCE.md** | Key findings & action items | You're making the ship decision |
| **GO_NO_GO_REPORT.md** | Full analysis | You need all the evidence |
| **SIDE_BY_SIDE_EXAMPLES.md** | Actual reply comparisons | You want to see the differences |
| **judge.py** | Automated checker | You're shipping a prompt change |
| **golden_set.jsonl** | Test cases | You're expanding the test suite |

---

## One-Sentence Summary

**Ship it, but fix the date math first - your new prompt is better than the old one and the "do whatever it takes" language is helping, not hurting.**

---

## Questions?

See **[README.md](README.md)** for:
- Harness status scorecard
- Questions to ask engineering
- How to expand the golden set
- What to monitor post-ship

---

📊 **Score:** Old 3/8 → New 4/8 (improvement)  
🐛 **Bug fixed:** Legal escalation (critical)  
🔧 **Bug found:** Date math (both prompts)  
✨ **Warmth:** 2.8/5 → 4.6/5 (team rating)  

**Recommended action:** Fix data layer → re-eval → ship Friday.
