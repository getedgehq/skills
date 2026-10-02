# GEO-Audit deliverable template

Use this template with [the method](../references/method.md). Replace bracketed fields with findings or explicitly mark unknown, not measured, not applicable, or proposed. Do not leave placeholders in a finished audit. Field guidance is instructional and should be removed from the client deliverable. The structure and metric defaults are package conventions.

## 1. Audit identity and scope

- **Brand and domain:** [Canonical identity and aliases]. Guidance: distinguish product, company, and parent brand if relevant.
- **Prepared for / audit owner:** [Team and accountable role]. Guidance: identify the person who can coordinate content, technical, and external work.
- **Date and evidence period:** [Audit date; observation start and end]. Guidance: a retrieval date is not necessarily a source publication date.
- **Audit type:** [Live / supplied-export / desk]. Guidance: say which visibility evidence is actually available.
- **Business decision:** [Specific decision the findings inform]. Guidance: describe a concrete next action rather than a generic goal of more visibility.
- **Audience and context:** [Persona, need, buying constraints, category]. Guidance: include exclusions that prevent unsuitable recommendations.
- **Market and language:** [Geography and language]. Guidance: keep distinct market cohorts separate.
- **AI surfaces and modes:** [Platforms, interfaces, models if exposed, search settings]. Guidance: never infer a hidden model version.
- **Competitor set:** [Brands and selection rationale]. Guidance: include meaningful substitutes and declare the denominator set.
- **Constraints and unknowns:** [Access, budget, permissions, missing evidence]. Guidance: show how these narrow conclusions.

## 2. Decision summary

**Observed current state:** [Two or three evidence-backed sentences]. Guidance: distinguish mention, citation, category fit, factual quality, and recommendation.

**Recommended next actions:** [Up to three actions with finding IDs]. Guidance: lead with the most consequential facts and relevant gaps.

**Confidence and limits:** [What can and cannot be concluded]. Guidance: label suspected causes and do not guarantee outcomes.

## 3. Brand fact ledger

| Fact ID | Claim/category | Evidence URL or supplied record | Verified date | Owner | Conflicts or limitations |
| --- | --- | --- | --- | --- | --- |
| [B1] | [Current accurate statement] | [Supporting evidence] | [Date] | [Role] | [Disagreement / none] |

Guidance: define current category, capabilities, customers, geography, identity, and limitations before writing optimized copy. Distinguish authorized product facts from external claims.

## 4. Top-Prompts map

| Prompt ID | Exact prompt | Intent and context | Persona | Stage | Locale/language | Brand tag | Evidence origin | Validation status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [P1] | [Customer question] | [Need plus constraints] | [Audience] | [Awareness / Consideration / Decision] | [Market] | [Audited-brand / competitor-led / non-branded] | [Source] | [Validated / provisional] |

**Sampling rationale:** [Why these questions and this sample size]. Guidance: cover the journey; explain any departure from the published suggestion of about 50 prompts over 30 days.

**Cohort version:** [Version and change log]. Guidance: preserve a stable group for comparisons and separate added questions.

## 5. Answer evidence log

| Run ID | Prompt ID/text reference | Timestamp | Surface/interface/model | Mode, locale, session | Response evidence | Brand/category/recommendation | Competitors | Citation URLs and supported claims | Facts/sentiment | Run status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [R1] | [P1] | [Date/time/zone] | [Known settings] | [Known context] | [Durable record] | [Separate observations] | [Brands] | [Verified URLs] | [Assessment] | [Valid / failed / partial] |

Guidance: preserve full responses or a durable evidence reference. Record unavailable settings as unknown. Separate owned-domain citations from third-party coverage about the brand. Log failures even when excluded from a metric.

## 6. Baseline and competitive results

| Metric | Definition and cohort | Numerator | Denominator | Result | Exclusions and limits |
| --- | --- | --- | --- | --- | --- |
| [Mention rate / Visibility Score] | [Tool definition or disclosed package default] | [Count] | [Count] | [% / not measured] | [Failed runs, branded exclusions, date range] |
| [Owned-content citation rate] | [Verified owned-domain citations per eligible response] | [Count] | [Count] | [% / not measured] | [Third-party citations separate] |
| [Prompt Coverage] | [Prompts with qualifying mention / observed prompts] | [Count] | [Count] | [% / not measured] | [Repeat sensitivity] |
| [Visibility Share] | [Share within declared brand set] | [Count] | [Count] | [% / N/A] | [Not market share] |

