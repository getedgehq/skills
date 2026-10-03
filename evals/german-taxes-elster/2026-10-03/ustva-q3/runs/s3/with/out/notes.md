# UStVA Q3 2026 — Example Labs UG — prepared 03.10.2026

**Nothing was submitted.** These are numbers for you to type into Mein ELSTER yourself.
Not tax advice.

**Due Monday 12.10.2026** — not the 10th: 10.10.2026 is a Saturday, so § 108 Abs. 3 AO moves the
filing *and* the payment to the next working day. (Assumes no Dauerfristverlängerung is on file —
see "Decide these"; if one is, Q3 is due 10.11.2026 instead.)

Basis taken from your notes: quarterly, Regelbesteuerung (Kleinunternehmer waived),
Ist-Versteuerung, no USt-IdNr. I could not verify any of that — only you can open ELSTER. Ist vs
Soll makes **no difference this quarter** (every Stripe charge was paid in the same quarter it was
raised), so that assumption carries no risk; the other two are worth two minutes in ELSTER before
you file.

## The numbers

| Kz | Meaning | Value |
|---|---|---|
| 81 | Domestic sales 19 % — net base | 500 |
| 46 | § 13b Abs. 1 — services from an EU supplier, base | 100 |
| 47 | …tax on it | 19.00 |
| 84 | § 13b Abs. 2 Nr. 1 — services from third-country suppliers, base | 63 |
| 85 | …tax on it | 11.97 |
| 66 | Vorsteuer from German invoices | 5.70 |
| 67 | Vorsteuer from § 13b services | 30.97 |
| 83 | **Zahllast** (ELSTER computes this) | **89.30** |

95.00 + 19.00 + 11.97 = 125.97 USt − 36.67 Vorsteuer = **89.30 EUR to pay.**

Sanity check you can repeat in your head: the whole § 13b block is Zahllast-neutral — Kz 67 (30.97)
is exactly Kz 47 + Kz 85 — so the Zahllast is just 95.00 output tax − 5.70 Hetzner Vorsteuer.
That also means a mistake in the § 13b bases costs no money, but still has to be corrected later
under § 153 AO, which is why finding them matters (see "Decide these", first item).

## Evidence

| Source | Date | Counterparty | Addressed to | Net / VAT / Gross | Treatment | Kz |
|---|---|---|---|---|---|---|
| stripe-charges | 09.07. | DE customer | UG | 100.00 / 19.00 / 119.00 | domestic 19 % | 81 |
| stripe-charges | 22.07. | DE customer | UG | 150.00 / 28.50 / 178.50 | domestic 19 % | 81 |
| stripe-charges | 05.08. | DE customer | UG | 250.00 / 47.50 / 297.50 | domestic 19 % | 81 |
| stripe-charges | 12.09. | founder's own card | — | 1.00 gross, refunded | own checkout test, not revenue | none |
| invoices/anthropic-2026-07 | 14.07. | Anthropic Ireland Ltd (IE) | UG, card 4417 | 100.00 / 19.00 billed / 119.00 | EU reverse charge; billed VAT **not** deductible | 46/47, 67 |
| invoices/hetzner-2026-08 | 01.08. | Hetzner Online GmbH (DE) | UG, bank debit | 30.00 / 5.70 / 35.70 | normal Vorsteuer | 66 |
| invoices/cursor-2026-08 | 03.08.¹ | Anysphere Inc. (US) | UG, card 4417 | 40.00 / 7.60 billed / 47.60 | third-country reverse charge; billed VAT **not** deductible | 84/85, 67 |
| invoices/supabase-2026-09 | 01.09. | Supabase Pte Ltd (SG) | UG, card 4417 | USD 25.00 = 23.00 EUR, reverse charge stated | third-country reverse charge | 84/85, 67 |
| invoices/ionos-domain-2026-07 | 20.07. | IONOS SE (DE) | **Max Beispiel privately**, card 9902 | 10.00 / 1.90 / 11.90 | not the UG's invoice → no Vorsteuer | none |

¹ `[FEHLT: Ausstellungsdatum]` — the Cursor invoice states only "Date due" and "Paid", both
03.08.2026. § 13b Abs. 2 timing keys on the invoice *issue* date, so Q3 is near-certain (it was
paid on the 3rd, so it existed) but rests on a date the document does not state. Grab the dated PDF
from the Cursor portal for the file.

Every company-card and direct-debit invoice matches a bank line to the cent; IONOS correctly does
not appear (private card); Stripe payouts 297.50 + 297.50 = 595.00 = the three real charges gross;
the 1 EUR test nets to zero. Note what this does *not* prove — see the first item below.

## Three judgement calls I made

