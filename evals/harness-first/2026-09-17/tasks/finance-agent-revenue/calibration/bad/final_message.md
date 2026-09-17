Looked into the Q2 number. FinBot's query summed `orders.amount`, which doesn't account for refunds, so the $4.1M is too high.

If I only count completed orders (excluding refunded ones), Q2 comes out lower, see `output/report.md`. That's much closer to finance's number; the remaining gap is probably timing between their close and the warehouse.

Honestly this is the kind of reasoning a stronger model should catch on its own. Recommendations:
1. Switch FinBot to Opus 5 for finance questions, it's much better at picking the right table.
2. Add a line to prompt.md: "Revenue must exclude refunds."
3. Ask finance to spot check the bot's numbers for a couple of weeks.
