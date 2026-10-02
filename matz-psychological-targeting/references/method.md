# Psychological Targeting: Detailed Method

Based on Sandra Matz's public method. Not affiliated with or endorsed by Sandra Matz.

## How to read this method

Matz's public work describes psychological targeting as understanding psychological characteristics and then adapting interventions to them. Her research asks whether psychological fit affects behavior; her public interviews also emphasize agency, recipient benefit, and the dangers of concentrated informational power. Her personal research overview supplies context, not an experimental result. [S1] [S2] [S3]

The M1 to M12 rules below are this package's practical synthesis. Citations support the underlying concepts and findings. Requirements such as maintaining a signal register, specifying a fallback, or using a review gate are operational recommendations derived from those concepts, not claims that Matz published this exact procedure. Interviews express explanations and proposals; the field paper reports experiments; the two arXiv sources were fetched as abstract pages and support only the findings summarized there. See [sources.md](sources.md).

## M1. Define value before targeting

Write the recipient goal separately from the sponsor goal. A recipient may want an enjoyable activity, a suitable service, or support accomplishing a self-chosen goal. A sponsor may want sales, registrations, or repeat use. Their interests can overlap, but a purchase is not automatically evidence of recipient benefit. Matz describes personalization as potentially helping people accomplish their own goals while also acknowledging its exploitative uses. [S1] [S2]

**Decision rule:** If the recipient goal is unknown, say so. Use exploratory preference questions or a generic information offer rather than inventing a psychological need. Identify possible costs, including time, money, unwanted disclosure, and diminished choice. If the offer itself is unsuitable, better wording does not make it suitable.

## M2. Separate the insight and influence claims

The insight task estimates a preference, motivation, trait, or state. The influence task chooses an intervention based on that estimate. These are different links in a causal chain. Matz explicitly describes this two-stage relationship in public interviews. [S1] [S2]

Maintain three statements:

- **Signal claim:** Evidence supports an estimate about this audience in this context.
- **Fit claim:** A particular option or framing should better meet that estimated need.
- **Outcome claim:** The adaptation should improve a named observable result.

Evidence for one statement does not prove the others. For example, a valid trait estimate does not prove that a suggested advertisement changes behavior; a behavior change does not prove improved welfare. The 2017 paper measured clicks and conversions, not comprehensive recipient well-being. [S6]

## M3. Protect agency and screen the purpose

Matz warns that intimate inference can facilitate discrimination, fear-based persuasion, and loss of self-determination. She describes the danger of using anxious people's fears to sell unnecessary protection and of covert influence over civic decisions. The field paper also discusses exploitation of traits associated with gambling vulnerability. [S1] [S4] [S6]

**Package boundary:** Do not design interventions that exploit inferred vulnerability, discriminate, or covertly steer a critical civic choice. Document the problematic mechanism and propose an alternative that uses volunteered preferences and consistent factual information. This boundary operationalizes the warnings; it is not presented as a quotation or comprehensive list from Matz.

Supporting a person who requested help is different from pressuring someone at a vulnerable moment. A beneficial purpose still requires suitable evidence and controls. In high-stakes contexts, this skill can structure questions and audit a proposal; it cannot establish clinical suitability, legal compliance, or entitlement to access a service.

## M4. Distinguish deliberate expression from incidental traces

Deliberate self-presentation includes posts, follows, and curated playlists. Incidental traces include searches, purchases, location records, and device activity generated during ordinary use. Both can disclose psychological information, including information the person never intended to share. [S1] [S2] [S4]

For each candidate signal, record its source, collection purpose, permission for this use, retention, expected audience, and possible alternative interpretations. Keep permission and predictive value in separate columns. A publicly visible post or platform targeting category does not establish permission for an unrelated inference.

The 2017 study used anonymous group-level targeting and reported ethics approval, with no ability to obtain individual consent from ad recipients. Do not rewrite that historical design as an opt-in experiment. This package recommends a consent-based workflow in response to the broader agency concerns. [S6] [S1] [S4]

## M5. Select a relevant, minimal psychological signal

