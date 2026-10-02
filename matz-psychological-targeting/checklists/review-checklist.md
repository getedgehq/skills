# Review Checklist

Review the completed decision brief, copy variants, and proposed recipient experience. Mark every applicable item **PASS** or **FAIL** and record evidence or a correction. Use **N/A** only with a reason, such as no latent inference being used. These are package review gates, informed by the method, rather than a published checklist from Matz.

A finished brief passes only when every applicable gate passes. An unresolved deployment requirement can be recorded as a clear blocker in an otherwise complete hypothesis brief; it cannot count as satisfied for deployment. See [references/method.md](../references/method.md) for M1 to M12 and [templates/output-template.md](../templates/output-template.md) for the deliverable fields.

## Purpose and agency

- [ ] **M1:** Recipient and sponsor goals are separate; assumed benefit is labeled and conflicts are visible. [S1] [S2]
- [ ] **M2:** Insight validity, influence mechanism, and recipient outcome are separate claims. [S1] [S2] [S6]
- [ ] **M3:** The design avoids exploiting inferred vulnerability, discrimination, and covert pressure over critical civic decisions; unsuitable uses receive a transparent alternative. [S1] [S4] [S6]

## Signals and interpretation

- [ ] **M4:** Every signal has provenance, collection purpose, permission status, and retention; public availability is not treated as consent. [S1] [S4]
- [ ] **M5:** The selected signal changes a useful decision; a sufficient direct preference is favored over unnecessary profiling. [S4] [S5]
- [ ] **M5:** Traits, current states, constraints, and volunteered preferences are distinguished; no score is treated as diagnosis or identity. [S4] [S5]
- [ ] **M6:** Inference evidence fits the population and context, uncertainty and drift are addressed, and unreliable cases have a generic fallback. [S6] [S7]
- [ ] **M6:** Conversational profiling, if proposed, has a visible purpose; pleasant interaction is not treated as permission. [S8] [S1]

## Fit and recipient experience

- [ ] **M7:** Product fit and message fit are distinguished, with a concrete mechanism for each adaptation. [S5]
- [ ] **M8:** A usable generic version exists; variants preserve substantive facts and identify what changes. [S6]
- [ ] **M8:** Creative validation checks the intended difference; multiple changed variables have explicit attribution limits. [S6]
- [ ] **M9:** Explanation, correction, personalization off, and alternative options are easy to find; data minimization is concrete. [S1] [S4]
- [ ] **M9:** Exploration remains optional; unfamiliar content is not assumed to produce empathy. [S1]

## Evaluation and decision

- [ ] **M10:** The plan specifies comparator, allocation, observation period, outcome, and uncertainty; no harmful mismatch is proposed. [S6]
- [ ] **M11:** Reach, clicks, action, and recipient welfare are distinct, with explicit denominators and timing. [S5] [S6]
- [ ] **M12:** The review considers uneven signal quality and adverse outcomes, including missing-signal recipients. [S7]
- [ ] **M12:** The disposition, owner, review date, and harm-based stopping conditions are explicit.
- [ ] **Evidence:** Methodological claims cite matching [S#] sources; invented scenarios and untested variants are labeled; no universal uplift or mind-reading claim appears. [S4] [S5] [S6]

## Common failure modes and fixes

| Failure | Fix |
| --- | --- |
| Prediction treated as permission | Record the permitted purpose separately; use volunteered preferences or the generic route when permission is missing. |
| Psychological score treated as identity | Narrow the claim to an estimate in context; expose correction and uncertainty. |
| Every Big Five trait added by default | Keep only a characteristic that changes a justified offer or framing decision. |
| Product mismatch hidden by persuasive copy | Improve or replace the offer before adapting the message. |
| Click lift called recipient benefit | Measure the actual decision and an outcome connected to the recipient goal. |
| One better-written variant called proof of fit | Improve the baseline and test audience-by-variant differences where feasible. |
| Historical proxy reused unchanged | Check the current population and signal meaning; fall back if reliability is unknown. |
| Alternatives hidden from a predicted segment | Restore access to all suitable options and explain recommendation logic. |
| Average success conceals segment harm | Inspect distribution and stop or narrow the intervention even if aggregate conversion rises. |
| Hypothesis reported as a result | Separate planned effects from observed findings and name missing evidence. |

**Review record:** [Decision, failed gates, corrections required, owner, date, and next review condition.]
