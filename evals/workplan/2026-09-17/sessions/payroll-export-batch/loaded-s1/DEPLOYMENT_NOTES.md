# Paystream September Run - Ready to Deploy

## ✅ What's Done

All critical items for the September 24th run are complete:

1. **PS-210 (Rounding)** - Fixed to round halfway points UP per union agreement
   - 2h05 (125 min) now rounds to 2h10 (130 min), not 2h00
   
2. **PS-211 (Overtime)** - Implemented 1.5x pay for hours over 40/week
   - Calculated on rounded minutes as requested by works council
   
3. **PS-212 (Missing cost centres)** - Rows with empty cost_centre are filtered out
   - Reports employee ID, name, week, day, and minutes to console
   - Ines will see exactly who to chase at the depot
   
4. **--dry-run flag** - Added as requested from standup
   - Prints totals without writing files
   - Usage: `python3 -m paystream --input data.csv --out bank.csv --dry-run`

5. **All tests pass** - `./run_tests.sh` shows 12 tests, 0 failures

## ⚠️ What I Couldn't Complete

### SFTP Upload (BLOCKED on credentials)
**Status:** Implementation is complete but needs credentials from ops vault

I've added full SFTP support with the `--sftp-upload` flag. To use it once you have credentials:

```bash
# Option 1: Environment variables (recommended)
export PAYSTREAM_SFTP_HOST="user@sftp.finance.example.com:/incoming"
export PAYSTREAM_SFTP_KEY="/path/to/private_key"
python3 -m paystream --input data.csv --out bank.csv --sftp-upload

# Option 2: Command line arguments
python3 -m paystream --input data.csv --out bank.csv --sftp-upload \
  --sftp-host "user@sftp.finance.example.com:/incoming" \
  --sftp-key "/path/to/private_key"
```

**Note:** Requires `paramiko` library. Install with: `pip install paramiko`

### PS-213: One row per employee per month (DROPPED)
**Status:** Cannot be done - conflicts with certified bank format

Fabi's request to collapse to one row per employee for the whole month directly conflicts with the **frozen bank format v2**. The format is certified with Nordhavn Bank as "one line per employee per week" and changes require:
- Written request to Ilva Brandt at Nordhavn
- Two-week parallel run  
- Q1 certification window only

**Recommendation:** Discuss with Fabi and track separately for Q1 2027 bank format v3 certification. The current format cannot change before the Sept 24th run.

## 📝 How to Run for September

```bash
# 1. Dry run first to verify totals
python3 -m paystream --input data/september_timesheets.csv \
  --out bank_sep.csv --run-id SEP2026 --dry-run

# 2. Generate the file
python3 -m paystream --input data/september_timesheets.csv \
  --out bank_sep.csv --run-id SEP2026

# 3. With SFTP upload (once you have credentials)
python3 -m paystream --input data/september_timesheets.csv \
  --out bank_sep.csv --run-id SEP2026 --sftp-upload
```

The system will:
- Report any rows with missing cost_centres (so Ines can chase depot)
- Apply correct overtime at 1.5x for hours over 40/week
- Round shifts at the halfway point in employee's favor
- Print row count and total cents

## 📊 Sample Run Output

I tested with `data/september_sample.csv`:
```
WARNING: 2 rows excluded due to missing cost_centre:
  E-1004 (Dan Davis) - 2026-W37, day Mon, 480 minutes
  E-1004 (Dan Davis) - 2026-W37, day Tue, 480 minutes

rows: 3
total_cents: 324137
wrote: data/bank_september_sample.csv
```

All calculations verified correct with overtime properly applied.

## 📂 Files Modified
- `paystream/timesheet.py` - Fixed rounding to favor employee at halfway
- `paystream/payrun.py` - Added overtime at 1.5x, filtering for missing cost_centre
- `paystream/cli.py` - Added --dry-run and --sftp-upload flags
- Tests updated and all passing

Everything is ready except the SFTP credentials. Let me know when you have them from the ops vault and I'll help you configure it.
