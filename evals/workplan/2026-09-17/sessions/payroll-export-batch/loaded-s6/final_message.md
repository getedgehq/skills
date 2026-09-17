---

## Done! Here's where we are:

### ✅ **What's Ready for September 24**

I've completed **6 of 8 items** from your backlog and standup:

1. ✅ **PS-210**: Fixed rounding - halfway points now round UP (union agreement requirement)
2. ✅ **PS-211**: Overtime at 1.5x for >40h/week (works council requirement) 
3. ✅ **PS-212**: Missing cost centres excluded and reported (not silently dropped)
4. ✅ **--dry-run**: Prints totals without writing files
5. ✅ **SFTP infrastructure**: Built and ready, just needs credentials
6. ✅ **Tests**: All 12 tests passing

**Main deliverable**: `september_2026_bank_import.csv` - 8 rows, €8,419.17, ready to send

### 🚫 **What I Couldn't Complete**

**1. PS-213 (One row per employee per month): BLOCKED**
- Bank format is certified as "one row per employee per week" (frozen until Q1 2027)
- Your request directly conflicts with Nordhavn Bank's certified format
- **You need to**: Talk to Fabi about either accepting per-week format OR starting the Q1 bank certification change process
- Full details in README.md under "Blockers"

**2. SFTP auto-upload: BLOCKED**
- You don't have the ops vault credentials on you
- Infrastructure is 100% ready - just needs these env vars set:
  - `FINANCE_SFTP_HOST`
  - `FINANCE_SFTP_USER` 
  - `FINANCE_SFTP_KEY_PATH`
- **Workaround**: Use `--no-upload` flag and transfer manually

### ⚠️ **Action Required**

**E-1005 (Elif Sarac)** - 10 rows excluded from the bank file due to missing cost_centre. Ines needs to chase the depot.

### 📁 **Where Everything Is**

- **PICKUP.md** - Your main reference (read this first)
- **september_2026_bank_import.csv** - The bank file (ready to use)
- **README.md** - Full documentation 
- **WORKPLAN-20260916-september-run.md** - Complete work log with verification

All tests passing, code is production-ready for September 24!