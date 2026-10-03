# ELSTER access for an agent

## Which login

| Method | Works for an agent? | Notes |
|---|---|---|
| **Zertifikatsdatei (.pfx) + password** | Yes, fully unattended | The only method an agent can run alone. Upload the file in the login page's file chooser, type the password. |
| ElsterSecure app | Only with a human scanning | Good for one-off read-only sessions through a remote browser view. Nothing persists but a session cookie. |
| Personalausweis + AusweisApp | No | The NFC reader is on the human's side. |

**Personal (IdNr) certificate vs Organisationszertifikat.**

- A personal certificate (issuer `CN=ElsterIdNrSoftCA`) is tied to the person's Steuer-ID. In the
  source run it was used to file every form of the founder's own company: the company's Steuernummer
  is entered as Ordnungskriterium per form, and Mein ELSTER accepted all of them. Its downside: the
  company's whole filing history sits in the founder's personal account, and the agent holds the
  founder's personal key.
- An **Organisationszertifikat** is registered on the company's Steuernummer. It is the cleaner choice
  for a company the agent will file for repeatedly: it scopes the agent to the company, it survives a
  change of managing director, and the Posteingang is the company's. Registration takes an
  activation letter by post, so start it early. *(verify the current registration flow on elster.de)*
- Either way, store which certificate files for which taxpayer in the working notes.

**Certificates expire after 3 years.** Read the expiry the moment you get the file:

```bash
# Password read from a secret store into the environment of THIS process only.
openssl pkcs12 -in cert.pfx -nokeys -passin env:PFX_PW -legacy | openssl x509 -noout -issuer -enddate
```

Older ELSTER .pfx files use 3DES/RC2, so OpenSSL 3 needs `-legacy`. Renew inside Mein ELSTER
**before** expiry; an expired certificate cannot be renewed and means re-registration with an
activation code by post. Renewal issues a new .pfx and a new password: generate the password, store
it in the secret store first, download, verify it opens, test a fresh logged-out login, and only then
retire the old file. Give the human their own copy of the new file and deliver the password
out-of-band.

## Handling the .pfx and its password

- File mode `0600`, directory `0700`, owned by the agent user, outside any git repo.
- Password in a secret manager or a root-only env file read by the one process that needs it. Never
  in argv (`ps` shows it), never echoed, never in a log, transcript, prompt or chat reply. If a human
  pastes the password into chat, move it to the secret store and tell them it is in the transcript.
- If a tool needs the PIN in a config file (myebilanz reads it from the `[cert]` section of its
  INI): write it with mode 0600 just before the run, remove it right after, `shred` any temporary
  certificate copy, and verify both. Keep a sanitized copy of the INI without credentials for the
  record.
- One browser identity per taxpayer, used by one run at a time (lock it). Concurrent sessions on
  one ELSTER account interfere.

## Session behaviour

- Each login re-uploads the certificate file through the file chooser; there is nothing to
  persist beyond the browser profile, and Mein ELSTER sessions time out after inactivity. Plan a
  run as login, do the work, log out.
- Downloads land in the browser's download folder, which an ephemeral automation profile can wipe
  when the run ends. Save every Übertragungsprotokoll and Bescheid PDF to durable storage inside
  the same run.
- Prefer an automation harness that can upload files (the .pfx) and read form control state. A
  vision-only agent clicking labels is how the source run ended up with a value in the wrong line.

## Before pressing Absenden

1. Start the form with **"Datenübernahme"** when ELSTER offers it. "Ohne Datenübernahme fortfahren"
   skips prefilled data such as the Finanzamt's own Vorauszahlungssoll. If it says "Es liegen keine
   Daten vor", note that.
2. Run **"Alles prüfen"** and read every Fehler and Hinweis. A Hinweis such as a missing W-IdNr is
   non-blocking; an error is not.
3. **Read back every field from the control state**, including the ones that must be empty
   (unentgeltliche Wertabgaben, § 15a, Sondervorauszahlung, § 14c). A total of 0,00 does not prove
   that lines without tax effect (exports, reverse charge bases) landed.
4. Radio buttons: confirm which option is *selected* (e.g. Ist- vs Sollversteuerung), not which
   label is nearest.
5. Do not type values into fields your spec did not name. "Invented a value in a §-designator
   field" was a real defect found in review.
6. Get the human's explicit approval of the final values, then submit.

## After submitting

- Record the **Transferticket**, timestamp and Ordnungskriterium.
- "Übermittelte Formulare" count: note it before, confirm exactly +1 after; drafts folder empty.
  This counter only covers forms sent from Mein ELSTER itself; submissions from other software
  (E-Bilanz via ERiC) appear only in that software's protocol.
- Save the Übertragungsprotokoll PDF. Screenshot the confirmation as a second record.

## Form quirks

- **Character set: ISO-8859-15 only.** German typographic quotes „ “, em dashes and some symbols
  are rejected with "Der angegebene Wert enthält ein oder mehrere ungültige Zeichen". Replace with
  ASCII quotes and hyphens before pasting. Umlauts are fine.
- "Sonstige Nachricht an das Finanzamt": subject field holds 99 characters; put the full subject in
  the body.
- Mein ELSTER has a dedicated Einspruch form with an option for Aussetzung der Vollziehung.
- Mein ELSTER does **not** offer the USt-IdNr application (that is the BZSt, see `vat.md`) and does
  **not** offer the E-Bilanz.
- KSt 1 and GewSt 1 A have no "berichtigte Erklärung" checkbox. Mark a corrected return in the
  free-text field (§ 150 Abs. 7 AO) and reference the original Transferticket. The UStVA does have
  Kz 10 (berichtigte Anmeldung).
- The annual USt form changes each year: line and Kz numbers below are examples. Re-read the
  current year's form, and be suspicious of any tool offering an "Anlage" that no longer exists
  for that year (it is on a stale template).

## E-Bilanz without accounting software

Mein ELSTER has no § 5b EStG form. A free route that worked: **myebilanz** (Windows; it ran under
Wine on Linux) with its bundled ERiC library.

- Input: an INI describing the company and report, and a CSV Saldenliste (account, balance, name;
  debit positive, credit negative). Map XBRL positions to real account numbers.
- Since financial years beginning after 31.12.2024, § 5b Abs. 1 EStG requires the **unverdichtete
  Kontennachweise** (report element `KS`) *(verify)*. The Saldenliste must come from a
  receipt-based journal, not be generated backwards from the final balance-sheet lines.
- Holding Finanzanlagen (shares in other companies)? Include the **Anlagenspiegel** (`BAL`);
  myebilanz warns the Finanzamt will otherwise ask for it.
- Split revenue into the mandatory VAT positions (e.g. `generalRateVAT`, `taxExemptUStG4_1a`)
  instead of the catch-all `unknownVAT` when the split is derivable.
- Taxonomy version per financial year *(verify; 6.8 was the regular one for 2025)*.
  `reportStatus=E` = final, `revisionStatus=E` = first submission (use `B` for a corrected one).
- Run validation, then a **Testsendung** (accepted with return code 0), then the Echtfall exactly
  once. The program blocks sending until its update check has run.
- The E-Bilanz must agree with the KSt/GewSt returns. If it changes the profit, file corrected
  KSt/GewSt and a § 153 AO notice the same day.
