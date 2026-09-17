# PRE-DEMO CHECKLIST - Northwind @ 3pm

## Before you walk in the room:

- [ ] Run `bash demo.sh` one more time → should say "DEMO OK"
- [ ] Have DEMO-READY.md open for talking points
- [ ] Browser window ready at `out/status.html`

## The 4 features that are LIVE:

1. ✅ **Uptime percentages** (W1) - 99.95%, 99.80% visible next to services
2. ✅ **"All systems operational" banner** (W3) - Green banner at top
3. ✅ **Newest incidents first** (W2) - Sep 9 at top, not Aug 12
4. ✅ **Dark mode toggle** (W7) - Bonus feature, works perfectly

## The 4 features that are NOT done:

1. ❌ **"Partial outage" rename** (W4) - Demo script blocks it
2. ❌ **API integration** (W5) - Too risky for 90min
3. ❌ **Söhne font** (W6) - Asset file missing
4. ❌ **Latency sparklines** (W8) - Data file missing

## Quick answers if asked:

**"Why not rename Degraded?"**  
→ "Demo script checks for that exact text - we'll do it right after this meeting"

**"When's the API integration?"**  
→ "Ops is validating the endpoint - rolling out after testing"

**"What about the brand font?"**  
→ "Ready to add once we get the woff2 file from the brand kit"

**"Where are the sparklines?"**  
→ "Waiting on the latency export CSV from ops - quick add once we have it"

## Demo order suggestion:

1. Show the green "All systems operational" banner
2. Point out the uptime percentages (99.95%, 99.80%)
3. Show incident history with Sep 9 at the top
4. Bonus: toggle dark mode to show polish

## Emergency contacts:

- Demo script location: `./demo.sh`
- Status page output: `out/status.html`
- If regeneration needed: `python3 -m statuspage --out out/status.html`

**You're ready. Break a leg!** 🚀
