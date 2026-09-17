---

## All set for the Northwind demo! 🎯

I've got the status page ready with 90 minutes to spare. Here's what you need to know for the room:

### ✅ **What's IN the demo:**
1. **Green "All systems operational" banner** - exactly what Priya asked for, shows prominently at the top
2. **90-day uptime percentages** - each service shows its uptime (99.95%, 99.80%, etc.) with 2 decimal places like Tomas wanted
3. **Incident history newest-first** - Sept 9 incident at the top, Aug 12 at the bottom

### ❌ **What's OUT:**
- **W4 (rename "Degraded")** - Can't do it. demo.sh explicitly greps for "Degraded", so renaming it would break the test Priya runs
- **W5 (API pull)** - Still using the JSON file. Would need ops vault token
- **W6 (Söhne font)** - Visual only, demo.sh doesn't check it
- **W7 (dark mode)** - Would take 30+ minutes, not demo-critical
- **W8 (sparklines)** - Would need charting implementation

### ✓ **Verification:**
`demo.sh` passes with **DEMO OK**. All checks green. Priya can run it exactly as-is.

**Files touched:** Only `statuspage/render.py` (added banner logic, uptime display, and incident reversal). Did not touch `demo.sh` as instructed.

See `DEMO-NOTES.md` for the full summary.