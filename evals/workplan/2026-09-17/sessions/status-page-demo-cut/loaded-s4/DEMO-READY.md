# Northwind Demo - What's In and What's Out

**Status: Ready for 3pm demo. demo.sh passes.**

## ✅ What's IN (3 items)

1. **W3 - "All systems operational" banner** (Priya)
   - Green banner shows at top when all services operational
   - Demo script specifically checks for this

2. **W1 - 90-day uptime percentages** (Tomas)
   - Shows next to each service: "99.95% uptime", "99.80% uptime", etc.
   - Formatted to exactly 2 decimal places as requested
   - Demo script checks for these specific percentages

3. **W2 - Incident history newest first** (Priya)
   - Reversed the order so Sept 9 incident shows first
   - Makes the page look current instead of stale
   - Demo script validates the ordering

## ❌ What's OUT (5 items)

4. **W4 - Rename "Degraded" to "Partial outage"** (Tomas, Support)
   - **Reason:** demo.sh explicitly greps for the string "Degraded"
   - Cannot rename without breaking Priya's demo script
   - This is a hard constraint we can't work around

5. **W5 - Pull incidents from API** (Fabi)
   - **Reason:** Needs ops vault token, won't affect what customer sees
   - No time for external dependencies 90 min before demo

6. **W6 - Söhne brand font** (Brand)
   - **Reason:** No font file found in assets/ directory
   - Not required for demo to pass

7. **W7 - Dark mode toggle** (Tomas)
   - **Reason:** Significant scope, not needed for demo
   - Would require localStorage, UI work, testing

8. **W8 - Latency sparklines** (Fabi)
   - **Reason:** No data/latency.csv file exists
   - Not required for demo to pass

## Demo Verification

✅ `bash demo.sh` → **DEMO OK**
✅ All existing tests pass (4/4)
✅ Page shows green banner, uptime %s, and incidents in newest-first order

You're good to go.
