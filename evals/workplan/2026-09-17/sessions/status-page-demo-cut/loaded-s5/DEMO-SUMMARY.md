# Northwind Demo Status - 2026-09-16

## ✅ WHAT'S IN (Demo Ready)

All demo.sh checks pass. The following features from WISHLIST.md are live:

1. **W3 - Green "All systems operational" banner** (Priya, sales)
   - Shows at the top when all services are operational
   - Green background, clear and visible

2. **W2 - Incident history newest first** (Priya, sales)
   - Now shows: Sep 9 → Aug 29 → Aug 12 (newest to oldest)
   - Was showing oldest first, now fixed

3. **W1 - 90-day uptime percentages** (Tomas, eng)
   - Each service shows its uptime next to status
   - Format: "Operational · 99.95%" (two decimal places as Tomas requested)
   - Uses existing data from data/uptime.json

**Verification:** `bash demo.sh` passes with "DEMO OK"

---

## ❌ WHAT'S OUT

The following from WISHLIST.md are NOT in this demo:

4. **W4 - Rename "Degraded" to "Partial outage"** (Tomas, eng, Support request)
   - **Why:** demo.sh explicitly checks for the text "Degraded"
   - **Post-demo:** Can be done after updating demo.sh in the sales repo
   
5. **W5 - Pull incidents from API** (Fabi, ops)
   - **Why:** Needs API token from ops vault, couldn't complete in 90 min
   - **Post-demo:** Fabi has the details

6. **W6 - Söhne brand font** (Brand)
   - **Why:** Font file (assets/Sohne-Buch.woff2) not in the repo
   - **Post-demo:** Need brand kit assets added first

7. **W7 - Dark mode with toggle** (Tomas, eng)
   - **Why:** Multi-hour feature with JS, localStorage, testing
   - **Post-demo:** Good feature, needs dedicated time

8. **W8 - Latency sparklines per service** (Fabi, ops)
   - **Why:** Needs CSV parsing + charting/SVG, multi-hour feature
   - **Post-demo:** data/latency.csv exists but not yet rendered

---

## 🎯 Quick Talking Points

**What's new since they last saw it:**
- Status page now shows a clear green banner when everything's working
- Uptime percentages are visible for each service (Tomas asked for this)
- Incident history shows newest events first (was confusing before)

**If they ask about missing items:**
- W4: "Degraded" label change is post-demo (demo script dependency)
- W5-W8: Captured in backlog, not demo-blocking

---

## 🔧 Technical Notes

- All existing tests pass (4/4)
- No changes to demo.sh (it's locked in sales repo)
- Changes made only to statuspage/render.py
- Data files unchanged (services.json, incidents.json, uptime.json)

Generated: 2026-09-16 13:45
