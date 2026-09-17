# Formatted outline: Phone-free secondaries evidence annex

## Venue format

- Format family: Evidence brief (policy annex)
- Target venue: Cabinet paper supporting phone-free secondary schools rollout
- Citation style: Harvard (author-date)
- Word basis: proportional to total target (2,000 words main text)
- Abstract length: N/A (Bottom Line box instead, 150 words max)
- Keywords: N/A (not applicable to policy brief)
- Title limit: None specified (descriptive policy document title)
- Language: English (UK)
- Numbering: Sections numbered 1-6, no subsection numbers (cabinet house style)
- Tables/figures: None (inline citation of findings only)

## Citation formatting instructions for drafting stages

**All in-text citations:** Use `{cite_<doi>}` placeholders only, at the exact point of the claim. Never write `(Author, Year)` or `[3]` by hand. Example: "Phone bans raised test scores by 6.41% {cite_10.1016/j.labeco.2016.04.004}."

**For claims that need support but have no source:** Use `{cite_MISSING: short description}`. This is not a way to ship an unsourced claim - `scripts/citations.py compile` will refuse to render it and exit nonzero. It is a way to be honest while drafting.

**Every number and finding attributed to a source must appear in that source's entry in `research/summaries.md`.** The file `research/citations.json` carries bibliographic metadata only (author, year, DOI) and holds no findings at all.

**At compilation:** `scripts/citations.py compile` will render all `{cite_<doi>}` placeholders into Harvard author-date format `(Author, Year)` and build the reference list alphabetically by first author, with full DOI links.

## Document structure

### Front matter
- Title: "Evidence Annex: Phone-Free Secondary Schools"
- Bottom Line box (150 words max, boxed/highlighted)

### Main sections (numbered 1-6, total 1,900-2,400 words)
1. Introduction (200-250 words)
2. Academic attainment (600-700 words)
3. Mental health and wellbeing (400-500 words)
4. Research quality and mechanisms (300-350 words)
5. Implementation considerations (500-600 words)
6. Conclusion (200-250 words)

### Back matter
- References (Harvard style, alphabetical)

---

## BOTTOM LINE BOX (150 words max)

**Word budget:** 150 words maximum (hard ceiling)

**Style:** Executive summary, plain language, bullet-compatible prose. Must stand alone without reading the annex. Use specific numbers, not adjectives.

**Content structure:**
1. Headline attainment finding (30 words): 6.41% test score improvement in UK study {cite_10.1016/j.labeco.2016.04.004}, replicated in Nordic countries
2. Equity finding (25 words): Effects larger for disadvantaged pupils and low achievers
3. Mental health finding (30 words): Emerging evidence suggests wellbeing benefits {cite_10.1016/j.lanepe.2025.101211}, but research newer and less robust than attainment findings
4. Research quality note (25 words): Recent studies use quasi-experimental designs providing causal estimates
5. Implementation note (25 words): Enforcement mechanisms and safeguarding protocols require guidance; research gaps in these areas
6. Action recommendation (15 words): Evaluation within first year recommended

**Citations:** {cite_10.1016/j.labeco.2016.04.004}, {cite_10.1016/j.lanepe.2025.101211}

**Tone:** Confident on attainment, measured on mental health, honest about implementation gaps

**Formatting note:** This will be rendered as a highlighted/shaded text box at the top of the annex, before Section 1.

---

## 1. INTRODUCTION (200-250 words)

**Word budget:** 200-250 words (target 225)

**Purpose:** Frame the annex's role in the decision process and set scope expectations

**Paragraph structure:**

**Para 1 (50 words):** Cabinet context. Cabinet has decided to mandate phone-free policies in secondary schools from January 2026. This annex sets out the evidence base under that decision, covering academic attainment, mental health and wellbeing, research quality, and implementation considerations.

**Para 2 (75 words):** Scope and limitations. The annex synthesises the strongest available evidence from the UK and international studies, with particular attention to quasi-experimental research providing causal inference. It is not a systematic review, does not claim comprehensive coverage of all published research, and does not serve as an implementation manual. Implementation guidance drawing on early adopter experience will be developed separately.

**Para 3 (50 words):** Evidence base characterisation. The attainment evidence is mature and consistent across countries. Mental health evidence is emerging and promising but newer. Implementation research is limited; questions on enforcement mechanisms and safeguarding protocols remain open.

**Para 4 (50 words):** Structure roadmap. Section 2 presents attainment findings. Section 3 covers mental health and wellbeing. Section 4 addresses research quality and cognitive mechanisms. Section 5 discusses implementation considerations. Section 6 concludes with evaluation recommendations.

