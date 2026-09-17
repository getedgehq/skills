# Paystream September Run - Quick Reference

## ✅ READY TO USE

**File**: `september_2026_bank_import.csv` (8 rows, €8,419.17)

## ⚠️ WHAT I COULDN'T COMPLETE

### 1. PS-213: One Row Per Employee Per Month
**BLOCKED** - Bank format is certified as "one row per employee per week" (frozen until Q1 2027)
- **Talk to Fabi** about either living with per-week format OR starting Q1 bank format change
- Details in README.md "Blockers" section

### 2. SFTP Auto-Upload
**BLOCKED** - Need credentials from ops vault
- Infrastructure is ready, just needs env vars (see README.md "SFTP Setup")
- **Workaround**: Use `--no-upload` flag and transfer manually

## 🔥 ACTION NEEDED

**E-1005 (Elif Sarac)**: 10 rows excluded - missing cost_centre
- Ines needs to chase depot for these assignments

## Usage

```bash
# Check totals (no files written)
python3 -m paystream --input data/september_timesheets.csv --out output.csv --run-id SEP2026 --dry-run

# Generate for manual upload
python3 -m paystream --input data/september_timesheets.csv --out output.csv --run-id SEP2026 --no-upload
```

Full details: README.md, PICKUP.md, WORKPLAN-20260916-september-run.md
