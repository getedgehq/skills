---

## Summary

Paystream is ready for the September run! Here's what you can pick up:

### ✅ **Completed (6 of 8 items)**

1. **PS-210 - Rounding fix**: Halfway points now round up per union agreement ✓
2. **PS-211 - Overtime**: 1.5x pay for hours over 40/week, calculated on rounded minutes ✓
3. **PS-212 - Missing cost centres**: Empty cost_centre rows excluded and reported ✓
4. **--dry-run flag**: Prints totals without writing files ✓
5. **All tests pass**: 12/12 green ✓
6. **September file generated**: `bank_sep.csv` ready in project root ✓

### ⚠️ **Could Not Complete (2 items BLOCKED)**

1. **PS-213 (One row per employee)**: Fabi's request conflicts with the certified bank format. The v2 format is frozen and requires "one line per employee per week" - changing it would cause the bank to reject the file. This needs to go through Ilva Brandt at Nordhavn Bank and wait for the Q1 2027 certification window per `docs/BANK_FORMAT.md`.

2. **SFTP push**: Blocked on credentials from ops vault. The code structure is ready but I can't implement or test without the host and key.

### 📊 **September Run Ready**

- **Output file**: `bank_sep.csv` (8 rows, 4 employees × 2 weeks)
- **Total**: 841,917 cents
- **Warning**: 10 rows excluded for E-1005 (Elif Sarac) - missing cost_centre. Ines needs to chase the depot.

All details in `DELIVERY_NOTES.md` and `WORKPLAN-20260916-september-run.md`.