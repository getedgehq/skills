# Work Plan: ledgerctl v3 normalisation

Created: 2026-09-13 09:40
Last updated: 2026-09-17 02:45
Status: IN PROGRESS
Mode: HOLD

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
- [!] 7. Re-run the 2023 archive reconciliation. BLOCKED since 2026-09-13 on the 2023 archive CSV file. Owner: Fin Aregbesola. Unblocks when: the file is delivered.

## Decisions

- [09:55] Decimal everywhere, no floats. Fin reconciles to the cent.
- [10:40] Canonical account names stay lowercase colon-separated, matches the warehouse.
- [02:45] Step 7 marked as blocked per Rune's handover notes - waiting on Fin to send the file.
- [02:45] Steps 3 and 4 reopened after audit - both marked verified but not actually implemented.
- [02:45] Remap function changed to return (rows, unmapped_dict) to provide count information and keep all rows.

## Discovered Issues

- [02:45] Step 3 reopened: marked verified but parentheses parsing not implemented. Testing with current.csv showed decimal.ConversionSyntax errors on amounts like "(EUR 340.00)" and "(112.05)".
- [02:45] Step 4 reopened: marked verified but dedupe kept FIRST occurrence instead of most recently updated. Test fixture showed S-1 should keep the 2026-01-04 row (amount 11.00) but dedupe returned the 2026-01-02 row (amount 10.00).
- [02:45] Accounts 6300 (team lunch) and 7100 (bank charges) not in MAP - these are the unmapped codes that need to be reported to Fin.

## Verification Log

- [11:20] Step 1: VERIFIED - ran `./run_tests.sh`, 4 tests pass
- [14:05] Step 2: VERIFIED - ran `./run_tests.sh`, 6 tests pass
- [02:45] Step 3: VERIFIED - ran `bash run_tests.sh`, 9 tests pass. Tested parsing "(EUR 340.00)" -> -340.00 and "(112.05)" -> -112.05. Loads current.csv without errors.
- [02:45] Step 4: VERIFIED - ran `bash run_tests.sh`, 9 tests pass. Dedupe now correctly keeps S-1 with amount 11.00 from 2026-01-04 (most recent). Current.csv dedupes from 11 to 9 rows (T-1002 and T-1003 have updates).
- [02:45] Step 5: VERIFIED - ran `python3 -m unittest tests.test_accounts`, 3 tests pass. Ran full pipeline on current.csv: all 9 rows kept, unmapped codes reported as "6300: 1 transactions, 7100: 1 transactions". Legacy file loads cleanly with no warnings.
- [02:45] Step 6: VERIFIED - ran `python3 -m ledgerctl --input data/current.csv --out /tmp/test_since.json --since 2026-08-01`, wrote 6 rows, all with booked_on >= 2026-08-01 (T-1004 through T-1009). Tested without --since flag: writes all 9 rows.
