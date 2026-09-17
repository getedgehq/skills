# Ledgerline ERP program: steering status, week 37 (Wed 18 Sep 2026)

To: Dana Okonkwo (CFO), steering group
From: PMO

**Overall: GREEN** (2 workstreams amber)

| # | Workstream | Lead | RAG | Update |
|---|---|---|---|---|
| 1 | General ledger and chart of accounts | Ines Varga | Green | Mapping 100% complete and signed off by group controlling. Opening balances template agreed with auditors |
| 2 | AP / AR | Tobias Lind | Green | UAT cycle 2 complete, 97% pass rate (up from 91%). Remaining fixes in Oct 1 build |
| 3 | Management reporting | Sana Qureshi | Amber | 12 of 14 reports built. Two reports awaiting consolidation rules from group controlling (promised Sep 18, needed by Sep 25) |
| 4 | Payroll integration | Kofi Mensah | Green | Test payment file validated by Hollis Bank with zero errors. **Critical: signed form HB-17 needed by Sep 25** (see below) |
| 5 | Data migration | Rui Almeida | Green | Mock load 3 complete: 0 critical defects, 4 minor (cosmetic) |
| 6 | Change and training | Hanna Berg | Green | 198 of 240 staff trained (28 remaining sessions booked Sep 22–24). Super-user network established at all sites |
| 7 | Interfaces | Nils Berger | Green | 11 of 12 interfaces built and tested |
| 8 | Cutover and hypercare | Dev Raghunathan | Amber | Runbook 60% complete (214 tasks). Week 2 hypercare rota unstaffed due to group close conflict (see below) |

**Budget:** 74% spent, forecast on budget (excludes two open items below).

**Key dates:** Final load rehearsal Sat Oct 3, go-live Mon Oct 26, first payroll run on Ledgerline Fri Oct 30.

---

## Decisions requested this week

**1. Hollis Bank form HB-17 signature (payroll SFTP key) — URGENT**

**Issue:** Payment file SFTP key registration requires form HB-17 signed by a mandate holder (Dana or Marcus). Form sent to EA pool Sep 8, still unsigned. Hollis require 15 business days from receipt of signed form to activate the key, and the key must be live by Fri Oct 16 for a mandatory test file.

**Deadline:** Signed form must reach Hollis by **Fri Sep 25** at latest.

**If late:** October payroll (Fri Oct 30, 1,140 employees) cannot be paid from Ledgerline. We would run October payroll on the legacy system (EUR 22k licence extension + ~60 hours manual reconciliation), and payroll cutover moves to the Nov 27 run.

**Action:** Dana to sign form HB-17 this week (Marcus unavailable until Oct 9 per EA note).

---

**2. Week 2 hypercare rota (Nov 2–6)**

**Issue:** Hypercare week 2 coincides with group close. No finance-side support currently rostered.

**Options:**
- Pull two people out of close for hypercare support, or
- Hire contract support for the week (~EUR 9k)

**Action:** Decision needed on approach and budget approval if contract route chosen.

---

## Other items for noting

- **Workstream 1:** Ines on holiday Sep 21 – Oct 2, Petr covering.
- **Workstream 2:** Kestrel (scanning vendor) has not delivered OCR template for credit notes. Not on critical path; manual workaround available if needed.
- **Workstream 6:** Malmo lead super-user (Erik Sandberg) resigned, last day Oct 9. Proposed replacement: Ida Lund (requires half day per week from October).
- **Budget:** Group finance disputing EUR 41k on systems integrator September invoice (weekend rate billing). Procurement managing, no plan impact.
- **Internal audit:** Observation raised on AP segregation of duties. Response due 30 Nov (post go-live), Tobias owning.
- **Training correction:** Week 36 status reported 212 trained; correct figure is 198 (14 Rotterdam no-shows now re-booked in the 28 remaining sessions).
- **Office move:** Vasagatan building move now Nov 14 (was Oct 31).
