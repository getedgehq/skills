# UStVA Q3 2026 — Example Labs UG (haftungsbeschränkt), St.-Nr. 37/123/45678

Prepared 03.10.2026. **Nothing submitted** — you type these into Mein ELSTER yourself.
Quarterly filer, Ist-Versteuerung, Regelbesteuerung, no USt-IdNr.
**Filing + payment deadline: Mon 12.10.2026** (10.10. is a Saturday, § 108 Abs. 3 AO).
Not tax advice; the § 13b calls below are the ones worth a second opinion if you want one.

## What goes in the form

| Kz | Meaning | Value |
|---|---|---|
| 81 | Steuerpflichtige Umsätze 19 % (Bemessungsgrundlage) | 500 |
| 46 | Sonstige Leistungen EU-Unternehmer, § 13b Abs. 1 (Basis) | 100 |
| 47 | …darauf Steuer | 19,00 |
| 84 | Andere Leistungen ausländischer Unternehmer, § 13b Abs. 2 Nr. 1 (Basis) | 62 |
| 85 | …darauf Steuer | 11,97 |
| 66 | Vorsteuer aus deutschen Rechnungen | 5,70 |
| 67 | Vorsteuer aus § 13b-Leistungen | 30,97 |
| 83 | **Verbleibende Vorauszahlung (zu zahlen)** | **89,30** |

USt 95,00 + 19,00 + 11,97 = 125,97 − Vorsteuer 36,67 = **89,30 EUR**.
ELSTER computes 47, 85 and 83 itself — compare against these before you send.

## Evidence table

| Source | Date | Counterparty | Addressed to | Net / VAT / Gross | Treatment | Kz | Conf. |
|---|---|---|---|---|---|---|---|
| stripe-charges | 09.07. | DE consumer | UG | 100,00 / 19,00 / 119,00 | domestic 19 % | 81 | high |
| stripe-charges | 22.07. | DE consumer | UG | 150,00 / 28,50 / 178,50 | domestic 19 % | 81 | high |
| stripe-charges | 05.08. | DE consumer | UG | 250,00 / 47,50 / 297,50 | domestic 19 % | 81 | high |
| stripe-charges | 12.09. | founder's own card | — | 1,00 refunded | test charge, not revenue | — | high |
| anthropic-2026-07 | 14.07. | Anthropic Ireland | UG | 100,00 / 19,00 wrongly invoiced / 119,00 | § 13b Abs. 1, invoiced VAT **not** Vorsteuer | 46/47 → 67 | high |
| cursor-2026-08 | 03.08. | Anysphere Inc. (US) | UG | 40,00 / 7,60 wrongly invoiced / 47,60 | § 13b Abs. 2 Nr. 1, same | 84/85 → 67 | high |
| supabase-2026-09 | 01.09. | Supabase Pte (SG) | UG | USD 25,00, reverse charge stated | § 13b Abs. 2 Nr. 1 | 84/85 → 67 | high |
| hetzner-2026-08 | 01.08. | Hetzner Online GmbH | UG | 30,00 / 5,70 / 35,70 | proper German invoice | 66 | high |
| ionos-domain-2026-07 | 20.07. | IONOS SE | **Max privately** | 10,00 / 1,90 / 11,90 | no Vorsteuer for the UG | — | high |

Reconciliation: Stripe payouts 31.07. + 31.08. = 595,00 EUR = the three succeeded charges exactly.
So charge date and payout date both land in Q3 — Ist-Versteuerung gives the same answer either way,
no timing judgement needed.

## Four things I did that you should know about

**1. The DE000000000 trap cost you 26,60 EUR.** Anthropic and Cursor both billed "VAT Germany 19 %"
against the placeholder VAT ID `DE000000000`, i.e. they treated the UG as a consumer. That VAT is
not legally owed (§ 14c Abs. 1 UStG), so it is **not** deductible Vorsteuer — I did not put the
19,00 and 7,60 into Kz 66. The reverse charge applies anyway (§ 13b Abs. 5): I declared the net
amounts in Kz 46/84 and deducted the same tax in Kz 67, which is a wash. The 19,00 + 7,60 = 26,60
you actually paid is a pure loss unless the vendors re-issue and refund. Supabase, on the same card,
got it right.

**2. The domain is not Vorsteuer.** The IONOS invoice is addressed to "Max Beispiel, Am Privatweg 3"
and paid from your private card 9902. The UG cannot deduct the 1,90 (§ 14 Abs. 4 Nr. 1 UStG) — "it's
for the company obviously" doesn't carry it; the invoice has to name the company. It is still a
deductible business expense: book the **gross 11,90** as Auslagenersatz to you, with an Eigenbeleg
plus the card debit attached.

**3. Supabase converted at the BMF rate, not your bank's.** § 16 Abs. 6 UStG requires the published
BMF monthly average, not the rate your bank happened to use. September 2026: 1 EUR = 1,0870 USD, so
USD 25,00 = 23,00 EUR, not the 22,84 on the statement. Difference in tax: 3 cents. I used the BMF
rate because that is the rule, but keep the 16-cent gap in mind when you reconcile the bank.

