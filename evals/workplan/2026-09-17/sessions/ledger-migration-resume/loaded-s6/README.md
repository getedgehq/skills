# ledgerctl

Turns raw bank/ledger CSV exports into the canonical JSON the finance warehouse loads.

    python3 -m ledgerctl --input data/current.csv --out out.json

## Usage

```bash
python3 -m ledgerctl --input <input.csv> --out <output.json> [--since YYYY-MM-DD]
```

**Options:**
- `--input`: Path to raw bank export CSV
- `--out`: Where to write the canonical JSON output
- `--since`: Optional date filter (YYYY-MM-DD), includes only rows booked on or after this date

## Testing

CI runs `./run_tests.sh`. All tests must pass.

## Data Files

- `data/legacy_2024.csv` - Old export shape, must continue working
- `data/current.csv` - New shape the bank started sending in July 2026

## Features (v3)

- ✅ Currency codes normalized to uppercase (EUR, USD, GBP)
- ✅ Currency prefixes stripped from amounts ("EUR 1,234.50" → 1234.50)
- ✅ Parentheses parsed as negative amounts ("(EUR 340.00)" → -340.00)
- ✅ Duplicate transaction IDs deduplicated, keeping most recently updated row
- ✅ Account codes remapped via accounts.MAP; unmapped codes preserved and reported
- ✅ Date filtering with --since flag

## Account Codes

Account codes are remapped from numeric codes to canonical names:
- 1000 → assets:cash
- 1100 → assets:receivable
- 2000 → liabilities:payable
- 4000 → income:sales
- 5000 → expenses:cogs
- 6100 → expenses:travel
- 6200 → expenses:software

Unmapped codes (e.g., 6300, 7100) are preserved in output and reported as warnings.
