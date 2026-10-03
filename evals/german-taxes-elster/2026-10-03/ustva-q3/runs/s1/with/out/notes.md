# UStVA Q3 2026 — Example Labs UG (haftungsbeschränkt)

Steuernummer 37/123/45678, Finanzamt Berlin Beispiel. Quarterly filer, Ist-Versteuerung,
Regelbesteuerung (Kleinunternehmer waived), **no USt-IdNr**.

Prepared 03.10.2026. **Nothing submitted.** You type these into Mein ELSTER yourself.
Not tax advice — the *(verify)* items below should be checked against the current form/law.

---

## 1. The numbers for ELSTER

| Kz | Line / meaning | Value |
|---|---|---|
| **81** | Steuerpflichtige Umsätze 19 % — Bemessungsgrundlage | **500** |
| **46** | Leistungen eines im anderen EU-Mitgliedstaat ansässigen Unternehmers (§ 13b Abs. 1 UStG) — Bemessungsgrundlage | **100** |
| **47** | …darauf entfallende Steuer | **19,00** |
| **84** | Andere Leistungen eines im Ausland ansässigen Unternehmers (§ 13b Abs. 2 Nr. 1 UStG) — Bemessungsgrundlage | **63** |
| **85** | …darauf entfallende Steuer | **11,97** |
| **66** | Vorsteuerbeträge aus Rechnungen von anderen Unternehmern | **5,70** |
| **67** | Vorsteuerbeträge aus Leistungen i. S. d. § 13b UStG | **30,97** |
| **83** | Verbleibende Umsatzsteuer (**computed by ELSTER** — check it matches) | **89,30** |

All other Kz stay empty. Bemessungsgrundlagen (81, 46, 84) are entered in **full euros,
rounded down**; Steuerbeträge with cents.

Check: 95,00 (on Kz 81) + 19,00 + 11,97 − 5,70 − 30,97 = **89,30 EUR to pay**.

**Deadline: Monday 12.10.2026.** The statutory date is 10.10., but that is a Saturday, so it
rolls to the next working day (§ 108 Abs. 3 AO). Payment is due the same day.
Verwendungszweck: `37/123/45678 USt 3VJ 2026`.

---

## 2. Evidence table

### Output side (revenue)

| Source | Date | Customer | Gross | Net | VAT | Treatment | Kz |
|---|---|---|---|---|---|---|---|
| stripe-charges, Pro annual | 09.07.2026 | DE, B2C | 119,00 | 100,00 | 19,00 | domestic 19 % | 81 |
| stripe-charges, Pro x1.5 seats | 22.07.2026 | DE, B2C | 178,50 | 150,00 | 28,50 | domestic 19 % | 81 |
| stripe-charges, Team | 05.08.2026 | DE, B2C | 297,50 | 250,00 | 47,50 | domestic 19 % | 81 |
| stripe-charges, checkout test | 12.09.2026 | founder's own card | 1,00 | — | — | **not revenue**, refunded same day | none |
| | | **Total** | **595,00** | **500,00** | **95,00** | | |

Reconciliation: Stripe payouts 31.07. (297,50) + 31.08. (297,50) = 595,00 on the bank
statement = exactly the three succeeded charges. The 1,00 test charge appears as +1,00/−1,00
on 12.09. and nets to zero. **Reconciles to the cent.**

All four customers are `DE`, so no OSS / EU-threshold question arises.

The 09.07. charge is an *annual* plan. Under Ist-Versteuerung the whole payment is taxable on
receipt (§ 13 Abs. 1 Nr. 1 Buchst. b UStG) — it is **not** spread over 12 months. Correct as is.

### Input side (purchases)

| Invoice | Date | Supplier seat | Addressed to | Net | Invoiced VAT | Treatment | Kz |
|---|---|---|---|---|---|---|---|
| anthropic-2026-07 (9F3A21C7-0007) | 14.07.2026 | **Ireland** (IE3668997OH) | the UG, Tax ID `DE000000000` | 100,00 EUR | 19,00 shown as "VAT Germany 19 %" | § 13b Abs. 1 UStG; invoiced VAT **not deductible** | 46 / 47, deducted in 67 |
| cursor-2026-08 (EF12A9-0003) | 03.08.2026 | **US** (Anysphere Inc.) | the UG, Tax ID `DE000000000` | 40,00 EUR | 7,60 shown as "VAT Germany 19 %" | § 13b Abs. 2 Nr. 1 UStG; invoiced VAT **not deductible** | 84 / 85, deducted in 67 |
| supabase-2026-09 (SB-77310) | 01.09.2026 | **Singapore** | the UG | USD 25,00 → 23,00 EUR | 0,00, "reverse charge" | § 13b Abs. 2 Nr. 1 UStG | 84 / 85, deducted in 67 |
| hetzner-2026-08 (R0025517744) | 01.08.2026 | **Germany** (DE812871812) | the UG | 30,00 EUR | 5,70 | normal Vorsteuer, invoice in hand | **66** |
| ionos-domain-2026-07 (100338812345) | 20.07.2026 | Germany | **Max Beispiel privately** | 10,00 EUR | 1,90 | **no Vorsteuer for the UG** — see §4(d) | **none** |

