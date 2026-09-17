# Ledgerline steering status, week 37

To: Dana Okonkwo (CFO), steering group. From: PMO.

**Overall: AMBER. The October payroll run on Ledgerline is at risk until Dana
signs Hollis form HB-17, and the signed form has to be at the bank by Fri Sep 25.**

Dana, this needs your signature personally: you and Marcus Reinholt are the only
mandate holders, and Marcus is abroad until Oct 9 and not signing paper. The
form has been with the EA pool since Sep 8.

## 01 Sign HB-17 this week or October payroll runs on the legacy system

- Hollis need 15 business days from receipt to activate the new SFTP key, and
  the key must be live by Fri Oct 16 so they can take a test payment file two
  weeks before the first real run. Fri Sep 25 is the last possible arrival date.
- If it slips, the Oct 30 payroll for 1,140 employees is paid out of the legacy
  system: about EUR 22,000 to extend the legacy payroll licence by a month, plus
  roughly 60 hours of manual reconciliation, and payroll cutover moves to the
  Nov 27 run.
- The build itself is fine: mapping done, test file validated by Hollis's own
  checker with zero errors. The risk is entirely the signature.

## 02 One decision to make today: hypercare cover for the week of Nov 2

Week 2 of hypercare collides with the group close and has nobody named on the
finance side. Pulling two people out of close or buying contract cover both cost
about EUR 9,000. Dev needs an answer to finish the runbook.

## 03 Everything else is on track for go-live Mon Oct 26

| Workstream | RAG | Where it stands |
|---|---|---|
| GL / chart of accounts | Green | Mapping 100%, signed off by group controlling |
| AP / AR | Green | UAT cycle 2 closed at 97% pass (was 91%); edge cases fixed in the Oct 1 build |
| Management reporting | Amber | 12 of 14 reports built; the last two need consolidation rules by Sep 25, otherwise Excel runs one more month |
| Payroll integration | Amber | Build complete, blocked on the HB-17 signature (see 01) |
| Data migration | Green | Mock load 3: 0 critical defects; rehearsal Sat Oct 3 confirmed |
| Change and training | Green | 198 of 240 trained after correcting the Rotterdam no-shows; remaining sessions booked Sep 22 to 24 |
| Interfaces | Green | 11 of 12 built; the Kestrel scanning feed can be built against the spec |
| Cutover and hypercare | Amber | Runbook 60% written; see 02 |

## 04 Budget holds at 74% unless payroll slips

74% spent, forecast on budget, and neither the EUR 22,000 nor the EUR 9,000
above is in it. For the record and with no impact on go-live: procurement are
disputing about EUR 41,000 of the integrator's September invoice, internal audit
have an observation on the AP approval matrix due 30 Nov, and Hanna proposes Ida
Lund to replace our Malmo super-user.

**Next step:** Dana signs HB-17 today or tomorrow and Kofi couriers it to Petra
Holm at Hollis the same day. If it is not signed by Thu, we start pricing the
legacy extension.
