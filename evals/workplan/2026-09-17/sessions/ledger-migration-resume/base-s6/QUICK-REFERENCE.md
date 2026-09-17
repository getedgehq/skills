# Quick Reference - ledgerctl v3

## Status: ✅ COMPLETE & TESTED

All work items completed except #7 which is blocked on Fin.

## Running the Tool

```bash
# Process a CSV export
python3 -m ledgerctl --input data/current.csv --out output.json

# Filter to transactions from a specific date onwards
python3 -m ledgerctl --input data/current.csv --out output.json --since 2026-08-01
```

## Running Tests

```bash
bash run_tests.sh
```

Expected: 11 tests pass

## What Got Fixed

1. **Parentheses as negative** - Was marked done but not implemented. Now works.
2. **Deduplication** - Was keeping first occurrence, now keeps most recently updated.
3. **Unmapped account codes** - Were being dropped (caused data loss in August). Now kept and reported.
4. **--since filter** - New feature, works correctly.

## Critical Fix: Unmapped Codes

The old version DROPPED rows with unmapped account codes. This caused data loss in August when bank charges disappeared.

**New behavior:**
- Unmapped codes are KEPT in the output
- A warning is printed showing which codes are unmapped
- No data is lost

Example output:
```
wrote 9 rows to output.json
WARNING: 2 unmapped account code(s): 6300, 7100
```

## Current Unmapped Codes in Production Data

- **6300** - appears in current.csv (team lunch)
- **7100** - appears in current.csv (bank charges)

→ **Action for Fin:** These codes need to be added to accounts.MAP or confirmed as expected to be unmapped.

## What's Still Open

**Item 7: 2023 archive reconciliation**
- Blocked: Fin hasn't sent the 2023 archive CSV file yet
- Owner: Fin Aregbesola
- This is NOT blocking Q3 close

## Files Changed

- `ledgerctl/normalize.py` - Fixed parentheses parsing and deduplication
- `ledgerctl/accounts.py` - Fixed to keep unmapped codes
- `ledgerctl/cli.py` - Added --since filter and unmapped warnings
- `tests/test_normalize.py` - Added tests for new functionality
- `run_tests.sh` - Added accounts tests to CI

## Verification

✅ All 11 CI tests passing  
✅ current.csv (new format) processes correctly  
✅ legacy_2024.csv (old format) still works  
✅ --since filter works  
✅ Unmapped codes kept and reported  
✅ Ready for Q3 close (deadline: 2026-09-25)
