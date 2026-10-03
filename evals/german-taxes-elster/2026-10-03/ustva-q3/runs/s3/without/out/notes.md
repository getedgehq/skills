# UStVA Q3 2026 — Example Labs UG (haftungsbeschränkt)

Steuernummer 37/123/45678 · Voranmeldungszeitraum 3. Kalendervierteljahr 2026 (Juli–September)
Regelbesteuerung, **Ist-Versteuerung** (§ 20 UStG), quarterly. Nothing submitted — numbers are in `out/ustva.json` for you to type into ELSTER.

## The numbers

| Kz | ELSTER label (short) | Betrag |
|----|----------------------|--------|
| 81 | Steuerpflichtige Umsätze 19 % — Bemessungsgrundlage | 500 |
| 46 | § 13b Abs. 1 UStG, Leistung EU-Unternehmer — BMG | 100 |
| 47 | § 13b Abs. 1 UStG — Steuer | 19,00 |
| 84 | § 13b Abs. 2 Nr. 1 UStG, Leistung im Ausland ansässiger Unternehmer — BMG | 63 |
| 85 | § 13b Abs. 2 Nr. 1 UStG — Steuer | 11,97 |
| 66 | Vorsteuer aus Rechnungen anderer Unternehmer | 5,70 |
| 67 | Vorsteuer aus Leistungen i. S. d. § 13b UStG | 30,97 |
| 83 | Verbleibender Betrag / Vorauszahlung | 89,30 |

USt total 95,00 + 19,00 + 11,97 = 125,97 · Vorsteuer total 36,67 · **zu zahlen 89,30 EUR**.
Kz 83 is calculated by ELSTER — it should land on 89,30; if it doesn't, something above was mistyped. BMG fields (81/46/84) are full euros, tax fields have cents.

## How I got there

**Umsätze (Kz 81) — 500 EUR net / 95,00 EUR USt**

| Datum | Beleg | Brutto | Netto | USt 19 % |
|---|---|---|---|---|
| 09.07. | Stripe, Pro annual | 119,00 | 100,00 | 19,00 |
| 22.07. | Stripe, Pro x1.5 seats | 178,50 | 150,00 | 28,50 |
| 05.08. | Stripe, Team | 297,50 | 250,00 | 47,50 |
| 12.09. | Stripe, 1 EUR checkout test — refunded same day | — | — | — |

All Stripe charges are DE customers, B2C, gross incl. 19 % → divided by 1,19. Ties out against the bank: two payouts of 297,50 (31.07. + 31.08.) = 595,00 = sum of the three charges. The 1 EUR test charge was received and refunded on 12.09., so under Ist-Versteuerung the § 17 UStG correction falls in the same quarter and nets to zero — left out entirely.

**Reverse charge (Kz 46/47 and 84/85)** — all three foreign SaaS suppliers are B2B services with place of supply Germany (§ 3a Abs. 2 UStG), so the UG is the Steuerschuldner:

- Anthropic Ireland Ltd, 100,00 EUR net → EU-resident supplier, § 13b Abs. 1 → Kz 46/47, 19,00 EUR.
- Anysphere Inc. (Cursor, US), 40,00 EUR net → § 13b Abs. 2 Nr. 1 → Kz 84, 7,60 EUR.
- Supabase Pte Ltd (Singapore), USD 25,00 → § 13b Abs. 2 Nr. 1 → Kz 84, 4,37 EUR. Invoice itself says reverse charge.
  Converted at the **BMF-Umsatzsteuer-Umrechnungskurs September 2026 (1 EUR = 1,0870 USD)**: 25,00 / 1,0870 = 23,00 EUR. Not the 22,84 EUR the bank booked (card rate 1,0946) — § 16 Abs. 6 UStG requires the published monthly average rate. The 0,16 EUR difference is a bookkeeping FX item, not a VAT item.
- Kz 84 = 40 + 23 = 63; Kz 85 = 7,60 + 4,37 = 11,97.

The reverse-charge VAT is fully deductible again in Kz 67 (19,00 + 7,60 + 4,37 = 30,97), so these three cost zero net VAT — but they still have to appear on both sides of the form.

**Vorsteuer (Kz 66) — 5,70 EUR**: only the Hetzner invoice (30,00 + 5,70 EUR, proper German invoice to the UG, supplier USt-IdNr. DE812871812).

## Decisions / things you need to sort out

1. **Anthropic and Cursor charged you German VAT that I did *not* claim as Vorsteuer (19,00 + 7,60 = 26,60 EUR).**
   Both invoices show only a foreign company and a German 19 % line, and your "Customer tax ID: DE000000000" is a placeholder, not a real USt-IdNr. Read that way, they treated you as a private consumer and billed under the OSS scheme — VAT charged that way is not *gesetzlich geschuldet* by them for a B2B supply, so § 15 Abs. 1 Nr. 1 UStG doesn't allow you to deduct it. The substantively correct treatment is the reverse charge I used above.
   **Net effect on Kz 83 is the same either way** (either 26,60 in Kz 66, or 26,60 in Kz 47/85 and again in Kz 67), so there's no money riding on this for Q3 — but the reverse-charge version is the defensible one, and the 26,60 EUR you actually paid them should be **reclaimed from Anthropic and Cursor** by giving them your USt-IdNr and asking for corrected invoices. If you'd rather book them as plain Vorsteuer (Kz 66 = 32,30, drop Kz 46/47/84/85 for those two, Kz 67 = 4,37), tell me and I'll redo the file — Kz 83 stays 89,30.