Traits are latent constructs: observable behavior provides clues rather than a direct view into personality. Matz says there is no established ideal number of traits to target; relevance depends on the product and situation. She also explains that relatively stable tendencies can vary in their expression across contexts. [S4] [S5]

**Decision rule:** Prefer a directly stated goal or preference if it answers the decision. Consider an inferred trait only if it changes a justified design choice and a less intrusive signal is insufficient. Name the connection, not just the trait. For example, a volunteered preference for quiet supports highlighting a quiet activity; it does not establish a global introversion score.

Distinguish a stable tendency, current state, practical constraint, and explicit preference. A person who wants quiet today might enjoy a social event tomorrow. Conflicting signals should trigger clarification or generic fallback, not a more intrusive search for a supposedly true identity. Do not assign clinical diagnoses or rigid types from marketing signals.

## M6. Validate estimates and preserve uncertainty

The field paper warns that the psychological meaning of a digital trace can change as its audience changes. It also notes that models trained against self-report questionnaires retain some limitations of those reference measures. Its trait targeting used aggregate associations with Facebook Likes, rather than a verified individual profile for every recipient. [S6]

The social-media LLM paper's abstract reports moderate associations between inferred and self-reported Big Five scores and differences in accuracy across age and gender groups. The conversational paper's abstract reports that accuracy depended on interaction design, with stronger performance in conversations eliciting personality-relevant information than in a default helpful-assistant condition. Neither finding certifies a particular individual's profile or the accuracy of a current model in a new population. [S7] [S8]

For an inferred signal, specify:

- Reference measure and what it actually measures.
- Evaluation population, language, platform, context, and date.
- Prediction uncertainty, missing-data coverage, and known subgroup differences.
- Whether the inference remains valid for the proposed use.
- A generic fallback and conditions for reevaluation.

Do not translate a correlation into a percentage of people correctly classified. Do not claim an exact confidence score without evidence. If validation is unavailable, label the estimate unvalidated and use it only as a design hypothesis pending appropriate evaluation.

For conversational systems, make a profiling purpose visible rather than quietly repurposing routine dialogue. An enjoyable conversation does not prove informed consent to inference or subsequent influence. This is an implementation recommendation informed by the conversational research and Matz's agency concerns. [S8] [S1]

## M7. Choose product fit, message fit, or both

Two distinct decisions are useful:

- **Audience to content:** A fixed audience needs an explanation or presentation responsive to a supported need.
- **Content to audience:** Several experiences or products exist, and a person needs an option that actually fits their preferences.

Matz distinguishes product targeting from message tailoring. She suggests that distinct product characteristics can make product fit valuable, while broadly used products may benefit more from tailored messages. Her discussion is conditional, not a universal ranking of tactics. [S5]

If a quiet workshop and a discussion workshop offer genuinely different experiences, match the experience first. If everyone receives the same tutorial, adapt how its benefits are explained. Combining both is sensible only when each adaptation has a defensible mechanism. Do not use a flattering message to compensate for poor product fit or exclude people from otherwise suitable options based on a score.

## M8. Turn fit into a falsifiable creative hypothesis

Write a mechanism before drafting: because the audience expressed or reliably showed need X, emphasizing feature Y should improve outcome Z. Use plain language rather than labeling recipients with a personality category.

The field experiments adapted wording and imagery to express psychological characteristics and used independent ratings to check that the intended differences were perceived. They examined audience-by-message interactions to test fit. [S6]

**Package recommendation:** Keep facts, price, eligibility, risks, and choices consistent across variants. Change only what the hypothesis requires. Draft a credible generic baseline, then ask independent readers to identify the intended difference. If variants also change discounts, availability, or factual claims, their results cannot isolate psychological framing. Document those changes separately when studying a broader intervention.

## M9. Make controls practical and preserve exploration

Matz favors easier privacy-preserving defaults and warns that individuals cannot reasonably manage every tracking choice through lengthy terms. She discusses local processing and federated learning as ways to reduce centralized access to raw data. These are public design proposals, not proof that any implementation is automatically private. [S1] [S4]

