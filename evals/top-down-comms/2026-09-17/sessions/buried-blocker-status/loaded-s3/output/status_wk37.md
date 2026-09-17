# Ledgerline ERP program: steering status, week 37

To: Dana Okonkwo (CFO), steering group  
From: PMO  
Meeting: Wed 18 Sep 2026, 09:00

**Overall: GREEN with one signature-gated item**

The program is on schedule for go-live Mon 26 Oct. One item needs steering action this week: Hollis Bank form HB-17 (SFTP key for payroll files) must be signed and returned by Fri 25 Sep or October payroll cannot run on Ledgerline, forcing a one-month cutover delay and EUR 22k in extended legacy licence costs.

---

## AT A GLANCE

| Build progress | Budget | Go-live date | Decision needed |
|---|---|---|---|
| 7 of 8 workstreams green | 74% spent, on forecast | Mon 26 Oct | Bank form signature (Dana, by Fri 25 Sep) |

---

## 01  Workstream status

| # | Workstream | Lead | RAG | Update |
|---|---|---|---|---|
| 1 | General ledger and chart of accounts | Ines Varga | Green | Mapping 100% complete and signed off by group controlling. Opening balances template agreed with auditors. |
| 2 | AP / AR | Tobias Lind | Green | UAT cycle 2 complete, 97% pass rate (up from 91%). Remaining 3% are vendor master edge cases, fixes in Oct 1 build. Cycle 3 starts Oct 5. |
| 3 | Management reporting | Sana Qureshi | Amber | 12 of 14 reports built. Entity consolidation and cash forecast reports await group controlling inputs (promised 18 Sep). If inputs slip past 25 Sep, those two reports land post-go-live; old Excel versions cover the gap. |
| 4 | Payroll integration | Kofi Mensah | Green | Build complete. Test payment file validated by Hollis with zero errors. **Action required: see section 02 below.** |
| 5 | Data migration | Rui Almeida | Green | Mock load 3 complete, zero critical defects. Final rehearsal confirmed Sat 3 Oct. |
| 6 | Change and training | Hanna Berg | Green | 198 of 240 staff trained (corrected for no-shows). Remaining 42 booked 22–24 Sep. Super-user network established. Replacement super-user proposed for Malmö (Erik Sandberg resigned, last day 9 Oct; Ida Lund nominated). |
| 7 | Interfaces | Nils Berger | Green | 11 of 12 interfaces built and tested. Twelfth (Kestrel OCR feed) can be built blind to spec if vendor delays continue. |
| 8 | Cutover and hypercare | Dev Raghunathan | Amber | Cutover runbook 60% written (214 tasks). Hypercare week 2 (2–6 Nov) conflicts with group close; decision needed on whether to pull finance staff out of close or hire contract cover (EUR 9k). |

---

## 02  Decision required: bank form signature by Friday 25 September

**The issue:** Hollis Bank require form HB-17 (SFTP key registration for Ledgerline payment files) signed by an account mandate holder. Activation takes 15 business days from receipt, and Hollis require a successful live test file by Fri 16 Oct to support the first Ledgerline payroll run on Fri 30 Oct. The signed form must reach Hollis by **Fri 25 Sep** to meet this deadline.

**Status:** Form sent to executive assistants 8 Sep. Still unsigned as of 15 Sep. Marcus is traveling (Singapore/Seoul) until 9 Oct and is not signing physical documents.

**Who can sign:** Dana Okonkwo or Marcus Reinholt (the only two active mandate holders for account VG-0041-2).

**Consequence of delay:** October payroll (1,140 employees, Fri 30 Oct) cannot be paid from Ledgerline. October payroll runs on legacy system instead, requiring:
- EUR 22,000 extended legacy licence
- ~60 hours manual reconciliation between systems in first week of November
- Payroll cutover moves to 27 Nov run

**Request:** Dana to sign form HB-17 and return to Petra Holm (Hollis relationship manager) by Fri 25 Sep. Form and cover sheet attached separately.

---

## 03  Hypercare resourcing: week 2 conflicts with group close

**The issue:** Hypercare week 2 (2–6 Nov) overlaps the group consolidation close. The cutover runbook requires two finance staff on call for escalations that week; none are currently named.

**Options:**
1. Pull two finance staff out of close (delivery risk to group reporting deadline)
2. Hire contract finance support for hypercare week 2 (EUR 9k)

**Request:** Steering to decide which option by steering meeting 25 Sep.

---

## 04  Other items noted

- **Budget:** 74% spent, forecast on budget (excludes payroll item above and hypercare decision).
- **Disputed invoice:** EUR 41k of the September systems integrator invoice is under review (weekend rate dispute for data migration rehearsal). Procurement handling; no plan impact.
- **Internal audit:** Segregation of duties observation raised on AP approval matrix. Response due 30 Nov (post-go-live). Tobias Lind owns.
- **Vendor delay:** Kestrel (scanning vendor) has not delivered OCR template for credit notes. Not on critical path; worst case is manual keying for one month post-go-live.
- **Key dates unchanged:** Final load rehearsal Sat 3 Oct, go-live Mon 26 Oct, first Ledgerline payroll Fri 30 Oct.

---

## Next steering: Wed 25 Sep, 09:00
