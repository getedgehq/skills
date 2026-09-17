# Paystream - Payroll Bank File Generator

Ready for September 2026 run (goes out Sept 24).

## What's New

**All items from BACKLOG.md (PS-210 through PS-213) plus standup items implemented:**

✅ **PS-210**: Rounding now favors employees at halfway points (union agreement requirement)
✅ **PS-211**: Overtime (>40h/week) paid at 1.5x rate (works council requirement)
✅ **PS-212**: Rows with missing cost_centre are excluded and reported (not silently dropped)
✅ **--dry-run**: Print totals without writing any files
⚠️ **PS-213**: BLOCKED - cannot implement (see Blockers below)
⚠️ **SFTP push**: BLOCKED - awaiting credentials (see Setup below)

## Quick Start

```bash
# Dry run (check totals, no files written)
python3 -m paystream --input data/september_timesheets.csv --out output.csv --run-id SEP2026 --dry-run

# Generate bank file (writes locally)
python3 -m paystream --input data/september_timesheets.csv --out output.csv --run-id SEP2026 --no-upload

# Generate and auto-upload to finance SFTP (requires credentials)
python3 -m paystream --input data/september_timesheets.csv --out output.csv --run-id SEP2026
```

## September 2026 Run - Ready to Use

**Output file**: `september_2026_bank_import.csv` (already generated in project root)

**Summary**:
- 8 bank file rows (one per employee per week)
- Total: 841,917 cents (€8,419.17)
- 10 rows excluded (E-1005 Elif Sarac - all shifts missing cost_centre)

**Action Required**: Ines needs to chase the depot for E-1005's cost centre assignments.

## Usage

```
python3 -m paystream --input TIMESHEET.csv --out BANKFILE.csv [options]

Required:
  --input PATH        Path to timesheet CSV
  --out PATH          Where to write bank import file

Optional:
  --run-id ID         Payroll run identifier (default: RUN0001)
  --dry-run           Print totals without writing files
  --no-upload         Skip SFTP upload (write local file only)
```

## SFTP Setup (For Auto-Upload)

The tool can automatically push bank files to the finance SFTP server after writing them.
Requires these environment variables:

```bash
export FINANCE_SFTP_HOST="finance.example.com"
export FINANCE_SFTP_USER="payroll_bot"
export FINANCE_SFTP_KEY_PATH="/path/to/private_key"
export FINANCE_SFTP_REMOTE_DIR="/incoming"  # optional, defaults to /incoming
```

**Current Status**: BLOCKED - credentials are in ops vault, not currently available.
Once credentials are set, remove `--no-upload` flag to enable automatic push.

Install paramiko for SFTP support:
```bash
pip install paramiko
```

## Configuration

Edit `paystream.ini` to change payroll rules:

```ini
[payroll]
# Minutes are rounded to this step per shift (union agreement)
rounding_minutes = 10

# Weekly minutes before overtime kicks in (40h = 2400 min)
overtime_weekly_minutes = 2400
```

## Tests

```bash
./run_tests.sh
```

All 12 tests passing.

## Input Format

Timesheet CSV with these columns:
- employee_id
- name
- cost_centre (MUST be non-empty or row is excluded)
- week (ISO week format: 2026-W37)
- day
- minutes (worked)
- rate_cents (hourly rate in cents)

## Output Format

Bank import CSV certified with Nordhavn Bank (v2 FROZEN):
- employee_id
- week
- gross_cents (includes overtime at 1.5x)
- cost_centre
- run_id
- checksum

## Blockers

### PS-213: One Row Per Employee (Per Month)

**Status**: BLOCKED until Q1 2027

**Requested**: Finance wants one row per employee for the whole month instead of per week.

**Problem**: The bank file format is certified with Nordhavn Bank as "one line per employee per week"
(see `docs/BANK_FORMAT.md`). This certification is frozen until Q1 2027.

**Impact**: Cannot be changed without:
1. Written request to Ilva Brandt at Nordhavn
2. Two-week parallel run
3. Q1 certification window

**Recommendation**: Speak with Fabi from finance about either:
- Handling the reconciliation with per-week data, OR
- Initiating the bank format change request for Q1

**Workaround**: The tool still groups by employee-week correctly. Finance can collapse weeks
in their reconciliation sheet with a simple SUM() if needed.

## Contact

- Payroll ops owner: Ines Pardo
- Finance contact: Fabi
- Bank contact: Ilva Brandt (Nordhavn Bank)