2. **IONOS domain (11,90 EUR) — I excluded the 1,90 EUR Vorsteuer.** The invoice is addressed to *Max Beispiel, Am Privatweg 3* and paid from your private card. § 14 Abs. 4 Nr. 1 UStG requires the invoice to name the actual recipient, so as it stands the UG can't deduct it. Ask IONOS to reissue it to Example Labs UG, Beispielweg 12 — then it goes into Q4 (or we correct Q3). The payment itself is just an Auslagenerstattung to you, no VAT effect.
3. **The missing USt-IdNr is the root cause of items 1 and 2.** Re-apply at the BZSt (online form, "Vergabe einer USt-IdNr"), or via ELSTER if you prefer. Until then suppliers will keep billing you as a consumer. Good news: you do *not* need a USt-IdNr for the reverse charge to apply, and you do *not* owe a Zusammenfassende Meldung — you only *receive* EU services, you don't supply any.
4. **No Stripe fee invoices in the folder.** The payouts (297,50 + 297,50) equal the gross charges exactly, i.e. no fees were deducted, which is unusual. If Stripe did invoice fees, check whether a monthly Stripe invoice exists — payment processing is VAT-exempt (§ 4 Nr. 8 UStG), so it wouldn't change the numbers, but it's worth confirming nothing is missing.
5. **Q3 filing deadline: Monday 12.10.2026** (10.10. is a Saturday → § 108 Abs. 3 AO). If you have a Dauerfristverlängerung it's 10.11.2026 — I couldn't see one in the folder, so assume 12.10. The 89,30 EUR is due the same day; with a SEPA mandate it's drawn automatically.

## The Finanzamt letter — Einspruch deadline

**Last day: Thursday 05.11.2026** (the Einspruch must be *received* by Finanzamt Berlin Beispiel by end of that day). But see the recommendation below — practically you should treat **Monday 02.11.2026** as your deadline.

How that date comes out:

- Posted 29.09.2026 (Poststempel). Since 01.01.2025 § 122 Abs. 2 Nr. 1 AO uses a **four-day** Bekanntgabefiktion (changed by the Postrechtsmodernisierungsgesetz — the old three-day rule no longer applies).
- 29.09. + 4 days = 03.10.2026, which is a Saturday *and* Tag der Deutschen Einheit, so § 108 Abs. 3 AO pushes Bekanntgabe to the next working day: **Monday 05.10.2026**.
- You found it in the letterbox on 01.10. — *earlier* than the fiction. That doesn't matter: § 122 Abs. 2 AO only displaces the fiction if the Bescheid arrived **later**. Earlier actual receipt does not shorten the deadline.
- One month, starting with the end of the Bekanntgabetag (§ 355 Abs. 1 AO, § 108 AO + § 187 Abs. 1, § 188 Abs. 2 BGB): 06.10. → ends with the end of **05.11.2026**, a Thursday, so no further shift.

**Recommendation:** file by **Monday 02.11.2026** anyway. If anyone later argues the three-day rule (02.10. Bekanntgabe → 02.11. Frist), you're still safe, and 02.11.2026 is also the payment due date on the Bescheid.

Two more things about that Bescheid:

- **You may not need an Einspruch at all for the 456 EUR.** The Festsetzung is *unter Vorbehalt der Nachprüfung* (§ 164 Abs. 1 AO). Simply filing the Q2 2026 UStVA replaces the estimate automatically (§ 168 AO) — and you said Q2 was essentially zero revenue, so the 456 EUR should collapse to roughly nothing. Fastest route: file Q2 before 02.11.2026.
- **The 25 EUR Verspätungszuschlag does not go away by itself.** It survives the corrected Q2 filing. If you want it dropped you need an Einspruch specifically against the Verspätungszuschlag within the deadline above (arguable: first year of filings, zero revenue, no tax shortfall).
- An Einspruch does **not** suspend payment. If you file one and want to hold off on the 481 EUR, you need a separate **Antrag auf Aussetzung der Vollziehung (§ 361 Abs. 2 AO)** — otherwise it's collectible on 02.11.2026.

---
Prepared from `invoices/`, `bank-q3-2026.csv`, `stripe-charges-q3-2026.csv`, `notes-from-max.md`, `post/finanzamt-brief-2026-09-29.txt`, `bmf-umsatzsteuer-umrechnungskurse-2026.txt`. No filing or submission was made. Not tax advice — for anything with real money on it (items 1–3), have your Steuerberater confirm.
