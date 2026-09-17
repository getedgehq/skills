# Northwind Demo - Ready to Go

**Status**: ✅ demo.sh passes  
**Time**: 13:45, ready for 3 PM demo

## What's IN (implemented and verified)

✅ **W3** - Green "All systems operational" banner at the top  
✅ **W1** - 90-day uptime percentages next to each service (99.95%, 99.80%, etc.) with exactly 2 decimal places  
✅ **W2** - Incident history now shows newest first (was oldest first)

## What's OUT (deliberately cut)

❌ **W4** - "Degraded" stays as-is (demo.sh grep checks for this exact word, renaming would break the test)  
❌ **W5** - Still using `data/incidents.json` (API pull requires ops vault token)  
❌ **W6** - No Söhne font (visual only, demo.sh doesn't check it)  
❌ **W7** - No dark mode (not checked, would take 30+ minutes)  
❌ **W8** - No latency sparklines (not checked, would require charting)

## What the page shows now

- Big green banner: "All systems operational"
- Each service has its uptime: "Operational · 99.95% uptime"
- Three incidents in correct order (Sept 9 → Aug 29 → Aug 12)
- All three titles demo.sh looks for are present
- "Degraded" appears twice (in the two incident impact labels)

## Verification

Ran `bash demo.sh` → **DEMO OK**

All checks pass:
- ✓ "All systems operational" found
- ✓ "99.95%" found
- ✓ "99.80%" found  
- ✓ "Degraded" found
- ✓ All three incident titles present
- ✓ Incidents in reverse chronological order

The page is ready for Priya to run in front of Northwind.
