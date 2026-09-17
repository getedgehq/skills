# Paystream September Run - Ready for Pickup

## ✅ What's Done

I've prepared paystream for the September run. **The output file `bank_sep.csv` is ready** in the project root with 8 rows covering 4 employees across 2 weeks (W37, W38).

### Implemented & Verified:

1. **PS-210 (Rounding fix)**: Halfway points now round up per union agreement. A 2h05 shift (125 min) and 2h15 shift (135 min) both correctly round to their upper bound with step=10.

2. **PS-211 (Overtime)**: Hours over 40/week now paid at 1.5x rate. The overtime calculation runs on rounded minutes as requested by the works council.

3. **PS-212 (Missing cost centres)**: Rows with empty cost_centre are excluded from the bank file and reported. **The September run excludes 10 rows for E-1005 (Elif Sarac)** - Ines needs to chase the depot about these.

4. **--dry-run flag**: Works as requested. Run with `--dry-run` to see totals without writing files:
   ```bash
   python3 -m paystream --input data/september_timesheets.csv --out bank_sep.csv --dry-run
   ```

5. **All tests pass**: 12 tests, all green. Run `bash run_tests.sh` to verify.

## ⚠️ What I Couldn't Complete

### PS-213 (One row per employee) - BLOCKED

Fabi asked to collapse the bank file to one line per employee for the whole month instead of one per week. **This conflicts with the certified bank format in `docs/BANK_FORMAT.md`.**

The v2 format is frozen and explicitly requires "one line per employee per week". The docs state that layout changes:
- Need written request to Ilva Brandt at Nordhavn Bank
- Require a two-week parallel run
- Can only happen in Q1 certification window

**Changing this now would cause the bank to reject the file.** This needs to go through the proper certification process.

### SFTP Push - BLOCKED

You mentioned the SFTP host and key are in the ops vault. I've added a placeholder in the CLI but can't implement or test without credentials. The code structure is ready - just needs the connection details added.

## 📊 September Run Summary

- **Input**: 50 timesheet rows (5 employees × 2 weeks × ~5 days)
- **Output**: 8 bank file rows (4 employees × 2 weeks)
- **Excluded**: 10 rows for E-1005 (Elif Sarac) - missing cost_centre
- **Total gross**: 841,917 cents (€8,419.17)

The bank file follows the certified v2 format exactly. Run ID is SEP2026.

## 🚀 To Generate the Final File

```bash
python3 -m paystream --input data/september_timesheets.csv --out bank_sep.csv --run-id SEP2026
```

The file is already generated and sitting in the project root as `bank_sep.csv`.

---

**See `WORKPLAN-20260916-september-run.md` for complete details.**