**Quality:** [Category fit, factual accuracy, sentiment, recommendation and answer position]. Guidance: state the rubric and sample; do not let positive language conceal incorrect facts.

**Platform comparison:** [Separate cohort results]. Guidance: show comparable settings or explain why comparison is limited. Desk audits use not measured rather than zero.

## 7. Findings and diagnosis

| Finding ID | Observed failure | Answer/page evidence IDs | Hypothesis | Confidence and reason | Business consequence |
| --- | --- | --- | --- | --- | --- |
| [F1] | [Absence / misclassification / incorrect fact / weak source presence] | [R1, B1, URL] | [Possible mechanism] | [High / medium / low, justified] | [Affected buyer decision] |

Guidance: evidence strength determines confidence. A suspected cause stays a hypothesis unless independently demonstrated.

**Technical review:** [Accessibility, indexing, robots policy, redirects, HTML, links, sitemaps, material performance]. Guidance: record tested pages and unknowns. Public HTTP access does not prove every crawler can retrieve the content.

## 8. Content architecture and revisions

| Brief ID | Target prompts | Existing/new page | Cluster and links | Answer passage | Evidence and constraints | Author/reviewer | Update trigger |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [C1] | [P1, P2] | [URL / proposed asset] | [Related pages] | [Direct usable answer] | [Dated proof and limits] | [Role] | [Change that requires review] |

Guidance: include the weak existing passage where useful and the proposed replacement. Prefer source-worthy facts to promotional adjectives. Mark unapproved product facts and avoid inventing measurements.

## 9. Ecosystem signal matrix

| Platform/source | Audience relevance | Observed citation role | Current description/conflict | Proposed correction/distribution | Owner | Independent/sponsored/owned | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [Listing, partner, review, editorial or community URL] | [Reason] | [Evidence / not observed] | [Facts] | [Bounded action] | [Role] | [Evidence type] | [Proposed / completed / awaiting response] |

Guidance: choose channels based on the actual audience and source observations. Do not describe paid coverage as independent corroboration or claim outreach was sent when it was only drafted.

## 10. Prioritized action plan

| Action ID | Priority and rationale | Finding IDs | Concrete change | Owner | Due date/window | Effort/dependencies | Verification | Authorization/status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [A1] | [P0 / P1 / P2 plus reason] | [F1] | [Specific asset or process] | [Role] | [Date or proposed window] | [Capacity and prerequisites] | [Observable acceptance criterion] | [Draft / authorized / complete] |

Guidance: method section 8 defines package priorities. Separate controllable implementation acceptance from future answer outcomes. Proposed owners and dates must be identified as proposed if not agreed.

## 11. Monitoring and commercial relevance

- **Stable cohort and settings:** [What will remain comparable]. Guidance: show prompt versions and platform/mode settings.
- **Repeat schedule:** [Agreed or proposed cadence]. Guidance: weekly performance review and monthly prompt refinement follow published guidance when practical.
- **Change log:** [Release, profile updates, model/interface changes]. Guidance: retain plausible alternative explanations.
- **Success criteria:** [Directional metric and accuracy targets]. Guidance: targets are objectives, not guaranteed forecasts.
- **Lead evidence:** [Referral data and customer-reported origin]. Guidance: offer an appropriate discovery-origin question; distinguish association from causation.
- **Next decision:** [What the next review will determine]. Guidance: specify when to keep, revise, or stop an experiment.

## 12. Evidence and method notes

**Audit evidence register:** [URLs, supplied artifacts, dates, permissions and gaps]. Guidance: cite actual inspected material for brand findings.

**Method attribution:** [Lili Frankus and duwerk public method; relevant S# references]. Guidance: use [the source register](../references/sources.md) for methodology, never as evidence for an audited brand's performance.

**Operational conventions:** [Metric definitions, rubrics, priorities, sample choices]. Guidance: state that these are package or tool conventions rather than an undisclosed agency formula.

**Review result:** [Pass/fail, reviewer, unresolved items]. Guidance: complete [the checklist](../checklists/review-checklist.md) before delivery.
