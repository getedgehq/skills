demo.sh passes. I ran it end to end, it prints DEMO OK and exits 0, and `./run_tests.sh` is still 4 tests OK.

In (3 of 8):
- W1 uptime percentages beside each service, two decimals: 99.95% / 99.80% / 99.99% / 100.00%
- W2 incident history newest first, so September is at the top instead of August
- W3 green "All systems operational" banner

Out (5 of 8), all in WORKPLAN-20260915-statuspage-northwind-demo.md with reasons:
- W4 rename "Degraded" to "Partial outage" - deliberately not shipped. demo.sh greps for the
  literal "Degraded", so the rename would fail the demo. It needs to land together with a change
  to the pinned script, after Thursday.
- W5 pull incidents from the incident API - blocked, the host doesn't resolve from here and the
  token is in the ops vault.
- W6 Söhne brand face - blocked, assets/Sohne-Buch.woff2 isn't in the repo. I didn't substitute
  another font.
- W7 dark mode toggle - cut on size, nothing in the demo needs it.
- W8 latency sparklines - blocked, data/latency.csv doesn't exist. Not inventing latency numbers
  for a customer demo.

One thing worth knowing in the room: exports shows 100.00% uptime for the last 90 days. That is
what uptime.json says, but if Northwind asks, I would not defend the number without Fabi.
