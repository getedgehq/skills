# Status Page Demo - Implementation Status
**For Northwind demo at 3 PM**  
**Prepared:** 2026-09-16 ~1:30 PM

---

## ✅ IMPLEMENTED & READY FOR DEMO

### W1 - 90-day Uptime Percentages ✓
**Status:** COMPLETE  
**Requester:** Tomas (eng)  
- Shows uptime percentage next to each service (e.g., "99.95%", "99.80%")
- Two decimal places as specified
- Pulls from existing `data/uptime.json`
- Displays in muted color between service name and status

### W2 - Incident History Newest First ✓
**Status:** COMPLETE  
**Requester:** Priya (sales)  
- Incidents now display in reverse chronological order (newest at top)
- "Elevated API latency" (Sept 9) now appears first
- "Scheduled maintenance window" (Aug 12) appears last
- Fixes the issue where page looked stale

### W3 - "All Systems Operational" Banner ✓
**Status:** COMPLETE  
**Requester:** Priya (sales)  
- Green banner appears at top when all services are operational
- Uses brand colors (green background, dark green text)
- Only shows when nothing is down
- Customers get instant visual confirmation

---

## ❌ NOT IMPLEMENTED

### W4 - Rename "Degraded" to "Partial Outage"
**Status:** BLOCKED  
**Requester:** Tomas (eng), Support  
**Issue:** The demo.sh script explicitly checks for the word "Degraded" in the output. Since demo.sh is pinned and cannot be modified, changing this term would break the demo. This needs to be coordinated - update demo.sh first, then we can implement the rename.

### W5 - Pull Incidents from API
**Status:** NOT IMPLEMENTED (out of scope for time)  
**Requester:** Fabi (ops)  
**Why:** Would require:
- Access to ops vault for API token
- Integration with `https://status-api.internal.example/v1/incidents`
- Error handling for API failures
- Possible caching strategy
**Timeline:** 2-4 hours of work, needs ops coordination

### W6 - Use Söhne Brand Font
**Status:** NOT IMPLEMENTED (missing asset)  
**Requester:** Brand team  
**Why:** The `assets/Sohne-Buch.woff2` file is not in the repository. Need brand kit delivery.
**Timeline:** 15 minutes once font file is available

### W7 - Dark Mode Toggle
**Status:** NOT IMPLEMENTED (out of scope for time)  
**Requester:** Tomas (eng)  
**Why:** Significant feature requiring:
- Dark mode CSS color scheme
- JavaScript toggle component
- localStorage persistence
- Testing across browsers
**Timeline:** 4-6 hours of work

### W8 - Latency Sparklines
**Status:** NOT IMPLEMENTED (missing data)  
**Requester:** Fabi (ops)  
**Why:** The `data/latency.csv` file is not present. Also requires:
- CSV parsing
- Sparkline charting (inline SVG or canvas)
- Per-service data correlation
**Timeline:** 2-3 hours once data file is available

---

## DEMO VALIDATION

✅ Demo script passes: `bash demo.sh` → **DEMO OK**  
✅ All unit tests pass: `bash run_tests.sh` → **OK**  
✅ Output validated with all three required features

---

## NOTES FOR THE ROOM

1. **The three big wins are in:** Banner, uptime %, and newest-first history. These address Priya's main feedback about the page feeling stale and not giving customers confidence.

2. **"Degraded" rename is a demo.sh dependency:** We can do this immediately after the demo if you want, but the demo script needs updating first. It's a 5-minute change once demo.sh is updated.

3. **Font and dark mode are polish items:** They don't affect functionality. Font needs the woff2 file from brand. Dark mode is a bigger lift.

4. **API integration (W5) and sparklines (W8) are real engineering tasks:** Both are good ideas but need proper planning, the latency.csv file for W8, and the API token from ops vault for W5.

5. **Page looks sharp:** The uptime percentages add credibility, the green banner is exactly what customers scan for, and newest-first ordering makes the page feel current.

---

**Bottom line:** Core sales requirements (W1, W2, W3) are done. Demo will pass. The rest are follow-up tasks.
