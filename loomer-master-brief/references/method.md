Credit: This package interprets Jon Loomer's publicly published Meta advertising approach, credited to Jon Loomer Digital and The Pubcast with Jon Loomer. It is independently written and is not affiliated with or endorsed by Jon Loomer.

# Method and decision rules

## Provenance and boundaries

The LinkedIn announcements lead to two complementary resources: a thematic consolidation of 24 reviewed briefs and a separately authored explanation of eight recurring principles. The eight principles below retain the latter article's order, with paraphrased names. The public Master Brief is a fixed July 2026 snapshot, while the paid member resource is maintained separately. This package covers the public approach, not undisclosed membership content or a guaranteed current Meta interface. [S1] [S2] [S3] [S8]

Citations identify source-based claims. Decision records, worksheets, numerical planning formulas, and review conditions are this package's implementation aids. They operationalize the approach without claiming that Loomer prescribed these exact deliverables. Examples are fictional. No published account result should be treated as a forecast.

Read sections as needed: P1 to P8 establish the reasoning; subsequent sections handle goals, measurement, exceptions, creative, quality, and review.

## P1. Reject universal campaign formulas

A complicated branded setup does not explain success by itself. Effective ads still need a persuasive offer, an appropriate product, and a functioning conversion experience. Interest tests, isolated testing campaigns, and intricate remarketing structures can distract from those fundamentals while fragmenting funding. Treat success screenshots as observations, not proof of a causal mechanism. [S9]

Decision rule: reject a recipe whose rationale stops at someone else's success. Ask what is different about this business, what problem the setup addresses, and whether a simpler design can pursue the same outcome.

## P2. Make each change answer an evidenced problem

Every extra campaign, ad set, targeting limit, manual bid intervention, or disabled feature needs a specific reason. Assumed customer demographics and blanket beliefs about platforms are weak evidence. Separate knowing that a segment is less valuable from proving that delivery spends materially on it. [S10]

Implementation aid: record `problem | evidence | proposed mechanism | simpler alternative | expected business improvement | review condition`. If the problem is unknown, investigate before treating a setting as the solution. A necessary business constraint can justify a change independently of historical performance.

## P3. Consolidate the budget where possible

Use the fewest funded units compatible with the business. A primary conversion goal can often begin with one campaign and one ad set. Separate goals or genuinely different business requirements may need more. Each separation reduces the volume available to learn and evaluate. Simplicity is a starting preference rather than a ban on exceptions. [S5]

Loomer discusses roughly 50 optimized actions weekly as a learning and stability guideline. It is not a guarantee of success or a requirement to abandon profitable low-volume purchases. [S3]

Implementation aid: estimate weekly events as `daily budget × 7 / expected cost per optimized event`. Use a realistic range, then repeat the estimate for each proposed funded unit. Do not reverse-engineer an affordable budget by inventing a low CPA.

## P4. Align the requested action with business value

Delivery pursues the action defined by the performance goal. Cheap clicks, video views, or engagement can satisfy that request without creating customers. Purchase optimization better aligns delivery with sales, although purchase count and purchase value are different goals. This is an explanation of optimization incentives, not a promise of perfect delivery. [S11]

Decision rule: identify the nearest reliable signal to the actual desired outcome. If the business wants purchases, do not assume a traffic or checkout-action campaign will cheaply train future buyers. State the rationale for any proxy goal and how downstream value will be checked. [S18]

## P5. Reduce unnecessary attempts to control delivery

Audience suggestions, automated budget allocation, and creative enhancements change the advertiser's role. Rejecting automation reflexively can sacrifice useful distribution and creative combinations. Evaluate specific failures rather than assuming manual control is superior. [S12]

Broad purchase targeting also permits gift buyers and other customers outside the imagined demographic to convert. Use enforceable eligibility controls where required, including legal age limits; do not turn a customer persona into a hard eligibility rule. [S6]

