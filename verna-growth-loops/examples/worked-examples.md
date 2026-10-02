# Worked examples

Both scenarios are invented illustrations. Every company, dataset, forecast, owner, and threshold is fictional. These examples demonstrate the method, not results from Verna's work. Source citations identify the public principles being applied.

## Illustration 1: a collaborative research product

### Scenario

FieldNotes helps research teams collect and review findings. The team wants to grow activated accounts and has proposed a conference sponsorship, referral rewards, and more reminder emails. Its planning dataset contains 100 newly activated teams per month. Actual exposure and recipient conversion events have not yet been instrumented.

### Weak first draft

> Our growth loop is ads -> signup -> login -> subscription -> more ads. We will sponsor a conference, reward every invitation, and send daily login reminders. Our 100 teams each invite ten people, so the product will acquire 1,000 customers monthly. Marketing owns invitations; product owns usage. Free teams are excluded from retention because revenue is the goal.

This draft mistakes recipient exposure for acquisition, offers no cash recovery model for its paid arrow, and ignores whether new participants can repeat the behavior. It treats logins as value, measures only paid accounts, and divides ownership into separate targets. [S2] [S3] [S5]

### Improved growth-model brief

**Decision:** Prioritize recipient-to-team activation before expanding referral incentives. This is a hypothesis supported by a proposed model, not a measured causal diagnosis.

**Context and value:** The core customer is a research team. The candidate value event is two teammates reviewing a shared findings page and recording a research decision. Setup requires a workspace, initial value requires collaborative review, and activation requires the first repeat review cycle. A proposed habit measure is meaningful team review activity in three of four weeks, subject to validation against natural usage. Measure at team level and include engaged free teams. [S5]

**Acquisition mechanism:** An activated team creates a useful findings page -> shares with an external collaborator -> the collaborator experiences useful research -> a genuinely new team forms and reaches activation -> that team can create and share findings pages. The closing input is an activated, share-capable team, not an email address or signup. This adapts the product-driven sharing pattern Verna describes. [S1]

**Evidence:** The 100 starting activated teams are observed in the fictional dataset. Exposure volume and all downstream conversion rates below are assumptions. They must exclude repeat recipients, existing users, and collaborators joining an existing account.

| Transition | Illustrative assumption | Output |
| --- | --- | --- |
| Starting teams to qualified external exposures | 2 shared pages x 5 distinct new recipients per team, with no overlap assumed | 1,000 recipients |
| Qualified recipient to new account | 10% | 100 new accounts |
| New account to activated, share-capable team | 20% | 20 next-cycle teams |

**Quantitative implication:** `100 x 10 x 0.10 x 0.20 = 20` next-cycle teams. R is 0.20. A seeded generation alone contracts at that rate; it is not self-sustaining expansion. Continuing shares from retained older teams could add output, but require a separate measured contribution. Assume a four-week cycle for planning and label that duration unverified. [S2]

**Sensitivity and constraint:** If recipient activation increased from 20% to 40% with other terms unchanged, output would rise to 40 teams. If exposures increased by 25%, output would rise to 25 teams. This comparison motivates investigating activation, but does not prove that doubling it is feasible or less costly.

**Investment:** Instrument recipient cohorts, interview failed team creators, and pilot a simpler collaborative setup. Classify setup improvements as a lubricant. Classify the conference as a possible seeding boost; reconsider it after a credible downstream mechanism exists. Avoid referral pressure that might damage collaboration. [S3]

**Ownership and learning:** The product growth lead owns activated teams from qualified recipients; engineering, research, and analytics support. Observe a six-week intake cohort through eight weeks of follow-up. The illustrative pilot success condition is a recipient-to-activated-team rate above the 2% assumed baseline with no decline in meaningful review activity. If exposure or account identity cannot be measured reliably, stop the comparison and repair instrumentation. The threshold is a planning choice, not an expert rule.

**Review trigger:** Revisit the mechanism if the qualified new-recipient pool shrinks, team habit declines, or added prompts reduce meaningful review. [S6]

### Rules that changed the result

- Loop closure replaces an invitation count with eligible next-cycle teams. [S2]
- Value activity, team-level measurement, and free cohorts replace paid-user logins. [S5]
- Investment classification connects each initiative to the diagnosed engine. [S3]
- One owner and explicit assumptions prevent departmental target inflation. [S2] [S4]

