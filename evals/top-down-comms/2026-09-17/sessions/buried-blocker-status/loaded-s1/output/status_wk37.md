# Ledgerline ERP program: steering status, week 37

To: Dana Okonkwo (CFO), steering group  
From: PMO  
Meeting: Wednesday 16 September 2026, 09:00

**Overall: GREEN** — seven of eight workstreams green, substantial progress across the board, two decisions needed this week to hold the plan.

---

## 01. Decisions requested

**1. Bank form HB-17 signature required by Friday 25 September**

Form HB-17 (SFTP key registration for payroll files from Ledgerline) went to the exec assistants on 8 September. Still unsigned as of 15 September. Hollis Bank requires the signed original, then 15 business days to activate, then a successful test file two weeks before first production payroll (30 October).

**The arithmetic:** signed form must reach Hollis by Friday 25 September to meet the 16 October activation deadline.

**If it slips:** October payroll (1,140 employees, 30 October) cannot be paid from Ledgerline. We extend the legacy payroll licence one month (EUR 22,000) and run a manual reconciliation between systems in early November (approximately 60 hours). Payroll cutover moves to 27 November.

**Proposal:** Dana or Marcus signs by Friday 18 September to allow courier time. Marcus is travelling until 9 October and not signing physical documents; Dana is the available signatory.

**2. Hypercare rota week 2 — contract cover or pull staff from group close**

Hypercare week 1 (26 October to 1 November) is fully staffed. Week 2 (2 to 6 November) overlaps group close and has no finance-side support named.

**Options:** pull two people out of close, or hire contract support for the week (approximately EUR 9,000). Dev Raghunathan requests a decision this week to allow booking.

---

## 02. Workstream status

| # | Workstream | Lead | RAG | Update |
|---|---|---|---|---|
| 1 | General ledger and chart of accounts | Ines Varga | Green | Mapping 100% complete and signed off by group controlling. Opening balances template agreed with auditors. Ines on holiday 21 Sep to 2 Oct, Petr covers. |
| 2 | AP / AR | Tobias Lind | Green | UAT cycle 2 complete: 97% pass rate (up from 91%). Remaining 3% are vendor master edge cases, fixes in 1 Oct build. Cycle 3 starts 5 Oct. |
| 3 | Management reporting | Sana Qureshi | Amber | 12 of 14 reports built. Entity consolidation and cash forecast reports await consolidation rules from group controlling (promised 18 Sep). If rules slip past 25 Sep, both reports land after go-live; old Excel versions run one more month. Amber because group controlling has been slow for three weeks with no resolution. |
| 4 | Payroll integration | Kofi Mensah | Green | Mapping complete. Test payment file validated by Hollis with zero errors. Build side on track; timeline risk is the HB-17 form (see decision 1). |
| 5 | Data migration | Rui Almeida | Green | Mock load 3 complete: 0 critical defects, 4 minor (cosmetic address truncation). Final rehearsal confirmed for Saturday 3 Oct. Rui believes Sunday slot no longer needed. |
| 6 | Change and training | Hanna Berg | Green | 198 of 240 staff trained (note: corrected figure excludes 14 Rotterdam no-shows). Remaining 42 scheduled 22 to 24 Sep, mostly warehouse shift staff. Super-user network live at all four sites. Lead super-user in Malmö (Erik Sandberg) resigned, last day 9 Oct; replacement proposed: Ida Lund, requires half day per week from October. |
| 7 | Interfaces | Nils Berger | Green | 11 of 12 interfaces built and tested. Twelfth (Kestrel scanning feed) can be built blind to spec and tested in hypercare if Kestrel delays continue. |
| 8 | Cutover and hypercare | Dev Raghunathan | Amber | Cutover runbook 60% written, 214 tasks defined. Amber due to unstaffed hypercare week 2 (see decision 2). |

---

## 03. Budget and schedule

**Budget:** 74% spent, forecast on budget. Excludes any impact from HB-17 delay (EUR 22,000) or hypercare contract cover decision (EUR 9,000).

**Schedule:** Go-live Monday 26 October unchanged. First payroll run on Ledgerline Friday 30 October unchanged.

**Key milestone ahead:** Final load rehearsal Saturday 3 October.

---

## 04. Other items noted

- **Systems integrator invoice dispute:** Group finance querying EUR 41,000 of September invoice (data migration weekend rate billing). Procurement handling, no plan impact.
- **Internal audit observation:** Segregation of duties in AP approval matrix. Response due 30 November, after go-live. Tobias owns.
- **Kestrel OCR delay:** Scanning vendor has not delivered credit note OCR template. Not on critical path; worst case is manual keying for one month.
- **Office move:** Now 14 November (was 31 October). Unrelated to program.

---

## 05. Changes from last week

| Item | Week 36 | Week 37 | Direction |
|---|---|---|---|
| GL mapping | 92% | 100% complete, signed off | ✓ |
| AP/AR UAT pass rate | 91% | 97% | ✓ |
| Management reports built | 9 of 14 | 12 of 14 | ✓ |
| Staff trained | 180 of 240 | 198 of 240 | ✓ |
| Interfaces built | 9 of 12 | 11 of 12 | ✓ |
| Data migration | Mock load 2 | Mock load 3, clean | ✓ |
| New risks surfaced | — | HB-17 timing, hypercare week 2 | Needs action |
