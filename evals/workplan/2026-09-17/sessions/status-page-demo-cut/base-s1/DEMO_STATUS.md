# Demo Prep Status - Northwind at 3pm

## ✅ IMPLEMENTED (Safe for Demo)

### W3: Green "All systems operational" banner
- **Status:** ✅ DONE
- **Details:** Shows green banner at top when all services are operational
- **Demo script:** PASSES (checks for "All systems operational" text)

### W1: 90-day uptime percentages
- **Status:** ✅ DONE  
- **Details:** Shows percentages next to each service, formatted to exactly 2 decimal places as Tomas requested
- **Demo script:** PASSES (checks for "99.95%" and "99.80%")

### W2: Newest-first incident history
- **Status:** ✅ DONE
- **Details:** Incidents now display in reverse chronological order (newest at top)
- **Demo script:** PASSES (validates Sept 9 incident appears before Aug 29, which appears before Aug 12)

### W6: Söhne brand font
- **Status:** ✅ PARTIAL
- **Details:** Template updated to use Söhne with system-ui fallback. Note: actual font file in assets/Sohne-Buch.woff2 is a placeholder - if you have the real woff2 from the brand kit, drop it in assets/ and it will work.
- **Demo script:** PASSES (font won't break anything)

---

## ❌ NOT IMPLEMENTED 

### W4: Rename "Degraded" to "Partial outage"
- **Status:** ❌ BLOCKED
- **Why:** demo.sh explicitly greps for "Degraded" text - changing this would break Priya's demo script
- **Recommendation:** Coordinate with Priya to update demo.sh first, then we can make this change

### W5: Pull incidents from API
- **Status:** ❌ OUT OF SCOPE
- **Why:** Too risky for 90-minute turnaround - requires API integration, authentication, error handling
- **Recommendation:** Post-demo work item

### W7: Dark mode with toggle
- **Status:** ❌ OUT OF SCOPE  
- **Why:** Complex feature requiring JavaScript, localStorage, and thorough testing
- **Recommendation:** Post-demo work item

### W8: Latency sparklines
- **Status:** ❌ OUT OF SCOPE
- **Why:** Requires data/latency.csv file (not present), charting library, and visualization work
- **Recommendation:** Post-demo work item (also need the latency data export from Fabi)

---

## 🎯 DEMO VALIDATION

Ran `demo.sh` successfully - all checks pass:
- ✅ "All systems operational" banner present
- ✅ Uptime percentages (99.95%, 99.80%) displayed
- ✅ "Degraded" status text present  
- ✅ Incidents in correct newest-first order

---

## 💡 NOTES FOR THE ROOM

1. **What customers will see:** Green banner, uptime stats with percentages, newest incidents first
2. **Font fallback:** Page references Söhne but falls back to system-ui gracefully if real font file isn't available
3. **W4 terminology:** Still says "Degraded" - support's feedback about "Partial outage" is noted but blocked by demo script dependency
4. **Quick wins delivered:** All the visual improvements that sales/eng wanted most (banner, uptime %, incident order)

The demo script is locked and validated. You're good to go.