## Illustration 2: a paid acquisition engine with delayed cash recovery

### Scenario

LedgerTrail sells expense-management software to small firms. Acquisition comes from paid search, activation from connecting a ledger and reconciling expenses, and monetization from a sales-assisted annual contract. The team proposes doubling ads because booked revenue looks strong.

### Weak first draft

> Our LTV:CAC ratio is 5:1, so paid growth compounds automatically. Spend EUR 20,000, acquire 100 accounts, and book EUR 50,000 revenue. Reinvest the EUR 50,000 immediately into ads. Raise prices 30% to accelerate growth. The growth marketer owns the whole plan; product can continue its roadmap independently.

This draft treats contracted revenue as spendable cash, assumes immediate recovery, and ignores the effects of pricing on activation and retention. Its owner has no stated capacity to repair product onboarding. [S3] [S4] [S6]

### Improved growth-model brief

**Decision:** Hold the spend increase. Verify cash recovery and repair ledger-connection activation before changing price or acquisition volume.

**Lever and motion:** Acquisition is marketing-led, activation and retained value are product-led, and monetization is sales-led. These motions support one growth system and require shared ownership of constraints. [S4]

**Paid loop:** Available capital -> qualified paid-search prospects -> activated paying accounts -> collected contribution cash -> approved reinvestment -> capital for the next acquisition cycle. The closing transition is cash available for new acquisition after required costs and reserves. [S3]

**Illustrative evidence:** An eight-week acquisition cohort used EUR 20,000 spend to produce 100 paying accounts. CAC is EUR 200 per paying account. In the fictional records, 40 paid accounts completed the first reconciliation habit cycle. This activation gap must remain visible even though all 100 purchased. Contracted first-year revenue is EUR 50,000; cash collection is staged.

| Time from spend | Cumulative collected revenue | Cumulative service cash costs | Contribution cash |
| --- | --- | --- | --- |
| Day 30 | EUR 10,000 | EUR 4,000 | EUR 6,000 |
| Day 90 | EUR 30,000 | EUR 12,000 | EUR 18,000 |
| Day 150 | EUR 50,000 | EUR 20,000 | EUR 30,000 |

**Cash model:** If 80% of contribution cash is reinvestable, the available amounts are EUR 4,800, EUR 14,400, and EUR 24,000. Under these fictional assumptions, contribution payback occurs between days 90 and 150, while enough approved acquisition cash to replace the original EUR 20,000 is first demonstrated at day 150. The observation points do not reveal the exact crossing date. Booked revenue does not establish either timing.

**Constraint and tradeoff:** With only EUR 20,000 initial acquisition capital and no replenishment, there is no basis for funding another equal cycle immediately. Increasing price might improve recovered cash, but could lower conversion or retained usage. Improving reconciliation setup may protect both renewal and acquisition economics. Compare these effects before changing price. [S3]

**Investment and ownership:** Finance and analytics validate collection, contribution, and cash-floor assumptions. A growth product manager leads a ledger-connection pilot with engineering capacity assigned. The marketer owns qualified demand and works against the shared outcome of activated paying accounts and recoverable acquisition cash. [S2] [S4]

**Learning and decision:** Track each account through connection, first reconciliation, repeat reconciliation, collection, and renewal. For illustration, review activation after six weeks and cash recovery at day 150. Increase acquisition spend only if activation improves, the cash floor is maintained, and the reinvestment model survives a 20% CAC increase. Stop expansion if collections lag or paid accounts fail to reach value. Continue observing renewal rather than claiming six weeks establishes annual retention.

**Review trigger:** Reassess when CAC rises, collection slows, or reconciliation habit weakens. A defensible paid loop still faces deterioration. [S6]

### Rules that changed the result

- Payback and collected contribution cash replace an LTV ratio as proof of immediate fuel. [S3]
- Separate activation reporting prevents paying accounts from hiding failed value delivery. [S5]
- Cross-functional ownership aligns marketing, product, sales, and finance. [S2] [S4]
- Observation windows and decline triggers prevent indefinite extrapolation. [S6]
