# Evaluation status

Status: measured pilot, inconclusive. The result did **not** clear this repository's bar (a 95 %
confidence interval on the judge delta that excludes zero); three paired samples cannot. It is
reported here as measured, not as a supported benefit.

On 2026-10-03, `skill-eval-loop` ran blind paired samples with Claude Code headless
(`claude-opus-5`, subscription, on a Linux host). The skill arm had `german-taxes-elster` installed
in the project and loaded it through normal discovery; the baseline arm had no skill. The same
model judged each pair blind, with the brief's objective verifier weighted first.

## Task 1: `german-tax-ustva-q3` (scored)

A founder asks for the Q3 2026 Umsatzsteuer-Voranmeldung of a small UG from a folder of messy
inputs (bank CSV, Stripe export, five vendor invoices, notes) and for the Einspruch deadline on an
estimated Q2 assessment. All data is fictional. The verifier checks the Kennzahlen and the deadline:
Kz 81 500; Anthropic Ireland billed on `DE000000000` with "VAT Germany 19 %" → Kz 46/47 on the
net, not Kz 66; Cursor (US) and Supabase (Singapore, USD at the BMF monthly rate) → Kz 84/85;
Kz 67 = reverse-charge tax; Kz 66 5.70 from the German invoice only (a domain invoice addressed to
the founder privately gives no Vorsteuer); Einspruch deadline 05.11.2026 under the 4-day
Bekanntgabe rule with the weekend and holiday roll.

| Sample | Skill verifier | Baseline verifier | Blind verdict |
|---|---|---|---|
| s1 | pass | **fail**: third-country reverse charge in Kz 52/53, which the 2026 form does not have (it is Kz 84/85) | skill |
| s2 | pass | pass | tie |
| s3 | pass | pass | skill |

- Wins 2, ties 1, losses 0. Verifier passes: skill 3/3, baseline 2/3.
- Skill loaded and read in 3 of 3 skill-arm runs (no forced load needed).
- Tool errors: 0 in both arms.

What the baseline already did well: `claude-opus-5` without the skill recognised the
`DE000000000` trap and the § 14c consequence, excluded the private-invoice VAT, and used the 4-day
Bekanntgabe rule in all three samples. The measurable margin came from form-specific knowledge (the
current Kennzahl for third-country reverse charge) and from operational advice the judge credited
(Dauerfristverlängerung, Auslagenersatz with Eigenbeleg, § 152 Abs. 12 AO, USt-IdNr via the BZSt).

## Task 2: `german-tax-ug-annual` (headroom filter, excluded)

A batch of UG annual and personal questions (GewSt for a corporation without the 24,500 EUR
Freibetrag, KSt-only Verlustrücktrag, § 7g with a planned closure, Verböserung risk on an
Einspruch, Fünftelregelung no longer applied by employers since 2025, Antragsveranlagung deadline).
Two baseline-only pilot runs both passed every objective check, so the task has no headroom for this
model and was dropped before any paired run, as the eval spec requires. Disclosed here so the filter
is visible.

## Reading this result

The general law is largely known to a frontier model. Where this skill should matter is the
operational layer the source run paid for: ELSTER certificate handling, form-year Kennzahlen,
read-back and submission verification, E-Bilanz via ERiC, and the human-approval gate. Those are not
yet covered by a measured task. A confirmatory run needs fresh samples on more task families with
proven baseline headroom.

After the run, an adversarial review corrected wording and citations in the references (KSt
rounding, § 11 GewStG citation, § 37 Abs. 3 EStG time limit, § 14c wording, filing duty for the
self-employed, the § 355 Abs. 1 Satz 2 AO exception for own Steueranmeldungen, and annual-return
completeness). No change touches what the scored task measures; the measured version is the
first commit of this package.

Reproducible artifacts (briefs, fixtures, verifiers, transcripts, outputs, verdicts) are in
`evals/german-taxes-elster/2026-10-03/`.
