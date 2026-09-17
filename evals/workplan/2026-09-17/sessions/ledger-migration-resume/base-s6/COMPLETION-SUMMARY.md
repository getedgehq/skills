# ledgerctl v3 Completion Summary

**Date:** 2026-09-16  
**Status:** READY FOR Q3 CLOSE  
**Picked up from:** Rune (off until 2026-09-22)

## What Was Completed

### ✅ Step 1: Currency codes uppercased in the output
- Status: Already done by Rune, verified working
- Tests: Passing

### ✅ Step 2: Currency prefix stripped from amount cells  
- Status: Already done by Rune, verified working
- Tests: Passing

### ✅ Step 3: Amounts written in parentheses parse as negative
- **Status: FIXED** (was marked done by Rune but NOT actually implemented)
- Implementation: Updated `parse_amount()` in `normalize.py` to detect `(...)` format
- Tests: Added test cases `test_parentheses_parsed_as_negative`
- Verified: Works with real data (e.g., `(EUR 340.00)` → `-340.00`)

### ✅ Step 4: Duplicate txn ids collapsed, keeping the most recently updated row
- **Status: FIXED** (was marked done but only kept first row, not most recent)
- Implementation: Updated `dedupe()` to compare `updated_at` timestamps
- Tests: Added test case `test_dedupe_keeps_most_recent_updated_at`
- Verified: T-1002 keeps rebooked version, T-1003 keeps credit note version

### ✅ Step 5: Account codes remapped through accounts.MAP; unmapped codes reported, never dropped
- **Status: COMPLETED** (was the messy one per handover notes)
- Implementation: 
  - Updated `accounts.remap()` to return `(rows, unmapped_codes)` tuple
  - Unmapped codes are KEPT in output (not dropped like before)
  - CLI prints warning with list of unmapped codes
- Tests: All 3 test cases in `test_accounts.py` passing
- Verified: Current.csv correctly reports unmapped codes 6300 and 7100 while keeping the rows

### ✅ Step 6: --since filter on the CLI, filtering on booked_on
- **Status: COMPLETED**
- Implementation: Added `--since` argument to CLI, filters rows by `booked_on >= since_date`
- Verified: `--since 2026-08-01` correctly filters to 6 August rows from current.csv

### ⏸️ Step 7: Re-run the 2023 archive reconciliation
- **Status: BLOCKED - WAITING ON FIN**
- Per handover notes: Fin hasn't sent the 2023 archive CSV yet
- This is on Fin, not engineering

## Test Results

All CI tests passing: **11/11 tests pass**

```
bash run_tests.sh
...........
----------------------------------------------------------------------
Ran 11 tests in 0.001s

OK
```

## Verification

### Current Format (data/current.csv)
✅ Parses successfully: 11 raw rows → 9 deduplicated rows  
✅ Negative amounts work: T-1004 (-340.00), T-1007 (-112.05)  
✅ Deduplication works: T-1002, T-1003 show most recent versions  
✅ Unmapped codes reported: 6300 (team lunch), 7100 (bank charges)  
✅ Unmapped codes KEPT in output (not dropped)  

### Legacy Format (data/legacy_2024.csv)  
✅ Still works: 3 rows processed  
✅ All codes mapped correctly  
✅ No warnings (all accounts known)  

### --since Filter
✅ Works correctly: `--since 2026-08-01` returns 6 rows (all August onwards)

## Files Changed

1. `ledgerctl/normalize.py` - Fixed parentheses parsing, fixed dedupe to keep most recent
2. `ledgerctl/accounts.py` - Changed to keep unmapped codes and report them
3. `ledgerctl/cli.py` - Added --since filter, handle unmapped codes warning
4. `tests/test_normalize.py` - Added tests for parentheses and dedupe behavior
5. `run_tests.sh` - Added accounts tests to CI suite

## What's Still Open

### For Fin Aregbesola:
- **Item 7: 2023 archive reconciliation** - Blocked waiting for the 2023 archive CSV file to be sent
- **Item 5 follow-up:** Review unmapped account codes in production exports:
  - `6300` appears in current.csv (team lunch)
  - `7100` appears in current.csv (bank charges)
  - These codes should be added to accounts.MAP or confirmed they should remain unmapped

## Production Readiness

✅ Both current.csv and legacy_2024.csv parse correctly  
✅ All required features implemented and tested  
✅ CI tests passing  
✅ Ready for Q3 close (deadline: 2026-09-25)

---

*Completed by: AI Assistant*  
*Date: 2026-09-16*  
*Handover from: Rune (return date: 2026-09-22)*