Kz 84 = 40,00 + 23,00 = 63,00 → **63**. Kz 85 = 19 % of 63,00 = **11,97**.
Kz 67 = 19,00 + 7,60 + 4,37 = **30,97** (the UG has full Vorsteuerabzug: all output is taxable 19 %).

Supabase currency conversion: § 16 Abs. 6 UStG requires the **BMF monthly average rate for the
month the service was performed**, not the card rate. Service period 01.–30.09.2026 → September
rate 1 EUR = 1,0870 USD → 25,00 / 1,0870 = **23,00 EUR** (22,9991). Your bank was debited
**22,84 EUR** (card rate 1,0946) — the 0,16 EUR difference is a currency gain in the books, not a
VAT correction. Do not use 22,84 in the form.

Bank reconciliation: every debit on bank-q3-2026.csv has a matching invoice and every invoice has
a matching debit. The IONOS 11,90 is correctly absent from the company account (private card
9902). Nothing unexplained, nothing `[FEHLT]`.

Timing all lands in Q3: Anthropic service ends 14.08. (EU reverse charge arises at the end of the
period the service was performed), Cursor invoiced 03.08., Supabase invoiced 01.09., Hetzner
invoice and service August *(verify § 13b Abs. 1/2 timing if you ever have a period straddling a
quarter end)*.

### Why the Anthropic and Cursor VAT is not in Kz 66

Both billed you with the placeholder customer VAT ID `DE000000000`, i.e. as a consumer. You are a
business customer regardless: place of supply is with you (§ 3a Abs. 2 UStG) and the tax liability
shifts to you (§ 13b Abs. 5 UStG) whether or not you gave a VAT ID. The German VAT they printed is
therefore **not legally owed** (§ 14c Abs. 1 UStG, unrichtiger Steuerausweis), and § 15 Abs. 1
UStG only allows deduction of legally owed tax. So: reverse charge on the net, deducted in Kz 67;
the 19,00 + 7,60 = **26,60 EUR you actually paid is a dead cost** unless the vendors re-issue.

Note Supabase, on the same facts, got it right ("reverse charge"). The difference is not the law,
it is the vendor's billing setup.

---

## 3. Einspruch deadline on the Q2 Schätzungsbescheid (post/finanzamt-brief-2026-09-29.txt)

**You can still file an Einspruch until the end of Thursday, 05.11.2026.**

The computation, step by step:

| Step | | Date |
|---|---|---|
| 1 | Bescheid dated / Poststempel | Tue **29.09.2026** |
| 2 | + 4 days = Bekanntgabe fiction (§ 122 Abs. 2 Nr. 1 AO) | Sat 03.10.2026 |
| 3 | 03.10. is a Saturday *and* Tag der Deutschen Einheit → next working day (§ 108 Abs. 3 AO) | Mon **05.10.2026** = Bekanntgabe |
| 4 | + 1 month, same-numbered day (§ 355 Abs. 1 AO, § 188 Abs. 2 BGB) | Thu **05.11.2026** |
| 5 | 05.11.2026 is a Thursday, a working day → no further roll | **deadline 05.11.2026, end of day** |

Two things that look like they should change this answer but don't:

- **You found it in the mailbox on 01.10.** — that is *earlier* than the fiction, which does not
  shorten the deadline. Only *later* actual receipt counts (and then the Finanzamt bears the
  burden of proof). So 05.10. stands. **Keep the envelope** anyway.
- **The 4-day rule, not 3.** For letters posted from 01.01.2025 Bekanntgabe is the **4th** day, not
  the 3rd. The old rule would have given you 02.11. — you would have thought the deadline was
  three days earlier than it is.

Watch the ordering: **payment of 481,00 EUR is due 02.11.2026, three days *before* the Einspruch
deadline.** An Einspruch does **not** suspend payment (§ 361 Abs. 1 AO).

---

## 4. Decisions for you

**(a) Dauerfristverlängerung — decide this week, it is the cheapest thing on the list.**
For a *quarterly* filer it is free (no Sondervorauszahlung; that only applies to monthly filers).
Filed before 12.10.2026 it moves Q3 to 10.11.2026 and every future quarter by one month, which is
exactly the kind of slip that produced the Q2 letter. In ELSTER pick
"Dauerfristverlängerung (vierteljährlich)", **not** the monthly/Sondervorauszahlung form.
→ Do you want it? If yes, file it before you file Q3.

