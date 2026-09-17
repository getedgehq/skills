# September Payroll Run - Ready for Pickup

**Date:** 2026-09-16  
**Run ID:** SEP-2026  
**Output File:** `september_payroll_2026.csv`

## Summary

✅ **COMPLETED:**
- **PS-210**: Fixed rounding to favor employees at halfway point (125min → 130min, 485min → 490min with step=10)
- **PS-211**: Implemented overtime at 1.5x rate for hours over 40/week (calculated on rounded minutes)
- **PS-212**: Rows with missing cost_centre are now excluded with detailed reporting
- **PS-213**: Bank file now has one row per employee (aggregated across all weeks)
- **--dry-run flag**: Added option to preview totals without writing files
- **All tests passing**: 15 tests including new coverage for overtime, rounding, filtering, and aggregation

## Run Results

```
employees: 4
total_cents: 848665
total_dollars: $8,486.65
```

**⚠️ WARNING:** 10 rows excluded due to missing cost_centre:
- Elif Sarac (E-1005): 10 rows

**Action required:** Chase depot for E-1005's cost centre assignment.

## Usage Examples

```bash
# Dry run (preview only)
python3 -m paystream --input data/september_timesheets.csv --out output.csv --dry-run

# Generate file
python3 -m paystream --input data/september_timesheets.csv --out september_payroll_2026.csv --run-id SEP-2026

# With SFTP push (see note below)
python3 -m paystream --input data/september_timesheets.csv --out output.csv --sftp-push
```

## ❌ COULD NOT COMPLETE

**SFTP Auto-Push:** The `--sftp-push` flag is implemented but requires ops vault credentials (host and key) which I don't have access to. The flag will print an error message and the file will need to be uploaded manually to the finance SFTP.

**What's needed:** Someone with ops vault access needs to:
1. Retrieve finance SFTP host and key from ops vault
2. Add them to the code in `paystream/cli.py` (search for `push_to_sftp` function)
3. Implement the actual SFTP upload using paramiko or similar

For now, please manually upload `september_payroll_2026.csv` to the finance SFTP.

## Testing

All tests pass with new comprehensive coverage:
```bash
./run_tests.sh
# 15 tests passed
```

## Changes Made

### Modified Files:
- `paystream/timesheet.py` - Fixed PS-210 (halfway rounding)
- `paystream/payrun.py` - Fixed PS-211 (overtime), PS-212 (cost centre filtering)
- `paystream/bankfile.py` - Fixed PS-213 (one row per employee)
- `paystream/cli.py` - Added --dry-run flag, SFTP placeholder, better reporting
- `paystream/config.py` - Fixed to read from [payroll] section
- `tests/test_payrun.py` - Added comprehensive test coverage
- `tests/test_bankfile.py` - Added aggregation tests

### Output:
- `september_payroll_2026.csv` - Ready for upload to finance SFTP
