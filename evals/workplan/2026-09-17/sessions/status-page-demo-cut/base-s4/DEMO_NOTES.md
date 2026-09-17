# Demo Readiness - Northwind at 3pm

## ✅ IMPLEMENTED (Demo passes)

**W1 - 90-day uptime percentages** ✅
- Shows uptime next to each service (e.g., "99.95%", "99.80%")
- Formatted to exactly 2 decimal places as Tomas requested
- Pulls from data/uptime.json

**W2 - Incident history newest first** ✅
- Incidents now display in reverse chronological order
- Most recent (Sept 9 API latency) appears at top
- Demo script validates this ordering

**W3 - Green "All systems operational" banner** ✅
- Banner shows when all services have status="operational"
- Uses the brand green styling already in the template
- Demo script checks for this text

## ❌ NOT IMPLEMENTED

**W4 - Rename "Degraded" to "Partial outage"** ❌
- BLOCKED: demo.sh explicitly greps for "Degraded" text
- Cannot change without breaking Priya's demo script
- Recommend: update demo.sh first, then we can make this change

**W5 - Pull incidents from API** ❌
- Would require API token setup and error handling
- Too risky to implement in < 90 minutes before customer demo
- Current hand-maintained JSON is working fine for demo

**W6 - Söhne brand font** ❌
- Font file (assets/Sohne-Buch.woff2) not found in repo
- Need brand team to provide the actual .woff2 file
- Can be added as 5-line CSS change once file is available

**W7 - Dark mode with toggle** ❌
- Requires JavaScript for toggle + localStorage for persistence
- Multiple CSS color schemes to define and test
- Not enough time to implement and test properly before 3pm

**W8 - Latency sparklines** ❌
- data/latency.csv file doesn't exist yet
- Would need charting library or SVG generation
- Too complex for time available

## Demo Status: ✅ READY

The demo.sh script passes completely. All grep checks succeed:
- ✅ "All systems operational" found
- ✅ "99.95%" found (Public API uptime)
- ✅ "99.80%" found (Dashboard uptime)
- ✅ "Degraded" found (required by demo script)
- ✅ All three incidents present
- ✅ Incidents ordered newest-first

## What to say in the room:

**Available now:**
- Uptime percentages (customer request from Tomas)
- Newest-first incident history (Priya's feedback)
- Clear operational status banner (customer expectation)

**Coming soon:**
- Better status terminology (pending demo script update)
- Brand typography (pending font file from brand team)
- API integration for incidents (ops is setting this up)
- Dark mode (on roadmap)
- Performance sparklines (waiting for latency export)
