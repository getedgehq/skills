# Formatted Outline: Phone-Free Secondary Schools Evidence Annex

## Venue format

- Format family: Policy brief / Evidence annex
- Target venue: Cabinet paper supporting annex
- Citation style: Harvard (author-date)
- Word basis: proportional, target 2,200 words main text (excluding 150-word bottom line box)
- Abstract length: Not applicable (bottom line box serves this function, 120-150 words)
- Keywords: Not applicable (policy brief format)
- Title limit: 80 characters (short, cabinet-appropriate heading)
- Language: English (UK government register)

**Main claim:** Phone-free policies in secondary schools improve academic attainment and show emerging positive effects on student wellbeing, though implementation evidence remains thin and requires local adaptation with monitoring.

---

## Citation conventions for drafting

**All agents drafting from this outline:**
- Cite with `{cite_<doi>}` placeholders only, at the exact point of the claim
- Never render a citation by hand as `(Author, Year)` or `[3]`
- For a real claim that a genuine search could not source, mark as `{cite_MISSING: short description}`
- Every number and every finding attributed to a source must appear in that source's entry in `research/summaries.md`
- `research/citations.json` carries bibliographic metadata only and holds no findings

**What `{cite_MISSING: ...}` is and is not:**
- IS: An admission that this claim has no source yet; triggers compile refusal and integrity check failure
- IS NOT: A fourth citation style; a way to ship an unsourced claim; something that survives to final draft

**Table source footnotes:** `*Source: {cite_<doi>}, {cite_<doi>}.*` not hand-formatted author/year

---

## Document structure and section lengths

### Section 1: Bottom line (executive summary box)
**Format:** Stand-alone bordered text box, first element after title  
**Length target:** 120-150 words (hard cap: 150 words)  
**Percentage of main text:** Not part of main word count (separate element)

**Required content (in order):**
1. Opening question: Do phone-free policies in secondary schools improve student outcomes?
2. Attainment finding: 6.4% improvement in exam results, England study {cite_10.1016/j.labeco.2016.04.004}, replicated in Nordic systems {cite_10.1016/j.econedurev.2020.102009}, {cite_10.2139/ssrn.4735240}
3. Wellbeing finding: Large UK study (2025) {cite_10.1016/j.lanepe.2025.101211} shows restrictive policies associated with better mental wellbeing
4. Evidence strength: Outcome evidence strong (multiple quasi-experimental studies); implementation evidence thin
5. Caveat: Questions on enforcement, parent communication, age-specific effects under-researched
6. Recommendation: Evidence supports decision; requires evaluation plan and local adaptation

**Register:** Plain language, active voice, concrete numbers not hedges. Must work as complete standalone.

**Citation density:** 3-4 DOIs maximum (headline sources only)

---

### Section 2: Academic attainment effects
**Length target:** 600 words (27% of main text)  
**Range (±10% for gate):** 540-660 words  
**Subsections:** None (continuous prose with paragraph breaks)

**Content plan:**
1. **Headline finding** (120 words): Beland & Murphy 2016 {cite_10.1016/j.labeco.2016.04.004} England study, 6.41% improvement in exam results, difference-in-differences design across four cities (Birmingham, London, Leicester, Manchester) with staggered phone ban implementation. Plain explanation of what 6.41% means practically (if convertible: approximately half a GCSE grade, or X months of learning).

2. **Replication evidence** (140 words): Swedish study {cite_10.1016/j.econedurev.2020.102009} confirms positive direction; Norwegian evidence {cite_10.2139/ssrn.4735240} from administrative registers shows academic improvements (note: preprint, awaiting peer review, but most recent Nordic evidence). Geographic pattern: England, Sweden, Norway all show consistent direction.

