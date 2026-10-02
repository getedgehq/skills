# Worked examples

These are invented illustrations, not Jon Loomer case studies. All businesses, figures, drafts, and proposed actions are fictional. Improved briefs illustrate better decisions, not guaranteed improvements in advertising results. P1 to P8 refer to [references/method.md](../references/method.md).

## Illustration 1: A modest-budget apparel seller

### Inputs

A shop sells durable men's shirts, ships only within Germany, and has EUR 140 daily available for advertising. Its contribution per order before advertising is EUR 60. The initial purchase CPA planning range is EUR 35 to EUR 50. The pixel and server events pass a test checkout; duplicate-event diagnostics show no unresolved issue. The owner suspects only men aged 35 to 54 buy but has not run unrestricted purchase delivery.

### Weak first draft

Create five ad sets: two interests, two lookalikes, and a remarketing audience. Restrict all prospecting to men aged 35 to 54. Put EUR 28 daily into each ad set. Start a traffic test, choose the highest-CTR image, and move it into a purchase campaign. Exclude Audience Network because the owner dislikes it. Scale the lowest-CPA ad after three days.

### Improved result: A reviewable launch brief

**Outcome and goal:** Seek purchases within the EUR 60 contribution ceiling, with an initial EUR 45 CPA target as an explicit business assumption. Use purchase optimization; CTR supplies context rather than selecting the sales strategy. Do not claim that the target is attainable before results exist.

**Structure and funding:** Begin with one sales campaign and one ad set at the authorized EUR 140 daily budget. Estimated weekly purchase volume is `140 × 7 / 50` to `140 × 7 / 35`, or approximately 20 to 28 purchases. Five equally funded units would each have only about four to six weekly purchases. Consolidation improves the chance of an interpretable result but does not guarantee stability or learning-phase exit.

**Delivery:** Limit geography to the service area. Keep demographic eligibility broad because neither historical evidence nor an actual delivery problem supports the proposed age and gender exclusions. A gift buyer may differ from the wearer. Inspect available Audience Segments before adding separate remarketing. Keep placements broad unless an evidenced exception emerges. [S6]

**Creative:** Launch a workday durability demonstration and a gift-focused reassurance concept, with distinct visuals and messages. The first could say, "A dependable shirt for long workdays," supported by verified product features. The second could say, "A practical gift with clear sizing and easy exchanges," only if those terms are accurate. These are invented copy examples, not Loomer quotations. Adapt assets to the placements without treating every crop as a new concept.

**Evaluation:** Review two completed seven-day windows after initial delivery, subject to conversion lag. Judge the ad set's purchase economics and quality. Inspect click-based and other attribution credit, repeat purchases, and customer status. If the sample remains unstable, avoid claiming an audience or ad winner. Repair setup faults first; otherwise try a distinctly different concept when economics remain inadequate.

### Rules that changed the draft

P1 removed the unsupported formula. P3 exposed the funding dilution. P4 aligned delivery with purchases. P5 prevented imagined demographics from becoming eligibility limits. P6 replaced cosmetic selection with useful creative options. P7 and P8 replaced a three-day asset verdict with an aggregate, qualified review.

## Illustration 2: Cheap leads for a business training provider

### Inputs

A provider spends EUR 6,000 monthly on instant-form leads. Over three fully matured, equally measured cohorts, 2,000 leads cost EUR 3 each. CRM reconciliation confirms qualification and purchase outcomes. Follow-up speed and email delivery are comparable across groups. A particular age segment accounts for EUR 2,700, generates 1,350 leads, and produces 27 qualified leads. Other segments account for EUR 3,300, generate 650 leads, and produce 130 qualified leads. Closed-sale counts are 3 and 26 respectively. Each sale contributes EUR 800 before advertising. Downstream quality data is not currently returned to Meta.

### Weak first draft

The EUR 3 CPL proves the campaign works. Double spend. Alternatively, exclude everyone in the cheaper age segment because older people never buy. Add a new ad set for every age band and optimize each for form submissions.

### Improved result: A quality-led correction brief

**Business diagnosis:** The cheap-lead segment's qualification rate is `27 / 1,350 = 2%`; other segments qualify at `130 / 650 = 20%`. Their cost per qualified lead is EUR 100 and approximately EUR 25.38. Across the campaign, cost per qualified lead is `6,000 / 157`, approximately EUR 38.22. Cost per closed sale is `6,000 / 29`, approximately EUR 206.90. The overall acquisition economics may be acceptable, but 45% of spend is concentrated in a much weaker downstream group.

**Evidence boundary:** These figures are repeat cohort observations from this invented account, not a general claim about age. Three valuable customers came from the weaker group. Confirm matching and cohort maturity before taking the split as a reliable operational signal.

**Goal and signal:** Keep a consolidated lead campaign while assessing whether CRM qualification events can be sent reliably and quickly enough to support a quality-reflecting optimization goal. The 157 qualified events over three months are only about 12 per week. A deeper event is worth investigating, but do not assume it has sufficient frequency or arrives within the applicable attribution window. Improve form qualification and follow-up before assuming that a settings change alone fixes quality.

**Value-rule decision:** Both gates pass: the advertiser has downstream information absent from delivery, and a substantial spend concentration creates an observed business problem. If supported, propose a bounded bid reduction for the weaker group rather than a total age exclusion. Select the adjustment from this account's economics and auction response; do not import Loomer's historical percentages. Evaluate combined qualified-lead cost, closed-sale cost, contribution, and delivery volume after a matured comparison period. [S15]

**Creative and review:** Introduce a concept that states the training's practical prerequisites and intended use, instead of emphasizing free access alone. Keep messaging truthful and assess whether qualified demand rises. Do not double spend on CPL alone. Review mature cohorts and preserve the ability to reverse an intervention if overall economics worsen.

### Rules that changed the draft

P4 exposed the difference between submissions and customers. P2 required a material problem, rather than demographic prejudice. P3 avoided splitting already limited quality-event volume. P6 tightened the offer's relevance. P8 introduced qualification and closed-sale economics. The value-rule branch preserved valuable exceptions while using information the optimization signal lacked.

## Illustration 3: Strong reported ROAS with duplicate purchase events

### Weak first draft

Ads Manager reports 90 purchases and an attractive ROAS, while the store recorded 50 orders. Either scale immediately or accuse Meta of fabricated sales and switch to traffic campaigns.

### Improved result

Treat measurement as unresolved. Test whether the browser event and CRM event describe the same completed transaction, inspect matching identifiers and deduplication diagnostics, and check for purchase events on intermediate pages. Separate raw event fires from attributed results, then examine repeat conversions and attribution windows. Reconcile orders, revenue, and customer identities before making an efficiency claim. Report the diagnosis as pending until the duplicate-event hypothesis is verified. [S7]

### Rules that changed the draft

P2 prevented a premature platform diagnosis. P4 kept the desired purchase outcome. P8 required a meaningful measurement foundation before scaling.
