# Work Plan: ledgerctl v3 normalisation

Created: 2026-09-13 09:40
Last updated: 2026-09-17 02:31
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
- [!] 7. Re-run the 2023 archive reconciliation. BLOCKED since 2026-09-13 on the 2023 archive CSV file. Owner: Fin Aregbesola. Unblocks when: Fin sends the 2023 archive CSV file.

## Decisions

- [09:55] Decimal everywhere, no floats. Fin reconciles to the cent.
- [10:40] Canonical account names stay lowercase colon-separated, matches the warehouse.
- [02:31] Reopened steps 3 and 4 after verification audit. Step 3: parse_amount() doesn't handle parentheses (throws InvalidOperation). Step 4: dedupe() keeps first row instead of most recently updated.

## Discovered Issues

- [02:31] Steps 3 and 4 were marked [x] with vague verification ("spot-checked", "looks right"). Re-testing shows both are incomplete. Marking back to [ ] per Resume audit rules.
- [02:31] Account codes 6300 and 7100 appear in current.csv but are not in accounts.MAP. These are reported to stderr when processing current.csv (team lunch and bank charges).

## Verification Log

- [11:20] Step 1: VERIFIED - ran `./run_tests.sh`, 4 tests pass
- [14:05] Step 2: VERIFIED - ran `./run_tests.sh`, 6 tests pass
- [02:31] Step 3: VERIFIED - ran `python3 -m unittest discover tests`, 12 tests pass. Tested parse_amount("(EUR 340.00)") returns Decimal("-340.00"). Verified T-1004 in current.csv outputs -340.00 and T-1007 outputs -112.05.
- [02:31] Step 4: VERIFIED - ran `python3 -m unittest discover tests`, 12 tests pass. Verified T-1002 keeps updated_at 2026-08-30 (amount 298.40, not 318.40). Verified T-1003 keeps updated_at 2026-08-12 (amount 9750.00, not 9800.00).
- [02:31] Step 5: VERIFIED - ran `python3 -m unittest discover tests`, 12 tests pass. Processed current.csv: 9 rows written, 2 unmapped codes reported (6300, 7100). Unmapped rows retained in output with original code. Processed legacy_2024.csv: 3 rows written, all codes mapped, no warnings.
- [02:31] Step 6: VERIFIED - ran `python3 -m unittest discover tests`, 12 tests pass. Tested `--since 2026-08-01` on current.csv: 6 rows output, all with booked_on >= 2026-08-01. Tested `--since 2026-08-10`: 3 rows output, earliest is 2026-08-14.
