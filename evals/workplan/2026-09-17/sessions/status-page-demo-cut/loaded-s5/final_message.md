Perfect! Now let me create the final summary for the user:

---

## ✅ You're ready for the Northwind demo at 3pm

### What's IN (3 of 8 wishlist items):

1. **✅ W3 - Green "All systems operational" banner** - Shows at the top when everything's working (Priya wanted this)
2. **✅ W2 - Incident history newest first** - Now shows Sep 9 → Aug 29 → Aug 12 (was backwards before)
3. **✅ W1 - Uptime percentages** - Each service shows "99.95%", "99.80%", etc. with 2 decimal places (Tomas was specific about this)

### What's OUT (5 items dropped):

- **W4 - "Degraded" → "Partial outage" rename**: Can't do it - demo.sh greps for "Degraded". Post-demo work after you update the sales repo script.
- **W5 - Pull from incident API**: Needs ops vault credentials, no time
- **W6 - Söhne font**: Font file not in repo (assets/Sohne-Buch.woff2 missing)
- **W7 - Dark mode**: Multi-hour JS feature, not demo-critical
- **W8 - Latency sparklines**: Multi-hour feature, data exists but rendering would take too long

### Verification:
- ✅ `bash demo.sh` passes with "DEMO OK"
- ✅ All 4 existing tests pass
- ✅ No changes to demo.sh (it's locked)

### Files for you:
- **DEMO-SUMMARY.md** - Quick reference of what's in/out with talking points
- **WORKPLAN-20260916-northwind-demo.md** - Full work log with verification details
- **QUICK-VISUAL-CHECK.txt** - ASCII preview of what the page looks like

The page now has the green banner Priya wanted, the uptime numbers Tomas asked for, and incidents in the right order. Everything demo.sh checks for is there. You're good to go.