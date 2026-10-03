# UStVA Q3 2026 — Example Labs UG

Zeitraum: 01.07.–30.09.2026 · Steuernummer 37/123/45678 · Ist-Versteuerung, Regelbesteuerung, vierteljährlich
Abgabefrist: **Montag, 12.10.2026** (10.10. ist ein Samstag) — keine Dauerfristverlängerung erkennbar.
Nichts wurde übermittelt. Die Werte unten tippst du selbst in ELSTER ein.

## Die Kennzahlen

| Kz | Bedeutung | Betrag |
|----|-----------|--------|
| 81 | Steuerpflichtige Umsätze 19 % (Bemessungsgrundlage) | 500 |
| 46 | § 13b Abs. 1 UStG — sonstige Leistung aus anderem EU-Staat (BMG) | 100 |
| 47 | Steuer darauf | 19,00 |
| 84 | § 13b Abs. 2 Nr. 1 UStG — Leistung eines im Drittland ansässigen Unternehmers (BMG) | 62 |
| 85 | Steuer darauf | 11,78 |
| 66 | Vorsteuer aus Rechnungen anderer Unternehmer | 5,70 |
| 67 | Vorsteuer aus § 13b-Leistungen | 30,78 |
| 83 | **Verbleibende Umsatzsteuer-Vorauszahlung** | **89,30** |

Rechenweg: Umsatzsteuer 95,00 + 19,00 + 11,78 = 125,78 − Vorsteuer (5,70 + 30,78 = 36,48) = **89,30 EUR zu zahlen**.

## Wie ich auf die Umsätze komme (Kz 81)

Stripe-Charges Q3 ohne den Test: 119,00 + 178,50 + 297,50 = 595,00 EUR brutto → 500,00 netto, 95,00 USt.

Bei Ist-Versteuerung zählt der Zahlungseingang. Ich habe geprüft, ob es einen Unterschied macht, ob man auf das
Charge-Datum oder auf das Payout-Datum abstellt — macht es hier nicht: die Payouts im Q3 (297,50 am 31.07. +
297,50 am 31.08.) ergeben ebenfalls genau 595,00 EUR. Keine Abgrenzungsfrage.

Alle Kunden DE, B2C → normal 19 %, keine Besonderheiten, kein OSS.

Die 1,00 EUR Test-Charge vom 12.09. ist draußen: am selben Tag erstattet, Bank zeigt −1,00/+1,00, saldiert null.

## Wie ich auf die Vorsteuer komme

| Rechnung | Sitz | Netto | ausgew. USt | Behandlung |
|---|---|---|---|---|
| Hetzner R0025517744 | DE | 30,00 | 5,70 | normaler Vorsteuerabzug → Kz 66 |
| IONOS Domain | DE | 10,00 | 1,90 | **nicht abgezogen**, s. Punkt 2 |
| Anthropic Ireland | IE | 100,00 | 19,00 | Reverse Charge § 13b Abs. 1 → Kz 46/47 + Kz 67; die 19,00 **nicht** als Vorsteuer |
| Cursor / Anysphere | US | 40,00 | 7,60 | Reverse Charge § 13b Abs. 2 Nr. 1 → Kz 84/85 + Kz 67; die 7,60 **nicht** als Vorsteuer |
| Supabase | SG | USD 25,00 | 0,00 | Reverse Charge § 13b Abs. 2 Nr. 1 → Kz 84/85 + Kz 67 |

Supabase-Umrechnung: USD 25,00 ÷ 1,0870 (BMF-Durchschnittskurs September 2026, § 16 Abs. 6 UStG) = 22,99 EUR.
Nicht der Bankkurs 1,0946 (= 22,84 EUR) — für die Umsatzsteuer ist der BMF-Kurs maßgeblich. Die 0,16 EUR
Differenz ist nur ein Kursverlust in der Buchhaltung, umsatzsteuerlich irrelevant.

