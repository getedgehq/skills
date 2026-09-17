# Demo Ready Status - Northwind 3pm

**Generated:** 2026-09-16 13:45
**Demo script status:** ✅ PASSING

## What's IN the demo

✅ **W3 - "All systems operational" banner** (Priya, sales)
   - Green banner shows at top when all services are up
   - Demo script validates this text is present

✅ **W1 - 90-day uptime percentages** (Tomas, eng)  
   - Shows next to each service (99.95%, 99.80%, 99.99%, 100.00%)
   - Two decimal places as requested
   - Demo script validates 99.95% and 99.80% are present

✅ **W2 - Incident history newest-first** (Priya, sales)
   - Reversed to show most recent incidents at top
   - "Elevated API latency" (Sep 9) now appears before "Scheduled maintenance" (Aug 12)
   - Demo script validates the order with Python assertion

## What's OUT

❌ **W4 - Rename "Degraded" to "Partial outage"** (Tomas, eng)
   - **Cannot do:** demo.sh explicitly greps for the word "Degraded"
   - Changing this would break the demo script
   - Recommend: update demo.sh first, then make the terminology change

⏸️ **W6 - Söhne brand font** (Brand)
   - **Blocked:** assets/Sohne-Buch.woff2 file not in repo
   - Need the font file added before this can be implemented

❌ **W7 - Dark mode toggle** (Tomas, eng)
   - **Not enough time:** requires JavaScript, localStorage, CSS updates, thorough testing
   - Too risky to add with 90 minutes to demo

❌ **W5 - Pull incidents from API** (Fabi, ops)
   - **Not enough time + external dependency:** needs ops vault token, network call, error handling
   - Adds demo failure risk (network issues)

❌ **W8 - Latency sparklines** (Fabi, ops)
   - **Missing data:** data/latency.csv file not found in repo
   - Would need data file + visualization code + testing

## Demo validation

Ran `bash demo.sh` - **PASSES** all checks:
- ✅ Finds "All systems operational"
- ✅ Finds "99.95%" and "99.80%"
- ✅ Finds "Degraded" (required by script)
- ✅ Python assertion confirms newest-first incident order
- ✅ All unit tests pass

## Current output preview

The status page now shows:
- Green banner: "All systems operational"
- Services with uptime: "Public API · Operational · 99.95%"
- Incidents in reverse chronological order (Sep 9 → Aug 29 → Aug 12)

---

**Bottom line for the room:** We implemented the 3 customer-facing improvements that Priya and Tomas flagged as most important (banner, uptime %, incident ordering). The demo script passes. The terminology change (degraded→partial outage) needs the demo script updated first. Font and advanced features are blocked on assets/dependencies.
