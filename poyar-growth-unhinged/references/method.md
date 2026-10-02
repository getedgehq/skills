# Method: Customer Value, Account Growth, and Monetization

Based on Kyle Poyar's public method. Not affiliated with or endorsed by Kyle Poyar.

## Evidence and attribution

This is an operational synthesis, not an official framework with this name. Source identifiers resolve in [sources.md](sources.md). S1 through S6 support only material visible in their public previews. A heading announcing a later section does not support claims about that section's contents. Do not infer unpublished recommendations or extrapolate historical statistics into current benchmarks.

Poyar's authored articles supply principles and warnings. S5 also contains Jesus Requena's account of Figma practices; attribute those practices to that interviewee rather than presenting them as universal Poyar rules. S7 through S9 support Poyar's interview statements, not every statement by a host or a page's later editorial summary.

The tables, bill calculations, comparison designs, stop criteria, and memo format in this package are operational suggestions derived from the principles. They are not quoted expert prescriptions. Label data as observed, customer-reported, calculated, hypothetical, or unknown. Cite the principle behind a recommendation without pretending the citation proves the customer's diagnosis.

## 1. Diagnose the customer journey

Poyar's organizing lens is progression through discovering the product, starting use, realizing value, becoming a paying customer, and scaling adoption. Product activity can reveal buying intent, and product investment can contribute to acquisition, conversion, and expansion. Traditional sales-centric metrics remain useful for some models but miss these mechanisms when applied mechanically. [S1]

Build a journey map with these operational fields:

| Stage | Decision to understand | Useful evidence |
| --- | --- | --- |
| Discover | Does a relevant customer recognize a problem the product solves? | High-intent traffic, invitations, segment fit |
| Start | Is the entry experience credible and easy enough to try? | Eligible visitors, signups, abandoned entry attempts |
| Activate | Has the customer experienced the promised value? | Completed valuable work, repeated use, time to value |
| Convert | Is payment the sensible next step after value? | Activated accounts, paid conversion, purchase objections |
| Scale | Does adoption deepen or spread after purchase? | New use cases, team participation, usage, expansion and contraction |

Use consistent cohorts and observation windows. Separate users, teams, accounts, and buyers so denominators do not shift silently. A signup measures entry; it does not establish activation. Choose the constraint with the strongest evidence and explain how resolving it should affect the next stage. Low conversion can arise from weak activation, poor fit, difficult entry, or unclear packaging, not only price. This diagnostic comparison operationalizes the journey lens. [S1] [S8]

When analytics are incomplete, propose a provisional value event and a minimal instrumentation or interview plan. Avoid calculating precise uplift from absent data. When early retention is poor, inspect delivered value before compensating with more traffic or sellers.

## 2. Focus on best-fit accounts

Prioritize accounts where the product works well, the company can win, and customers can renew and expand. Compare segments using win rates, deal sizes, sales cycles, and retention or expansion evidence. Attractive logos alone do not establish fit. Poyar argues that lead scoring and attribution disputes often obscure whether the right accounts are actually moving toward purchase. [S6]

Create an account-level view joining relevant contacts, product activity, buying status, and revenue. Ask how many best-fit accounts exist, where each stands, and which interventions appear to advance them. Define a target account denominator before reporting progression. MQLs can remain an activity signal, but they are insufficient proof of business impact. [S6]

With little history, describe segment advantages as hypotheses and list the evidence needed to distinguish them. With multiple workspaces per company, record how they map to an account before classifying an account as active or qualified. These are implementation safeguards for an account-centric view, not fixed identification rules from Poyar.

## 3. Move from individual value to team value

An individual can discover the product while the durable commercial opportunity comes from team and organizational adoption. Poyar warns that optimizing monetization around isolated power users can neglect stronger team economics. His public pricing guidance favors broad access to user value while considering organizational needs such as administration, security, billing, and support as monetization opportunities. [S2]

Define the bridge explicitly: which real activity requires colleagues, creates shared value, or introduces a broader use case? Inspect invitations, collaboration access, plan restrictions, and who sees or approves a bill. Do not equate cheap entry with a functioning expansion path. Where the product is genuinely collaborative, make team participation feasible rather than forcing every early user through a commercial gate. [S2] [S5]

In Requena's Figma account, activation involved collaboration within the first week. Poyar separately highlighted the invitation and administrator billing experience. Use these as examples of value realization and admin control. Neither the timing nor the historical billing practice is a default for other products. [S5]

For a product that legitimately serves one specialist, do not invent a team use case. Test whether expansion should come from more consumption, additional workflows, or a more sophisticated package. This is a contextual application of value-metric selection. [S8]

## 4. Select the pricing unit

