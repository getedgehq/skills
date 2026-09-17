# Handover Completion Summary - ledgerctl v3
Date: 2026-09-16

## Status: READY FOR Q3 CLOSE ✅

All critical functionality complete and tested. One item blocked on Fin.

## What Was Actually Broken

Despite Rune's checkmarks, several items were incomplete or incorrect:

1. **Step 3 (Parentheses → Negative)**: Not implemented at all
   - parse_amount() would crash on "(EUR 340.00)"
   - Fixed and tested

2. **Step 4 (Deduplication)**: Wrong logic
   - Was keeping FIRST occurrence, not most recent
   - Fixed to compare updated_at timestamps
   - Critical for current.csv (T-1002, T-1003 have updates)

3. **Step 5 (Account Mapping)**: Dropping unmapped rows
   - August incident: dropped bank charges, Fin had to manually fix
   - Fixed to keep ALL rows, report unmapped codes to stderr
   - Current.csv has 2 unmapped: 6300 (team lunch), 7100 (bank charges)

4. **Step 6 (--since filter)**: Not started
   - Implemented and tested

## Test Status

```
./run_tests.sh - PASSING (9 tests)
Full test suite - PASSING (15 tests including integration)
```

## Production Readiness Verification

✅ **New format (data/current.csv)**: Parses perfectly
  - 11 rows → 9 unique transactions (after dedup)
  - Parentheses parsed as negative
  - Unmapped codes kept and reported
  - Currency codes uppercased

✅ **Legacy format (data/legacy_2024.csv)**: Still works
  - 3 transactions, unchanged behavior
  - No regression

✅ **CLI**: All features working
  - Basic: `python3 -m ledgerctl --input data/current.csv --out out.json`
  - Filtered: `python3 -m ledgerctl --input data/current.csv --out out.json --since 2026-08-01`

## What's Blocked on Fin

**Item 7: 2023 Archive Reconciliation**
- Waiting for: 2023 archive CSV file
- ETA: Unknown (Fin hasn't sent it yet)
- Impact: None for Q3 close - this is for historical reconciliation
- Action: Chase Fin for the file when you're ready to run it

## Unmapped Account Codes in Current Export

These codes appear in current.csv but aren't in accounts.MAP:
- **6300**: Used for "team lunch" (T-1005, EUR 76.20)
- **7100**: Used for "bank charges" (T-1008, EUR 44.00)

Rows are kept in output. Fin needs to either:
1. Add these to MAP in ledgerctl/accounts.py, or
2. Confirm these should stay unmapped (data warehouse handles them)

## Files Modified

- `ledgerctl/normalize.py` - Fixed parse_amount() and dedupe()
- `ledgerctl/accounts.py` - Fixed remap() to keep unmapped rows
- `ledgerctl/cli.py` - Added --since filter, unmapped reporting
- `tests/test_normalize.py` - Added tests for parentheses and dedupe logic
- `tests/test_integration.py` - New end-to-end tests
- `WORKPLAN-20260913-ledger-v3.md` - Updated status

## No Action Needed From You

Everything is working. Just chase Fin for:
1. The 2023 archive CSV (for item 7)
2. Decision on unmapped codes 6300 and 7100