Kz 84 = 40,00 + 22,99 = 62,99 → als Bemessungsgrundlage auf volle Euro abgerundet: 62. Kz 85 = 19 % davon = 11,78.
Die Abrundung hat **keinen** Effekt auf die Zahllast, weil derselbe Betrag in Kz 67 wieder abgezogen wird.

## Was du entscheiden musst

### 1. Anthropic und Cursor haben fälschlich 19 % deutsche USt berechnet — 26,60 EUR hängen in der Luft

Beides sind sonstige Leistungen an einen Unternehmer, Leistungsort Deutschland (§ 3a Abs. 2 UStG), also schuldest
**du** die Steuer (§ 13b UStG), nicht der Lieferant. Passiert ist das, weil bei beiden als Customer tax ID die
Platzhalter-Nummer `DE000000000` steht — ohne gültige USt-IdNr. behandeln die dich als Privatkunden.

Ich habe es rechtlich korrekt gebucht: Reverse Charge deklariert (Kz 46/47 bzw. 84/85), Vorsteuer in gleicher Höhe
gezogen (Kz 67) → unterm Strich null. Die von dir an Anthropic/Cursor gezahlten 19,00 + 7,60 = **26,60 EUR sind
dagegen nicht als Vorsteuer abziehbar** (§ 15 Abs. 1 Nr. 1 UStG erlaubt nur gesetzlich geschuldete Steuer).

Du musst entscheiden:

- **Meine Empfehlung:** so lassen (89,30 EUR zahlen) und bei Anthropic und Cursor korrigierte Rechnungen ohne USt
  anfordern und die 26,60 EUR zurückfordern. Das ist eine zivilrechtliche Rückforderung, keine UStVA-Korrektur —
  die Voranmeldung muss später **nicht** geändert werden.
- **Die bequeme Variante** wäre, die 26,60 EUR einfach in Kz 66 zu stecken und § 13b weglassen; dann wären nur
  62,70 EUR fällig. Davon rate ich ab: in einer USt-Sonderprüfung wird die Vorsteuer gestrichen **und** die
  § 13b-Steuer nachgefordert, plus Zinsen. Doppelter Schaden für 26,60 EUR Vorteil.

### 2. Die IONOS-Rechnung läuft auf dich privat — 1,90 EUR Vorsteuer habe ich rausgelassen

Rechnungsempfänger ist „Max Beispiel, Am Privatweg 3". Für den Vorsteuerabzug muss der vollständige Name und die
Anschrift des **Leistungsempfängers** auf der Rechnung stehen, also der UG (§ 14 Abs. 4 Nr. 1 UStG). Dass du mit
deiner privaten Karte gezahlt hast, ist dabei egal — das ist nur eine Auslage, die dir die UG erstattet. Das
Problem ist allein der Rechnungsempfänger.

Zu tun: bei IONOS Rechnungsanschrift auf die UG ändern und für die Juli-Rechnung eine korrigierte anfordern. Die
1,90 EUR kannst du in dem Quartal ziehen, in dem die korrigierte Rechnung vorliegt — nicht rückwirkend in Q3.
Entscheide, ob du dir das für 1,90 EUR antun willst.

### 3. USt-IdNr. endlich beantragen

Du hast laufend EU-Eingangsleistungen (Anthropic, wahrscheinlich auch Stripe-Gebühren), dafür brauchst du eine
USt-IdNr. Beim BZSt online beantragen (nicht über den Fragebogen, der ist offenbar versandet), dann bei Anthropic,
Cursor, Supabase, Stripe im Billing-Profil eintragen. Danach kommen die Rechnungen automatisch ohne USt und
Punkt 1 wiederholt sich nicht. Hinweis: Reverse Charge gilt auch **ohne** USt-IdNr. — die Nummer ändert nichts an
deiner Steuerschuld, sie verhindert nur die falschen Rechnungen.

### 4. Fehlende Unterlage: Stripe-Gebührenabrechnung

