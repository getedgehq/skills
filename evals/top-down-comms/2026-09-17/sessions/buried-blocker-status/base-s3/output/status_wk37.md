# Ledgerline ERP program: steering status, week 37 (for Wed 18 Sep 2026)

To: Dana Okonkwo (CFO), steering group
From: PMO

**Overall: GREEN** (mostly green this week)

| # | Workstream | Lead | RAG | Update |
|---|---|---|---|---|
| 1 | General ledger and chart of accounts | Ines Varga | Green | Mapping 100% complete and signed off. Opening balances template agreed with auditors |
| 2 | AP / AR | Tobias Lind | Green | UAT cycle 2 complete, 97% pass rate. Cycle 3 starts Oct 5 |
| 3 | Management reporting | Sana Qureshi | Amber | 12 of 14 reports built. Two reports awaiting consolidation rules from group controlling (promised Sep 18) |
| 4 | Payroll integration | Kofi Mensah | Green | Test payment file validated with zero errors. **See decision item below** |
| 5 | Data migration | Rui Almeida | Green | Mock load 3 complete: 0 critical defects, 4 minor cosmetic issues |
| 6 | Change and training | Hanna Berg | Green | 198 of 240 staff trained (was 180). Remaining 28 sessions booked Sep 22–24 |
| 7 | Interfaces | Nils Berger | Green | 11 of 12 interfaces built and tested |
| 8 | Cutover and hypercare | Dev Raghunathan | Amber | Runbook 60% complete (214 tasks). **See decision item below** |

**Budget:** 74% spent, forecast on budget (excludes potential costs noted below).

**Key dates:** Final load rehearsal Sat Oct 3, go-live Mon Oct 26, first payroll run on Ledgerline Fri Oct 30.

---

## Decisions requested this week

### 1. URGENT: Hollis Bank form HB-17 signature (payroll integration)

**Issue:** The bank requires form HB-17 (SFTP key registration for payment files) to be signed by a mandate holder. The signed form must reach Hollis by **Fri Sep 25** at the latest to allow 15 business days activation plus 2 weeks for test file before the Oct 30 payroll run.

Form was sent to exec assistants on Sep 8. As of Tue Sep 15, still unsigned. Marcus is traveling until Oct 9 and not signing physical documents.

**Impact if not signed by Sep 25:** October payroll (1,140 employees, Fri Oct 30) cannot be paid from Ledgerline. Would require:
- Running October payroll on legacy system
- Extending legacy payroll licence one more month (EUR 22,000)
- ~60 hours manual reconciliation between systems in early November
- Payroll cutover moves to Nov 27 run

**Decision needed:** Dana to sign form HB-17 this week (Dana is on the account mandate).

### 2. Hypercare rota week 2 staffing (cutover & hypercare)

**Issue:** Week 2 of hypercare (Nov 2–6) coincides with group close. No finance-side support currently assigned.

**Options:**
- Pull two people out of group close for hypercare support, OR
- Hire contract support for the week (~EUR 9,000)

**Decision needed:** Approve approach and, if contract route, approve EUR 9,000 contingency.

---

## Other items for noting

- **Management reporting amber:** If group controlling's consolidation rules slip past Sep 25, two reports (entity consolidation and cash forecast) will land after go-live. Old Excel versions can bridge for one month if needed.
- **AP/AR Kestrel delay:** Scanning vendor Kestrel has not delivered OCR template for credit notes. Not on critical path; worst case is manual keying for one month.
- **Malmö super-user:** Erik Sandberg (lead super-user) resigned, last day Oct 9. Hanna proposes Ida Lund as replacement (requires half day/week from October).
- **Data migration:** Rui queries whether Sunday Oct 4 rehearsal slot still needed; he believes Saturday Oct 3 is sufficient.
- **Systems integrator invoice:** EUR 41,000 disputed (weekend rates for data migration rehearsal). Procurement managing, no impact on plan.
- **Internal audit:** Segregation of duties observation on AP approval matrix. Response due Nov 30, Tobias owns.
- **Ines holiday:** Sep 21–Oct 2, Petr Novak covers.

---

*Prepared by Lea Fontaine, PMO, 17 Sep 2026*