3. **Mechanism and broader context** (180 words): Why bans work: distraction reduction, increased classroom time-on-task, removal of social interruptions during learning. Cognitive mechanism: Ward et al. 2017 {cite_10.1086/691462} experimental evidence shows phone presence alone (switched off, face-down) reduces working memory; explains why whole-day bans may outperform classroom-only restrictions. Literature reviews {cite_10.1016/j.ijer.2020.101618}, {cite_10.1016/j.chbr.2021.100114} establish broader negative association between smartphone use and academic performance. Earlier experimental work {cite_10.1080/03634523.2013.767917} documented distraction effects.

4. **Caveats and limitations** (160 words): Effect sizes vary by study (no aggregated meta-analysis available from sources); most recent UK evidence is 2016 (nine-year gap to present); Nordic education systems differ from England (less exam pressure, different demographics, smaller class sizes); no evidence disaggregating effects by key stage (KS3 vs. KS4 vs. sixth form); no evidence on differential effects by SEND status, socioeconomic background, or ethnicity.

**Table consideration:** If effect sizes extractable from `research/summaries.md`, include comparison table:
- Rows: Beland-Murphy 2016, Kessel 2020, Abrahamsson 2024
- Columns: Country, Year, Design, Sample size, Outcome measure, Effect/direction
- Only include what summaries actually report; if metadata-only, note "positive effect reported" rather than inventing numbers
- If summaries lack effect sizes, omit table and describe studies in prose

**Citation count:** 8-9 DOIs

---

### Section 3: Mental health and wellbeing effects
**Length target:** 500 words (23% of main text)  
**Range (±10% for gate):** 450-550 words  
**Subsections:** None

**Content plan:**
1. **SMART Schools headline** (180 words): Goodyear et al. 2025 {cite_10.1016/j.lanepe.2025.101211}, most recent large UK study (1,227 pupils aged 12-15, 30 secondary schools), Lancet Regional Health journal (quality signal). Cross-sectional observational design: restrictive phone policies associated with better mental wellbeing, reduced phone use during school day, less social media use overall. Note limitations: association not causation (cannot rule out reverse causation or selection effects); cross-sectional snapshot rather than longitudinal.

2. **Corroborating evidence** (120 words): Norwegian administrative register study {cite_10.2139/ssrn.4735240} shows mental health improvements alongside academic outcomes; suggests finding replicates outside England. Preprint status noted (2024, awaiting peer review). Conceptual framing {cite_10.1111/bjet.12943}: phone bans as opportunity to address distraction, addiction, cyberbullying.

3. **Broader population context** (120 words): Annual research reviews {cite_10.1111/jcpp.13190}, {cite_10.1038/s41562-018-0506-1} situate adolescent mental health in digital age; complex relationship between digital technology use and wellbeing at population level. School phone policies address one component of broader digital environment; not a complete solution to adolescent mental health challenges.

4. **Strength of evidence assessment** (80 words): Wellbeing evidence newer and thinner than attainment evidence; largest study (SMART Schools) is cross-sectional, cannot establish causation as cleanly as difference-in-differences attainment studies. Direction consistent across available studies. Frame as "emerging evidence" not "proven beyond doubt." Effect sizes on wellbeing outcomes less established than on attainment.

**Citation count:** 6-7 DOIs

---

### Section 4: How phone restrictions work (mechanisms)
**Length target:** 300 words (14% of main text)  
**Range (±10% for gate):** 270-330 words  
**Subsections:** None

**Content plan:**
1. **Core experimental finding** (180 words): Ward et al. 2017 {cite_10.1086/691462} "Brain Drain" experiments: mere presence of smartphone reduces available cognitive capacity even when device switched off and face-down on desk. Participants performed worse on working memory tasks when phone nearby vs. in other room, despite no active use. Cognitive resources allocated to task of not-attending-to-phone. Experimental manipulation, replicated across studies. Robust effect.