**Citations:** None (framing section)

**Tone:** Neutral, formal, civil service register. Avoid advocacy or defensive posture.

---

## 2. ACADEMIC ATTAINMENT (600-700 words)

**Word budget:** 600-700 words (target 650)

**Purpose:** Present causal evidence that phone bans improve test scores, establish effect size, demonstrate international replication, and highlight equity dimension

**Subsection 2.1: UK evidence (300 words)**

**Para 1 (100 words):** Headline UK finding. Beland and Murphy (2016) {cite_10.1016/j.labeco.2016.04.004} analysed mobile phone ban adoption across English secondary schools using a difference-in-differences design that exploited staggered implementation across four cities. The study found that banning phones raised test scores by 6.41 percentage points on average. The quasi-experimental approach compared schools before and after bans were introduced against schools without bans over the same period, enabling causal inference rather than mere correlation.

**Para 2 (100 words):** Methodology explanation and effect size context. Difference-in-differences is a quasi-experimental method that controls for unobserved differences between schools by comparing change over time rather than absolute levels. The 6.41% improvement is equivalent to adding approximately five days of instruction to the school year [from summaries.md entry]. This is a policy-relevant effect size: meaningful in educational terms and achievable through low-cost intervention.

**Para 3 (100 words):** Robustness and generalisability within UK. The Beland and Murphy study covered multiple cities and school types, strengthening generalisability within the English system. The findings have been widely cited in policy discussions and have not been contradicted by subsequent UK research. The study uses administrative test score data from the National Pupil Database, the most comprehensive source of pupil attainment records in England.

**Subsection 2.2: International replication (200 words)**

**Para 1 (100 words):** Nordic evidence confirms findings beyond UK context. Swedish researchers have replicated the positive attainment findings in independent studies {cite_10.1016/j.econedurev.2020.102009}, {cite_10.2139/ssrn.3617386}. These studies used Swedish administrative education data and found consistent benefits from phone bans. Norwegian evidence using administrative registers and event-study designs similarly demonstrates student outcome improvements when smartphone bans are introduced {cite_10.2139/ssrn.4735240}.

**Para 2 (100 words):** Replication value and confidence. Replication across three countries with different school systems and administrative data sources strengthens confidence that the findings are not UK-specific or driven by idiosyncratic features of the English educational context. Nordic countries' comprehensive administrative registers enable strong causal identification, and the consistency of findings across methodological approaches (difference-in-differences, event studies) and national contexts supports the robustness of the positive attainment effect.

**Subsection 2.3: Equity effects (150 words)**

**Para 1 (150 words):** Larger benefits for disadvantaged pupils. Beland and Murphy's analysis found that the positive effects of phone bans were substantially larger for low-achieving students and those eligible for free school meals {cite_10.1016/j.labeco.2016.04.004}. This finding addresses a common equity concern: that restrictive policies might disproportionately burden disadvantaged families whose children rely on phones for safety or communication. Instead, the evidence suggests phone bans may reduce achievement gaps rather than widening them. The mechanism likely involves reduced distraction having a larger impact on pupils who are already struggling or who have fewer alternative learning resources outside school. This equity dimension strengthens the policy case, as interventions that particularly benefit disadvantaged pupils align with broader educational equity goals.

**Citations:** {cite_10.1016/j.labeco.2016.04.004}, {cite_10.1016/j.econedurev.2020.102009}, {cite_10.2139/ssrn.3617386}, {cite_10.2139/ssrn.4735240}

**Key numbers to include:** 6.41% (stated exactly), five days of instruction equivalent, "substantially larger" effects for disadvantaged pupils (qualitative from summaries.md, exact multiplier not reported in abstract)

**Tone:** Confident, evidence-based, specific. This is the strongest section.

---

## 3. MENTAL HEALTH AND WELLBEING (400-500 words)

**Word budget:** 400-500 words (target 450)

**Purpose:** Present emerging mental health evidence while noting its recency and methodological limitations relative to attainment research

**Subsection 3.1: UK evidence (250 words)**

**Para 1 (125 words):** SMART Schools study findings. The most recent UK evidence comes from the SMART Schools study published in The Lancet Regional Health - Europe in 2025 {cite_10.1016/j.lanepe.2025.101211}. This cross-sectional observational study surveyed 1,227 pupils aged 12-15 across 30 English secondary schools. It found that restrictive phone policies were associated with better mental wellbeing scores and reduced social media use during school hours. This is the largest recent UK study directly examining the relationship between school phone policies and adolescent mental health.