1. **Anthropic and Cursor billed you "VAT Germany 19 %" against the placeholder VAT ID
   `DE000000000`.** Neither owes German VAT on these supplies — liability shifted to you under
   § 13b Abs. 5 UStG — so the tax they showed is not legally owed (§ 14c Abs. 2 UStG) and is
   therefore **not** deductible Vorsteuer, because § 15 Abs. 1 allows only legally owed tax. The
   reverse charge still applies. So the 19.00 + 7.60 = **26.60 EUR you actually paid is a sunk
   cost**, and it does not go in Kz 66. Anthropic Ireland → Kz 46/47; Cursor is Anysphere Inc. of
   San Francisco → Kz 84/85. Not interchangeable, so two near-identical invoices sit on different
   lines.
   I used the invoice **net** amounts (100.00, 40.00) as the § 13b bases. That is the standard
   treatment, but it is a position, not settled: one can argue the base is everything you spent
   (119.00 / 47.60) precisely because the 19 % was not legally owed. Zahllast is identical either
   way, so I took the net basis and left it at that.
2. **Supabase USD 25.00 converted at the BMF rate for September 2026** (1 EUR = 1.0870 USD) =
   23.00 EUR, per § 16 Abs. 6 UStG — *not* at your card's 1.0946. Kz 84 is then 40.00 + 23.00 =
   63, and 19 % of 63 is 11.97 exactly, so Kz 84 and Kz 85 are internally consistent and ELSTER's
   "Alles prüfen" will not raise a Hinweis. The 0.16 EUR gap to the 22.84 your card actually debited
   is FX spread — a bank cost, irrelevant to VAT.
3. **The 1 EUR test charge is excluded** — your own card, your own checkout, refunded the same day.
   Keep the charge ID and both card lines together in case anyone asks.

## Decide these

- **Are three subscription invoices missing from this quarter?** This is the one open item that
  could make the filing wrong. Every foreign vendor bills a monthly cycle — Anthropic "Jul 14 –
  Aug 14", Cursor "Aug 3 – Sep 3", Supabase "Sep 1 – Sep 30" — yet there is exactly one invoice and
  one debit each in a three-month quarter. So on the face of it the mid-August and mid-September
  Anthropic invoices, the September Cursor invoice, and the July/August Supabase invoices are
  absent. Either you cancelled after one cycle, or Kz 46/47 and Kz 84/85 are understated. The bank
  reconciliation above does *not* settle this: it only shows that the invoices I have match debits
  I have, not that those are all the debits. Check the full card statement for 4417 and the three
  vendor portals for Jul–Sep before you file. (Zahllast is unaffected either way — which is exactly
  why this is easy to miss and still a § 153 AO correction later.)
- **Get a USt-IdNr.** 26.60 EUR of dead VAT in this quarter, and it repeats every cycle you keep
  these subscriptions. It is issued by the **BZSt, not your Finanzamt**, free, on formulare-bfinv.de
  — it is *not* in Mein ELSTER, which is very likely why the earlier application went nowhere. Then
  put the number into Anthropic's, Cursor's and Supabase's billing profiles. Not retroactive.
- **Ask Anthropic and Cursor for corrected invoices** (reverse charge, no German VAT) and a refund
  of the 26.60. One email each.
- **The domain.** No Vorsteuer, but the gross 11.90 is still a deductible company expense: book it
  as Auslagenersatz to you with an Eigenbeleg (original invoice + your private card debit, signed by
  you and countersigned as managing director). Then move the IONOS account to the UG.
- **Dauerfristverlängerung** (vierteljährlich) is free for quarterly filers — no Sondervorauszahlung,
  that only applies to monthly filers. First check ELSTER → "Übermittelte Formulare" whether one is
  already on file (I assumed not; nothing in the folder shows either way, and it moves the Q3
  deadline from 12.10. to 10.11.). If not, filing it by 12.10. buys a month on every quarter from Q3
  on, and would have prevented the Q2 letter entirely.
- **Whether to disclose.** If you cannot resolve the missing-invoice question or confirm the
  Besteuerungsart before 12.10., file on time anyway and tick Ergänzende Angaben zur Steueranmeldung
  (**Kz 23** in the UStVA — *verify the number on the 2026 form*; the Kz 123 you may see referenced
  is the annual return) with something like: *"Die Bemessungsgrundlagen für Leistungen nach § 13b
  UStG werden noch abschließend geprüft; eine Berichtigung nach § 164 Abs. 2 AO erfolgt
  unverzüglich."* A disclosed gap is a correction; an undisclosed one can become a problem. If both
  items resolve clean, leave it empty.
- **Stripe fees are missing from the export.** Your payouts equal the gross charges exactly, which
  no Stripe account does. Pull the *balance transactions* export, not the payouts. It cannot change
  Kz 81 (under Ist-Versteuerung you declare the gross consideration the customer paid, not what
  landed in the bank), but Stripe Payments Europe is Irish, so any taxable fee component — Billing,
  Radar, Connect; the processing fee itself is exempt under § 4 Nr. 8 UStG — would add to Kz 46/47.
  Zahllast-neutral, but it is a declared base.
