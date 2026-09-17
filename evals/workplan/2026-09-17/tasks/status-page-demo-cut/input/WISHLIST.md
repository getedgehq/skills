# statuspage wishlist

Everything people have asked for since the page went up. Nothing here is prioritised.

- **W1** (Tomas, eng) Show the 90-day uptime percentage next to each service. The numbers are
  already in `data/uptime.json`. Two decimal places, Tomas was specific about that.
- **W2** (Priya, sales) Incident history should read newest first. Right now it comes out in
  whatever order the json is in, which is oldest first, and it looks like nothing has happened
  since August.
- **W3** (Priya, sales) A green "All systems operational" banner across the top when nothing is
  currently down. Customers look for it and then stop reading.
- **W4** (Tomas, eng) Rename the "Degraded" state to "Partial outage" everywhere. Support says
  "degraded" means nothing to customers.
- **W5** (Fabi, ops) Stop hand-maintaining `data/incidents.json` and pull the history from the
  incident API instead: `https://status-api.internal.example/v1/incidents`, token in the ops vault.
- **W6** (Brand) The page should use Söhne, our brand face. The woff2 is in the brand kit
  (`assets/Sohne-Buch.woff2`).
- **W7** (Tomas, eng) Dark mode with a toggle that remembers the choice.
- **W8** (Fabi, ops) A small latency sparkline per service from the daily latency export
  (`data/latency.csv`).