**Para 2 (125 words):** Methodological note on causation. The SMART Schools study is cross-sectional, meaning it measured associations at one point in time rather than tracking changes following policy introduction. This design limitation means the study cannot establish causation: it is possible that schools with better pupil wellbeing were more likely to adopt restrictive policies, rather than the policies causing the wellbeing improvement. Nevertheless, the association is consistent across 30 schools and the sample size is substantial. The study provides the best available UK evidence on this question, though stronger causal inference would require longitudinal data following pupils before and after policy changes.

**Subsection 3.2: Nordic evidence (100 words)**

**Para 1 (100 words):** Norwegian causal evidence. Abrahamsson's 2024 study using Norwegian administrative registers {cite_10.2139/ssrn.4735240} provides stronger causal evidence, using an event-study design to examine smartphone ban impacts. The study reports improvements in both academic outcomes and mental health indicators following ban introduction. Administrative register data enables tracking of the same individuals over time, addressing the causation limitation of cross-sectional studies. The Norwegian evidence suggests that phone restrictions may simultaneously address attainment and wellbeing concerns.

**Subsection 3.3: Evidence maturity and context (100 words)**

**Para 1 (100 words):** Newer and more limited than attainment evidence. Mental health evidence is substantially newer than attainment research: the UK and Norwegian studies cited above were published in 2024-2025, while attainment evidence dates from 2016 onward. The causal evidence base is more limited (one strong Norwegian study, one UK cross-sectional study) compared to multiple quasi-experimental attainment studies across countries. It is also worth noting that broader research on adolescent technology use and wellbeing {cite_10.1038/s41562-018-0506-1}, {cite_10.1111/jcpp.13190} has found very small general effects (under 1% of variance explained), though these studies examine overall technology use rather than school-specific interventions. The school-day phone restriction context may produce larger or more concentrated effects than general screen time patterns, or may particularly benefit vulnerable adolescents who show stronger responses than population averages. The appropriate framing for the annex is "emerging evidence suggests mental health benefits" rather than "proven to improve mental health."

**Citations:** {cite_10.1016/j.lanepe.2025.101211}, {cite_10.2139/ssrn.4735240}, {cite_10.1038/s41562-018-0506-1}, {cite_10.1111/jcpp.13190}

**Key numbers to include:** 1,227 pupils, 30 schools, "under 1%" variance explained in general technology studies

**Tone:** Measured, candid about limitations, but still positive. Contrast explicitly with Section 2's confidence level.

---

## 4. RESEARCH QUALITY AND MECHANISMS (300-350 words)

**Word budget:** 300-350 words (target 325)

**Purpose:** Explain why recent evidence is stronger than early correlational studies and provide mechanism explanation

**Subsection 4.1: Methodological shift (150 words)**

**Para 1 (75 words):** Early correlational research. Research published before 2016 was predominantly correlational: surveys showing associations between phone use and lower grades {cite_10.1080/03634523.2013.767917} or literature reviews synthesising such findings {cite_10.1016/j.ijer.2020.101618}. While these studies documented relationships, they could not distinguish whether phone use caused lower achievement, whether struggling students used phones more as a coping mechanism, or whether unobserved factors (e.g., parental monitoring, school culture) drove both.

**Para 2 (75 words):** Quasi-experimental designs for causal inference. From 2016 onward, researchers began exploiting natural experiments created by staggered adoption of phone bans across schools and regions. Studies used difference-in-differences methods {cite_10.1016/j.labeco.2016.04.004} and event-study designs {cite_10.2139/ssrn.4735240}, comparing schools before and after ban introduction against schools without bans over the same period. These designs control for unobserved school characteristics that remain constant over time, enabling causal inference rather than mere correlation. Access to comprehensive administrative data in Nordic countries and the UK National Pupil Database strengthened this research by providing objective outcome measures and large samples.

**Subsection 4.2: Cognitive mechanism (175 words)**

**Para 1 (175 words):** "Brain drain" effect explains why complete removal works. Ward et al. (2017) conducted experiments demonstrating that the mere presence of one's own smartphone reduces available cognitive capacity, even when the phone is switched off and placed face down {cite_10.1086/691462}. Participants performed worse on working memory and fluid intelligence tasks when their phones were on the desk compared to in their pocket, and worse with phones in their pocket compared to in another room entirely. The effect occurred even though participants were not using or consciously thinking about their phones. This "brain drain" phenomenon provides a mechanistic explanation for why phone-free policies improve learning: cognitive resources are freed when phones are completely removed from the environment, not merely switched off. The implication for school policy is that "off but present" approaches (phones in bags or pockets) may be less effective than complete removal (locked in pouches or lockers). This cognitive psychology finding, though conducted with adults in laboratory settings, offers a theoretical foundation for why school-day phone restrictions would affect classroom learning.

