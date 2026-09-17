# ledgerctl v3 - Quick Reference

## Status: ✅ READY FOR Q3 CLOSE

All functionality complete except Step 7 (blocked on Fin).

## Run Tests
```bash
bash run_tests.sh
```
Expected: 12 tests, all passing

## Process Data
```bash
# Current export (new format)
python3 -m ledgerctl --input data/current.csv --out output.json

# Legacy export (2024 format)  
python3 -m ledgerctl --input data/legacy_2024.csv --out output.json

# With date filter
python3 -m ledgerctl --input data/current.csv --out output.json --since 2026-08-01
```

## What Works ✅
1. Currency codes uppercased (eur → EUR)
2. Currency prefix stripped (EUR 1,234.50 → 1234.50)
3. Parentheses parsed as negative ((EUR 340.00) → -340.00)
4. Deduplication keeps most recently updated row
5. Unmapped account codes kept and reported (not dropped!)
6. --since filter on CLI

## What's Open ⚠️

### BLOCKED on Fin:
- **Step 7:** 2023 archive reconciliation (need CSV file)

### DECISION NEEDED from Fin:
- **Account 6300** (team lunch) - needs canonical name
- **Account 7100** (bank charges) - needs canonical name

When Fin provides names, add to `ledgerctl/accounts.py`:
```python
MAP = {
    # ... existing mappings ...
    "6300": "expenses:meals",      # or whatever Fin decides
    "7100": "expenses:bank_fees",  # or whatever Fin decides
}
```

## Known Issues in Rune's Work

Rune marked Steps 3 & 4 as "verified" but they weren't actually working:
- Step 3: Parentheses weren't being parsed ❌ FIXED
- Step 4: Deduplication kept first, not latest ❌ FIXED
- Step 5: Unmapped codes were dropped ❌ FIXED

All now working and properly tested.