Choose what customers pay for before debating the number on the price tag. Plausible units include users, active users, transactions, contacts, workloads, or consumption. Poyar warns against adopting seats automatically: some small teams produce substantial value or usage without adding people. Conversely, seats can still fit software whose value spreads through more users. [S7] [S8]

As an operational evaluation, compare each candidate on:

- Customer value: Does a higher bill accompany a valuable outcome or merely internal activity?
- Landing: Can a customer begin with a reasonable purchase given uncertain needs?
- Expansion: Can successful use grow revenue without a forced renegotiation every time?
- Legibility: Can a buyer explain the unit and estimate a plausible bill?
- Operability: Can the business meter the unit, reconcile bills, and forecast delivery costs?

The first three tests reflect pricing and growth principles; legibility and operability implement purchasing and finance concerns. [S7] [S8] [S9]

Calculate at least three scenarios: a new customer, an expanding customer, and a mature customer. State unit definition, included quantity, rate, package fee, billing period, and any discounts. Show arithmetic and the value that accompanies higher spend. Treat proposed rates as hypotheses until researched. For lumpy or expensive workloads, include a spike case and cost-to-serve sensitivity. Metered activity that grows while customer benefit stays flat is a reason to investigate the unit, not to declare expansion healthy.

## 5. Build packages with jobs

Good, better, best is Poyar's starting point when no stronger context suggests otherwise. A single bundle can be inflexible and eliminate an upsell path. Unlimited customization can create choice overload, an impression of excessive itemization, and more procurement negotiation points. Poyar explicitly cautions that packaging principles can conflict and require judgment. [S3]

For each package, identify the customer, outcome, entry condition, included capabilities, and reason to graduate. This is a practical way to create the purchase clarity and sophistication-based upsell path described in the public preview, not a reconstruction of its gated sections. [S3]

Evaluate an add-on when one or more of these conditions hold:

1. A minority values it highly while most buyers do not need it.
2. It serves a different buyer or budget.
3. It replaces something purchased from another vendor.
4. It becomes relevant later in adoption.
5. Providing it involves meaningful cost or work that should not be incurred indiscriminately. [S3]

Specify the buyer and expected adoption timing. One condition makes an add-on a candidate, not a certainty. Poyar warns against expecting the average customer to buy more than one or two add-ons in the initial transaction. Use that as a complexity warning rather than a ban on every specialized configuration. Delivery cost is a consideration, not a license to base the entire pricing strategy on cost plus a markup. [S3]

## 6. Make sales incremental and reach the buyer

Product-led growth and sales can work together when engagement starts from the customer journey, uses product signals, and adds incremental value. Sales should solve a readiness or adoption problem, not simply claim credit for customers already buying unaided. [S4]

For each proposed play, document the account profile, product signal, customer need, assistance offered, champion, budget holder, and expected outcome. Compare assisted and self-service outcomes where feasible. A randomized eligible-account holdout is one operational option; matched cohorts are weaker evidence and should disclose selection bias. Count incremental revenue or progression after assistance costs, not all revenue from accounts touched by sales.

Distinguish a product-qualified lead or user from a product-qualified account. Aggregate adoption across the account, then connect users to people with authority over broader deployment. Requena's Figma case combined active-account prioritization with decision-maker content; Poyar's authored warning also emphasizes that users and buyers are often different people. [S4] [S5]

Poyar explicitly warns against these six practices:

- Hiding prices to force every user into a sales conversation.
- Weakening free or self-service offers to protect enterprise deals.
- Contacting every new free user regardless of product behavior.
- Prioritizing commercial pressure over customer experience and upfront value.
- Demanding too much in the first purchase before value and internal support exist.
- Speaking only to existing users without finding the buyer. [S4]

For low-value accounts with strong self-service conversion, seller involvement may add cost without lift. For a security or deployment blocker, targeted assistance can be useful even when usage volume alone is modest. These are hypotheses to assess against readiness, fit, and measured incrementality.

## 7. Balance flexibility and predictability

Usage pricing can lower entry friction and align spend with success, while enterprise buyers may need budget certainty. Consider a hybrid commitment, volume discount, annual allowance, explicit overages, or a renewal-based adjustment. Explain what happens when usage falls short or exceeds expectations. Annual allowances can accommodate seasonality better than rigid monthly caps. [S7] [S9]

Avoid large upfront commitments when a new customer cannot estimate volume. For established customers, use their usage history and deployment plan to evaluate commitment size. Spend alerts, calculators, and continuing account monitoring can improve predictability. Do not assume every committed deal requires a deep discount or every overage requires a grace period. Poyar cautions against overusing grace periods. [S8] [S9]

Review entry communication separately from the underlying model. State customer benefits, who each plan serves, and how the bill works. Poyar highlights pricing-page usability as an acquisition lever: confusing feature grids and unexplained jargon can undermine an otherwise sensible offer. Test whether target buyers can select a plan and estimate cost. [S8]