Die Payouts sind brutto (297,50 berechnet → 297,50 ausgezahlt), es taucht nirgends eine Stripe-Gebühr auf. Falls
Stripe doch Gebühren abrechnet (üblich: ~1,5 % + 0,25 EUR, hier wären das grob 10 EUR im Quartal), sind das
Leistungen von Stripe Payments Europe (Irland) → ebenfalls Reverse Charge, Kz 46/47 + Kz 67, netto null Effekt auf
die Zahllast. Schau im Stripe-Dashboard unter Documents nach den Monatsabrechnungen Juli–September. Wenn welche
existieren, müssen Kz 46/47/67 um die Beträge hoch — die 89,30 EUR ändern sich dadurch nicht.

## Der Finanzamt-Brief: bis wann Einspruch?

**Letzter Tag: Donnerstag, 05.11.2026** (Eingang beim Finanzamt Berlin Beispiel bis 24:00 Uhr).

So kommt das Datum zustande:

1. Aufgabe zur Post: 29.09.2026 (Dienstag, Poststempel).
2. Bekanntgabefiktion § 122 Abs. 2 Nr. 1 AO: **am vierten Tag** nach Aufgabe zur Post. Achtung, das ist seit dem
   01.01.2025 so (Postrechtsmodernisierungsgesetz) — früher waren es drei Tage. Vierter Tag = 03.10.2026.
3. 03.10.2026 ist ein Samstag **und** Tag der Deutschen Einheit → die Fiktion verschiebt sich auf den nächsten
   Werktag (§ 108 Abs. 3 AO). 04.10. ist Sonntag → **Bekanntgabe = Montag, 05.10.2026**.
4. Einspruchsfrist ein Monat (§ 355 Abs. 1 AO), beginnt mit Ablauf des 05.10.2026, endet mit Ablauf des
   05.11.2026. Das ist ein Donnerstag, keine weitere Verschiebung.

Dass du den Brief schon am 01.10. im Briefkasten hattest, verkürzt die Frist **nicht**. Die Fiktion weicht nur
einem *späteren* tatsächlichen Zugang (§ 122 Abs. 2 Satz 3 AO), nie einem früheren.

Wenn du ganz safe sein willst: reiche bis **Montag, 02.11.2026** ein. Dann passt es auch, falls das Finanzamt
versehentlich noch mit der alten Drei-Tage-Regel rechnet.

### Wichtiger: du brauchst den Einspruch vermutlich gar nicht

Der Bescheid steht unter **Vorbehalt der Nachprüfung (§ 164 Abs. 1 AO)**. Das heißt: sobald du die Q2-Voranmeldung
abgibst, ersetzt sie die Schätzung automatisch — auch noch nach dem 05.11. Die geschätzten 2.400 EUR Umsatz
(456 EUR USt) fallen damit auf deine echten Zahlen, laut deinen Notizen nahe null.

Praktischer Weg:

- Q2-UStVA **vor dem 02.11.2026** abgeben (das ist der Fälligkeitstag der 481 EUR). Dann ist die Festsetzung
  korrigiert, bevor gezahlt werden muss.
- Schaffst du das nicht: entweder die 481 EUR zahlen und später erstatten lassen, oder zusätzlich einen Antrag auf
  **Aussetzung der Vollziehung (§ 361 AO)** stellen. Ein Einspruch allein stoppt die Zahlungspflicht nämlich nicht.
- Der **Verspätungszuschlag von 25,00 EUR** fällt nicht unter den Vorbehalt der Nachprüfung. Den bekommst du nur
  per Einspruch weg — und die Aussichten sind schlecht, weil die Q2-Anmeldung tatsächlich nicht abgegeben wurde
  (§ 152 AO). Für 25 EUR würde ich den Einspruch nur einlegen, wenn du ihn ohnehin schreibst.

Beachte außerdem: Q3 ist jetzt der zweite Zeitraum in Folge mit Auffälligkeiten. Nach zwei versäumten
Voranmeldungen setzt das Finanzamt gern den Voranmeldungszeitraum auf monatlich um. Pünktliche Abgabe am
12.10.2026 hilft.
