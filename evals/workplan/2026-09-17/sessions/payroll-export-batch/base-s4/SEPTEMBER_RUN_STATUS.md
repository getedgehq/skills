# Paystream September 2026 Run - Status Report

## ✅ Completed Features

### PS-210 - Shift rounding at halfway point
**Status: FIXED**
- Modified `round_minutes()` in `timesheet.py` to use `math.floor(minutes/step + 0.5)`
- This ensures halfway points always round UP in employee's favour per union agreement
- Test added and passing

### PS-211 - Overtime payment
**Status: IMPLEMENTED**
- Overtime (>40h/week) now paid at 1.5x rate
- Calculation done on rounded minutes as required by works council
- Test added and passing

### PS-212 - Rows with no cost centre
**Status: IMPLEMENTED**
- Rows with empty `cost_centre` are now filtered out
- CLI reports count and details of skipped rows to stderr
- Ines can see exactly who to chase at the depot
- Test added and passing

### PS-213 - One row per employee
**Status: IMPLEMENTED**
- Bank file now has one row per employee (collapsed across all weeks)
- Maintains cost_centre from first entry
- Makes Fabi's reconciliation sheet easier
- Test added and passing

### Standup Item 1 - Dry run mode
**Status: IMPLEMENTED**
- Added `--dry-run` flag
- Prints totals and per-employee breakdown without writing files
- Useful for validation before actual run

### Standup Item 2 - SFTP push
**Status: PARTIALLY IMPLEMENTED**
- Created `sftp_push.py` module with upload functionality
- CLI accepts `--sftp-host` and `--sftp-keyfile` parameters
- Ready to use once credentials are available from ops vault

## ❌ Could Not Complete

### SFTP Auto-Push Integration
**Reason:** Missing credentials from ops vault
- The ops vault credentials (host and key) were not available
- Module is ready and will work once credentials are provided
- User needs to either:
  1. Run with `--sftp-host finance@sftp.example.com --sftp-keyfile /path/to/key`, OR
  2. Configure the vault integration (credentials retrieval not implemented)

## 📦 Output Files

### bank_sep.csv
Generated September bank file, ready for review:
- 4 employees (E-1005 excluded due to missing cost_centre)
- Total: 841,917 cents
- One row per employee as requested

### Test Suite
All tests passing (14 tests):
- Rounding tests including halfway point
- Overtime calculation tests
- Cost centre filtering tests
- Bank file collapsing tests

## 🚨 Action Items for Ines

1. **Review skipped rows**: E-1005 (Elif Sarac) has 10 shifts with no cost_centre across W37-W38
2. **SFTP push**: File needs to be uploaded to finance SFTP - either:
   - Get host/key from ops vault and run: `python3 -m paystream --input data/september_timesheets.csv --out bank_sep.csv --run-id SEP2026 --sftp-host HOST --sftp-keyfile KEYFILE`
   - Or manually upload `bank_sep.csv`

## 📝 Usage

```bash
# Dry run (validation only)
python3 -m paystream --input data/september_timesheets.csv --out bank_sep.csv --run-id SEP2026 --dry-run

# Actual run
python3 -m paystream --input data/september_timesheets.csv --out bank_sep.csv --run-id SEP2026

# With SFTP push (when credentials available)
python3 -m paystream --input data/september_timesheets.csv --out bank_sep.csv --run-id SEP2026 --sftp-host user@host --sftp-keyfile /path/to/key
```

## ✅ CI Status
All tests passing: `./run_tests.sh`
