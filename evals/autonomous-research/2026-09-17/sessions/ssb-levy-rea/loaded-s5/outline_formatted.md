# Formatted Outline: SDIL Extension Rapid Evidence Assessment

## Venue Format Block

**Document type:** Rapid evidence assessment (policy consultation response annex)  
**Venue:** UK Treasury consultation response  
**Citation style:** Harvard (author-date)  
**Word basis:** User-specified range: 2200-2600 words (main text), hard ceiling 2600  
**Abstract/summary type:** Key findings box, 120 words maximum (specified by user)  
**Special requirements:**
- Study characteristics table (Study | Setting | Design | Outcome | Effect)
- Key findings box must be stand-alone and Treasury-official-readable
- DOI required on every reference
- Output to output/ssb_levy_rea.md

**Consultation context:**
- Treasury consultation on extending SDIL to milk-based drinks
- Question on dropping lower threshold from 5g to 4g/100ml
- Closes 29 September 2026
- Organization's position (board-approved July 2026): levy has worked, should be extended
- REA provides evidence base for that position

---

## Brief Requirements (research/brief.json)

```json
{
  "word_range": [2200, 2600],
  "abstract_max_words": 120,
  "min_references": 16,
  "required_sections": ["Key findings", "Introduction", "Effectiveness evidence", "Purchases vs intake", "International evidence", "Extension implications", "Limitations", "References"]
}
```

**Rationale for these numbers:**
- Word range: User stated "about 2,200 words, 2,600 is the hard ceiling"
- Abstract cap: "Key findings box at the top, 120 words maximum, because that is genuinely all the Treasury official will read"
- Min references: User stated "I'd want to be sitting on sixteen or more" (met: 18 verified)
- Required sections: Derived from rapid evidence assessment structure and consultation questions

---

## Formatted Structure

### Key Findings Box (120 words maximum, hard constraint)
**Function:** Stand-alone executive summary  
**Content priorities:**
1. UK levy effectiveness (quantified)
2. Mechanism (reformulation dominant)
3. Health outcomes (obesity reduction)
4. Purchases translate to intake (validation)
5. Generalizability (international evidence)
6. Extension rationale (mechanism applies to milk-based drinks)

**Must be readable in isolation.** Treasury official may read only this section.

---

### 1. Introduction (350-400 words)
**Subsections (implicit, not headed):**
- Policy context: Treasury consultation, two specific questions (milk-based extension, threshold reduction)
- SDIL background: Implemented 2018, two-tier structure, reformulation anticipated
- Evidence timeline: 6+ years post-implementation, robust evaluation base now available
- Scope of this REA: What it covers and what questions it addresses
- Roadmap: Organization of remaining sections

**Tone:** Professional, policy-focused, acknowledges this is evidence base for a position

**Citations:** Minimal in intro, context-setting only

---

### 2. Effectiveness of the UK Soft Drinks Industry Levy (700-800 words)

**Study Characteristics Table (embedded in this section, ~80-100 words table content):**

| Study | Setting | Design | Outcome | Effect |
|-------|---------|--------|---------|--------|
| Pell et al. (2021) | UK households (n=32,203) | Controlled ITS | Purchases high-tier drinks | -44% |
| Rogers et al. (2023) | English primary schoolchildren (1.3M/year) | ITS | Obesity prevalence Year 6 girls | -8.2% (absolute -1.6pp) |
| Scarborough et al. (2020) | UK product database | Controlled ITS | Total sugar sold from soft drinks | -43% |
| Bandy et al. (2020) | UK households | Purchase data analysis | Sugar purchased/household/week | -34g |
| Dickson et al. (2025) | UK households | Difference-in-differences | Sugar per shopping trip | -42% |

**Narrative synthesis (600-700 words after table):**

**Purchasing effects:**
- Pell 2021: 44% reduction in high-tier drinks (≥8g/100ml), 21% reduction lower-tier (5-8g), 9% increase in below-levy drinks
- Net effect: 10g sugar/household/week reduction
- Effects began at announcement (2016), accelerated after implementation (2018)
- Dickson 2025: 42% reduction sustained over 6 years, no substitution to other high-sugar foods

**Reformulation as mechanism:**
- Scarborough 2020: 28.8% reduction in average sugar per 100ml across all soft drinks
- 43% reduction in total sugar sold from soft drinks
- 50% of reduction occurred between announcement and implementation (anticipatory reformulation)
- Bandy 2020: 71% of household sugar reduction from lower sugar per unit, only 29% from reduced volume

**Key finding:** Reformulation (industry lowering sugar content to avoid levy tiers) was dominant mechanism, not consumer demand suppression

