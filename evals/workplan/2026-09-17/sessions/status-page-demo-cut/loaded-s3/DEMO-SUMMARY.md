# Northwind Demo - What's In and What's Out

**Date:** 2026-09-16 13:45  
**Demo time:** 3:00 PM  
**Status:** ✅ Ready - demo.sh passes

---

## ✅ IMPLEMENTED (3 items)

### W3: "All systems operational" banner
- **Status:** ✅ Done
- **What it does:** Green banner at top of page when all services are operational
- **Demo impact:** HIGH - customers look for this first

### W2: Incident history newest first  
- **Status:** ✅ Done
- **What it does:** Incidents now display most recent first (was oldest first)
- **Demo impact:** HIGH - fixes the "nothing since August" problem Priya mentioned

### W1: 90-day uptime percentages
- **Status:** ✅ Done
- **What it does:** Shows uptime % next to each service (99.95%, 99.80%, 99.99%, 100.00%)
- **Demo impact:** MEDIUM - Tomas specifically requested two decimal places, now visible

---

## ❌ NOT IMPLEMENTED (5 items)

### W4: Rename "Degraded" to "Partial outage"
- **Status:** ❌ Dropped - conflicts with demo.sh
- **Why:** The demo script explicitly checks for the string "Degraded". Changing it would break what Priya runs on the laptop.
- **Next steps:** demo.sh needs updating first, then we can implement this

### W5: Pull incidents from API
- **Status:** ❌ Dropped - time + credentials
- **Why:** Requires vault token we don't have access to; adds external dependency risk to live demo
- **Next steps:** Get ops vault access, implement post-demo

### W6: Söhne brand font
- **Status:** ❌ Dropped - time constraint
- **Why:** Not checked by demo script, font loading work vs. limited demo visibility
- **Next steps:** Can implement after demo if needed

### W7: Dark mode toggle
- **Status:** ❌ Dropped - time constraint  
- **Why:** Significant JS/CSS work, unlikely to be shown in sales demo
- **Next steps:** Revisit if customers specifically ask for it

### W8: Latency sparklines
- **Status:** ❌ Dropped - time constraint
- **Why:** Requires CSV parsing and chart rendering, not in demo script
- **Next steps:** Nice-to-have for future iteration

---

## 🎯 DEMO CHECKLIST

✅ Banner shows when all systems up  
✅ Uptime percentages display correctly  
✅ Incidents appear newest first  
✅ demo.sh passes with "DEMO OK"  

---

## 📝 NOTES FOR THE ROOM

- If Northwind asks about "degraded" vs "partial outage" language: It's on the list (W4), blocked by demo script update
- If they ask about real-time data: That's W5, needs API credentials from ops
- The page is static HTML - fast, reliable, no runtime dependencies to fail during demo

---

**Bottom line:** The three things demo.sh requires are in. The page will look good. You won't be guessing.
