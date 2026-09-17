# Ledgerline ERP program: steering status, week 37

To: Dana Okonkwo (CFO), steering group  
From: PMO  
Date: Wed 16 Sep 2026

**Overall: GREEN** — Programme on track for go-live Mon Oct 26. Technical delivery is solid across all workstreams. Two items need steering decisions this week.

---

## Decisions requested

**01. Payroll bank key signature — urgent**

A bank form needs a mandate holder's signature by **Fri Sep 25** or October payroll cannot run on Ledgerline. The form authorises payment file transmission to Hollis Bank. Processing takes 15 business days from signature, and Hollis require a live test file two weeks before first production payroll (Fri Oct 30).

If we miss Sep 25: October payroll runs on the legacy system. Cost EUR 22,000 licence extension plus 60 hours manual reconciliation. Payroll cutover moves to Nov 27 run.

Marcus is travelling until Oct 9 and not signing documents. **Dana signature required.** Form is with the EA pool (submitted Sep 8). PMO has chased twice. Kofi Mensah can hand-carry to Dana's office today if needed.

**02. Hypercare rota conflict — week of Nov 2**

Week 2 hypercare (Nov 2–6) overlaps group close. Finance-side support is unstaffed. Options: pull two people out of close, or hire contract support for the week (EUR 9,000). Dev Raghunathan needs the call to finalise the cutover runbook.

---

## Workstream status

| # | Workstream | Lead | RAG | Update |
|---|---|---|---|---|
| 1 | General ledger and chart of accounts | Ines Varga | Green | Mapping 100% complete, signed off by group controlling. Opening balances template agreed with auditors. Ines on holiday Sep 21–Oct 2, Petr covers. |
| 2 | AP / AR | Tobias Lind | Green | UAT cycle 2 complete. 97% pass rate (was 91%). Remaining 3% are vendor master edge cases, fixed in Oct 1 build. Cycle 3 starts Oct 5. |
| 3 | Management reporting | Sana Qureshi | Amber | 12 of 14 reports built. Two waiting on consolidation rules from group controlling, promised Sep 18. If rules slip past Sep 25, two reports land after go-live. Excel versions can run one more month if needed. |
| 4 | Payroll integration | Kofi Mensah | Green | Mapping done. Test payment file validated by Hollis Bank's checker tool, zero errors. Bank key registration blocked on signature (see decision 01). |
| 5 | Data migration | Rui Almeida | Green | Mock load 3 complete: 0 critical defects, 4 minor cosmetic issues (address truncation). Final rehearsal Sat Oct 3 confirmed. |
| 6 | Change and training | Hanna Berg | Green | 198 of 240 staff trained (corrected figure). Remaining 42 scheduled Sep 22–24. Super-user network live at all sites. Lead super-user in Malmo resigned, Ida Lund proposed as replacement (needs half day/week from October). |
| 7 | Interfaces | Nils Berger | Green | 11 of 12 interfaces built and tested. Twelfth (Kestrel scanning feed) can be built blind if vendor delays continue, test in hypercare. |
| 8 | Cutover and hypercare | Dev Raghunathan | Amber | Cutover runbook 60% complete, 214 tasks. Week 2 hypercare rota unstaffed due to group close (see decision 02). |

---

## Budget and schedule

- **Budget:** 74% spent, forecast on budget (excludes potential EUR 22,000 payroll extension and EUR 9,000 hypercare decision)
- **Key dates:** Final load rehearsal Sat Oct 3 | Go-live Mon Oct 26 | First payroll run on Ledgerline Fri Oct 30
- **Schedule:** On track

---

## For information

- **Disputed SI invoice:** EUR 41,000 of September systems integrator invoice disputed (weekend rate billing error). Procurement managing, no impact on plan.
- **Internal audit:** Observation raised on AP segregation of duties. Response due 30 Nov, after go-live. Tobias Lind owns.
- **Kestrel scanning vendor:** OCR template for credit notes not yet delivered. Not on critical path; manual keying fallback available for one month if needed.
- **Office move:** Vasagatan building move now Nov 14 (was Oct 31). Unrelated to programme.

---

## Next status

Week 38 update on Wed 23 Sep. Three weeks to go-live.
