# Ledgerline ERP program: steering status, week 37 (for Wed 16 Sep 2026)

To: Dana Okonkwo (CFO), steering group
From: PMO

**Overall: GREEN** (2 amber workstreams, 1 urgent decision required)

## Decision required this week

**Payroll banking form HB-17:** Dana's signature required by Fri 25 Sep at the latest to enable Oct 30 payroll run on Ledgerline. Form sent to EA pool 8 Sep, unsigned as of 15 Sep. Marcus unavailable (travelling) until 9 Oct. **If form reaches Hollis Bank after 25 Sep, October payroll must run on legacy system, adds EUR 22k cost and delays payroll cutover to November.**

## Workstream status

| # | Workstream | Lead | RAG | Update |
|---|---|---|---|---|
| 1 | General ledger and chart of accounts | Ines Varga | Green | Mapping 100% complete, signed off by group controlling. Opening balances agreed with auditors. Ines on holiday 21 Sep–2 Oct, Petr covers. |
| 2 | AP / AR | Tobias Lind | Green | UAT cycle 2 complete: 97% pass rate (up from 91%). Remaining 3% are vendor master edge cases, fixed in Oct 1 build. Cycle 3 starts 5 Oct. Kestrel OCR template for credit notes still outstanding, not on critical path. |
| 3 | Management reporting | Sana Qureshi | Amber | 12 of 14 reports built. Entity consolidation and cash forecast reports await consolidation rules from group controlling (promised 18 Sep). If rules slip past 25 Sep, these two reports deliver post go-live; Excel workaround available for one month. |
| 4 | Payroll integration | Kofi Mensah | Green | Mapping complete. Test payment file validated by Hollis with zero errors. **Banking admin blocker:** see decision item above. Build work on track. |
| 5 | Data migration | Rui Almeida | Green | Mock load 3 complete: 0 critical defects, 4 minor (cosmetic only). Final load rehearsal confirmed for Sat 3 Oct. Rui queries whether Sunday slot still needed. |
| 6 | Change and training | Hanna Berg | Green | 198 of 240 staff trained (corrected from 212: excludes 14 Rotterdam no-shows). Remaining 28 sessions booked 22–24 Sep. Super-user network live at all sites. Malmo lead Erik Sandberg resigned (last day 9 Oct); Ida Lund proposed as replacement (0.5 day/week from Oct). |
| 7 | Interfaces | Nils Berger | Green | 11 of 12 interfaces built and tested. Twelfth (Kestrel scanning feed) can be built to spec and tested in hypercare if vendor delays continue. |
| 8 | Cutover and hypercare | Dev Raghunathan | Amber | Cutover runbook 60% complete (214 tasks). **Hypercare staffing gap:** week 2 (2–6 Nov) overlaps with group close. Decision needed on whether to pull 2 people from close or hire contract support (~EUR 9k). |

## Budget and dates

- **Budget:** 74% spent, forecast on budget (excludes potential payroll delay cost and hypercare contract support decision).
- **Key dates:** Final load rehearsal Sat 3 Oct | Go-live Mon 26 Oct | First payroll on Ledgerline Fri 30 Oct.

## Other items

- **Invoice dispute:** EUR 41k of SI's September invoice disputed (weekend rates for data migration rehearsal). Procurement handling, no plan impact.
- **Internal audit:** SegDuty observation on AP approval matrix. Response due 30 Nov, Tobias owns.
- **Office move:** Vasagatan building move now 14 Nov (was 31 Oct).
