# paystream backlog - September run

Owner: Ines Pardo (payroll ops). Target: the September run goes out on the 24th.

## PS-210 - shift rounding is wrong at the halfway point

Ines: "a 2h05 shift and a 2h15 shift both come back as 2h10. The union agreement says
partial units round in the employee's favour, so anything sitting exactly halfway goes up,
never down." The step itself is a setting, not a constant - ops changes it when the
agreement is renegotiated, so it stays in paystream.ini.

## PS-211 - overtime is not being paid

Everything over 40h in a week is supposed to be paid at 1.5x. Right now the export pays
the same rate for every minute. The overtime split has to be done on the rounded minutes,
not the raw ones - Ines has been asked this by the works council twice.

## PS-212 - rows with no cost centre disappear

Some rows come out of the depot terminal with an empty cost_centre. They are currently
carried into the bank file with a blank column. They should be left out of the run, but
Ines needs to know how many were left out and who they were, so she can chase the depot.
Do not drop them quietly.

## PS-213 - one row per employee in the bank file

Fabi from finance: "the reconciliation sheet would be much easier if the bank file had one
line per employee for the whole month instead of one per week. can we collapse it?"
