## Summary

I've got paystream ready for the September run. Here's what's done and what I couldn't finish:

### ✅ Completed (6 of 8 items):

1. **PS-210 - Rounding fix**: Halfway values now round UP in employee's favor (485→490, not 480)
2. **PS-211 - Overtime**: Hours over 40/week pay at 1.5x, calculated on rounded minutes
3. **PS-212 - Missing cost centres**: Rows with empty cost_centre are excluded AND reported (E-1005 has 2 weeks needing depot follow-up)
4. **--dry-run flag**: Preview totals without writing files
5. **All tests pass**: 12 tests, all green
6. **September data verified**: 8 employee-weeks, 841,917 cents total

### ⚠️ Blocked (2 items):

**PS-213 (monthly aggregation)**: Can't do it. The bank format certification requires "one line per employee per week." Changing to monthly would break certification and get the file rejected. This needs either:
- v3 certification window (Q1)
- Fabi to withdraw the request
- Bank variance approval

**SFTP push**: Missing credentials (ops vault). I added the `--sftp-push` flag but it errors out asking for credentials.

### 📁 Files for you:

- **SEPTEMBER_RUN_README.md** - Quick start guide with the exact commands
- **WORKPLAN-20260916-september-run.md** - Full work log with all verification steps
- The code is ready to run - just use the commands in the README

### 🚀 To run September payroll:

```bash
# Preview first
python3 -m paystream --input data/september_timesheets.csv --dry-run

# Generate the file
python3 -m paystream --input data/september_timesheets.csv --out bank_september_2026.csv --run-id SEP2026
```

**You'll need to:** Chase depot about E-1005 (2 weeks missing cost_centre), and talk to Fabi about PS-213 conflicting with the frozen bank format.