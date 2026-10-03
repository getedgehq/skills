# Umsatzsteuer: UStVA, annual return, reverse charge

Kennzahlen (Kz) and line numbers are from the 2025/2026 forms. Check the current BMF Vordruckmuster
for the year you file *(verify every year)*.

## Deadlines and rhythm

- UStVA due on the **10th day after the period** (§ 18 Abs. 1 UStG). Quarterly filer: 10.04.,
  10.07., 10.10., 10.01.
- **Dauerfristverlängerung** (§§ 46-48 UStDV) adds one month to every period. For a **quarterly**
  filer it is free: the Sondervorauszahlung of 1/11 only applies to monthly filers. ELSTER has two
  different forms: "Dauerfristverlängerung (vierteljährlich)" and "Dauerfristverlängerung /
  Sondervorauszahlung (monatlich)"; pick the right one. No approval letter is issued; it applies
  unless refused and stays until revoked. File it before the deadline of the first period it should
  cover. It is the cheapest fix after a late Voranmeldung.
- New businesses: the monthly-filing duty for the founding year and the next is suspended for
  2021-2026 (§ 18 Abs. 2 Satz 6 UStG) *(verify for 2027 onward)*.
- Annual USt return: same deadline as the other annual returns (see `notices-and-appeals.md`).
- A Voranmeldung or annual return that does not deviate from the declared numbers is itself the
  assessment under Vorbehalt der Nachprüfung (§ 168 AO). The Finanzamt then sends a
  "Bestätigung der Festsetzung" without numbers; the numbers are your own submission.

## Classify each purchase (input side)

| Supplier sits in | Invoice shows | Treatment | UStVA |
|---|---|---|---|
| Germany | 19 % or 7 % German VAT, addressed to the company | Vorsteuer if invoice in hand | Kz 66 |
| EU (e.g. Anthropic Ireland, Meta Ireland, Lovable Sweden) | "Reverse charge", net | § 13b Abs. 1 UStG, place of supply § 3a Abs. 2 | Kz 46 (base) / 47 (tax), deduct in Kz 67 |
| Third country (e.g. Cursor/Anysphere US, Supabase Singapore, Vercel US, Render US) | no VAT or "reverse charge" | § 13b Abs. 2 Nr. 1 UStG | Kz 84 / 85, deduct in Kz 67 |
| Any foreign SaaS | **"VAT Germany 19 %" with customer VAT ID `DE000000000`** | see below: not deductible as Vorsteuer | still § 13b on the net amount |
| Any | addressed to the founder privately | not the company's purchase | none; see "founder-billed" |
| Any | only a bank debit, no invoice | no Kz 66; reverse-charge base needs other proof of service, recipient and period | flag `[FEHLT]` |

Check the **seller's legal entity on the invoice**, not the brand: the same brand bills from the US
to some customers and from Ireland to others, and that decides Kz 46 vs 84.

With full Vorsteuer entitlement the reverse-charge tax and its deduction cancel out (net zero), but
both must be declared. "Left out for simplicity" is a correction you will owe later under § 153 AO.

Foreign-currency invoices: convert at the BMF monthly rate (§ 16 Abs. 6 UStG). Compute the tax from
the exact base; only the base field is truncated to whole euros.

Timing: EU services (§ 13b Abs. 1) at the end of the period in which the service was performed;
third-country services at invoice issue, at the latest the end of the month after the service
*(verify § 13b Abs. 1/2)*.

## The DE000000000 trap

A company that has a Steuernummer but **no USt-IdNr** gets billed by many SaaS vendors as a consumer:
the invoice says "VAT - Germany (19 %)" and the customer VAT ID field holds the placeholder
`DE000000000`. Seen on Anthropic and Cursor invoices; Supabase on the same account correctly wrote
"Reverse charge".

- The company is still a business customer. Place of supply is with the recipient (§ 3a Abs. 2
  UStG) and the tax liability shifts to it (§ 13b Abs. 5) regardless of whether it gave a VAT ID.
- The vendor owes the invoiced German VAT only because it put it on the invoice (§ 14c Abs. 1
  UStG, unrichtiger Ausweis); it is not tax owed *for the supply*, so it is **not deductible** as
  Vorsteuer (§ 15 Abs. 1 Satz 1 Nr. 1 UStG).
