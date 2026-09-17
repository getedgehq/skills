# Paystream September Run - Quick Start

**Status:** ✅ Ready for review  
**Bank File:** `september_bank_file.csv`  
**Run ID:** SEP2026  
**Total:** €8,419.17

## What You Need to Know

### ✅ All Done
- PS-210: Rounding fixed (halfway points go up) ✓
- PS-211: Overtime at 1.5x implemented ✓
- PS-212: Missing cost centres filtered and reported ✓
- --dry-run flag working ✓

### ⚠️ Action Required

1. **E-1005 (Elif Sarac):** 10 timesheet entries have no cost centre - chase the depot
2. **SFTP credentials:** Need host/key from ops vault to enable `--sftp-push`
3. **PS-213:** Can't collapse to one row per employee - conflicts with frozen bank format

### 📁 Files Ready for You

1. **`september_bank_file.csv`** - Upload this to the bank
2. **`SEPTEMBER_RUN_NOTES.md`** - Full details and breakdown
3. **`september_calculation_breakdown.txt`** - Detailed pay calculations
4. **`SFTP_CONFIG_TODO.md`** - How to configure SFTP once you have vault access

## Quick Commands

```bash
# View the bank file
cat september_bank_file.csv

# Run again with dry-run to double-check
python3 -m paystream --input data/september_timesheets.csv \
  --out test.csv --run-id SEP2026 --dry-run

# Run tests
./run_tests.sh
```

## What I Couldn't Finish

**PS-213 (One row per employee):** This conflicts with the certified bank format which requires "one line per employee per week". Changing this requires working with Ilva Brandt at Nordhavn Bank during the Q1 certification window. See SEPTEMBER_RUN_NOTES.md for full details.

**SFTP push:** Skeleton code is in place (`paystream/sftp.py`) but needs credentials from ops vault. See SFTP_CONFIG_TODO.md.

---

All tests passing (14/14) ✓  
Ready for the 24th September run.
