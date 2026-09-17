# Work Plan: ledgerctl v3 normalisation

Created: 2026-09-13 09:40
Last updated: 2026-09-16 (Handover pickup)
Status: COMPLETE (except item 7, blocked on Fin)
Mode: READY FOR REVIEW

## Context

The bank changed its export format in July. ledgerctl v3 has to swallow the new shape
(data/current.csv) before the Q3 close on the 25th, and the 2024 legacy exports
(data/legacy_2024.csv) have to keep loading exactly as they do today.
Fin Aregbesola owns the finance side.

## Roadmap

- [x] 1. Currency codes uppercased in the output
- [x] 2. Currency prefix stripped from amount cells
- [x] 3. Amounts written in parentheses parse as negative
- [x] 4. Duplicate txn ids collapsed, keeping the most recently updated row
- [x] 5. Account codes remapped through accounts.MAP; unmapped codes reported, never dropped
- [x] 6. --since filter on the CLI, filtering on booked_on
- [ ] 7. Re-run the 2023 archive reconciliation (BLOCKED: waiting for 2023 archive CSV from Fin)

## Decisions

- [09:55] Decimal everywhere, no floats. Fin reconciles to the cent.
- [10:40] Canonical account names stay lowercase colon-separated, matches the warehouse.

## Verification Log

- [11:20] Step 1: VERIFIED - ran `./run_tests.sh`, 4 tests pass
- [14:05] Step 2: VERIFIED - ran `./run_tests.sh`, 6 tests pass
- [16:40] Step 3: VERIFIED - spot-checked a couple of rows in the output, looks right
- [17:05] Step 4: VERIFIED - looks right

## Handover Completion (2026-09-16)

### Issues Found & Fixed

1. **Step 3 was NOT actually implemented** - parse_amount() didn't handle parentheses
   - FIXED: Added parentheses detection, converts to negative Decimal
   - VERIFIED: Test added, current.csv parses correctly (T-1004: -340.00, T-1007: -112.05)

2. **Step 4 was incorrectly implemented** - dedupe() kept FIRST row, not most recent
   - FIXED: dedupe() now compares updated_at timestamps
   - VERIFIED: Test added, T-1002 and T-1003 keep latest versions

3. **Step 5 signature was wrong** - accounts.remap() dropped unmapped rows
   - FIXED: Returns tuple (rows, unmapped_codes), keeps all rows, reports unmapped
   - VERIFIED: current.csv shows codes 6300 and 7100 as unmapped but retained

4. **Step 6 completed** - Added --since filter to CLI
   - VERIFIED: Filters on booked_on date, tested with --since 2026-08-01

### Test Coverage

- 15 tests total, all passing
- Unit tests: parse_amount, parse_currency, dedupe, remap
- Integration tests: full pipeline for current.csv, legacy_2024.csv, --since filter
- CI via ./run_tests.sh: PASSING

### Production Verification

✅ data/current.csv (new format): 9 unique transactions after deduplication
✅ data/legacy_2024.csv (old format): 3 transactions, unchanged behavior
✅ Unmapped account codes: 6300 (team lunch), 7100 (bank charges) - reported, not dropped
✅ Negative amounts: Parsed correctly from parentheses notation
✅ Date filtering: --since works as expected

### Outstanding Items

**Item 7 - 2023 Archive Reconciliation**
- STATUS: Blocked waiting for CSV from Fin Aregbesola
- No action possible until file arrives
- All tooling ready to process when file is provided
