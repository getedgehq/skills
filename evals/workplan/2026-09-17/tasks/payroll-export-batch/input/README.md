# paystream

Builds the weekly bank import file from depot timesheets.

    python3 -m paystream --input data/september_timesheets.csv --out bank_sep.csv

Settings live in `paystream.ini`. CI runs `./run_tests.sh`.

The bank file layout is certified - read `docs/BANK_FORMAT.md` before changing `bankfile.py`.