**(b) How to deal with the Q2 Bescheid.** The estimate (2.400 EUR revenue → 456,00 USt, Vorsteuer
0,00) stands **under Vorbehalt der Nachprüfung** (§ 164 Abs. 1 AO). That means:
- The clean fix is simply to **file the real Q2 UStVA** — it replaces the estimate, and under
  § 164 Abs. 2 AO it can still do so *after* 05.11. The Einspruch is not strictly required for the
  tax itself.
- But the **25,00 EUR Verspätungszuschlag** is a separate discretionary decision (§ 152 Abs. 1 AO);
  attacking that is cleanest inside the one-month window. If the underlying tax changes, the
  surcharge must be adjusted (§ 152 Abs. 12 AO) — ask for that **explicitly**, it is not automatic.
- And payment is due 02.11. If Q2 is not filed and assessed by then, consider **Einspruch +
  Aussetzung der Vollziehung** (§ 361 Abs. 2 AO) to stop the clock. Säumniszuschlag otherwise is
  1 % per started month on 456 rounded down to 450 = **4,50 EUR/month** (§ 240 AO) — small, so this
  is a convenience call, not an emergency.
- One caution: an Einspruch reopens the **whole** Q2 assessment (§ 367 Abs. 2 AO, Verböserung
  possible after a warning). For Q2 that looks harmless, but it is the reason not to file an
  Einspruch reflexively when filing the return does the job.
→ My recommendation: **file the real Q2 UStVA before 02.11.2026** and, in the same message, ask for
the Verspätungszuschlag to be adjusted under § 152 Abs. 12 AO. Add an Einspruch by 05.11. only if
Q2 will not be ready in time. Tell me which route and I will prepare it — Q2 is **not** included
in the numbers above, those are Q3 only.

**(c) Get a USt-IdNr. This quarter alone the `DE000000000` billing cost you 26,60 EUR** and it
recurs every month you keep those subscriptions. It is issued by the **BZSt, not the Finanzamt**,
free, via the form on formulare-bfinv.de — it is *not* in Mein ELSTER, which is probably why
"applied once, never came" (ticking the box in the Fragebogen does not guarantee one arrives).
If the form rejects you, the message matters: "Daten stimmen nicht überein" means the stored
name/address differ, "nicht als Unternehmer registriert" means that Steuernummer carries no VAT
registration. Don't keep guessing the company name — every attempt is logged. It is **not
retroactive**: once you have it, enter it in the Anthropic, Cursor and Supabase billing profiles.
→ Want me to prepare the BZSt application?

**(d) The IONOS domain (11,90 EUR) needs an Eigenbeleg from you.** The invoice is addressed to
*Max Beispiel, Am Privatweg 3* and paid from your private card, so the UG gets **no Vorsteuer**
(the 1,90 is deliberately not in Kz 66 — this does not change the Q3 numbers). The cost is still
fully deductible for the UG as an operating expense, but booked **gross at 11,90** either as
Auslagenersatz (the UG owes you, reimburse it) or as an Einlage if you never take the money back.
Paperwork needed: the IONOS invoice + your private card debit + a signed Eigenbeleg.
→ Reimburse yourself or treat it as Einlage? Also: move the domain to the company's IONOS account
so this stops recurring.

**(e) Ask Anthropic and Cursor for corrected invoices** (net, "reverse charge", your USt-IdNr once
you have it) and a refund of the 26,60 EUR. Worth one support ticket each; don't count on it.

---

## 5. What I did not do

- **Nothing was submitted or transmitted.** No ELSTER login was used.
- **Q2 2026 is not prepared** — you asked for Q3 only. Note that Q2 is probably not a plain zero
  even with ~no revenue: if there were reverse-charge SaaS purchases in Q2, Kz 46/47 and 84/85 must
  be declared (they net to zero against Kz 67, but "left out for simplicity" becomes a § 153 AO
  correction later). Send me the Q2 invoices and bank rows and I will do it.
- **No September revenue appears in the data** (last real charge 05.08.2026). If you invoiced
  anything in September that is missing from stripe-charges-q3-2026.csv, the Kz 81 figure changes —
  please confirm the export covers the whole quarter.
- Kz/line numbers are the 2026 UStVA form as I understand it. When you are in ELSTER, run
  **"Alles prüfen"**, read every Hinweis, and check that Kz 83 comes out as 89,30. If any Kz number
  on screen differs from this table, trust the form's label text (EU § 13b Abs. 1 vs. other foreign
  suppliers § 13b Abs. 2) over my Kz number and tell me.
