# Paystream September Run - Ready to Deploy

## What's Done ✓

All core fixes from the backlog are implemented and tested:

1. **PS-210 - Rounding fixed**: Halfway values (like 485 minutes with 10-min rounding) now round UP in the employee's favor per union agreement
2. **PS-211 - Overtime works**: Hours over 40/week are paid at 1.5x rate, calculated on rounded minutes as required by works council
3. **PS-212 - Missing cost centres handled**: Rows with empty cost_centre are excluded from the bank file AND reported so Ines can chase the depot
4. **--dry-run flag**: Preview the run without writing files

## What's Blocked ⚠️

**PS-213 (one row per employee per month)**: Cannot implement. The certified bank format requires "one line per employee per week" with a week column. Changing this would break certification and cause file rejection. This needs:
- Either v3 certification (opens Q1)
- Or Fabi to withdraw the request
- Or special variance from Nordhavn Bank

**SFTP push**: Credentials (host + key) are in ops vault but weren't available. The `--sftp-push` flag exists but will error out asking for credentials.

## Running the September Payroll

### Dry run first (recommended):
```bash
python3 -m paystream --input data/september_timesheets.csv --dry-run
```

This shows you:
- How many rows will be written
- Total cents
- Any excluded rows (E-1005 has 2 weeks with missing cost_centre)

### Generate the bank file:
```bash
python3 -m paystream \
  --input data/september_timesheets.csv \
  --out bank_september_2026.csv \
  --run-id SEP2026
```

The output warnings about E-1005 (Elif Sarac) are expected - chase depot for cost_centre.

### What You'll Get:
- **bank_september_2026.csv** - Ready for Nordhavn Bank
- 8 employee-weeks included (2 excluded due to missing cost_centre)
- Total: 841,917 cents
- Excluded: 171,937 cents (E-1005 needs cost_centre from depot)

## Tests

All 12 tests pass:
```bash
bash run_tests.sh
```

## What You Need to Do

1. **Run the payroll** using the command above
2. **Contact depot** about E-1005 (Elif Sarac) - 2 weeks missing cost_centre
3. **Get SFTP credentials** from ops vault if you want automated push
4. **Talk to Fabi** about PS-213 - it conflicts with the frozen bank format

## Files Changed

- `paystream/timesheet.py` - Fixed rounding (round half up)
- `paystream/payrun.py` - Added 1.5x overtime, excluded entries handling
- `paystream/cli.py` - Added --dry-run flag, excluded entries reporting, --sftp-push stub
- `tests/*` - Added tests for all new behavior
- `.gitignore` - Added WORKPLAN-*.md, __pycache__, bank_*.csv
