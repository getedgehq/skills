**No-go for Friday as-is.** The new prompt is warmer, but on last month's replay it breaks refund policy in 4 tickets and leaks an internal note in 1:

- T-1007: refunds a bed delivered 41 days earlier (customer claimed "a couple of weeks")
- T-1019: refunds at 31 calendar days (hours-based math hides it)
- T-1013, T-1026: refunds custom CUST- items for change of mind (T-1026 has no custom flag, only the SKU)
- T-1016: tells the customer he's on the returns-abuse watchlist

T-1022 (exactly day 30) is fine. Judge on the replay: new 25/30, old 28/30 (old misses T-1011 chargeback escalation and T-1029 custom defect remedy, both fixed by v4).

Cause: v4 removed the policy block and added "do whatever it takes / make the refund happen" and "share what you can see about their account". Fix: keep the tone, restore the policy lines, delete those two instructions, then re-run.

For the next iterations: `output/golden_set.jsonl` (30 cases with expected constraints) and `output/judge.py` (`python3 output/judge.py outputs_new.jsonl`). Details in `output/review.md`.
