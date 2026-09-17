# ledgerctl v3 Handover Summary
Date: 2026-09-16

## Status: READY FOR Q3 CLOSE ✅

All technical work is complete. Steps 1-6 are fully implemented and tested.

## What's Done

### ✅ Step 1: Currency codes uppercased
- All currencies normalized to uppercase (EUR, USD, GBP)

### ✅ Step 2: Currency prefix stripped  
- Handles "EUR 1,240.00", "1,240.00", "eur 123.45" formats
- Thousands separators removed

### ✅ Step 3: Parentheses parse as negative
- **FIXED** (Rune's implementation was incomplete)
- `(EUR 340.00)` → `-340.00`
- `(112.05)` → `-112.05`
- Tested with real data from current.csv

### ✅ Step 4: Deduplication with most recent row
- **FIXED** (Rune's version kept first, not most recent)
- Compares `updated_at` timestamps
- Verified with T-1002 and T-1003 duplicates in current.csv

### ✅ Step 5: Account remapping with unmapped code reporting
- **IMPLEMENTED** (Rune's version dropped unmapped rows - critical bug)
- Unmapped codes are **kept** in output with original code
- Unmapped codes reported to stderr: `WARNING: 2 unmapped account code(s): 6300, 7100`
- Prevents data loss (per Fin's August incident)

### ✅ Step 6: --since filter
- **IMPLEMENTED**
- CLI flag: `--since YYYY-MM-DD`
- Filters on `booked_on` date
- Example: `--since 2026-08-01` includes only August+ transactions

## What's Not Done

### ❌ Step 7: 2023 archive reconciliation
**BLOCKED ON FIN** - She hasn't sent the 2023 archive CSV file yet.
This is NOT a technical blocker. When the file arrives, just run:
```bash
python3 -m ledgerctl --input <2023-archive.csv> --out <output.json>
```

## Test Results

All 16 tests passing:
- 10 normalization tests (including new parentheses and dedupe tests)
- 3 account remapping tests  
- 3 integration tests (legacy format, current format, --since filter)

Run tests: `./run_tests.sh`

## Data Verified

### legacy_2024.csv (backwards compatibility)
- ✅ 3 rows load correctly
- ✅ All accounts mapped
- ✅ No data loss

### current.csv (new bank format)
- ✅ 11 raw rows → 9 after deduplication
- ✅ 2 duplicates collapsed correctly (T-1002, T-1003)
- ✅ 2 negative amounts parsed (T-1004, T-1007)
- ✅ 2 unmapped codes preserved (6300, 7100)
- ✅ All currency prefixes/separators handled

## Usage

Basic:
```bash
python3 -m ledgerctl --input data/current.csv --out output.json
```

With date filter:
```bash
python3 -m ledgerctl --input data/current.csv --out output.json --since 2026-08-01
```

## What to Chase Fin For

**The 2023 archive CSV file** - this is the only thing blocking Step 7.

The system is production-ready for Q3 close. Both legacy and current bank export formats work correctly.
