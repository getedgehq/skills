# UStVA Q3 2026 — Example Labs UG (haftungsbeschränkt)

Steuernummer 37/123/45678 · Finanzamt Berlin Beispiel · Zeitraum: 3. Kalendervierteljahr 2026
Ist-Versteuerung (§ 20 UStG), Regelbesteuerung, quarterly. Nothing submitted — numbers are for you to type into ELSTER.

**Due date: Monday 12.10.2026** (10.10.2026 is a Saturday → § 108 Abs. 3 AO). Payment of the Zahllast is due the same day. If you have a Dauerfristverlängerung it's 10.11.2026 — I couldn't see one in the folder, so assume 12.10.2026.

## The Kennzahlen

| Kz | What it is | Value |
|----|-----------|------:|
| 81 | Steuerpflichtige Umsätze 19 % (Bemessungsgrundlage) | 500 |
| 46 | § 13b Abs. 1 — Leistungen EU-Unternehmer (BMG) | 100 |
| 47 | …darauf entfallende Steuer | 19.00 |
| 52 | § 13b Abs. 2 Nr. 1 — Leistungen Drittland-Unternehmer (BMG) | 63 |
| 53 | …darauf entfallende Steuer | 11.97 |
| 66 | Vorsteuer aus Rechnungen anderer Unternehmer | 5.70 |
| 67 | Vorsteuer aus § 13b-Leistungen | 30.97 |
| 83 | **Verbleibender Betrag (Zahllast)** | **89.30** |

Check: USt 95.00 + 19.00 + 11.97 = 125.97 − Vorsteuer 36.67 = **89.30 EUR to pay**.

## How I got there

**Revenue — Kz 81 = 500 EUR**

Stripe charges, all DE customers, B2C, gross incl. 19 %:

| Date | Gross | Net | USt |
|------|------:|----:|----:|
| 09.07. | 119.00 | 100.00 | 19.00 |
| 22.07. | 178.50 | 150.00 | 28.50 |
| 05.08. | 297.50 | 250.00 | 47.50 |
| | **595.00** | **500.00** | **95.00** |

- Under Ist-Versteuerung I used the **charge dates**, not the payout dates — Stripe collects as your agent, so you've "vereinnahmt" when the customer pays. Doesn't matter here: charges and both payouts (31.07. + 31.08. = 595.00) all fall in Q3 and reconcile exactly to the gross charges.
- The **1 EUR test charge** on 12.09. is out: refunded the same day (bank shows +1.00 / −1.00), so zero net Umsatz in the period, and it was your own card anyway.

**Vorsteuer from normal invoices — Kz 66 = 5.70 EUR**

Only Hetzner qualifies: net 30.00 + 5.70 USt, German supplier, invoice correctly addressed to the UG, all § 14 Abs. 4 details present.

**Reverse charge — Kz 46/47 and 52/53**

All three foreign SaaS suppliers shift the VAT to you (place of supply Germany, § 3a Abs. 2 UStG). This is mandatory by law and does **not** depend on you having a USt-IdNr — it only depends on you being an Unternehmer, which you are.

| Supplier | Seat | Net | § 13b | Kz | USt |
|---|---|---:|---|---|---:|
| Anthropic Ireland | IE (EU) | 100.00 | Abs. 1 | 46/47 | 19.00 |
| Anysphere (Cursor) | US | 40.00 | Abs. 2 Nr. 1 | 52/53 | 7.60 |
| Supabase Pte | SG | 23.00 | Abs. 2 Nr. 1 | 52/53 | 4.37 |

The § 13b tax is fully deductible again as Vorsteuer in Kz 67 (19.00 + 11.97 = 30.97), so it nets to zero in cash terms — it just has to appear on both sides.

**Supabase currency conversion:** USD 25.00 at the BMF-Umrechnungskurs for September (1 EUR = 1.0870 USD, § 16 Abs. 6 UStG) = 22.9991 → 23 EUR. I did **not** use the 22.84 EUR your bank booked (card rate 1.0946) — for USt purposes only the BMF monthly rate counts. The 0.16 EUR difference is a Kursdifferenz in the books, not a VAT item.

## Two things that cost you money — please decide

**1. Anthropic and Cursor charged you German VAT they shouldn't have (26.60 EUR)**

Both invoices show `Customer tax ID: DE000000000` — a placeholder, because you have no USt-IdNr. So they treated you as a consumer and added 19 % German VAT (19.00 from Anthropic, 7.60 from Cursor).

That VAT is **wrongly invoiced** (§ 14c Abs. 1 UStG) and therefore **not deductible as Vorsteuer** — I have deliberately left it out of Kz 66. Instead you self-assess the same amounts via § 13b. Net effect: you paid 26.60 EUR of VAT that the Finanzamt will not give back.

What to do:
- **Get the USt-IdNr.** Apply via BZSt (or ELSTER → "Vergabe USt-IdNr"); you said you applied once and never heard back, so apply again and keep the confirmation. Then enter it in the Anthropic and Cursor billing settings. Supabase already handled you correctly as reverse charge, which is what all three should look like.
- **Ask Anthropic and Cursor for corrected invoices** (0 % / reverse charge) and a refund of the 26.60 EUR. This is a vendor matter, not a Finanzamt matter.
- Tell me if you'd rather I claim the 26.60 as Vorsteuer anyway — I don't recommend it; it's a standard audit finding and would turn into a correction plus interest.

