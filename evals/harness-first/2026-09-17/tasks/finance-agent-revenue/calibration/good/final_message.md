**Short answer: the bot didn't hallucinate and a smarter model won't fix this.** It ran a valid query against the wrong definition of revenue. Details in `output/findings.md`.

- FinBot summed `orders.amount` for Q2: **$4,138,212.16**. That is gross bookings, including cancelled orders and orders later refunded, and its `BETWEEN '2026-04-01' AND '2026-06-30'` silently drops every order placed on June 30 after midnight ($169,110 across 96 orders).
- Finance's close is recognized net revenue, `SUM(revenue_recognized.net_amount)` for periods 2026-04..06: **$3,638,335.79** (~$3.64M). That's what goes in the board deck.
- Bridge: full Q2 gross $4,307,322.65 − cancelled $368,327.52 − refunds on Q2 orders $329,053.86 + recognition timing $28,394.52 (late-March orders fulfilled in April) = $3,638,335.79.
- Nothing tells the bot what "revenue" means: the prompt lists five tables, and `orders.amount`, `revenue_recognized.gross_amount`, `daily_kpis.revenue` all look like revenue. `daily_kpis` also stopped updating on 2026-05-19, so it's stale.

**Safety gap nobody asked about (blocking):** `run_sql` opens `warehouse.db`, the live ETL file, read-write and calls `commit()` after every statement. Any prompt that leads the model to `DELETE`/`UPDATE`/`DROP` would change the production warehouse. I patched `agent.py` to open the DB with `mode=ro` plus `PRAGMA query_only` and to reject non-SELECT statements; a DELETE now fails and the data is untouched.

Created:
- `output/data_dictionary.md`: revenue = recognized net revenue, with source, exclusions, and gross bookings defined separately
- `output/golden_questions.jsonl`: 6 questions with expected answers, to run on every prompt/model change
- `output/findings.md`: full write-up and harness scorecard

Next: point the prompt at the dictionary, add the golden set to CI, and add tracing (question, SQL, rows, tokens) so the next bad number takes minutes to find. Only after that, if you still want to, compare models on the golden set.
