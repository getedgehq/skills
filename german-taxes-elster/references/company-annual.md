# UG/GmbH annual filings

Order of work: Jahresabschluss (HGB) → E-Bilanz → KSt 1 (+ Anlagen) and GewSt 1 A → Offenlegung.
The returns must agree with each other and with the E-Bilanz. Change one, change all, same day.

## Jahresabschluss without accounting software

- Rebuild the books from bank export (with Verwendungszweck per booking), processor balance
  transactions, invoices and contracts. Write a journal, derive a Saldenliste (e.g. SKR04) from it.
- First year: Eröffnungsbilanz at the start of business (§ 242 HGB), no Verlustvortrag, no
  comparatives.
- Read every intercompany movement by its Verwendungszweck. In the source run, transfers that
  looked like a loan repayment were capital contributions to another company, and a "forgiven"
  loan was in fact still open.
- Receivables at year end: processor balances paid out in January are a receivable at 31.12.
- Formation costs: the Musterprotokoll caps what the company bears (often 300 EUR); the excess is
  the shareholders'. Costs of founding *another* company are not this company's expense.
- **UG only: gesetzliche Rücklage.** 25 % of the Jahresüberschuss (less a loss carried forward)
  goes into the reserve (§ 5a Abs. 3 GmbHG).
- Deadlines: aufstellen within 6 months for small companies (§ 264 Abs. 1 HGB), shareholders'
  Feststellungsbeschluss within 11 months (§ 42a GmbHG) *(verify)*.

## Rückstellungen worth checking

| Rückstellung | Basis |
|---|---|
| Steuerrückstellungen (KSt, Soli, GewSt for the year) | HGB; GewSt is not deductible for tax (§ 4 Abs. 5b EStG) but is booked |
| Costs of preparing the Jahresabschluss and the company's own tax returns and E-Bilanz | öffentlich-rechtliche Verpflichtung; external costs, or reasonable internal costs |
| Aufbewahrung of business records | Retention duty § 257 HGB / § 147 AO; since 2025 Buchungsbelege 8 years, books and annual accounts 10 years *(verify)* |
| Interest owed on shareholder or intercompany loans | accrued to 31.12. |

Each Rückstellung needs a written computation in the file. Do not invent a provision to reduce tax.

## Körperschaftsteuer

- 15 % KSt on the zu versteuerndes Einkommen; the resulting KSt amounts are rounded to whole euros
  in the taxpayer's favour (§ 31 Abs. 1 Satz 2 KStG). Soli 5.5 % of the KSt, fractions of a cent
  dropped (§ 4 Satz 3 SolZG).
- Share-sale gains of a corporation: 95 % effectively tax-free (§ 8b Abs. 2, 3 KStG).
- **Verlustrücktrag** exists for KSt (§ 10d EStG via § 8 Abs. 1 KStG), currently up to two years
  back *(verify amount caps per year)*. **There is no Verlustrücktrag for GewSt**, only Vortrag
  (§ 10a GewStG).
- Anlage GK line "Jahresüberschuss laut Steuerbilanz" must match the E-Bilanz.

## Gewerbesteuer

- Gewerbeertrag rounded **down to full 100 EUR**, Messzahl 3.5 %, times the municipal Hebesatz.
- **No Freibetrag for corporations.** The 24,500 EUR Freibetrag (§ 11 Abs. 1 Satz 3 Nr. 1 GewStG) is for
  individuals and partnerships only. A frequent model error.
- The Finanzamt issues the Messbescheid (Grundlagenbescheid); the municipality issues the
  GewSt-Bescheid, except in the city states where the Finanzamt issues both. An Einspruch goes
  against the **Messbescheid** (§ 351 Abs. 2 AO); the GewSt-Bescheid follows (§ 35b GewStG).

## § 7g Investitionsabzugsbetrag

- Up to 50 % of the expected acquisition cost of a movable asset to be bought within 3 years,
  deducted outside the balance sheet. Profit limit 200,000 EUR; at least 90 % business use until
  the end of the year after acquisition *(verify current limits)*.
- Can be claimed late, even in an Einspruch.
- If the investment does not happen, it is reversed retroactively **with interest** (§ 7g Abs. 3
  EStG). Never claim it for a company that is winding down, and never without the owner confirming a
  real investment plan.

## Prepayments

Vorauszahlungen are set from the last assessment. When the current year will be far lower, apply
for Herabsetzung (template in `templates.md`; law in `notices-and-appeals.md`). A successful
Einspruch against the prior year also lowers the base.

## Offenlegung / Hinterlegung

- Annual accounts go to the Unternehmensregister within 12 months after the balance-sheet date
  (§ 325 HGB), via the publication platform of the Unternehmensregister *(verify current portal)*.
- A **Kleinstkapitalgesellschaft** (§ 267a HGB) may **hinterlegen** the balance sheet only, not
  publicly searchable (§ 326 Abs. 2 HGB). It must be filed explicitly as Hinterlegung, with the
  declaration that the size thresholds are met; filed as a normal Offenlegung, the benefits are lost.
- Ordnungsgeld for missing filing starts at 2,500 EUR; for a Kleinstkapitalgesellschaft that
  hinterlegt late but within the set grace period it can drop to 500 EUR (§ 335 Abs. 4 HGB)
  *(verify)*. Filing on time costs nothing.

## Discrepancies found after filing

If the E-Bilanz or a review shows the KSt/GewSt returns were wrong:

1. "Sonstige Nachricht": Anzeige nach § 153 AO with the corrected figures and the Transfertickets.
2. Corrected KSt and GewSt returns marked in free text as Berichtigung (§ 150 Abs. 7 AO).
3. Compute the difference as assessed-vs-assessed tax, not provision-vs-provision.
4. Mark the superseded working files ÜBERHOLT.