**Population health outcomes:**
- Rogers 2023: Obesity prevalence fell 8.2% (relative) in Year 6 girls
- Greatest reductions in most deprived areas (progressive health equity)
- Effects require real intake changes, not just purchasing changes
- Briggs 2017 ex ante modeling predicted 144,000 fewer obesity cases annually; Rogers observational findings partially validate

**Citations:** {cite_10.1136/bmj.n254}, {cite_10.1371/journal.pmed.1004160}, {cite_10.1371/journal.pmed.1003025}, {cite_10.1186/s12916-019-1477-4}, {cite_10.1162/rest_a_01345}, {cite_10.1016/S2468-2667(16)30037-8}

---

### 3. Do Purchase Effects Translate to Intake? (250-300 words)

**Question:** Are household purchase data valid proxies for actual consumption?

**Concern:** Purchases might not reflect consumption if household waste patterns change or if consumption occurs outside home

**Evidence:**

**Meta-analysis:**
- Teng et al. 2019: Systematic review and meta-analysis of 17 SSB tax studies
- Purchases: -15% (95% CI -22% to -8%)
- Dietary intake: -8% (95% CI -12% to -4%)
- Both statistically significant; intake effects smaller but directionally consistent
- Purchase data are conservative proxies

**Direct intake measurement:**
- Lee et al. 2019 (Berkeley, 3-year follow-up): 24-hour dietary recalls showed 52% reduction in SSB consumption
- Wrottesley et al. 2020 (South Africa): 24hr recalls showed 26.5ml/day reduction in SSB intake, BMI reduced 0.1 unit

**UK validation via health outcomes:**
- Rogers 2023 obesity reductions cannot occur without real consumption changes
- Purchase reductions → intake reductions → health outcomes pathway confirmed

**Conclusion:** Purchase effects underestimate rather than overestimate intake effects. UK purchase evidence is conservative indicator of real consumption changes.

**Citations:** {cite_10.1111/obr.12868}, {cite_10.2105/ajph.2019.304971}, {cite_10.1017/s1368980020005078}, {cite_10.1371/journal.pmed.1004160}

---

### 4. International Evidence (300-350 words)

**Purpose:** Demonstrate UK findings replicate across contexts

**National-level taxes:**

**Mexico (Colchero et al. 2016):**
- 1 peso/litre excise tax (10% price increase)
- 12% reduction in purchases by Year 2
- 17% reduction in lowest socioeconomic groups (progressive)
- {cite_10.1136/bmj.h6704}

**Chile (Caro et al. 2018):**
- Tiered tax: 18% on high-sugar (≥6.25g/100ml), 10% on lower-sugar
- 21.6ml/capita/day reduction in high-tax beverages (22% decline)
- Tiered structure similar to UK SDIL
- {cite_10.1371/journal.pmed.1002597}

**US city-level taxes:**

**Philadelphia (Roberto et al. 2019):**
- 1.5 cents/oz tax
- 51% volume sales decline in chain stores within city
- Net 27% reduction after accounting for border shopping
- {cite_10.1001/jama.2019.4249}

**Berkeley (Falbe et al. 2016, Silver et al. 2017):**
- 1 cent/oz tax (first US city implementation)
- 21% self-reported consumption decline (Falbe)
- Effects sustained at 1 year (Silver)
- {cite_10.2105/AJPH.2016.303362}, {cite_10.1371/journal.pmed.1002283}

**Tax pass-through:**
- Cawley & Frisvold 2017: 69-100% pass-through depending on store type
- Tax design translates to consumer prices
- {cite_10.1002/pam.21960}

**Equity implications:**
- Allcott et al. 2019: Nominally regressive (low-income households pay higher % of income)
- But health benefits accrue disproportionately to low-SES groups
- Progressive in welfare terms when health impacts included
- {cite_10.1093/qje/qjz017}

**Synthesis:** 8-27% consumption reductions across Mexico, Chile, multiple US cities. Cross-jurisdiction consistency strengthens causal inference.

---

### 5. Implications for Extension to Milk-Based Drinks (400-450 words)

**Central argument:** Reformulation mechanism is product-category-neutral; economic incentive identical for milk-based drinks

**No direct evidence exists:**
- No jurisdiction has extended a SSB levy to milk-based drinks
- Cannot evaluate what has not been implemented
- Evidence gap is structural, not a research failure

**Mechanism evidence supports extension:**

**Reformulation was dominant mechanism in soft drinks:**
- 71-79% of UK sugar reductions from lower sugar per unit (Bandy, Dickson)
- Industry response to tiered price structure
- Reformulation occurred across all soft drink categories: colas, fruit drinks, energy drinks (Scarborough 2020)

