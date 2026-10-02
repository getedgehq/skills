---
name: matz-psychological-targeting
description: "Use Sandra Matz's public psychological targeting method to assess or design consent-based personalization when a task links digital behavior, psychological needs, message fit, and real outcomes."
---

# Psychological Targeting

Based on Sandra Matz's public method. Not affiliated with or endorsed by Sandra Matz.

## When to use

Use this skill when a user asks how to personalize a message, product recommendation, or behavior change intervention around people's psychological needs, or asks to audit an existing targeting system. It is especially useful when someone proposes inferring personality from digital traces, claims a message will change behavior, or wants to evaluate whether personalization benefits the recipient. Apply the procedure to an actual goal and audience. Do not treat the mere availability of personal data as a reason to use it. [S1] [S2] [S4]

## Procedure

### 1. Define the decision and whose interests count

1. Write the concrete behavior or decision the user wants to affect, the recipient's own stated goal if known, and the benefit and cost to each party. If recipient benefit is speculative while the sponsor benefit is clear, make that conflict visible before designing a message. Matz frames the worthwhile use of personalization as helping people find what fits their needs or reach goals they want, while recognizing that the same insight can be used to exploit them. [S2] [S3]

2. State separately the **insight task** and the **influence task**. Insight estimates a need, preference, trait, or state from evidence. Influence chooses what information, product, or experience to present. A plan that validates only prediction has not shown that its intervention helps people; a plan that measures only clicks has not established the intended behavior or welfare outcome. [S1] [S2] [S5]

3. Check the setting before proceeding. If the requested intervention would use inferred fear, anxiety, health, sexuality, political orientation, or another vulnerability to pressure people, discriminate against them, or steer a critical civic choice without their awareness, stop that design and propose a transparent, user directed alternative. Matz's central concern is the power that psychological insight gives whoever controls the message, particularly when people lose agency or a shared view of the world. [S1] [S4]

### 2. Choose the smallest defensible psychological signal

4. Inventory the available evidence and distinguish intentional identity claims from unintentional behavioral residue. Posts and follows can express how people wish to present themselves; searches, location traces, purchases, and device activity can disclose more than they intended. Record source, consent or permission, retention, and whether the recipient would reasonably expect this inference. [S1] [S2]

5. Prefer a directly stated goal or preference when it answers the task. Infer a latent trait only when it would change a real design decision and a less intrusive signal will not do. Treat a psychological profile as an estimate, never a diagnosis or a complete account of a person. Matz notes that psychological traits are not directly observable, that digital traces are partial clues, and that people vary across situations. [S4] [S5]

6. Select the trait or need for the particular product and context rather than filling in every Big Five score by habit. In Matz's account, openness may matter for novelty oriented experiences and extraversion for social stimulation, while the relevant dimension can change with the offer and the moment. If no meaningful link between a characteristic and the choice can be articulated, use a nonpsychological baseline. [S5]

7. Validate any inferred signal against a suitable reference and current population before using it for decisions. Report uncertainty, coverage, and differences across groups. A 2017 field study depended on the quality of its trait proxies and warned that the meaning of a digital signal can drift over time; later work found that language based inference accuracy can differ across age and gender categories. A model that worked in one platform, era, or group cannot be assumed to work in another. [S6] [S7]

8. For a conversational assistant, recognize that ordinary dialogue can reveal personality even without a formal questionnaire. Make any profiling purpose visible, ask only for information needed for the task, and do not silently turn routine conversation into a personality assessment. Research by Matz and colleagues found that conversational setting changed both inference accuracy and user experience. [S8]

### 3. Pick what to adapt

9. Decide between **audience to content** and **content to audience**. If the user has a fixed audience or a predefined group, adapt the wording, framing, or presentation to that group's supported needs. If several products or pieces of content are available, first find which one genuinely fits a person's preferences. Matz describes product fit and message fit as different levers and cautions that the better choice depends on whether the product has distinctive psychological characteristics. [S5] [S6]

10. Translate the chosen characteristic into a verifiable creative hypothesis, such as a calmer experience for someone who explicitly prefers quiet or a novelty focused explanation for someone seeking exploration. Change the relevant words, images, or option order while keeping the underlying facts, price, risks, and available choices consistent. In the field experiments, the researchers varied ad language and imagery to express a trait and checked that independent judges perceived the intended difference. [S6]

11. Show the user why an option was recommended and provide an easy way to correct the profile, choose a different route, or turn personalization off. Matz argues that people need practical control and that privacy choices cannot depend on each person reading every set of terms. Treat opt in and minimal data collection as design decisions, not fine print. When architecture is in scope, consider keeping raw data on the person's device rather than pooling it centrally. [S1] [S4]

12. Keep room for exploration. If personalization repeatedly reinforces past choices, add an explicit path to other perspectives or options that the person can choose. Do not optimize only for familiarity. Matz warns that perfectly tailored feeds can narrow preferences, increase echo chambers, and erode common reference points; she also suggests using the same capability to help people encounter different viewpoints. [S1]

