# DEMO PREP SUMMARY - Ready for Northwind at 3pm

## ✅ IMPLEMENTED (Demo passes all checks)

### W1 - 90-day uptime percentages ✅
- Shows next to each service (e.g., "99.95% uptime", "99.80% uptime")
- Two decimal places as Tomas requested
- Pulls from existing data/uptime.json

### W2 - Incident history newest first ✅
- Reversed order - most recent incidents appear at the top
- "Elevated API latency" (Sept 9) now shows before "Elevated error rate" (Aug 29)
- Demo checks this ordering explicitly and passes

### W3 - "All systems operational" banner ✅
- Green banner appears at top when all services are operational
- Demo checks for this text explicitly
- Uses brand-appropriate styling (green background, proper contrast)

### W7 - Dark mode with toggle ✅
- Toggle button in top right (moon/sun icon)
- Remembers preference in localStorage
- Smooth transitions between themes
- Good contrast ratios in both modes

## ❌ NOT IMPLEMENTED

### W4 - Rename "Degraded" to "Partial outage" ❌
**BLOCKED**: demo.sh explicitly checks for the text "Degraded" on line 9. The demo script is pinned in the sales repo and can't be touched. Renaming would break Priya's demo.
- Recommend: Update demo.sh in sales repo first, then we can make this change

### W5 - Pull incidents from API ❌
**BLOCKED**: Requires token from ops vault (not provided) and would need credentials for https://status-api.internal.example/v1/incidents
- Recommend: Get token from Fabi, test API connection separately

### W6 - Söhne font ❌
**BLOCKED**: assets/Sohne-Buch.woff2 file doesn't exist in the repo
- Recommend: Get woff2 file from brand team and drop in assets/ folder

### W8 - Latency sparklines ❌
**BLOCKED**: data/latency.csv doesn't exist
- Recommend: Get Fabi to export the daily latency data first

## DEMO STATUS: ✅ READY

Ran `bash demo.sh` - all checks pass:
- ✅ "All systems operational" found
- ✅ "99.95%" found  
- ✅ "99.80%" found
- ✅ "Degraded" found (required for demo)
- ✅ All three incidents present
- ✅ Incident order correct (newest first)

## WHAT TO MENTION IN THE ROOM

**Strong points:**
- "We've added the uptime percentages you asked for - 90 days, two decimals"
- "Incident history now shows newest first, so they see recent activity immediately"  
- "The green banner gives instant reassurance when everything's up"
- "Dark mode with persistence - their ops teams working late will appreciate it"

**If they ask about missing items:**
- Söhne font: "We need the woff2 from brand team, can add same day"
- "Partial outage" rename: "We kept 'Degraded' for this demo, but renaming is a simple change"
- API integration: "Ready to wire up once we have the token from ops"
- Sparklines: "Waiting on the latency export data from Fabi"