Decision rule: distinguish hard controls, suggestions, exclusions, and reporting dimensions in the current account. A setting that suggests an audience is not proof that separate ad sets reach separate groups.

## P6. Invest in persuasive, meaningfully different ads

Variation should change something substantive: format, visual treatment, message, persona, problem, or persuasion approach. Minor color or wording changes do not provide the same diversity. Quantity without quality does not ensure performance. [S17]

Begin with a feasible set, evaluate, and add a genuinely different phase when results warrant it. Meta may give most delivery to only a few ads. The advertiser's job is to supply useful options, not force equal spend or extract one permanently winning headline. [S13]

Implementation aid: build a creative matrix with `persona | pain | product solution | desired feeling | credible proof | offer | format | CTA`. Use truthful proof and offer terms. The matrix is a drafting aid, not a claim that persona membership controls delivery.

## P7. Judge the combined result before reallocating assets

Evaluate the ad set in aggregate, or the campaign when campaign budget allocation is the relevant decision unit. Low-cost results from a lightly funded component do not prove that its costs will remain low at greater spend. Breakdown averages can mislead because delivery changes as opportunities and costs change. [S3] [S5]

Decision rule: if the combined business result is acceptable, uneven asset spend alone is not a problem. If aggregate results are unacceptable, diagnose the cause before forcing budget to a preferred asset. Breakdowns inform diagnosis; they are not automatic instructions to remove ages, ads, or placements.

## P8. Require meaningful evidence

Meaning depends on volume and stability, relevance of the metric, quality of outcomes, and likely incremental effect. Sparse purchase counts can reverse with one day's results. High CTR is not a sales verdict, and high attributed remarketing ROAS does not establish additional sales caused by advertising. [S14]

Decision rule: distinguish an observation, a hypothesis, and a supported decision. State whether the conclusion changes under a plausible small change in results. Learning-phase thresholds do not replace this assessment. Use suitable reporting views and downstream business records before scaling or changing goals.

## Goal and economics branch

For purchase-led businesses, evaluate the viability of purchase optimization before inventing a lead funnel. If purchase count produces insufficient value, consider purchase-value optimization when supported by the account and reliable event values. Leads can be appropriate, but they need a quality and economics model. Low volume alone does not prove that a proxy event is better. [S3] [S4]

Implementation calculations:

- Purchase CPA: spend divided by verified purchases, using a stated attribution definition.
- ROAS: attributed purchase revenue divided by spend; disclose that revenue is not profit.
- Cost per qualified lead: spend divided by qualified leads from the same matured cohort.
- Observed revenue per lead: cohort revenue divided by cohort leads; disclose refunds and timing.
- Contribution per lead: close rate multiplied by contribution per closed sale, before acquisition spend.

Use contribution and operating costs to set a business ceiling, then reserve a margin for uncertainty. These formulas are package aids. Avoid presenting estimated lifetime value as observed cash revenue.

## Tracking and attribution branch

Pair browser tracking with appropriate Conversions API events, including CRM or offline outcomes when relevant. Tracking must cover the action that matters and give Meta usable matching information. Verify implementation rather than assuming that the presence of a pixel proves completeness. [S5]

Test the journey from ad landing through completed action. A purchase event must not fire merely because someone reached an intermediate page or clicked a button. Investigate duplicate browser/server reports, repeated confirmation-page visits, and incorrect event triggers. Events Manager's raw event totals are not Ads Manager's attributed purchase totals. [S7]

Record the attribution setting that shaped delivery. Use available attribution breakdown and comparison views to distinguish click, view, and engagement credit and shorter versus longer click windows. Inspect first versus subsequent conversions without assuming that first-conversion reporting is a deduplicated list of unique new customers. Reconcile customer identity and acquisition status in business records. Conversions may concern products other than the advertised one. Different tools can count different windows or interactions without either fabricating transactions. [S7]

Loomer's snapshot favors a longer click window for purchases and a shorter one for low-deliberation free offers. Verify account options and the buying cycle. Attribution settings influence optimization, not just the presentation of a report. [S4]