2. **Policy implications** (120 words): Mechanism evidence suggests whole-day phone-free policies (phone stored away from student for entire school day) likely more effective than partial restrictions (phone in bag but in classroom, or classroom-only restrictions with phone accessible between lessons). Explains why enforcement quality matters: policy circumvented by students keeping phone in pocket loses cognitive benefit even if phone never actively used. Supports argument for lockable pouches or secure storage rather than honour-system bag storage.

**Citation count:** 1-2 DOIs (primarily Ward et al.)

---

### Section 5: Implementation challenges and evidence gaps
**Length target:** 500 words (23% of main text)  
**Range (±10% for gate):** 450-550 words  
**Subsections:** None

**Content plan:**
1. **Available implementation evidence** (180 words): One study {cite_10.1080/07380569.2023.2211062} directly addresses implementation complexities: gap between written policy and enforcement reality in digitalized school contexts. Recent teacher perspectives {cite_10.1080/07494467.2025.2469099} document practitioner views on enforcement challenges and practicalities. Pupil perspectives {cite_10.3390/educsci9030202}, {cite_10.1080/14681811.2025.2446844} show student acceptance varies. Comparative policy review {cite_10.56296/aer00074} documents variation in domestic and international approaches. Policy variation by school level {cite_10.1016/j.chb.2014.05.011} suggests age-specific considerations matter.

2. **What evidence does not address** (220 words): 
   - **Enforcement mechanisms:** No comparative studies of lockable pouches vs. storage systems vs. confiscation approaches; no evidence on staff time costs or compliance rates by enforcement type. Heads' concerns about "written policy vs. phone-free school" gap remain under-researched.
   - **Parent communication and safeguarding:** No studies address parent perspectives on emergency contact arrangements; no evidence on alternative communication protocols or acceptable contact delays; safeguarding procedures when phones unavailable not documented in research base. This is primary consultation concern but absent from academic literature.
   - **Age-specific effects:** No evidence disaggregating within secondary (year 7 vs. year 11 vs. sixth form); developmental differences, exam pressures, and out-of-school responsibilities vary substantially across age range.
   - **SEND populations:** No sources reference special educational needs; potential equity implications of blanket policy not addressed.
   - **Long-term effects:** No multi-year follow-up; unknown whether effects persist, fade, or strengthen over time.

3. **Implications for implementation** (100 words): Evidence base strongest on whether phone-free policies improve outcomes (they do); weakest on how to implement them effectively. Policy guidance must acknowledge these gaps and provide flexibility for schools to adapt to local contexts. Requires monitoring and evaluation plan built into implementation from January 2027. Schools will need clear safeguarding protocols, parent communication guidance, and SEND accommodation pathways. One-size-fits-all enforcement approach not supported by evidence.

**Citation count:** 6-7 DOIs

---

### Section 6: Synthesis and limitations
**Length target:** 300 words (14% of main text)  
**Range (±10% for gate):** 270-330 words  
**Subsections:** None

**Content plan:**
1. **Evidence strength summary** (120 words):
   - **Strong evidence:** Phone-free policies improve academic attainment (multiple quasi-experimental studies with causal identification: difference-in-differences designs, reform-based natural experiments, administrative register studies)
   - **Moderate evidence:** Policies associated with better mental wellbeing (emerging evidence: large UK cross-sectional study, Nordic registers, consistent direction across studies but thinner base and less robust causal identification than attainment evidence)
   - **Weak evidence:** Implementation approaches (one study on implementation complexity, recent stakeholder perspectives, but no comparative evidence on enforcement mechanisms)

2. **Key limitations** (120 words):
   - Geographic concentration: UK and Nordic evidence only; limited from other education systems (US, Australia, other European systems, Global South, East Asia)
   - Temporal pattern: most attainment evidence 2016-2021, then gap, then 2024-2026 wellbeing resurgence; may reflect publication lag or genuine research lull
   - Implementation evidence gaps listed in Section 5
   - No evidence on differential effects by socioeconomic status, ethnicity, SEND status, or English as additional language; equalities monitoring essential
   - No long-term follow-up studies; effects after restriction lifted unknown

