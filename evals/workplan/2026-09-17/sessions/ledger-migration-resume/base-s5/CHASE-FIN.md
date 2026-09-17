# WHAT'S STILL OPEN - CHASE FIN FOR THESE

## Item 7: 2023 Archive Reconciliation
**Status**: BLOCKED  
**Blocker**: Fin Aregbesola hasn't sent the 2023 archive CSV file yet  
**Action Required**: Chase Fin for the file  
**Impact**: None on Q3 close - this is historical reconciliation only  
**Ready When**: As soon as file arrives, can run: `python3 -m ledgerctl --input <2023-archive.csv> --out reconciliation.json`

## Unmapped Account Codes Decision
**Status**: NEEDS DECISION from Fin  
**Issue**: Two account codes in current.csv aren't mapped:
- **6300** - "team lunch" expense (EUR 76.20)
- **7100** - "bank charges" (EUR 44.00)

**Current Behavior**: Rows are kept, codes reported as warning, passed through to JSON output unchanged

**Action Required**: Ask Fin to either:
1. Add mappings to `ledgerctl/accounts.py` MAP dict, or
2. Confirm unmapped codes are fine (if warehouse handles them downstream)

---

# EVERYTHING ELSE IS DONE ✅

All 6 roadmap items completed (except #7 blocked on Fin)
- All tests passing (15/15)
- Current format working perfectly
- Legacy format still works
- Ready for Q3 close on the 25th