**2. The IONOS domain invoice is addressed to you privately — 1.90 EUR not claimable**

`Max Beispiel, Am Privatweg 3` instead of the UG at Beispielweg 12. I know it's a company expense and I know you only used your private card because 4417 was blocked — but § 15 Abs. 1 i. V. m. § 14 Abs. 4 Nr. 1 UStG requires the invoice to name the UG as Leistungsempfänger. Who paid is irrelevant; the wrong recipient is not.

So 1.90 EUR stays out of Kz 66. Ask IONOS to reissue the invoice to the UG (and move the customer account to the UG for the future). Note that a corrected invoice naming a *different legal person* is generally **not** retroactively effective, so expect to claim it in the quarter the correction arrives rather than in Q3. The 11.90 EUR itself is still a company expense — book it as an Auslagenerstattung to you (income-tax/bookkeeping side, no VAT effect).

## Smaller points

- **Stripe fees:** there is no Stripe fee invoice in the folder, and the two payouts add up to exactly the gross charges (595.00), so I booked no fees. If Stripe did charge fees (usually Stripe Payments Europe Ltd., Ireland → reverse charge into Kz 46/47, deductible again in Kz 67), pull the monthly fee invoices from the Stripe dashboard and tell me — it would raise Kz 46/47 and Kz 67 by the same amount, so Kz 83 wouldn't change.
- **Rounding:** Bemessungsgrundlagen go in as full euros, Steuerbeträge with cents. Supabase at 22.9991 I rounded to 23 so that Kz 53 (63 × 19 % = 11.97) stays consistent with Kz 52 and passes ELSTER's plausibility check. Taking 22 instead would change Kz 52→62, Kz 53→11.78, Kz 67→30.78 and leave Kz 83 unchanged at 89.30 (it cancels out). Not worth worrying about.
- **Bank reconciliation is complete:** every debit in `bank-q3-2026.csv` has a matching invoice, and the only invoice without a bank debit is IONOS (private card, as expected). No gaps.
- **No Zusammenfassende Meldung** needed — you have no outbound EU B2B supplies.
- Kz 21/89 (innergemeinschaftliche Erwerbe) stay empty: you bought services, not goods, from the EU.

---

# The Finanzamt letter — Einspruch deadline

**You can file an Einspruch until the end of Thursday, 5 November 2026.**

How that date comes out:

1. **Aufgabe zur Post: 29.09.2026** (Tuesday) — the Poststempel.
2. **Bekanntgabefiktion: + 4 days** (§ 122 Abs. 2 Nr. 1 AO). This was *three* days until 31.12.2024; the Postrechtsmodernisierungsgesetz raised it to four days for anything posted from 01.01.2025, so four applies here. 29.09. + 4 = **03.10.2026**.
3. That's a **Saturday and also Tag der Deutschen Einheit**, so the Bekanntgabe shifts to the next Werktag (§ 122 Abs. 2 Satz 3 AO): **Monday 05.10.2026**.
4. **Einspruchsfrist: one month** from Bekanntgabe (§ 355 Abs. 1 AO), computed per § 108 AO with §§ 187, 188 BGB → ends with the end of **05.11.2026**, a Thursday, so no further shift.

That you actually found it in the letterbox on **01.10.2026** does not shorten anything — the fiction applies even when the letter arrives earlier. (Only *later* actual receipt would help you, and then you'd have to prove it.) Keep the envelope anyway.

## But you probably don't need the Einspruch at all

The Bescheid is **unter dem Vorbehalt der Nachprüfung (§ 164 Abs. 1 AO)**. That means: simply **filing the Q2 UStVA is itself an application to change the assessment under § 164 Abs. 2 AO**, and it works long after the Einspruchsfrist has run out. The 456 EUR is a § 162 AO estimate of 2.400 EUR revenue at 19 % with zero Vorsteuer — you said Q2 was basically no revenue, so filing should collapse it to roughly nothing or a refund.

So the practical plan:

- **File Q2 as fast as you can** — ideally before 02.11.2026. That kills the 456 EUR on the merits.
- **The 25 EUR Verspätungszuschlag is a separate decision** and does *not* disappear just because the tax drops. If you want to fight it (late filing was your fault, so chances are moderate — you'd argue it down as discretionary under § 152 Abs. 1 AO for a first-time, near-zero-tax quarter), that needs an **Einspruch by 05.11.2026**. For 25 EUR I'd let it go unless you're sending an Einspruch anyway.
- **Watch the payment date: 481 EUR is due 02.11.2026** — three days *before* the Einspruch deadline. An Einspruch does **not** suspend payment (§ 361 Abs. 1 AO). If Q2 isn't filed and processed by then and you don't want to pay the 481 EUR, you need an **Antrag auf Aussetzung der Vollziehung (§ 361 Abs. 2 AO)** alongside the Einspruch. Otherwise expect Säumniszuschläge from 03.11.2026.

**Decide for me:** do you want me to prepare the Q2 UStVA next (and if so, send me the Q2 invoices/bank), and do you want an Einspruch + AdV drafted as a safety net in case Q2 doesn't get processed before 02.11.2026?