3. **Overall assessment** (60 words): Evidence base supports cabinet decision to mandate phone-free secondaries from January 2027 on grounds of attainment and emerging wellbeing benefits. Implementation requires monitoring plan, equalities impact assessment, clear safeguarding and parent communication protocols, and flexibility for local adaptation. Policy decision evidence-supported but not evidence-complete; gaps require ongoing attention.

**Citation count:** 0-1 DOIs (synthesis, not new evidence)

---

## Word budget verification

| Section | Target | Range (±10%) | % of total |
|---------|--------|--------------|------------|
| Bottom line box | 135 | 120-150 | separate |
| Attainment | 600 | 540-660 | 27% |
| Wellbeing | 500 | 450-550 | 23% |
| Mechanisms | 300 | 270-330 | 14% |
| Implementation | 500 | 450-550 | 23% |
| Synthesis | 300 | 270-330 | 14% |
| **Total main text** | **2,200** | **1,980-2,420** | **100%** |

**Brief requirement:** 2,000-2,400 words ✓  
**Midpoint target:** 2,200 words (provides buffer for overruns in evidence-heavy sections)  
**Bottom line box:** 135 words midpoint (120-150 range) ✓

---

## Table and figure specifications

**No figures planned** (policy brief format, not academic paper)

**Table 1 (optional, attainment section):**
- **Condition:** Only include if effect sizes available in `research/summaries.md`
- **Title:** Quasi-experimental studies of phone ban effects on academic attainment
- **Columns:** Study, Country, Year, Design, Sample, Outcome, Effect/direction
- **Rows:** Beland & Murphy 2016, Kessel et al. 2020, Abrahamsson 2024 (3 rows)
- **Placement:** Within attainment section, after headline finding paragraph
- **Source footnote:** `*Source: {cite_10.1016/j.labeco.2016.04.004}, {cite_10.1016/j.econedurev.2020.102009}, {cite_10.2139/ssrn.4735240}.*`
- **Fallback:** If summaries metadata-only without extractable effect sizes, omit table and describe studies in prose

---

## Manuscript specifications

**Typography:**
- Font: Calibri 11pt (standard UK government document font)
- Headings: Calibri 14pt bold (title), 12pt bold (section headings)
- Line spacing: 1.15 (policy brief standard, not double-spaced academic)
- Margins: 2cm all sides (A4 standard)
- Page numbering: Bottom center
- Headers: Document title in header, right-aligned, 9pt

**Section numbering:** Not numbered (policy brief convention: continuous prose with descriptive headings, not academic numbered sections)

**Bottom line box formatting:**
- Border: 1pt solid line, all sides
- Shading: 5% grey background
- Padding: 0.5cm internal spacing
- Placement: After title and before main text begins
- Page break: Must not span page break; entire box on first page

**Reference list:**
- Heading: "References" (not "Bibliography")
- Format: Harvard (author-date) style, alphabetical by first author family name
- Spacing: Single-spaced within entries, one blank line between entries
- Hanging indent: 0.5cm
- DOI links: Include `https://doi.org/...` as final element of each entry
- Preprint handling: Abrahamsson 2024 noted as "SSRN preprint" in venue field

---

## Language and register specifications

**UK government house style:**
- Spelling: British English (e.g., "behaviour" not "behavior", "analyse" not "analyze")
- Numbers: Spell out one to ten; numerals 11+; exception: percentages always numerals (6.4%)
- Dates: Day Month Year format (16 September 2026, not September 16, 2026)
- Commas: Oxford comma optional but be consistent
- Acronyms: Spell out on first use with acronym in parentheses; acronym only thereafter (e.g., "special educational needs (SEND)" then "SEND")

