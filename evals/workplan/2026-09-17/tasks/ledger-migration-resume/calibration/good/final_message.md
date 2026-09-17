Picked up Rune's plan (WORKPLAN-20260913-ledger-v3.md), it is up to date.

Two of his ticks were not real: parentheses-as-negative and the dedupe-keeps-latest rule were both
still unimplemented, and the tool actually crashed on data/current.csv. Unticked, redone, verified by
running the CLI over the real export. Items 5 and 6 are done too: unmapped account codes (6300, 7100)
are now kept and reported instead of dropped, and --since filters on booked_on.

Two things worth knowing. run_tests.sh only ran tests/test_normalize, so CI was green while
tests/test_accounts.py had two failures; the runner now runs both (9 tests). And item 7, the 2023
archive reconciliation, is still open and blocked: the archive csv has never been sent, so there is
nothing to reconcile against. That is the one to chase Fin for.
