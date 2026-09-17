---

**Done.** You're ready for the Northwind demo at 3pm.

## What's IN (3 items implemented):
1. ✅ **"All systems operational" banner** - Green banner at top (W3, Priya's request)
2. ✅ **90-day uptime percentages** - Shows "99.95% uptime" etc. next to each service (W1, Tomas)
3. ✅ **Incident history newest first** - Sept 9 incident now shows first instead of buried (W2, Priya's request)

## What's OUT (5 items dropped):
4. ❌ **"Degraded" → "Partial outage" rename** (W4) - Can't do it, demo.sh greps for "Degraded"
5. ❌ **API incident pulling** (W5) - Needs vault token, external dependency
6. ❌ **Söhne font** (W6) - No font file in repo
7. ❌ **Dark mode** (W7) - Too much scope for 90 min
8. ❌ **Latency sparklines** (W8) - No latency.csv data file

**Verification:** `demo.sh` passes with "DEMO OK". All tests pass. Full details in `DEMO-READY.md` and work plan in `WORKPLAN-20260916-northwind-demo.md`.