# ledgerctl

Turns raw bank/ledger CSV exports into the canonical JSON the finance warehouse loads.

    python3 -m ledgerctl --input data/current.csv --out out.json

CI runs `./run_tests.sh`.

`data/legacy_2024.csv` is the old export shape and has to keep working.
`data/current.csv` is a sample of the new shape the bank started sending in July.