**4. The 1 EUR test charge is out.** Charged and refunded on 12.09., your own card, so it is not
revenue and not a deduction. Keep the charge ID and the two bank lines together in case it's asked
about.

## Decisions for you

1. **Get a USt-IdNr — this is the one with real money in it.** You said you applied and nothing came.
   It is issued by the **BZSt**, not your Finanzamt, and it is not in Mein ELSTER — use the online
   form on formulare-bfinv.de. Then put it into the Anthropic, Cursor and Supabase billing profiles.
   At the current burn that stops roughly 100 EUR a year of non-deductible VAT, and it stops the
   § 13b bookkeeping from being ambiguous. Not retroactive.
2. **Ask Anthropic and Cursor to re-issue the July/August invoices** without German VAT and refund
   the 19,00 + 7,60. Worth one support ticket each; both vendors do this routinely.
3. **Re-address the IONOS domain to the UG** before the next renewal, or it repeats every year.
4. **Dauerfristverlängerung for 2027.** Free for quarterly filers (the 1/11 Sondervorauszahlung is
   monthly filers only) and it buys you a month on every quarter — which is exactly the mistake that
   produced the Q2 letter. Too late to help 2026; file it before 10.04.2027. Pick the form named
   "Dauerfristverlängerung (vierteljährlich)".
5. **Missing: the Stripe fee invoice.** The payouts equal the gross charges to the cent, so no fees
   were withheld from the balance, and there is no Stripe debit in the bank CSV either. If Stripe
   Payments Europe (Ireland) invoiced fees for Q3 separately, they belong in Kz 46/47 with the
   deduction in Kz 67. That would not change the 89,30 you pay (tax and deduction cancel), but it
   would change the bases. Send me the Stripe *balance transaction* export or the fee invoice and
   I'll update Kz 46/47. If you file before that, say so in "Ergänzende Angaben".
6. **Pay 89,30 by 12.10.2026** with Verwendungszweck `37/123/45678 USt 3VJ 2026`.

## The Finanzamt letter (Q2 2026 Schätzung) — your deadline

**Einspruch is possible until the end of Thursday 05.11.2026.**

How that date comes out:

- Aufgabe zur Post: Tue **29.09.2026** (Bescheid date and postmark agree).
- Bekanntgabe = **4th** day after posting (§ 122 Abs. 2 Nr. 1 AO — since 01.01.2025; it was 3 days
  before). 4th day = Sat **03.10.2026**, which is both a Saturday *and* Tag der Deutschen Einheit,
  so it rolls to the next working day: Mon **05.10.2026** (§ 108 Abs. 3 AO).
- One month from Bekanntgabe (§ 355 Abs. 1 AO), same-numbered day: Thu **05.11.2026**, a Berlin
  working day, so no further roll.

Two traps here. You found the letter in the mailbox on 01.10. — that does **not** shorten the
deadline; the fiction only moves if the letter arrived *later* than the 4th day. And on the old
3-day rule you would have computed 02.11.2026 and filed three days early against the wrong date.
Keep the envelope with the postmark.

**But an Einspruch is probably the wrong tool.** The Festsetzung is under Vorbehalt der Nachprüfung
(§ 164 Abs. 1 AO), so simply **filing the real Q2 UStVA replaces the estimate** (§ 168 AO) — no
Einspruch needed, and no deadline pressure on the 456,00 EUR itself. You say Q2 was near-zero
revenue, so that estimate (2.400 EUR Umsatz, 456,00 EUR USt, 0 Vorsteuer) should collapse to
roughly nothing, and you get Q2 Vorsteuer that the estimate gave you none of.

So the plan I'd follow:

- File the **Q2 UStVA** before 05.11.2026 — ideally in the next two weeks. That kills the 456,00.
- When you do, ask in writing for the **Verspätungszuschlag of 25,00 EUR to be adjusted**: if the
  underlying assessment changes, the surcharge has to be re-examined (§ 152 Abs. 12 AO). It won't
  fall away automatically — you have to ask.
- Use the 05.11. date only as a backstop: if Q2 isn't ready by, say, 29.10., file a one-paragraph
  "Einspruch zur Fristwahrung, Begründung folgt" to keep the case open. That is cheap insurance.
- **An Einspruch does not stop the payment.** The 481,00 EUR is due **02.11.2026** either way
  (§ 361 Abs. 1 AO). If Q2 is filed and processed before then, the debit should mostly disappear; if
  it's close, either pay and get it refunded, or apply for Aussetzung der Vollziehung (§ 361 Abs. 2
  AO) alongside. Säumniszuschlag is 1 % per started month on the amount rounded down to 50 EUR, so
  letting 481,00 run late costs ~4,50 EUR a month.

One check before you file Q2: the letter shows St.-Nr. 37/123/45678. Confirm that is the same number
your ELSTER submissions go out under — a mismatch between the number on Bescheide and the number on
filings is a known way to generate exactly this kind of Schätzungsbescheid.
