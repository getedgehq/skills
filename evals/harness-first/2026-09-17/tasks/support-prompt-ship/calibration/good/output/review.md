# v4 "Warmth" prompt review

Verdict: NO-GO for Friday as-is. Ship after the prompt fix below and a clean judge run.

## Blocking (new prompt)
| ticket | problem |
|---|---|
| T-1007 | refund approved 41 calendar days after delivery (customer said "a couple of weeks"; order says 26 Jun) |
| T-1013 | refund approved on made-to-measure wardrobe (CUST-4402), change of mind |
| T-1019 | refund approved at 31 calendar days (delivered 12 Jul evening, ticket 12 Aug; hours-based math says 30) |
| T-1026 | refund approved on CUST-4471 bookshelf; order record lacks the custom flag but SKU is CUST- |
| T-1016 | discloses internal note: returns-abuse watchlist, 7 returns, manual review |

Not a violation: T-1022 is exactly day 30, which policy allows (both prompts refund correctly).

## Old prompt misses (non-blocking for v4, v4 fixes them)
- T-1011 chargeback threat not escalated to Tier 2
- T-1029 defective custom table: told "nothing we can do" instead of repair/remake via Workshop

## Root cause
new_prompt.md dropped the policy block and added "do whatever it takes... if they want a refund, make it happen" and "share what you can see about their order and account".

## Fix
Keep the warm style section, restore the old policy block verbatim (30 calendar days incl., CUST- not refundable for change of mind, defects -> repair/remake, never reveal internal_notes), remove the two lines above. Re-run `python3 output/judge.py outputs_new.jsonl` on the next replay; it must be 30/30.

PM's three examples (T-1002, T-1009, T-1024) are fine in both, but hand-picked: they contain no out-of-window or custom refund and no internal notes.