### 4. Test fit and consequences

13. Write the predicted mechanism before looking at results: which audience characteristic matters, how the variant speaks to it, and which observable outcome should change. Include a credible generic version and, when ethical and feasible, matched and mismatched versions so that a result can be attributed to fit rather than to one variant simply being better crafted. Matz's field work tested interactions between audience and ad personality and checked the ad manipulation independently. [S6]

14. Measure the real decision or recipient outcome, not only attention. Report reach, click rate, conversion or follow through, and any recipient welfare measure tied to the stated goal. Keep these measures distinct: Matz found that clicks can be noisy and spontaneous, and one of her field studies showed a purchase effect without a click effect. A lift in clicks alone does not establish better decisions. [S5] [S6]

15. Compare the personalized route with an ordinary behavioral or demographic baseline where relevant, and say when the evidence is inconclusive. Matz explicitly identified the comparative value of psychological targeting against existing approaches as an open question. Avoid claiming a universal uplift, a fixed ideal number of traits, or an ability to transform deep beliefs from a single exposure. [S4] [S5]

16. Audit distribution as well as average performance. Check whether a segment is misclassified, excluded from useful options, pressured at vulnerable moments, or shown a different factual reality. If those harms emerge, narrow or end the targeting even when the sponsor's conversion metric improves. Matz's later work highlights uneven prediction accuracy, and her public interviews place self determination and shared experience at the center of the risk assessment. [S1] [S7]

## Common failure modes

- **Mistaking prediction for permission.** A digital trace may predict something intimate without the person intending to disclose it. Require a justified use and a real choice before acting on that inference. [S1] [S2]
- **Treating a score as identity.** Context changes behavior, proxies drift, and group averages do not certify an individual's trait. Preserve uncertainty and let the person override the system. [S4] [S6]
- **Calling engagement a benefit.** More clicks or purchases may reflect greater influence without improving the recipient's life. Return to the recipient's stated objective and the actual outcome. [S2] [S5]
- **Overstating precision or power.** Matz's experiments show effects in specific settings, while she rejects claims that a few tailored messages can simply reverse core identities. State the population, intervention, comparison, and limit of each finding. [S4] [S6]

## Finished output

Deliver a short decision brief with the recipient's goal, sponsor's goal, candidate psychological signal and its provenance, uncertainty and consent status, chosen fit strategy, sample variants or product options, the control and outcome plan, likely recipient benefit and harm, and the controls people have over personalization. If evidence or authorization is missing, label the proposed variant as a hypothesis and identify what would have to be learned before deployment. [S1] [S5] [S6]

## Worked example (illustration)

A library asks for help increasing signups for an optional weekend reading club. Its form already lets adults select "quiet reading" or "group discussion"; it has no need to infer personality from browsing histories. The agent defines a recipient goal of finding an enjoyable format and a library goal of sustained participation, then drafts two factual invitations: one foregrounds uninterrupted reading time, the other foregrounds conversation. Both display the same schedule and cost and let readers switch formats. The agent proposes comparing each invitation with a plain generic invitation, measuring attendance and satisfaction as well as signups. It asks the library to offer other club formats for exploration and to avoid calling either preference a permanent personality type. This illustrates goal fit, message fit, recipient control, and outcome measurement without covert profiling. [S1] [S2] [S5] [S6]

## Sources

1. [S1] Josie Cox, "What Your Digital Footprint Says About You," interview with Sandra Matz, Columbia Magazine. https://www.magazine.columbia.edu/article/digital-footprint-sandra-matz-mindmasters
2. [S2] "Sandra Matz: Mindmaster - Data & Behavior," interview excerpts, The Second City. https://www.secondcity.com/sandra-matz-mindmaster-data-behavior
3. [S3] Sandra Matz, biography and research overview, personal site. https://sandramatz.com/
4. [S4] Jason Hreno, "Q&A with Sandra Matz," Rotman Management. https://rotmanutorontoca-lb01-production.terminalfour.net/news-events-and-ideas/rotman-magazine/back-issues/2025/winter-2025/sandra-matz/
5. [S5] "Personality & marketing effectiveness," interview with Sandra Matz, Center for Applied Product Personality Research. https://cappr.org/sandra-matz-personality-marketing-effectiveness-makes-ctr-conversion-go-roof/
6. [S6] S. C. Matz and colleagues, "Psychological targeting as an effective approach to digital mass persuasion," PNAS, open full text via Europe PMC. https://www.ebi.ac.uk/europepmc/webservices/rest/PMC5715760/fullTextXML
7. [S7] Heinrich Peters and Sandra C. Matz, "Large Language Models Can Infer Psychological Dispositions of Social Media Users," arXiv. https://arxiv.org/abs/2309.08631
8. [S8] Heinrich Peters, Moran Cerf, and Sandra C. Matz, "Large Language Models Can Infer Personality from Free-Form User Interactions," arXiv. https://arxiv.org/abs/2405.13052
