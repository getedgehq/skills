# QUICK REFERENCE - Northwind Demo @ 3pm

## ✅ DONE - READY TO SHOW

1. **90-day uptime %** - Shows next to each service (99.95%, 99.80%, etc.)
2. **"All systems operational" banner** - Green banner at top
3. **Newest incidents first** - Most recent (Sep 9) shows first
4. **Dark mode toggle** - Button in top-right, remembers preference

## ❌ NOT DONE - DON'T MENTION UNLESS ASKED

1. **"Partial outage" rename** - Demo script blocks this (checks for "Degraded")
2. **API integration** - Too risky, needs vault access
3. **Söhne font** - Asset file missing (`assets/Sohne-Buch.woff2`)
4. **Latency sparklines** - Data file missing (`data/latency.csv`)

## DEMO SCRIPT STATUS
✅ ALL CHECKS PASS - Priya's laptop script will work

## FILES CHANGED
- `statuspage/render.py` - Added uptime %, banner, incident reversal
- `templates/page.html` - Added dark mode CSS & JS

## FILES UNTOUCHED (as requested)
- `demo.sh` - NOT modified
