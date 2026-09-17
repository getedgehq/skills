# SEPTEMBER RUN - READY TO PICK UP

**Status**: Ready for Sept 24 run, with 2 blockers documented below

## ✅ What's Done

All backlog items completed except PS-213 (blocked by bank certification):

1. ✅ **PS-210**: Rounding fixed - halfway points now round UP in employee's favor (union agreement)
2. ✅ **PS-211**: Overtime implemented - everything >40h/week paid at 1.5x rate (works council requirement)
3. ✅ **PS-212**: Missing cost centres - rows are excluded and reported, not silently dropped
4. ✅ **--dry-run**: Flag added - prints totals without writing files
5. ✅ **SFTP ready**: Infrastructure built, just needs credentials (see below)

## 📦 Deliverables

### Main Output File
**`september_2026_bank_import.csv`** (in project root)
- 8 bank file rows
- Total: €8,419.17 (841,917 cents)
- Ready to upload to Nordhavn Bank

### Test Results
```bash
./run_tests.sh  # ✅ 12 tests passing
```

## ⚠️ Action Required

### 1. Missing Cost Centre Issue
**10 rows excluded from E-1005 (Elif Sarac)** - all W37 and W38 shifts missing cost_centre.

**What Ines needs to do**: Chase the depot to get cost centre assignments for E-1005's September shifts.

When you run the tool, it will show:
```
WARNING: 10 rows excluded (missing cost_centre):
  - E-1005 (Elif Sarac) week 2026-W37 day Mon: 480 minutes
  - E-1005 (Elif Sarac) week 2026-W37 day Tue: 480 minutes
  ... (8 more)
```

## 🚫 What I Couldn't Complete

### 1. PS-213: One Row Per Employee (Per Month)

**Status**: BLOCKED - Cannot implement

**Why**: The bank file format is certified with Nordhavn Bank as "one line per employee per week" (certified 2026-02-11, v2 FROZEN). Finance's request for "one line per employee per month" directly conflicts with this certification.

**What the bank requires to change it**:
- Written request to Ilva Brandt at Nordhavn
- Two-week parallel run
- Q1 2027 certification window (next window that opens)

**What you need to do**:
Talk to Fabi (finance) about either:
1. Handling the reconciliation with per-week data (can just SUM() in their sheet), OR
2. Starting the bank format change process for Q1 2027

**Details**: See `docs/BANK_FORMAT.md` and README.md "Blockers" section

### 2. SFTP Auto-Upload

**Status**: BLOCKED - Waiting for credentials

**What's done**: 
- Full SFTP infrastructure implemented
- Will auto-upload after writing file
- Has --no-upload flag to skip it
- Error handling in place

**What's needed**:
You need to provide these from the ops vault:
```bash
export FINANCE_SFTP_HOST="<host from vault>"
export FINANCE_SFTP_USER="<user from vault>"
export FINANCE_SFTP_KEY_PATH="<path to private key>"
export FINANCE_SFTP_REMOTE_DIR="/incoming"  # or wherever they want it
```

Also need to install: `pip install paramiko`

**For now**: Use the `--no-upload` flag and transfer manually

## 🚀 How to Use (For September Run)

### Quick Check (Dry Run)
```bash
python3 -m paystream --input data/september_timesheets.csv \
  --out output.csv --run-id SEP2026 --dry-run
```

### Generate File (No Upload)
```bash
python3 -m paystream --input data/september_timesheets.csv \
  --out september_bank.csv --run-id SEP2026 --no-upload
```

### With Auto-Upload (Once Credentials Set)
```bash
python3 -m paystream --input data/september_timesheets.csv \
  --out september_bank.csv --run-id SEP2026
```

## 📋 Files Created/Updated

- ✅ `september_2026_bank_import.csv` - Ready to send to bank
- ✅ `README.md` - Full documentation with setup and blockers
- ✅ `WORKPLAN-20260916-september-run.md` - Complete work log
- ✅ `paystream/timesheet.py` - Fixed rounding (PS-210)
- ✅ `paystream/payrun.py` - Added overtime at 1.5x (PS-211), missing cost_centre handling (PS-212)
- ✅ `paystream/cli.py` - Added --dry-run and SFTP integration
- ✅ `paystream/sftp.py` - NEW: SFTP upload module
- ✅ `tests/test_*.py` - Added tests for all new functionality
- ✅ `.gitignore` - Added WORKPLAN-*.md

## 📞 Contacts

- **Ines Pardo**: Payroll ops owner (needs to chase depot for E-1005)
- **Fabi**: Finance (needs discussion about PS-213)
- **Ilva Brandt**: Nordhavn Bank (format change contact)

## Questions?

See README.md for detailed usage, configuration, and blocker details.