## 8. Research and pilot before rollout

Poyar recommends beginning with win-loss analysis, ideally conducted independently of the seller. Ask what drove the decision, how alternatives compared, and whether price signaled value or cheapness. Repeated wins because of low price can indicate poorly matched customers rather than a sound strategy. Give pricing an accountable owner with customer, competitive, and execution capabilities; the exact job title is secondary. [S7]

Match the research method to the uncertainty:

| Uncertainty | Evidence to gather |
| --- | --- |
| Why customers buy or reject | Independent win-loss interviews |
| Which features and packages matter | Package-choice research or conjoint-style survey |
| What buyers expect to spend | Price-expectation research, potentially Van Westendorp |
| Whether buyers understand the offer | Pricing-page usability tests |
| Whether a negotiated proposal works | Limited sales pilot with willing, value-oriented reps |
| Whether new self-service pricing converts | Bounded new-customer cohort test with clear offer terms |

S7 discusses the first, second, third, and fifth options. S8 discusses usability and new self-service cohorts. Neither survey responses nor a sales pilot guarantee realized willingness to pay or a causal effect. [S7] [S8]

The apparent experimentation tension is contextual: S7 warns about ill will from aggressive variation of live prices and favors research and unpublished sales pilots; S8 permits new-cohort self-service tests and pricing-page design tests. Do not translate the former into a prohibition on every experiment or the latter into arbitrary inconsistent quotes. Explain what varies, who is eligible, and how customer expectations are handled. [S7] [S8]

A practical pilot plan records owner, target segment, duration, comparison, decision criteria, downside limits, and what to do if evidence is inconclusive. These controls are package recommendations. Small sales samples and enthusiastic reps can bias the result. Early businesses can learn from frequent interactions; more mature businesses should avoid disrupting buyers and sellers with constant changes. Pricing evolves as the company, product, and market evolve. [S7] [S8]

## 9. Evaluate economics and incentives

Usage models require granular historical usage, metering, billing, and customer-cohort forecasts. Finance should work with GTM and customer-facing teams to understand use cases, implementation, and adoption. Maintain conservative and upside scenarios rather than assuming every account expands or presenting only a pessimistic forecast. [S9]

Evaluate payback using fully loaded acquisition costs and the margin from revenue recognized over time. Annual cash received upfront helps liquidity but does not prove economic recovery while infrastructure, implementation, support, and other service costs continue. Separate revenue streams with materially different margins. Do not assume software implies negligible delivery costs. [S1] [S9]

As an operational calculation, identify the first period when cumulative recognized revenue less directly attributable delivery costs equals acquisition cost. Disclose cost allocation and avoid double counting implementation in both acquisition and delivery. A constant-margin shortcut may be useful for stable subscriptions, but usage ramp and variable costs warrant a cohort schedule.

Interpret net dollar retention alongside payback, customer segment, and motion. A business with quick recovery can tolerate different retention economics from one that waits years to recover acquisition costs. Historical public-company retention figures are not automatic targets for a smaller business. Growth from retaining and expanding customers deserves attention alongside new acquisition. [S9]

Inspect incentives: Poyar warns that compensating sellers for committed bookings can encourage discounting already-successful self-service customers, adding commissions while lowering revenue. Commitments can still help adoption and predictability; assess whether they add enough customer and vendor value. Include realized consumption or customer success in the incentive discussion rather than rewarding oversized commitments alone. [S9]

## Decision rules and edge cases

| Situation | Appropriate response | Basis |
| --- | --- | --- |
| Many signups, little delivered value | Prioritize activation evidence and friction before adding sellers | [S1] [S4] |
| Individuals succeed, teams do not form | Inspect the collaboration bridge and plan gates | [S2] [S5] |
| Small team, large customer outcome | Compare usage or outcome-related units with seats | [S7] [S8] |
| Unsure of future volume at entry | Explore a smaller or flexible landing offer | [S7] [S8] |
| Enterprise requires predictable budget | Compare commitments, allowances, and clear overage terms | [S7] [S9] |
| Bookings rise while consumption and revenue fall | Inspect discounts, seller costs, and incentives | [S9] |
| Lead volume rises without target-account progress | Reassess account fit and journey evidence | [S6] |
| Historical retention looks exceptional | Check cohort definitions and acquisition economics before using it as a target | [S1] [S9] |
| No dependable customer data | State hypotheses and specify the next evidence-gathering action | Operational suggestion |
| Narrow request or single-user use case | Use relevant modules and mark others outside scope | Operational suggestion |

Deliver a decision memo with an explicit recommendation, evidence gaps, alternatives, bill scenarios where relevant, and a bounded next action. A recommendation may be to instrument, interview, or pilot rather than immediately change pricing. Review it against [../checklists/review-checklist.md](../checklists/review-checklist.md).