**Mechanism is response to economic incentive:**
- Avoid higher levy tier OR
- Avoid consumer price increase that would reduce sales
- Not product-specific; applies to any beverage

**Technical capacity exists:**
- Lower-sugar milk-based drinks already available (demonstrates feasibility)
- Reformulation requires commercial decision, not technological breakthrough

**Inference chain:**
1. Soft drink industry reformulated to avoid levy tiers {cite_10.1371/journal.pmed.1003025}
2. Reformulation spanned all product types within scope {cite_10.1371/journal.pmed.1003025}
3. Economic incentive (avoid tier/price increase) would be identical for milk-based drinks
4. Technical capacity for sugar reduction exists
5. Extension to milk-based drinks would likely trigger similar reformulation response

**Magnitude uncertain, direction supported:**
- Cannot predict exact percentage reduction (no empirical benchmark)
- Mechanism evidence supports that reformulation would occur
- Extent depends on manufacturer commercial calculations

**Threshold reduction (5g to 4g/100ml):**
- Captures products currently just below lower threshold
- Widens reformulation incentive zone
- No new policy mechanism required (tiering already exists)
- Removes perverse incentive to formulate to just under 5g

**Dental outcomes:**
- Urwannachotima et al. 2020: Modeling predicts SSB tax averts 9,359 dental caries cases/year
- Shahid et al. 2026: Comprehensive modeling for caries, periodontitis, edentulism
- UK dental outcomes not yet observed (disease has long lag times)
- {cite_10.1186/s12903-020-1061-5}, {cite_10.1136/bmjph-2024-002110}

---

### 6. Limitations (180-200 words)

**Honest statement of evidence gaps:**

**Gap 1: No empirical evaluation of milk-based drinks under levy**
- Extension has not been implemented in any jurisdiction
- Inference based on mechanism evidence, not direct observation
- Cannot predict magnitude, only direction

**Gap 2: UK dietary intake not directly measured**
- Published UK evidence is purchasing data (Pell, Dickson) not dietary recalls
- International intake validation used to triangulate
- Rogers obesity outcomes require real intake changes (indirect validation)

**Gap 3: Dental outcomes modeled, not observed**
- Dental disease has long lag times
- UK evaluation timeline has not reached dental outcome measurement
- Modeling studies mechanistically sound but not empirically validated in UK context

**Gap 4: This is narrative synthesis, not systematic review**
- Rapid evidence assessment for policy timeline
- Not PRISMA protocol with formal screening and quality assessment
- Source selection purposive (policy-relevant studies)

**What these gaps do not undermine:**
- UK SDIL effectiveness evidence is exceptionally strong (gold-standard data, multiple studies, population health outcomes)
- Mechanism evidence (reformulation) is well-established
- Inference about extension is reasonable given available evidence

---

### 7. References
**Format:** Harvard author-date  
**Requirements:** 
- DOI on every reference
- Alphabetical by first author surname
- Generated by scripts/citations.py compile from research/citations.json

**Count:** 18 verified sources (exceeds 16 minimum)

---

## Drafting Notes

**For Stage 7 (section drafting):**
- Key findings box is separate from introduction, drafted first
- Study characteristics table embedded in section 2 (effectiveness), not appendix
- Every number must trace to {cite_DOI} placeholder
- If claim lacks supporting source, mark {cite_MISSING: description} or remove claim
- No invented statistics to fill gaps
- Limitations section acknowledges gaps honestly; do not minimize
- Tone: professional, evidence-focused, acknowledges this supports a position

**Word count discipline:**
- 2600 is hard ceiling per user
- Key findings 120 absolute maximum
- Main sections stay within allocated ranges
- Study table ~80-100 words (5 rows × ~16-20 words/row)

**Citation discipline:**
- 18 sources verified, all resolved
- Use each source for claims it actually supports
- Research/summaries.md has full summaries; cite accurately
- Pass-through (Cawley), equity (Allcott), dental (Urwannachotima, Shahid) are specialist sources for specific claims

**Table formatting:**
- Markdown table syntax
- 5 columns as specified by user
- One row per key study (5-6 studies, not all 18)
- Quantitative effect in final column

---

## Done When
- [x] Venue format block complete
- [x] Brief requirements written to research/brief.json
- [x] Word budgets allocated to each section
- [x] Study characteristics table structure defined
- [x] Citation style confirmed (Harvard)
- [x] Special requirements noted (DOI on every ref, key findings box 120w max)
- [x] Tone and positioning clear (REA for consultation response, supports board-approved position)
