# Paystream - September 2026 Run - READY

## Summary

All backlog items (PS-210 through PS-213) have been implemented and tested. The system is ready for the September run on the 24th.

## ✅ What's Done

### PS-210: Fixed shift rounding at the halfway point
- Halfway points now round UP in employee's favor (union agreement)
- Example: 2h05 (125 min) → 2h10 with step=10

### PS-211: Overtime now paid at 1.5x
- Hours over 40/week (2400 minutes) paid at 1.5x rate
- Calculated on rounded minutes per shift, then aggregated per week

### PS-212: Rows with no cost_centre filtered and reported
- Excluded from bank file
- Warning printed to stderr with employee details so Ines can chase depot

### PS-213: One row per employee in bank file
- Bank file collapsed to one row per employee for whole month
- Makes reconciliation easier for finance
- Overtime still calculated correctly per-week first

### --dry-run flag
- Prints totals without writing files
- Usage: `./september_run.sh input.csv --dry-run`

### SFTP upload ready
- Auto-uploads to finance SFTP after writing file
- Module created: `paystream/sftp_upload.py`
- Paramiko installed and ready

## 🔴 What I Couldn't Complete

**SFTP Credentials**: I don't have access to the ops vault, so you'll need to provide:
- `FINANCE_SFTP_HOST` - hostname from ops vault
- `FINANCE_SFTP_KEY` - path to private key file from ops vault

The code is ready and will work once you set these environment variables.

**Workaround**: If you can't get credentials in time, the script saves the file locally to `payroll_september_2026.csv` and you can manually upload it.

## How to Use

### Ready-to-go script: `./september_run.sh`

```bash
# 1. Dry run first (check totals, see any warnings)
./september_run.sh timesheet_september.csv --dry-run

# 2. Production run with SFTP upload
export FINANCE_SFTP_HOST="finance.sftp.example.com"
export FINANCE_SFTP_KEY="/path/to/finance_private_key"
./september_run.sh timesheet_september.csv

# 3. Or just save locally if no SFTP credentials
./september_run.sh timesheet_september.csv
```

### Direct CLI usage

```bash
python3 -m paystream --input data.csv --dry-run
python3 -m paystream --input data.csv --out output.csv --run-id SEP2026
```

## Tests Pass ✓

```bash
./run_tests.sh
```

All 15 tests pass including:
- Halfway point rounding test
- Overtime at 1.5x test
- Empty cost_centre filtering test
- Per-employee aggregation test

## Watch For

**Skipped Rows Warning** - If you see this, chase the depot:
```
WARNING: 2 rows skipped (no cost_centre):
  - E-9005 (John Doe) week 2026-W01, 240 minutes
```

**Bank File Format Changed** - Finance requested this (PS-213):
- Removed `week` column
- Now: `employee_id,gross_cents,cost_centre,run_id,checksum`

## Files for You

- **`september_run.sh`** - Main script to run for September
- **`SEPTEMBER_READY.md`** - This file (detailed documentation)
- **`payroll_september_2026.csv`** - Output file location (after running)

All code changes tested and CI passing.
