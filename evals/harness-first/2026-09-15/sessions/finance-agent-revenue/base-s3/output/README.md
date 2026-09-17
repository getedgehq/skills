# FinBot Q2 Revenue Investigation - Output Files

This directory contains the complete analysis of the Q2 revenue discrepancy between FinBot ($4.1M) and Finance ($3.6M).

## Quick Start

**For Daniel (CEO) - Read this first:**
- 📄 `ONE_PAGER.txt` - Visual one-page summary (30 seconds)
- 📄 `EXECUTIVE_SUMMARY.md` - Quick overview with action items (2 minutes)

**For the team:**
- 📄 `FINDINGS.md` - Complete root cause analysis (5 minutes)
- 📄 `TECHNICAL_ANALYSIS.md` - Deep technical dive for engineers (10 minutes)

**Implementation:**
- 📄 `prompt_FIXED.md` - Updated prompt that fixes the issue (deploy this)

**Data:**
- 📄 `analysis_data.json` - Raw analysis data
- 📄 `comparison_data.csv` - Side-by-side comparison of all metrics

## Key Findings

### The Issue
FinBot reported Q2 2026 revenue as **$4,138,212** when the correct figure is **$3,638,336** - a $500K discrepancy that made it into the board pre-read.

### Root Cause
The bot queried the **wrong table** (`orders` instead of `revenue_recognized`), which included cancelled and refunded orders. This is **not a model capability issue** - the prompt lacks business context about which table to use for financial reporting.

### The Fix
**Update the prompt** (10 minutes, $0 cost) - see `prompt_FIXED.md`

**DO NOT** upgrade the model - it won't help without better instructions.

### Impact
- ✅ Correct Q2 revenue: **$3.6M**
- ✅ Bot is not hallucinating
- ✅ Model (Claude Sonnet 4.5) is working correctly
- ✅ Fix is simple and immediate

## File Descriptions

### ONE_PAGER.txt
ASCII-formatted visual summary with the key facts, data breakdown, and action items. Best for quick scanning.

### EXECUTIVE_SUMMARY.md
Plain-language explanation for non-technical stakeholders. Includes:
- The numbers
- What went wrong
- Why it's not a model issue
- Recommended fix
- Action items

### FINDINGS.md
Comprehensive root cause analysis with:
- Full timeline of events
- Data breakdown by table and status
- Explanation of why this happened
- Recommendations (immediate, short-term, long-term)
- Supporting evidence

### TECHNICAL_ANALYSIS.md
Deep technical dive for engineers:
- SQL queries executed
- Data model relationships
- Why the model made this choice
- Testing methodology
- Implementation recommendations

### prompt_FIXED.md
The corrected system prompt with:
- Table descriptions
- Business context
- Usage guidelines
- Examples

Deploy this to fix the issue immediately.

### analysis_data.json
Raw data from the investigation in JSON format:
```json
{
  "bot_calculation": 4138212.16,
  "finance_calculation": 3638335.79,
  "orders_by_status": [...],
  "revenue_recognized": {...},
  "monthly_breakdown": [...]
}
```

### comparison_data.csv
Detailed comparison metrics in CSV format for further analysis in Excel/Sheets.

## Timeline

- **Sept 11, 2026**: Priya asks finbot for Q2 revenue in Slack
- **Sept 11, 2026**: Bot responds with $4.1M (from orders table)
- **Sept 11, 2026**: Number goes into board deck
- **Sept 14, 2026**: Finance VP flags $500K discrepancy in exec thread
- **Sept 14, 2026**: CEO (Daniel) questions if bot is hallucinating
- **Sept 15, 2026**: Investigation completed, root cause identified

## Action Items

- [ ] Review findings (Daniel)
- [ ] Deploy fixed prompt
- [ ] Correct board deck ($3.6M, not $4.1M)
- [ ] Test fix with original question
- [ ] Add test suite for future prevention
- [ ] Brief team on what happened

## Questions?

All evidence is in the warehouse.db database. The Slack transcripts are in:
- `../transcripts/2026-09-11_board-deck.md`
- `../notes/slack-exec-thread.txt`

The bot code is in:
- `../agent.py`
- `../prompt.md` (current prompt with the issue)
- `../config.py`

---

**Investigation completed:** September 15, 2026  
**Prepared for:** Daniel Kurz (CEO)  
**Conducted by:** Data team analysis
