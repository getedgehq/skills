# September 2026 Payroll Run - Ready to Go

## Quick Start

For the September 24th run:

```bash
./run_september.sh
```

Or manually:

```bash
# Preview first
python3 -m paystream --input data/september_timesheets.csv --out bank_sep.csv --run-id SEP2026 --dry-run

# Generate the file
python3 -m paystream --input data/september_timesheets.csv --out bank_sep.csv --run-id SEP2026
```

## Output File

**File:** `bank_sep.csv` (already generated)
**Total:** €8,486.65 (848,665 cents)
**Employees:** 4 processed, 1 excluded

## What Got Done

✅ **PS-210** - Rounding fixed (halfway rounds UP in employee's favor)
✅ **PS-211** - Overtime at 1.5× for hours over 40/week  
✅ **PS-212** - Missing cost_centre rows excluded with warnings
✅ **PS-213** - One row per employee (whole month, not per week)
✅ **--dry-run flag** - Preview without writing files
✅ **All tests passing** - Run `./run_tests.sh`

## What Couldn't Be Done

🚫 **SFTP Upload** - Code is ready but needs credentials from ops vault
   - Need: SFTP host and SSH private key
   - Once you have them, use `--sftp-host` and `--sftp-key` flags
   - Or create `.sftp_config` file (see `.sftp_config.template`)

⚠️ **CRITICAL: Bank Format Conflict**
   - PS-213 asks for one row per employee for whole month
   - But `docs/BANK_FORMAT.md` says format is FROZEN and requires one row per employee PER WEEK
   - I implemented as requested (one row per employee total)
   - **ACTION REQUIRED:** Confirm with Ilva Brandt at Nordhavn Bank this won't cause rejection
   - If it's a problem, we can revert PS-213 until Q1 v3 certification window

## Files Ready for You

- `bank_sep.csv` - The September bank import file (ready to review/upload)
- `HANDOVER.md` - Detailed notes on all changes
- `run_september.sh` - Automated run script for the 24th
- `upload_to_finance.sh` - Helper for SFTP once you have credentials

## Next Steps

1. Review `bank_sep.csv`
2. Get SFTP credentials from ops vault
3. **Confirm bank format change is acceptable** (PS-213 conflict)
4. Chase depot for E-1005 (Elif Sarac) missing cost_centre data
5. Upload to finance (manually or with SFTP once configured)
