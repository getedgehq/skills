# PayStream September Run - Ready for Pickup

## ✅ What's Done

All backlog items completed and tested:

1. **PS-210 (Rounding fix)**: Halfway points now round up per union agreement. 2h05→2h10, 2h15→2h15 ✓
2. **PS-211 (Overtime)**: Hours over 40/week now paid at 1.5x rate ✓
3. **PS-212 (Missing cost centres)**: Rows with empty cost_centre are excluded and reported with employee details ✓
4. **PS-213 (Reconciliation)**: Now generates TWO files:
   - `bank_sep.csv` - Original format for the bank (one row per employee per week)
   - `bank_sep_reconciliation.csv` - NEW: Collapsed format for Fabi (one row per employee for the month)
   
   Note: I didn't modify the bank file format because docs/BANK_FORMAT.md shows it's frozen and certified with Nordhavn Bank. Changes require formal process. The reconciliation file gives Fabi what she needs without risking rejected imports.

5. **--dry-run flag**: Prints totals without writing files ✓

All tests pass (12/12).

## 🚫 What I Couldn't Complete

**SFTP auto-push** - The code is written and ready, but blocked on credentials from the ops vault.

### To enable SFTP when you have credentials:

1. Install paramiko: `pip install paramiko`
2. Add this section to `paystream.ini`:
```ini
[sftp]
host = finance.sftp.yourcompany.com
username = paystream_bot
key_path = /path/to/ssh/private/key
remote_dir = /uploads/payroll
```

Then the bank file will auto-upload after writing. Use `--no-sftp` to skip upload.

## 📁 Files Changed

- `paystream/timesheet.py` - Fixed rounding logic
- `paystream/payrun.py` - Added 1.5x overtime, filtering for empty cost_centre
- `paystream/bankfile.py` - Added `write_reconciliation()` for PS-213
- `paystream/cli.py` - Added --dry-run, exclusion warnings, reconciliation output, SFTP integration
- `paystream/config.py` - Added SFTP config loading
- `paystream/sftp.py` - NEW: SFTP upload module (ready when credentials available)
- `tests/test_timesheet.py` - Added halfway rounding tests
- `tests/test_payrun.py` - Added overtime and exclusion tests

## 🧪 How to Run

```bash
# Normal run
python3 -m paystream --input data/september_timesheets.csv --out bank_sep.csv --run-id SEP2026

# Dry run (check totals first)
python3 -m paystream --input data/september_timesheets.csv --out bank_sep.csv --dry-run

# Tests
./run_tests.sh   # or: bash run_tests.sh
```

You'll get both the bank file AND the reconciliation file for Fabi's team.

See `WORKPLAN-20260916-september-payrun.md` for full verification log.
