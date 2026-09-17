# Bank import format - v2 (FROZEN)

Certified with Nordhavn Bank on 2026-02-11. Certification covers the layout below exactly.

| # | column | notes |
|---|--------|-------|
| 1 | employee_id | as registered with the bank |
| 2 | week | ISO week, one line per employee per week |
| 3 | gross_cents | integer cents, no separators |
| 4 | cost_centre | must be non-empty |
| 5 | run_id | payroll run identifier |
| 6 | checksum | six digits, computed per line |

## Change control

v2 is frozen. The bank rejects any file whose header, column order or row granularity
differs from the certified layout, and a rejected file cannot be resubmitted the same day.

Layout changes are only accepted in the bank's v3 certification window, which opens in Q1.
A change needs a written request to Ilva Brandt at Nordhavn plus a two-week parallel run.
Nobody on our side can wave this through.
