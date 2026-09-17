# Work Plan: ledgerctl v3 normalisation

Created: 2026-09-13 09:40
Last updated: 2026-09-16 (handover completion)
Status: COMPLETED (except item 7 - blocked on Fin)
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
- [ ] 7. Re-run the 2023 archive reconciliation (BLOCKED: waiting for Fin to send 2023 archive CSV)

## Decisions

- [09:55] Decimal everywhere, no floats. Fin reconciles to the cent.
- [10:40] Canonical account names stay lowercase colon-separated, matches the warehouse.

## Verification Log

- [11:20] Step 1: VERIFIED - ran `./run_tests.sh`, 4 tests pass
- [14:05] Step 2: VERIFIED - ran `./run_tests.sh`, 6 tests pass
- [16:40] Step 3: VERIFIED - spot-checked a couple of rows in the output, looks right
- [17:05] Step 4: VERIFIED - looks right
- [2026-09-16] **RE-VERIFIED ALL STEPS** after discovering issues:
  - Steps 3 & 4 were NOT actually working correctly despite being marked done
  - Fixed parse_amount() to handle parentheses as negative
  - Fixed dedupe() to keep most recently updated row (was keeping first seen)
  - Fixed accounts.remap() to return (rows, unmapped) tuple and keep unmapped codes
  - Added --since CLI filter
  - All 12 tests now pass
  - Verified with current.csv: deduplication, negative amounts, unmapped codes all working
  - Verified with legacy_2024.csv: backward compatibility maintained
  - Verified --since filter: correctly filters by booked_on date

## Completion Notes (2026-09-16)

**What was completed:**
- All steps 1-6 are now fully working and tested
- Test suite expanded from 6 to 12 tests
- run_tests.sh fixed to run all tests (was only running test_normalize)
- Current export format (current.csv) parses correctly
- Legacy export format (legacy_2024.csv) continues to work
- Unmapped account codes (6300, 7100) are properly reported with warnings

**What's still open:**
- Step 7: 2023 archive reconciliation - BLOCKED on Fin sending the archive CSV file
  - No action possible until file is received
  - Priority: Chase Fin for the 2023 archive CSV

**Known unmapped codes in current.csv:**
- 6300: appears in current data (team lunch)
- 7100: appears in current data (bank charges)
- Fin needs to decide on canonical names for these accounts
