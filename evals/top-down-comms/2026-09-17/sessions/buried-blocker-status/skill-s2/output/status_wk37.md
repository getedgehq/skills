# Ledgerline ERP program: steering status, week 37 (for Wed 16 Sep 2026)

To: Dana Okonkwo (CFO), steering group
From: PMO

**Overall: GREEN** (with one escalation requiring decision)

| # | Workstream | Lead | RAG | Update |
|---|---|---|---|---|
| 1 | General ledger and chart of accounts | Ines Varga | Green | Mapping 100% complete and signed off by group controlling. Opening balances template agreed with auditors |
| 2 | AP / AR | Tobias Lind | Green | UAT cycle 2 complete, 97% of test cases passing (up from 91%). Remaining 3% edge cases fixed in Oct 1 build |
| 3 | Management reporting | Sana Qureshi | Amber | 12 of 14 reports built. Two reports awaiting consolidation rules from group controlling (promised Sep 18). Risk: delivery after go-live if rules slip past Sep 25 |
| 4 | Payroll integration | Kofi Mensah | Green | Mapping complete. Test payment file validated with zero errors. **Escalation: bank form signature needed** (see below) |
| 5 | Data migration | Rui Almeida | Green | Mock load 3 complete: zero critical defects, 4 minor cosmetic issues |
| 6 | Change and training | Hanna Berg | Green | 198 of 240 staff trained (corrected figure). Remaining 42 sessions booked Sep 22-24 |
| 7 | Interfaces | Nils Berger | Green | 11 of 12 interfaces built and tested |
| 8 | Cutover and hypercare | Dev Raghunathan | Amber | Cutover runbook 60% complete (214 tasks). Week 2 hypercare rota unresolved due to group close timing conflict |

**Budget:** 74% spent, forecast on budget (excludes potential hypercare contract support of EUR 9,000).

**Key dates:** Final load rehearsal Sat Oct 3, go-live Mon Oct 26, first payroll run on Ledgerline Fri Oct 30.

---

## Decisions requested this week

### 1. URGENT: Hollis Bank form HB-17 signature (payroll payments)

**Context:** Ledgerline payroll payments require a new SFTP key registered with Hollis Bank. Form HB-17 must be signed by a mandate holder (Dana or Marcus). Form sent to exec assistants Sep 8, still unsigned.

**Timing:** Hollis require 15 business days to activate the key after receiving the signed form, plus a successful live test file two weeks before first production payroll. **Signed form must reach Hollis by Fri Sep 25** to meet the Oct 30 payroll deadline.

**Impact if missed:** October payroll (1,140 employees, Fri Oct 30) cannot be paid from Ledgerline. Fallback: run October payroll on legacy system, requiring EUR 22,000 license extension + 60 hours manual reconciliation. Payroll cutover delays to Nov 27.

**Decision needed:** Confirm signature route (Dana available this week; Marcus in Asia until Oct 9 and not signing physical documents while traveling per EA note).

### 2. Hypercare week 2 support (Nov 2-6)

**Context:** Week 2 of hypercare coincides with group close. Finance-side support rota for that week is unstaffed.

**Options:**
- Pull two people out of group close for hypercare support, or
- Hire contract support for the week (EUR 9,000)

**Decision needed:** Which option to proceed with.

### 3. Malmö super-user replacement

**Context:** Lead super-user Erik Sandberg resigned (last day Oct 9). Hanna proposes Ida Lund as replacement, requires half day per week from October.

**Decision needed:** Approval to proceed.

---

## Other items for awareness

- **Management reporting amber status:** Sana escalating group controlling's delay on consolidation rules (three weeks of warnings, no action). If rules arrive by Sep 18 as promised, two reports will be ready for go-live. If rules slip past Sep 25, two reports (entity consolidation and cash forecast) deliver post go-live; Excel versions can cover one more month.

- **Kestrel scanning vendor:** OCR template for credit notes still outstanding. Not on critical path; manual keying is fallback for first month if needed.

- **Internal audit observation:** Segregation of duties query on AP approval matrix raised. Response due Nov 30 (post go-live), Tobias owns.

- **Invoice dispute:** EUR 41,000 of systems integrator's September invoice disputed (weekend rates for data migration rehearsal). Procurement handling, no impact on plan.

- **Coverage:** Ines on holiday Sep 21 to Oct 2, Petr covering.

- **Office move:** Now Nov 14 (was Oct 31).

---

*Note: Marcus requested status to be readable in two minutes.*
