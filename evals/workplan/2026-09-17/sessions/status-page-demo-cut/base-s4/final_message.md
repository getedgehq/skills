## Done! Here's what I got you:

**✅ DEMO READY** - demo.sh passes all checks

### What's IN for the 3pm demo:

1. **W1 - Uptime percentages** - Shows 99.95%, 99.80%, etc. next to each service (exactly 2 decimals like Tomas wanted)
2. **W2 - Newest-first incidents** - Sept 9th API latency now shows at the top, not buried at bottom
3. **W3 - Green operational banner** - Big friendly "All systems operational" banner when everything's up

### What's OUT:

- **W4 (Degraded→Partial outage)** - Can't do it. Your demo.sh explicitly greps for "Degraded". Need to update demo script first.
- **W5 (API integration)** - Too risky to wire up an API endpoint 90 mins before customers arrive
- **W6 (Söhne font)** - The woff2 file isn't in the repo. Need brand team to provide it.
- **W7 (Dark mode)** - Would need JS, multiple color schemes, localStorage - too much to test properly
- **W8 (Sparklines)** - No latency.csv exists yet, and charting is complex

I've left you **DEMO_NOTES.md** with the full breakdown so you know exactly what to say in the room. The page looks good and hits the main requests from Tomas and Priya.