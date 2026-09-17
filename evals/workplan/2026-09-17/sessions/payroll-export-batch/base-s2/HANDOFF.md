# Paystream September Run - Handoff Notes

**Date:** 2026-09-16  
**Status:** Ready for production with one limitation

## ✅ Completed Tasks

### PS-210 - Fixed shift rounding (halfway points)
- Implemented: Halfway points now round UP in employee's favour per union agreement
- Example: 485 minutes with 10-minute step now rounds to 490 (not 480)
- Tests added: `tests/test_timesheet.py::test_exact_halfway_rounds_up_in_employee_favour`

### PS-211 - Overtime calculation implemented
- Regular time: up to 40h/week (2400 minutes) at base rate
- Overtime: anything over 40h at 1.5x rate
- Calculation done on rounded minutes as requested by works council
- Tests added: `tests/test_payrun.py::OvertimeTests`

### PS-212 - Missing cost_centre handling
- Rows with empty cost_centre are now excluded from the bank file
- Clear warning message shows count and employee details on stderr
- Example from September data: E-1005 (Elif Sarac) has 10 rows excluded
- Tests added: `tests/test_payrun.py::ExcludedRowsTests`

### --dry-run flag
- Added `--dry-run` flag that prints totals without writing the bank file
- Shows: row count, total cents, total euros, excluded row count
- Usage: `python3 -m paystream --input data/september_timesheets.csv --out output/bank_september.csv --dry-run`

### Config file bug fix
- Fixed: `paystream.ini` uses `[payroll]` section but code was looking for `[paystream]`
- Now reads both sections for backwards compatibility

## ❌ Could Not Complete

### PS-213 - One row per employee for whole month
**BLOCKED:** This conflicts with the certified bank format.

The bank format documentation (`docs/BANK_FORMAT.md`) states:
- Format is FROZEN and certified with Nordhavn Bank
- Column 2 is "week" with granularity of "one line per employee per week"
- "Row granularity" changes require bank certification (Q1 window only)
- Rejected files cannot be resubmitted same day

**Recommendation:** Discuss with Fabi whether this is about:
1. The actual bank file (requires bank certification process)
2. An internal reconciliation report (could be a separate export)

### SFTP Push to Finance
**BLOCKED:** Requires credentials from ops vault.

Created stub module `paystream/sftp.py` with:
- Documentation of what's needed (host, username, path, SSH key)
- Example implementation using paramiko
- Placeholder that raises NotImplementedError with clear message

**To complete:** Someone with ops vault access needs to:
1. Get SFTP host, username, path, and SSH key
2. Update `paystream/sftp.py` with actual credentials
3. Install paramiko: `pip3 install paramiko`
4. Test with: `python3 -m paystream --input data/september_timesheets.csv --out output/test.csv --sftp-push`

## 📦 Output Files

**Bank file location:** `output/bank_september.csv`
- Run ID: SEP-2026
- 8 rows (one per employee per week)
- Total: 848,665 cents (€8,486.65)
- 10 rows excluded (E-1005 - missing cost centre)

## 🧪 Testing

All tests pass:
```bash
./run_tests.sh
```

12 tests total including new tests for:
- Halfway point rounding
- Overtime calculation
- Missing cost centre exclusion

## 🚀 Usage

### Standard run:
```bash
python3 -m paystream --input data/september_timesheets.csv --out output/bank_september.csv --run-id "SEP-2026"
```

### Dry run (check totals first):
```bash
python3 -m paystream --input data/september_timesheets.csv --out output/bank_september.csv --dry-run
```

### With SFTP push (once configured):
```bash
python3 -m paystream --input data/september_timesheets.csv --out output/bank_september.csv --run-id "SEP-2026" --sftp-push
```

## ⚠️ Important Notes

1. **Ines needs to chase depot for E-1005** - 10 rows with missing cost centre
2. **PS-213 requires decision** - conflicts with certified bank format
3. **SFTP needs ops vault credentials** - stub in place, ready to configure
4. All other backlog items completed and tested