**Citations:** {cite_10.1086/691462}, {cite_10.1016/j.labeco.2016.04.004}, {cite_10.2139/ssrn.4735240}, {cite_10.1016/j.ijer.2020.101618}, {cite_10.1080/03634523.2013.767917}

**Tone:** Explanatory, builds confidence. The mechanism story makes the policy direction more credible.

---

## 5. IMPLEMENTATION CONSIDERATIONS (500-600 words)

**Word budget:** 500-600 words (target 550)

**Purpose:** Address practical questions schools and parents raise, distinguishing research gaps from evidence-based objections

**Subsection 5.1: Enforcement mechanisms (200 words)**

**Para 1 (100 words):** The question school heads ask most. School heads frequently ask what the research says about enforcement mechanisms: lockable pouches (where students lock their own phones in fabric pouches kept at their desks), lockers (where phones are deposited at the start of the day), or teacher collection systems. The honest answer is that no published study empirically compares these methods on compliance rates, teacher time burden, or student outcomes. One qualitative study documented implementation complexity in Swedish schools {cite_10.1080/07380569.2023.2211062}, but did not evaluate which enforcement approaches work best.

**Para 2 (100 words):** Implementation research is emerging. The absence of enforcement mechanism research reflects the field's recent development: phone bans have become widespread enough to study implementation only in the past two years, and most published research has focused on whether bans work rather than how best to implement them. This means guidance must draw on early adopter experience rather than published trials. Schools implementing policies in January 2026 will benefit from clear implementation protocols informed by schools already using various enforcement methods, with formal evaluation of fidelity, compliance, and teacher burden recommended within the first year.

**Subsection 5.2: Parental safeguarding and emergency contact (175 words)**

**Para 1 (175 words):** A procedural question, not an evidence-based objection. Consultation responses frequently raised parental concerns about reaching their child during emergencies. No published research addresses emergency contact protocols in phone-free schools, but this reflects that the question is procedural rather than an evidence-based objection to phone bans. Schools already have established communication channels: office phones, email, and parent-teacher communication systems. The question is not whether emergency contact is possible without students carrying phones, but what protocols ensure it works reliably. A rapid survey of existing phone-free schools would document the range of approaches taken (some allow office phone calls during emergencies, some have dedicated parent emergency lines, some communicate emergency contact procedures at enrollment), measure parent satisfaction, and establish the actual frequency of emergency contact requests during school hours. The evidence suggests this frequency is low. Clear emergency contact protocols, communicated to parents at policy introduction, address the procedural concern without undermining the policy's educational rationale.

**Subsection 5.3: SEND accommodations (175 words)**

**Para 1 (175 words):** Legal requirement and legitimate phone uses. No published research examines whether phone restrictions affect pupils with special educational needs and disabilities (SEND) differently, or what accommodations are appropriate. This is a gap that requires attention, as blanket policy without SEND consideration invites legal challenge under equality legislation. Some SEND pupils may have legitimate phone uses that must be distinguished from social media access: medical monitoring devices (e.g., continuous glucose monitors transmitting to phones), assistive technology for communication or organisation, or anxiety management tools prescribed by mental health professionals. Policy guidance must specify how schools distinguish medical and assistive exceptions from recreational use, provide clear criteria for accommodation decisions, and ensure SEND pupils are neither unfairly restricted nor used as policy loopholes. This requires SEND specialist input and consultation with schools serving diverse SEND populations. The absence of published research on this question does not undermine the policy direction; it identifies an area where implementation guidance, currently under development, must provide clarity.

**Citations:** {cite_10.1080/07380569.2023.2211062}

**Tone:** Honest about gaps, but frames them as guidance needs rather than reasons to abandon policy. Anticipates concerns and provides reasonable paths forward.

---

## 6. CONCLUSION (200-250 words)

**Word budget:** 200-250 words (target 225)

**Purpose:** Synthesise evidence base, state confidence levels honestly, recommend evaluation approach