- So: declare § 13b on the net amount (gross / 1.19 for a 19 % invoice), deduct the same in Kz 67,
  do **not** put the invoiced 19 % into Kz 66. The 19 % actually paid is a cost unless the vendor
  refunds it against a corrected invoice.
- Whether this applies at all depends on the company, not the founder, being the customer
  (account, billing name, payment card). Decide that first.

**Fix at the source:** get a USt-IdNr and enter it in every vendor's billing profile. It is not
retroactive; past invoices stay as they are unless the vendor re-issues them.

## Getting a USt-IdNr (§ 27a UStG)

- Issued by the **BZSt**, not the Finanzamt, free. Online form on formulare-bfinv.de ("Antrag auf
  Erteilung ... einer Umsatzsteuer-Identifikationsnummer"). It is not in Mein ELSTER.
- The online form matches name, postcode and Steuernummer in real time against data the
  Finanzamt sent to the BZSt. Rejection messages differ: "Daten stimmen nicht überein" (the number
  is known but stored name/address differ) vs "(noch) nicht als umsatzsteuerrechtlicher
  Unternehmer registriert" (that number carries no VAT registration). Do not keep guessing the
  company name; every attempt is logged.
- Fixes: a written application to the BZSt (Dienstsitz Saarlouis), or ask the Finanzamt which
  Steuernummer carries the VAT registration and which name and address are stored there ("Sonstige
  Nachricht", template in `templates.md`). The BZSt cannot change the data; the Finanzamt can.
- Ticking "USt-IdNr benötigt" in the Fragebogen zur steuerlichen Erfassung does not guarantee one
  arrives. Check that it did.
- A Zusammenfassende Meldung (§ 18a UStG) is needed only for services/supplies the company
  **provides** to EU businesses, not for ones it buys.

## Founder-billed vendors (invoice in the founder's name)

Domains, SaaS plans, inventory bought by the founder's personal card for the company:

- The company has no Vorsteuer from an invoice not addressed to it.
- The cost is still the company's operating expense if it was incurred for the company (§ 4 Abs. 4
  EStG via § 8 Abs. 1 KStG). Book it **gross** with a liability to the shareholder
  (Auslagenersatz) or, if never reimbursed, as an Einlage. Either way it is deductible.
- Paperwork: the original invoice, the private bank/card debit, and an **Eigenbeleg** (template in
  `templates.md`) signed by the payer and countersigned by the managing director.
- Going forward: re-address the vendor account to the company and add the USt-IdNr.
- Test charges a company makes to itself (checkout tests) are not revenue; keep charge IDs, the
  card debit and the purpose together.

## Output side, briefly

| Sale | UStVA |
|---|---|
| Domestic 19 % | Kz 81 |
| Exports of goods to third countries (proof of export required) | Kz 43 |
| B2B services to EU businesses (reverse charge at the customer; ZM required) | Kz 21 |
| Services to third-country customers, not taxable in Germany | Kz 45 |
| Electronic services to EU consumers below the 10,000 EUR EU-wide threshold | German VAT; above it OSS *(verify)* |
| Sale of shares in another company | exempt § 4 Nr. 8 f UStG if held as part of business activity (Kz 48), outside VAT entirely if passive holding |

Reconcile revenue per quarter: processor payouts are net of fees and refunds; declare the gross
consideration. A payout in January can be the previous year's revenue.

## Annual USt return

- Sum of the Voranmeldungen plus corrections. The "Vorauszahlungssoll" line is what was declared and
  assessed, not what was paid; unpaid amounts are a collection matter on the Steuerkonto.
- EU reverse charge and third-country reverse charge sit in **different lines** (2025: line 65
  Kz 846/847 vs line 67). Don't merge them.
- The annual return must contain the correct full-year amounts, including reverse charge that was
  missing from earlier Voranmeldungen. Where a base is still uncertain, enter your best evidenced
  estimate and say so in "Ergänzende Angaben" (line 21, Kz 123 in 2025); correct it under § 164
  Abs. 2 AO once the invoices are in, while the assessment is still under Vorbehalt.
- Before filing, confirm the Kleinunternehmer waiver and the Besteuerungsart on the source form.
