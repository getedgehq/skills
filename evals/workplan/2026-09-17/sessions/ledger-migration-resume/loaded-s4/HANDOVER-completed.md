# ledgerctl v3 Completion Summary

Date: 2026-09-17 02:52
Picked up from: Rune (out until 2026-09-22)
Status: 6 of 7 items completed and verified, 1 blocked

## What Was Completed

### Steps 1-2: Already Working ✓
- Currency codes uppercased (EUR, USD, GBP)
- Currency prefix stripped from amounts
- Thousands separators handled

### Steps 3-4: Fixed and Verified ✓
**Issue**: Rune marked these as done but they weren't implemented correctly.

- **Step 3 (Parentheses as negative)**: `parse_amount()` now handles `(EUR 340.00)` → `-340.00`
  - Tested with current.csv: 2 negative amounts load correctly (T-1004, T-1007)
  
- **Step 4 (Deduplication)**: Now keeps most recently updated row by comparing `updated_at` timestamps
  - Tested with current.csv: T-1002 keeps "rebooked" version, T-1003 keeps "credit note applied"

### Step 5: Account Remapping ✓
**Critical Fix**: Original implementation dropped unmapped codes (caused August data loss per Rune's notes).

- Unmapped codes now KEPT in output with original code
- Unmapped codes reported to stderr with WARNING
- Tested: codes 6300 and 7100 are kept and reported

### Step 6: --since Filter ✓
- New CLI flag: `--since YYYY-MM-DD`
- Filters on `booked_on` field
- Reports how many rows filtered

## What's Blocked

### Step 7: 2023 Archive Reconciliation
**BLOCKED** on Fin Aregbesola since 2026-09-13
- Waiting for: 2023 archive CSV file
- Cannot proceed without the file
- Action needed: Chase Fin for the file

## Test Coverage

- **All tests pass**: 16 tests, 0 failures
- CI command: `./run_tests.sh` (runs core normalize tests)
- Full suite: `python3 -m unittest discover tests`

## Data Verification

### current.csv (new bank format)
- 11 raw rows → 9 deduplicated rows
- 2 negative amounts parsed correctly
- 2 unmapped account codes (6300, 7100) kept and reported
- All amounts parse to Decimal

### legacy_2024.csv (old format)
- 3 rows load correctly
- Backward compatible

## Usage

```bash
# Basic
python3 -m ledgerctl --input data/current.csv --out output.json

# With date filter
python3 -m ledgerctl --input data/current.csv --out output.json --since 2026-08-01
```

## Outstanding Action Items

1. **Chase Fin for 2023 archive CSV** - needed to unblock step 7
2. **Consider adding account codes 6300 and 7100 to MAP** - they appear in current data:
   - 6300: team lunch (expenses category?)
   - 7100: bank charges (expenses:fees?)

## Files Modified

- `ledgerctl/normalize.py` - fixed parentheses parsing and deduplication
- `ledgerctl/accounts.py` - fixed to keep unmapped codes
- `ledgerctl/cli.py` - added --since filter and unmapped warnings
- `tests/test_normalize.py` - added tests for steps 3 & 4
- `tests/test_cli.py` - added CLI and integration tests
- `.gitignore` - created (was missing)
- `WORKPLAN-20260913-ledger-v3.md` - updated with audit findings

## Ready for Q3 Close

✅ All new bank format parsing complete
✅ Legacy format compatibility maintained
✅ All tests passing
✅ CI green
⚠️  Step 7 blocked but not critical for Q3 close (2023 is historical)
