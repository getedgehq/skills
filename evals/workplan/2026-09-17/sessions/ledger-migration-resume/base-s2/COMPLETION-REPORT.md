# ledgerctl v3 - Completion Status

**Date:** 2026-09-16  
**Status:** READY FOR Q3 CLOSE  
**Previous owner:** Rune (on leave until 2026-09-22)  
**Completed by:** AI Assistant

## Summary

All critical items for Q3 close have been completed and verified. The system now correctly processes both legacy (2024) and current (July 2026+) bank export formats.

## Completed Items

### ✅ Step 1: Currency codes uppercased in the output
- **Status:** COMPLETE (was already done by Rune)
- **Verification:** All tests pass

### ✅ Step 2: Currency prefix stripped from amount cells
- **Status:** COMPLETE (was already done by Rune)
- **Verification:** Handles "EUR 1,234.50" format correctly

### ✅ Step 3: Amounts written in parentheses parse as negative
- **Status:** COMPLETE (fixed - Rune's verification was incorrect)
- **Issue found:** Code was not handling parentheses at all
- **Fix applied:** Updated `parse_amount()` to detect and handle parentheses format
- **Verification:** 
  - `(EUR 340.00)` → `-340.00` ✓
  - `(112.05)` → `-112.05` ✓
  - New tests added to prevent regression

### ✅ Step 4: Duplicate txn ids collapsed, keeping the most recently updated row
- **Status:** COMPLETE (fixed - Rune's verification was incorrect)
- **Issue found:** Code was keeping first row, not most recent
- **Fix applied:** Updated `dedupe()` to compare `updated_at` timestamps
- **Verification:**
  - T-1002: keeps 2026-08-30 update (298.40) not 2026-07-11 (318.40) ✓
  - T-1003: keeps 2026-08-12 update (9750.00) not original (9800.00) ✓
  - New test added to verify behavior

### ✅ Step 5: Account codes remapped through accounts.MAP; unmapped codes reported, never dropped
- **Status:** COMPLETE (implemented)
- **Issue found:** Original `remap()` function was dropping unmapped rows entirely (the August bank charges disaster)
- **Fix applied:** 
  - Refactored `remap()` to return tuple: `(rows, unmapped_codes)`
  - Unmapped codes kept in output with original code
  - Warning printed to stderr listing unmapped codes
  - Each unmapped code reported once in order first seen
- **Verification:**
  - Code 6300 (team lunch) kept in output ✓
  - Code 7100 (bank charges) kept in output ✓
  - Warning shows: "WARNING: 2 unmapped account code(s): 6300, 7100" ✓

### ✅ Step 6: --since filter on the CLI, filtering on booked_on
- **Status:** COMPLETE (implemented)
- **Implementation:** Added `--since` argument that filters rows by `booked_on >= date`
- **Verification:**
  - `--since 2026-08-01` on current.csv returns 6 rows (T-1004 through T-1009) ✓
  - All returned dates are >= filter date ✓
  - Test added

### ⏸️ Step 7: Re-run the 2023 archive reconciliation
- **Status:** BLOCKED - waiting on Fin Aregbesola
- **Blocker:** Fin hasn't sent the 2023 archive CSV file yet
- **Note:** This is on Fin to provide and reconcile, not a dev task
- **Action required:** Chase Fin for the 2023 archive file

## Testing

### Test Coverage
- **Total tests:** 14 tests (up from 6)
- **All tests passing:** ✓
- **CI script updated:** Now runs all tests (`unittest discover`)

### Test Files
- `tests/test_normalize.py` - 8 tests (added 3 new)
- `tests/test_accounts.py` - 3 tests (all fixed)
- `tests/test_cli.py` - 1 test (new)
- `tests/test_integration.py` - 2 tests (new, end-to-end verification)

### Manual Verification
- ✅ `data/legacy_2024.csv` processes correctly (backward compatibility maintained)
- ✅ `data/current.csv` processes with all new features
- ✅ Both deduplications in current.csv work correctly
- ✅ Both negative amounts (parentheses) in current.csv parse correctly
- ✅ Unmapped account codes 6300 and 7100 are kept and reported

## Files Modified

1. `ledgerctl/normalize.py` - Fixed parentheses parsing and deduplication logic
2. `ledgerctl/accounts.py` - Refactored to keep unmapped codes and report them
3. `ledgerctl/cli.py` - Added --since filter and unmapped code warnings
4. `run_tests.sh` - Updated to run all tests (was only running test_normalize)
5. `tests/test_normalize.py` - Added tests for parentheses and dedupe behavior
6. `tests/test_cli.py` - New file with --since filter test
7. `tests/test_integration.py` - New file with end-to-end tests

## Known Issues / Follow-ups

### For Fin Aregbesola (Finance)
1. **URGENT:** Two account codes need to be added to the MAP or documented as intentionally unmapped:
   - **6300** - "team lunch" (appears in current.csv, 1 transaction)
   - **7100** - "bank charges" (appears in current.csv, 1 transaction)
   
2. **2023 archive reconciliation** - Still waiting on the CSV file from Fin

### Notes
- All code changes maintain backward compatibility with legacy_2024.csv format
- System warns but doesn't fail when encountering unmapped account codes (per Fin's August feedback)
- Decimal precision maintained throughout (no floats used)
- Account names remain lowercase colon-separated format (matches warehouse)

## How to Run

```bash
# Run all tests (what CI runs)
./run_tests.sh

# Process current export
python3 -m ledgerctl --input data/current.csv --out output.json

# Process with date filter
python3 -m ledgerctl --input data/current.csv --out output.json --since 2026-08-01

# Process legacy export (backward compatibility)
python3 -m ledgerctl --input data/legacy_2024.csv --out output.json
```

## Q3 Close Readiness

**STATUS: ✅ READY**

All development work is complete. The system can successfully process:
- ✅ New bank export format (July 2026+)
- ✅ Legacy 2024 exports (backward compatible)
- ✅ All required normalizations and transformations
- ✅ Proper handling of edge cases (duplicates, negatives, unmapped codes)

**Remaining non-dev items:**
- Fin needs to add account codes 6300 and 7100 to the MAP
- Fin needs to provide 2023 archive CSV for reconciliation
