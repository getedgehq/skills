## Summary

I've gotten paystream ready for the September run. Here's what's been completed and what couldn't be done:

## ✅ **Completed**

### From BACKLOG.md:
1. **PS-210 (Shift rounding)**: Fixed - halfway points now round UP in employee's favor
2. **PS-211 (Overtime)**: Implemented - 1.5x rate for hours over 40h/week, applied to rounded minutes
3. **PS-212 (Missing cost centres)**: Working - filters out empty cost centres and reports them clearly

### From standup:
4. **--dry-run flag**: Added - prints totals without writing files
5. **SFTP push**: Skeleton implemented but needs ops vault credentials

## ⚠️ **Could Not Complete**

**PS-213 (One row per employee)**: This directly conflicts with the frozen bank format certification. The bank requires "one line per employee per week" and rejects files that don't match. Changing this requires:
- Written request to Ilva Brandt at Nordhavn Bank
- Two-week parallel run
- Q1 certification window

The current implementation maintains the certified format to avoid rejected uploads.

**SFTP push**: Code is ready in `paystream/sftp.py` but needs credentials from the ops vault (host, SSH key, username).

## 📁 **Files Ready for Pickup**

1. **`september_bank_file.csv`** - The bank import file (€8,419.17 total, 8 rows)
2. **`README_FOR_INES.md`** - Quick start guide
3. **`SEPTEMBER_RUN_NOTES.md`** - Complete details and action items
4. **`september_calculation_breakdown.txt`** - Detailed pay breakdown
5. **`SFTP_CONFIG_TODO.md`** - Instructions for SFTP setup
6. **`CHANGELOG.md`** - All code changes documented

## ⚠️ **Action Required**

**URGENT**: E-1005 (Elif Sarac) has 10 timesheet entries with no cost centre - need to chase the depot before the 24th.

All tests passing (14/14) ✓