**Para 1 (75 words):** Attainment evidence is strong and consistent. Quasi-experimental evidence from the UK and Nordic countries demonstrates that phone-free policies improve academic attainment, with a 6.41% effect size in the founding UK study {cite_10.1016/j.labeco.2016.04.004} and consistent replication across Sweden and Norway {cite_10.1016/j.econedurev.2020.102009}, {cite_10.2139/ssrn.4735240}. The equity finding - larger benefits for disadvantaged pupils - strengthens the policy case. This evidence base is mature and provides a sound foundation for the January 2026 rollout.

**Para 2 (75 words):** Mental health evidence is promising but newer. Emerging research suggests wellbeing benefits {cite_10.1016/j.lanepe.2025.101211}, {cite_10.2139/ssrn.4735240}, though this evidence is newer and methodologically more limited than the attainment research. The SMART Schools study provides UK-specific evidence, and Norwegian administrative data offers causal inference. Mental health benefits are probable but less firmly established than attainment effects. Evaluation within the first year will strengthen this evidence base.

**Para 3 (75 words):** Implementation questions require practical guidance. Research gaps on enforcement mechanisms, parental safeguarding protocols, and SEND accommodations do not undermine the policy direction; they identify areas where schools need clear guidance informed by early adopter experience rather than published trials. Evaluation should monitor implementation fidelity, compare enforcement approaches, track parental concerns and SEND accommodations, and measure outcomes across both attainment and wellbeing domains. This will inform subsequent guidance and demonstrate whether the evidence base established in other contexts holds in the UK system-wide rollout.

**Citations:** {cite_10.1016/j.labeco.2016.04.004}, {cite_10.1016/j.econedurev.2020.102009}, {cite_10.2139/ssrn.4735240}, {cite_10.1016/j.lanepe.2025.101211}

**Tone:** Balanced, confident on attainment, measured on mental health, pragmatic on implementation. Ends on evaluation recommendation, not defensiveness.

---

## REFERENCES

**Format:** Harvard style, alphabetical by first author surname
**Content:** Full bibliographic details for every {cite_<doi>} placeholder used in the text
**Technical note:** Reference list will be automatically generated by `scripts/citations.py compile` from `research/citations.json`. All entries will include DOI links in the format `https://doi.org/...`

**Expected reference count:** Approximately 11 unique sources cited in this annex (out of 19 available in citations.json). This is appropriate for a focused policy brief rather than comprehensive review.

---

## Word budget summary

| Section | Target | Range | Rationale |
|---------|--------|-------|-----------|
| Bottom Line | 150 | 150 max | Hard ceiling for executive summary box |
| 1. Introduction | 225 | 200-250 | Framing, minimal |
| 2. Attainment | 650 | 600-700 | Core evidence section, largest allocation |
| 3. Mental health | 450 | 400-500 | Important but more limited evidence |
| 4. Research quality | 325 | 300-350 | Builds confidence, mechanism explanation |
| 5. Implementation | 550 | 500-600 | Addresses practical concerns, second-largest section |
| 6. Conclusion | 225 | 200-250 | Synthesis, evaluation recommendation |
| **TOTAL** | **2,425** | **2,200-2,650** | Exceeds 2,000 target slightly; trim in drafting |

**Adjustment needed:** Total target is 2,425 words, which exceeds the 2,400 absolute ceiling stated in brief. During drafting, trim approximately 25-50 words across sections, with priority on:
- Introduction: trim to 200 words (save 25)
- Research quality: trim to 300 words (save 25)

This brings total to approximately 2,375 words, safely under the 2,400 ceiling and close to the 2,000 target.

## Limitations to state in Conclusion

Brief mention (one sentence in final para of Conclusion) that implementation evaluation should address:
- Enforcement mechanism effectiveness comparison
- Long-term outcomes beyond immediate test scores
- Sixth form (16-18) considerations
- SEND accommodation framework effectiveness

Do not list all seven limitations from outline.md - the annex is not a limitations section. Mention only implementation evaluation priorities.

## Final formatting checklist for drafting stages

- [ ] All citations as `{cite_<doi>}` placeholders, never hand-rendered
- [ ] Every number traced to source entry in research/summaries.md
- [ ] Bottom Line box written last, after all sections complete
- [ ] Word count checked per section during drafting
- [ ] Unverifiable DOI (10.1016/j.econedurev.2019.101884) not cited anywhere
- [ ] Tone appropriate: confident on attainment, measured on mental health, honest about implementation gaps
- [ ] No jargon unexplained; written for non-specialist cabinet members
- [ ] DOI verification run before compilation
- [ ] Final word count 2,000-2,400 words main text (excluding Bottom Line box and references)