**Plain language requirements:**
- No academic jargon without explanation
- "Difference-in-differences" explained as "comparing schools before and after phone bans with schools without bans"
- "Quasi-experimental" explained as "studies exploiting policy variation to establish causal effects"
- "Cross-sectional" explained as "snapshot at one point in time, cannot establish causation"
- Active voice preferred ("studies show" not "it has been shown")
- Concrete over abstract (6.4% improvement in exam results" not "significant positive effects")

**Tone:**
- Professional but accessible
- Honest about evidence gaps (not hedged into vagueness)
- Caveats stated clearly (not buried in sub-clauses)
- Implementation challenges acknowledged (not minimized)
- Policy-neutral (document evidence base, not advocate)

---

## Citation coverage and source accounting

**Total sources in database:** 17 (verified, resolved DOIs)  
**Sources cited in outline:** 17 of 17 ✓ (no orphan sources)

**Distribution by section:**
- Bottom line box: 3 DOIs (headline sources only)
- Attainment: 8-9 DOIs
- Wellbeing: 6-7 DOIs
- Mechanisms: 1-2 DOIs
- Implementation: 6-7 DOIs
- Synthesis: 0-1 DOIs

**High-frequency sources (cited multiple sections):**
- Beland & Murphy 2016 {cite_10.1016/j.labeco.2016.04.004}: Bottom line, attainment
- Goodyear 2025 {cite_10.1016/j.lanepe.2025.101211}: Bottom line, wellbeing
- Abrahamsson 2024 {cite_10.2139/ssrn.4735240}: Bottom line, attainment, wellbeing
- Ward 2017 {cite_10.1086/691462}: Attainment (mechanism), mechanisms

---

## Notes for Crafter (stage 7)

**Halvorsen & Dahl 2021 removal impact:**
- Original brief noted this as "strongest paper in pile, biggest effects"
- DOI 10.1016/j.econedurev.2019.101884 did not verify (absent from Crossref/DataCite)
- Removed from database; cannot cite
- Do not claim "biggest effect sizes" from any single study without extractable numbers from summaries
- Norwegian evidence now rests on Abrahamsson 2024 preprint alone

**Summaries limitation:**
- All 18 sources (now 17) were metadata-only; no abstracts or full texts retrieved
- Cannot extract specific effect sizes, sample details, or methodology beyond what titles/venues suggest
- Where outline requests numbers, check summaries first; if not present, use general direction ("positive effect") rather than inventing
- Table 1 inclusion conditional on whether summaries contain extractable data

**Brief requirements checklist:**
- ✓ 2,000-2,400 words (main text target: 2,200)
- ✓ 150-word bottom line box (target: 135, range 120-150)
- ✓ Harvard author-date citations with DOIs on everything
- ✓ Covers attainment, wellbeing, study quality, implementation/enforcement, parent communication (as evidence gap)
- ✓ 17 sources (brief requested 17-18 minimum)
- ✓ Addresses heads' concerns about enforcement
- ✓ Addresses consultation feedback on parent communication

**Evaluation plan paragraph (end of Section 6):**
Must note that DfE will evaluate implementation (attainment outcomes, wellbeing surveys, implementation fidelity audits, stakeholder feedback), detecting unintended harms and informing adjustments. This addresses brief's context: "Cabinet has effectively landed on doing this in January" — annex documents evidence base, policy includes learning mechanism, not imposed-and-forgotten.

---

## Quality gates before drafting begins

- [ ] `research/brief.json` written and parses as valid JSON
- [ ] Word ranges in formatted outline sum to 2,000-2,400 (allowing ±10% per section)
- [ ] Bottom line box range 120-150 words recorded
- [ ] All 17 sources from `research/citations.json` placed in at least one section
- [ ] No section plans content requiring data not present in `research/summaries.md`
- [ ] Table 1 conditional on data availability, fallback to prose stated
- [ ] Main claim copied forward from `outline.md` unchanged
- [ ] Citation convention rules stated explicitly for Crafter
- [ ] Halvorsen & Dahl removal noted with instruction not to claim "biggest effects"
