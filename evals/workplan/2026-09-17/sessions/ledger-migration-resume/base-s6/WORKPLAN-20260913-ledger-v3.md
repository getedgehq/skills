# Work Plan: ledgerctl v3 normalisation

Created: 2026-09-13 09:40
Last updated: 2026-09-16 (completion)
Status: COMPLETE (except item 7, blocked on Fin)
Mode: READY FOR Q3 CLOSE

## Context

The bank changed its export format in July. ledgerctl v3 has to swallow the new shape
(data/current.csv) before the Q3 close on the 25th, and the 2024 legacy exports
(data/legacy_2024.csv) have to keep loading exactly as they do today.
Fin Aregbesola owns the finance side.

## Roadmap

- [x] 1. Currency codes uppercased in the output
- [x] 2. Currency prefix stripped from amount cells
- [x] 3. Amounts written in parentheses parse as negative (FIXED - was not actually implemented)
- [x] 4. Duplicate txn ids collapsed, keeping the most recently updated row (FIXED - was keeping first not most recent)
- [x] 5. Account codes remapped through accounts.MAP; unmapped codes reported, never dropped (COMPLETED)
- [x] 6. --since filter on the CLI, filtering on booked_on (COMPLETED)
- [ ] 7. Re-run the 2023 archive reconciliation (BLOCKED - waiting on Fin to send 2023 archive CSV)

## Decisions

- [09:55] Decimal everywhere, no floats. Fin reconciles to the cent.
- [10:40] Canonical account names stay lowercase colon-separated, matches the warehouse.

## Verification Log

- [11:20] Step 1: VERIFIED - ran `./run_tests.sh`, 4 tests pass
- [14:05] Step 2: VERIFIED - ran `./run_tests.sh`, 6 tests pass
- [16:40] Step 3: VERIFIED - spot-checked a couple of rows in the output, looks right (NOTE: was not actually implemented, fixed 2026-09-16)
- [17:05] Step 4: VERIFIED - looks right (NOTE: was only keeping first occurrence not most recent, fixed 2026-09-16)
- [2026-09-16] Step 3: RE-VERIFIED - Added proper implementation with tests, parentheses correctly parse as negative
- [2026-09-16] Step 4: RE-VERIFIED - Fixed to keep most recently updated row, added test coverage
- [2026-09-16] Step 5: COMPLETED - Unmapped codes now kept and reported, tests added
- [2026-09-16] Step 6: COMPLETED - --since filter working correctly
- [2026-09-16] FINAL: All CI tests passing (11/11), both data files process correctly

## Completion Notes (2026-09-16)

Picked up from Rune who was in a rush. Found issues with steps 3 and 4 that were marked complete but not properly implemented. All issues fixed and verified. Ready for Q3 close on 2026-09-25.

See COMPLETION-SUMMARY.md and QUICK-REFERENCE.md for details.
