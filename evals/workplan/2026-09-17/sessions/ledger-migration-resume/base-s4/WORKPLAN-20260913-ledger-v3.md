# Work Plan: ledgerctl v3 normalisation

Created: 2026-09-13 09:40
Last updated: 2026-09-16 (by assistant, continuing Rune's work)
Status: STEPS 1-6 COMPLETE
Mode: READY FOR Q3 CLOSE

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
- [ ] 7. Re-run the 2023 archive reconciliation

## Decisions

- [09:55] Decimal everywhere, no floats. Fin reconciles to the cent.
- [10:40] Canonical account names stay lowercase colon-separated, matches the warehouse.

## Verification Log

- [11:20] Step 1: VERIFIED - ran `./run_tests.sh`, 4 tests pass
- [14:05] Step 2: VERIFIED - ran `./run_tests.sh`, 6 tests pass
- [16:40] Step 3: VERIFIED - spot-checked a couple of rows in the output, looks right
- [17:05] Step 4: VERIFIED - looks right

## 2026-09-16 Update (Assistant Pick-up)

Re-verified and fixed steps 3-4 per handover notes warning. Completed steps 5-6.

### Issues Found and Fixed:
- **Step 3**: parse_amount() was not handling parentheses - FIXED, tested with (EUR 340.00) and (112.05)
- **Step 4**: dedupe() was keeping first occurrence instead of most recent - FIXED to compare updated_at
- **Step 5**: remap() was dropping unmapped rows - FIXED to keep all rows and return list of unmapped codes
- **Step 6**: --since filter - IMPLEMENTED, filters on booked_on date (YYYY-MM-DD format)

### Test Coverage:
- All 16 tests passing (10 normalize, 3 accounts, 3 integration)
- Integration tests verify both legacy_2024.csv and current.csv work correctly
- Current.csv tests verify: deduplication, negative amounts, unmapped code handling, --since filter

### Verified Features:
✅ Legacy 2024 format loads correctly (backwards compatible)
✅ Current format with all edge cases: EUR prefixes, thousands separators, parentheses, lowercase currency
✅ Deduplication keeps most recent updated_at (T-1002: kept 2026-08-30 version, T-1003: kept credit note)
✅ Negative amounts: (EUR 340.00) → -340.00, (112.05) → -112.05
✅ Unmapped codes kept and reported: 6300 and 7100 preserved in output, warning to stderr
✅ --since filter: `--since 2026-08-01` correctly filters on booked_on date

### Outstanding:
- **Step 7**: Blocked on Fin - waiting for 2023 archive CSV file
