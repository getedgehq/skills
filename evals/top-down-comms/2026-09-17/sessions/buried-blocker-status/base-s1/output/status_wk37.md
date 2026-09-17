# Ledgerline ERP program: steering status, week 37 (for Wed 18 Sep 2026)

To: Dana Okonkwo (CFO), steering group
From: PMO

**Overall: GREEN**

| # | Workstream | Lead | RAG | Update |
|---|---|---|---|---|
| 1 | General ledger and chart of accounts | Ines Varga | Green | Mapping 100% complete and signed off by group controlling. Opening balances template agreed with auditors |
| 2 | AP / AR | Tobias Lind | Green | UAT cycle 2 complete, 97% pass rate (up from 91%). Remaining issues fixed in Oct 1 build. Cycle 3 starts Oct 5 |
| 3 | Management reporting | Sana Qureshi | Amber | 12 of 14 reports built. Final 2 (consolidation, cash forecast) waiting on group controlling inputs, promised 18 Sep. Risk of post-go-live delivery if inputs slip past 25 Sep |
| 4 | Payroll integration | Kofi Mensah | Green | Mapping done, test file validated by Hollis with zero errors |
| 5 | Data migration | Rui Almeida | Green | Mock load 3 complete, 0 critical defects. Final rehearsal confirmed for Sat 3 Oct |
| 6 | Change and training | Hanna Berg | Green | 198 of 240 staff trained (28 remaining sessions booked 22-24 Sep). Super-user network live at all sites |
| 7 | Interfaces | Nils Berger | Green | 11 of 12 interfaces built and tested |
| 8 | Cutover and hypercare | Dev Raghunathan | Amber | Cutover runbook 60% complete (214 tasks). Week 2 hypercare rota unresolved (conflict with group close, Nov 2-6) |

Budget: 74% spent, forecast on budget (excludes potential hypercare contract costs).

Key dates: final load rehearsal Sat Oct 3, go-live Mon Oct 26, first payroll run on Ledgerline Fri Oct 30.

---

## Decisions requested this week

**1. Hollis Bank form HB-17 signature (URGENT)**

Form HB-17 (SFTP key registration for payment files) requires signature by Dana or Marcus. Sent to exec assistants 8 Sep, still unsigned.

**Critical timeline:**
- Signed form must reach Hollis by **Fri 25 Sep** (latest)
- Hollis activation takes 15 business days
- Key must be live by Fri 16 Oct for required test file
- Test file must succeed by Fri 23 Oct (2 weeks before first payroll run)

**Impact if late:** October payroll (Fri 30 Oct, 1,140 employees) cannot run on Ledgerline. Fallback is legacy system payroll at EUR 22,000 cost plus ~60 hours manual reconciliation. Payroll cutover moves to November.

**Note:** Marcus in Singapore/Seoul until 9 Oct and not signing physical documents while travelling (per EA note). Requires Dana's signature this week.

**2. Hypercare week 2 staffing (Nov 2-6)**

Week 2 hypercare coincides with group close. Decision needed:
- Option A: Pull 2 finance staff out of close for hypercare support
- Option B: Hire contract support for the week (~EUR 9,000)

---

## Other items

- **Super-user change:** Erik Sandberg (Malmo lead, resigning 9 Oct). Hanna proposes Ida Lund as replacement (requires half day/week from October). [Recommendation: approve]
- **Kestrel scanning vendor:** Credit note OCR template still delayed. Mitigation: manual keying for one month if needed (not critical path).
- **Systems integrator invoice dispute:** EUR 41,000 disputed (weekend rate billing). Procurement handling, no plan impact.
- **Internal audit:** Segregation of duties observation raised on AP approval matrix. Response due 30 Nov (post go-live), Tobias owning.
- **Office move:** Vasagatan building move now 14 Nov (was 31 Oct).

---

## Progress highlights

- GL mapping 100% complete (nice change from August!)
- UAT pass rate up to 97%
- Test payroll file validated perfectly by Hollis
- Mock data load 3 had zero critical defects
- Training nearly complete (82% done)
