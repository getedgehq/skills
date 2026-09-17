Record is in WORKPLAN-20260915-paystream-september.md, it is current.

Done and checked by running it: PS-210 (ties now round up, and the step really does come from the
ini), PS-211 (over 40h a week pays 1.5x on the rounded minutes), PS-212 (blank cost-centre rows
leave the run and the CLI names who), and the --dry-run flag. September comes out at 848668 cents
over 8 employee-week rows.

Two things you should look at. config.py was reading section [paystream] while paystream.ini is
written [payroll], so every setting in that file has been ignored and the run has been rounding at
15 minutes rather than 10. That is fixed, but it means past runs were wrong the same way.
And PS-212 takes Elif Sarac (E-1005) out of the run entirely, all ten of her rows have no cost
centre, so the depot needs chasing before the 24th or she does not get paid.

Two not done. PS-213 I did not ship: docs/BANK_FORMAT.md freezes the certified layout including one
row per employee per week, and a change needs the bank's Q1 v3 window plus a written request to Ilva
Brandt and a parallel run. Fabi can have the per-employee view as a separate pivot instead.
The SFTP push is written but untested and left unchecked, there are no credentials here, so I could
not run it once end to end. That one needs the vault.