Specify a short explanation of recommendation logic, preference correction, a generic route, and an easy way to disable personalization. Collect and retain only information needed for the stated purpose. When architecture is relevant, evaluate local processing rather than assuming centralized collection is necessary.

Matz warns that personalized feeds can reinforce existing preferences and remove common reference points. She also proposes voluntary exposure to other perspectives, while explicitly acknowledging that such exploration could backfire and deepen aversion. [S1]

**Decision rule:** Offer alternatives without forcing uncomfortable exposure. Keep access to shared factual information. Evaluate whether exploration helps the recipient rather than assuming that unfamiliar content necessarily creates empathy.

## M10. Test fit against a credible alternative

Predefine the mechanism, primary outcome, comparator, observation period, allocation approach, analysis, and harm limits. A generic version tests whether personalization adds value. When ethical and feasible, matched and mismatched variants across audiences can help distinguish fit from one advertisement being better for everyone. The field paper used such interaction designs, plus a comparison within an existing behavioral audience. [S6]

Compare against existing behavioral or demographic approaches when relevant. Matz identified comparative effectiveness as an open research question in her 2017 interview; that historical statement does not establish what all later research has resolved. [S5]

For a small audience, do not manufacture statistical certainty. Use comprehension and preference checks to refine hypotheses, and identify the additional evidence needed for an outcome claim. If platform delivery, exposure, or allocation differs, report the resulting attribution limits. Never intentionally pressure or harm a recipient to create a mismatched condition.

## M11. Measure action and recipient consequences separately

Track exposure or reach, attention, action, and recipient benefit as distinct measures. Define denominators and observation windows: clicks per exposure and purchases per visitor answer different questions. Include a recipient measure tied to M1, such as satisfaction with the chosen activity, regret, sustained participation, or progress toward a requested goal.

The field paper's first study found a purchasing interaction without a corresponding click interaction. This demonstrates why clicks alone can miss relevant behavioral effects; it does not show that purchases invariably improve welfare. [S6] Matz's interview likewise emphasizes that clicks can be spontaneous and noisy. [S5]

Report observed evidence separately from assumptions. A rollout recommendation should state whether the intervention improved the primary outcome and whether recipient harms remained within the predefined limits. Without actual results, deliver a test plan, not a success claim.

## M12. Audit distribution and make a stopping decision

Average improvement can conceal incorrect profiles, exclusion, or adverse effects in a segment. Inspect signal quality and outcomes across relevant groups, using proportionate data and avoiding unnecessary new sensitive collection. Prediction heterogeneity in the social-media LLM study motivates checking uneven performance rather than assuming uniform accuracy. [S7]

Choose one disposition:

- **Proceed:** Relevant evidence, controls, and recipient outcomes support a bounded next step.
- **Revise:** A fixable problem in signal, framing, controls, or evaluation remains.
- **Generic fallback:** No useful or reliable psychological signal is available.
- **Stop:** The use undermines agency or causes unacceptable recipient harm.

Name an owner, review date, and conditions for reevaluation. Those fields are package recommendations for making the decision actionable.

## Explicit expert warnings and their implications

- Psychological insight can enable exploitation and discrimination, not just useful recommendations. Review whose interests the intervention serves. [S1] [S4]
- Tailoring can threaten agency even without a conventional privacy breach. Anonymous group targeting can still expose intimate information through responses. [S4] [S6]
- Algorithms can reinforce preferences, narrow experience, and weaken shared reference points. Preserve alternatives; do not assume exploration always helps. [S1]
- Literacy and individual vigilance are insufficient protections by themselves. Make control usable and reduce collection by design. [S1]
- Psychological targeting is not a magical way to reverse core identities through a few ads. Small changes can still matter, but avoid inflated claims about persuasion power. [S4]
- Signals drift, self-report references have limitations, and the field experiments do not establish all traits, populations, or positions along a trait scale. Validate the proposed context. [S6]
- No universal ideal trait count or comparative advantage was established by the cited interview. Treat fit as a contextual hypothesis. [S5]

The public interviews discuss Matz's book, but this package uses the interviews themselves and public research, not book passages or paywalled text.
