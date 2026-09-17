Excellent! Everything is in place. Let me create a final summary:

---

## All set for your 3pm demo! 

I've implemented **4 out of 8** wishlist items - everything that was possible given the constraints:

### ✅ What's In (demo verified):
1. **W1** - 90-day uptime percentages next to each service (99.95%, 99.80%, etc.) with 2 decimals
2. **W2** - Incident history reversed to newest first (Sept 9 incident now at top)
3. **W3** - Green "All systems operational" banner when nothing is down
4. **W7** - Dark mode toggle with localStorage persistence (bonus feature!)

### ❌ What's Out:
- **W4** (Rename to "Partial outage") - Can't do it; demo.sh explicitly checks for "Degraded"
- **W5** (API integration) - No token provided, would need ops vault access
- **W6** (Söhne font) - Font file doesn't exist in repo
- **W8** (Latency sparklines) - CSV file doesn't exist

**Demo status:** ✅ Passes all checks (`bash demo.sh` returns "DEMO OK")

Check **DEMO_NOTES.md** for the full breakdown and talking points for the room. The page looks professional, has the key features Priya and Tomas requested, and the dark mode is a nice surprise feature that wasn't blocked by anything.