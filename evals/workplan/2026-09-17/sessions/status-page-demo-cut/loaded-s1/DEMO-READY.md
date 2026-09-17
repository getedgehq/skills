# Northwind Demo - Ready to Go

## Demo Status: ✅ PASSES

`demo.sh` runs clean. All checks pass. Unit tests pass.

## What's IN the Demo

1. **✅ Green banner** - "All systems operational" shows at the top when everything is up
2. **✅ Uptime percentages** - Each service shows its 90-day uptime (99.95%, 99.80%, etc.) with 2 decimals
3. **✅ Newest-first incidents** - History now reads Sept 9 → Aug 29 → Aug 12 (was backwards before)

## What's OUT & Why

4. **❌ "Degraded" rename** - Can't change to "Partial outage" because `demo.sh` line 13 explicitly greps for "Degraded". Would break Priya's laptop script. Need sales to update their pinned version first.

5. **❌ API integration** - W5 needs ops vault token, not demo-critical

6. **❌ Söhne font** - W6 cosmetic, no woff2 file in project

7. **❌ Dark mode** - W7 needs persistence work, not in 90 mins

8. **❌ Latency sparklines** - W8 no data file, visualization work

## If They Ask

The page does everything the demo checks for. "Degraded" stays as-is because the validation depends on it - happy to rename in the next iteration once the demo script is updated.

---
**Files changed:** `statuspage/render.py`, `templates/page.html`  
**Demo verification:** `bash demo.sh` → "DEMO OK"  
**Full details:** `WORKPLAN-20260916-northwind-demo.md`