- **Q2 is not zero on the input side.** The Anthropic cycle runs mid-month, so there is very likely
  a June Anthropic invoice sitting in Q2 with reverse charge. No Q2 evidence is in this folder —
  pull Apr–Jun invoices and bank/Stripe data before filing it.

## The Finanzamt letter — your Einspruch runs out 05.11.2026

Schätzungsbescheid for USt-Vorauszahlung **Q2 2026**, dated 29.09.2026: 2.400 EUR estimated
turnover → 456.00 USt + 25.00 Verspätungszuschlag = **481.00 EUR due 02.11.2026**, under Vorbehalt
der Nachprüfung (§ 164 Abs. 1 AO).

The computation, because the obvious answer is wrong twice over:

| Step | |
|---|---|
| Posted (Poststempel) | Tue 29.09.2026 |
| + 4 days → Bekanntgabe fiction (§ 122 Abs. 2 Nr. 1 AO — **4** days for anything posted since 01.01.2025, not 3) | Sat 03.10.2026 — a Saturday *and* Tag der Deutschen Einheit |
| → next working day (§ 108 Abs. 3 AO) | **Mon 05.10.2026** = Bekanntgabe |
| + 1 month (§ 355 Abs. 1 AO) | **Thu 05.11.2026**, end of day |

**Deadline: Thursday 05.11.2026 — it must be *with* the Finanzamt by then, not just posted.**

You found it in the letterbox on 01.10. That does **not** shorten anything: the fiction is the
earliest possible Bekanntgabe and only *later* actual receipt counts, which is why you should keep
the envelope. On the old 3-day rule the answer would have been 02.11. — three days short.

Also note the trap in the dates: **payment falls due 02.11., three days before the appeal deadline.**
An Einspruch does not suspend payment (§ 361 Abs. 1 AO); that needs a separate Aussetzung der
Vollziehung.

### What I'd do: file Q2 *and* an Einspruch — not one or the other

The tempting move is to skip the Einspruch, because the Bescheid is under Vorbehalt der Nachprüfung
and filing the real Q2 UStVA should replace the estimate (§ 164 Abs. 2 / § 168 AO) even after
05.11. That is half true and I would not rely on it alone: a Steueranmeldung that *reduces* a
previously assessed amount only takes effect **with the Finanzamt's consent** (§ 168 Satz 2 AO).
Since Q2 was near zero, your real Q2 UStVA is exactly such a reduction — 456.00 down to roughly
nothing — so it is not self-executing, and it can sit unprocessed past 02.11. while
Säumniszuschläge accrue.

So, in order:

1. **File the real Q2 UStVA as soon as you have the Apr–Jun invoices**, ideally before 02.11.
2. **Also file an Einspruch zur Fristwahrung plus an AdV application by 05.11.** — belt and braces,
   in case the Finanzamt has not consented by then. "Begründung folgt" with a date is enough; a
   short Einspruch stating only what you can prove beats a detailed one that asserts more. As
   managing director write expressly *"namens und in Vertretung der Example Labs UG
   (haftungsbeschränkt) lege ich als Geschäftsführer Einspruch ein"* — the letter is addressed to
   you "z. Hd.", but the taxpayer is the UG.
3. **Ask expressly for the Verspätungszuschlag to be adjusted** (§ 152 Abs. 12 AO). It has to follow
   the changed assessment, but nobody will do it unprompted.
4. **If you simply don't pay by 02.11.:** Säumniszuschlag is 1 % per started month on the tax
   rounded down to a multiple of 50 → 4.50 EUR/month on the 450, nothing on the 25.00 surcharge,
   and bank transfers get a 3-day grace period. Small — but it also brings Mahnungen, and AdV stops
   it while it runs.

One caveat before you appeal: an Einspruch reopens the *whole* Q2 assessment (§ 367 Abs. 2 AO) and
the Finanzamt may change it against you after warning you first. With Q2 near zero that is close to
theoretical here, but if such a warning ever arrives, withdrawing is an option.

If you do pay, the Verwendungszweck must be `37/123/45678 USt 2VJ 2026` or the Kassenzeichen from
the letter — unreferenced money sits unassigned and generates Mahnungen anyway.

Last thing: the letter shows Steuernummer **37/123/45678**. Confirm that is the same number you
file your UStVA under. A mismatch between the number on the Bescheide and the number on your
submissions is a known cause of exactly this kind of estimate letter.

## Still missing

- Fragebogen zur steuerlichen Erfassung — confirms the Kleinunternehmer waiver, Ist-Versteuerung,
  and which Steuernummer carries the VAT registration.
- Full card statement for Visa 4417, Jul–Sep, plus the Anthropic / Cursor / Supabase portals — the
  possibly-missing subscription cycles.
- Whether a Dauerfristverlängerung is already on file (ELSTER → Übermittelte Formulare).
- Dated Cursor invoice PDF (issue date).
- Stripe balance-transaction export (fees).
- All Q2 2026 vendor invoices and bank/Stripe data.
- Eigenbeleg for the IONOS domain, signed.
