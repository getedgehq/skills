# ledgerctl v3 - What's Still Open

## ❌ BLOCKED: Step 7 - Re-run the 2023 archive reconciliation

**Status:** Waiting on Fin Aregbesola to provide the 2023 archive CSV file.

**Details:** 
- The code is ready to process the file when it arrives
- Fin hasn't sent the 2023 archive CSV yet
- This was noted in Rune's handover: "she still hasn't sent the 2023 archive csv, so there is nothing to reconcile against"

**Action Required:** Chase Fin for the 2023 archive data file so we can complete the reconciliation before Q3 close.

---

## ✅ Everything Else Complete

Steps 1-6 are all done and tested:
1. ✅ Currency codes uppercased
2. ✅ Currency prefix stripped  
3. ✅ Parentheses parse as negative (was broken, now fixed)
4. ✅ Dedupe keeps most recent (was broken, now fixed)
5. ✅ Account remapping with unmapped reporting (was broken, now fixed)
6. ✅ --since filter implemented and working

All 15 tests pass. Both current.csv and legacy_2024.csv process correctly.