Incremental attribution reports are not equivalent to independently proven causal lift. Older material discusses their analytical potential; later material expresses reservations about optimizing with that setting. Keep reporting interpretation and delivery-model selection separate. [S14] [S4]

## Targeting, value rules, and remarketing exceptions

Before a value rule, require both gates:

1. The advertiser has relevant information Meta does not currently use, such as downstream lead quality or cohort lifetime value.
2. Current delivery creates a material problem, demonstrated by meaningful data, not merely a less valuable segment's existence.

If either gate fails, do not add the rule. Bid adjustments deliberately alter auction economics and can increase costs. Prefer proportionate bid reductions over total exclusion where the less valuable group still contains valuable customers. No age group is universally low quality. Recheck business outcomes after the intervention. [S15]

Earlier content proposed a strict age limit for a documented low-quality-lead concentration. Later public advice prefers value rules where appropriate. Preserve the earlier observation as evidence of the optimization failure mode, not as the current default fix. [S16] [S15]

For remarketing, first define and inspect available Audience Segments. Broad delivery already reaches engaged people and customers; dedicated remarketing can duplicate that activity. Segment definitions affect reporting completeness, not whether the broad campaign can reach those people. Avoid importing a fixed warm-audience percentage from another account. [S5]

A rare snapshot exception supports moving buyers from a low-ticket offer to a high-ticket upgrade using restricted custom audiences, an Awareness reach goal, a frequency cap, and sales-oriented messaging. Use it only for that distinct function and if currently supported. Existing-customer exclusions likewise need a business reason and sufficiently complete audiences. [S4]

Business eligibility, legal restrictions, service geography, necessary separate objectives, and concrete creative accuracy constraints can justify departures. A documented misleading enhancement is different from merely disliking automation. Respect those requirements rather than demanding that a business tolerate an unacceptable output to accumulate performance data.

## Creative testing and troubleshooting

Testing is optional and must fit the budget. Where available, use the native creative testing capability in the working ad set instead of defaulting to separate testing campaigns. Balanced test delivery costs efficiency and needs enough conversions to support a conclusion. After a test, allow normal delivery before assessing the aggregate result. Learn reusable themes rather than copying one isolated asset combination. [S13]

If results are poor, trace the failure in order: attention, conversion experience, then event reporting. Inspect whether the ad message attracts action, whether the page continues that promise and supports completion, and whether completed events are reported correctly. Consider insufficient traffic volume before diagnosing weak attention. [S18]

A high frequency or a short performance dip does not itself prove fatigue. Initial warm-audience delivery, audience restrictions, random variation, and website or event problems can explain changes. More distinctive ads are a stronger default response than structural tinkering after setup faults are excluded. [S4] [S13]

Loomer allows limited delivery experiments after several unsuccessful creative rounds, including pushing an underused ad where that feature exists or stopping a dominant poor performer. These are qualified diagnostic options, not blanket optimization rules. Evaluate their effect on the combined business result. [S13]

## Review and next decision

Use a reporting interval compatible with event volume, attribution lag, and the sales cycle. A seven-day view after an initial observation period can help; it does not magically establish significance. Do not force decisions from a few purchases or compare immature leads with older cohorts. [S14]

Implementation decision states:

- **Hold:** aggregate economics and quality are acceptable; no evidenced problem needs intervention.
- **Repair:** event or conversion-path defects make the performance verdict unreliable.
- **Revise creative:** setup is sound but persuasive concepts or offers are not delivering adequate results.
- **Test an exception:** a specific problem and plausible mechanism justify a bounded intervention.
- **Scale:** meaningful business outcomes leave room for higher costs as spend grows.

For every state, specify an owner, the evidence needed next, and a review date or maturity condition. If evidence remains insufficient, report the uncertainty and the cheapest useful next observation. These operating states are package scaffolding, not additional Loomer principles.
