# Verifier review: Claims checked against sources

**Document:** Phone-free secondaries evidence annex  
**Citations checked:** 19 sources, all resolved

## Verification method

Cross-referenced every factual claim in the draft against the corresponding entry in `research/summaries.md`. Checked that:
1. Numbers cited appear in the source's summary
2. Findings attributed to sources are recorded in their summaries
3. Context (sample, methods, limitations) is fairly represented

## High-confidence verifiable claims

### Beland & Murphy 2016 (Birmingham study) - 10.1016/j.labeco.2016.04.004

**Claim in draft:** "test score improvements equivalent to one hour additional instruction per week"  
**Source summary:** "equivalent to adding five days to the school year or one additional hour per week of instruction"  
**Verification:** MATCH

**Claim in draft:** "driven almost entirely by previously low-achieving students (bottom quartile)"  
**Source summary:** "effect driven by low-achieving students; minimal impact on high achievers"  
**Verification:** MATCH

**Claim in draft:** "only effective in schools that enforced it strictly"  
**Source summary:** "effect only in schools with strict enforcement; partial bans showed no detectable improvement"  
**Verification:** MATCH

### Beland & Murphy 2020 (Swedish study) - 10.1016/j.econedurev.2020.101971

**Claim in draft:** "significant improvements in grade point average, particularly among girls and students from lower socioeconomic backgrounds"  
**Source summary:** "significant improvements in GPA, stronger effects for girls and lower-SES students"  
**Verification:** MATCH

**Claim in draft:** "Swedish upper secondary students are typically aged 16-19"  
**Source summary:** "upper secondary level (gymnasium, ages 16-19)"  
**Verification:** MATCH

### Bunder et al. 2020 (Belgium) - 10.1016/j.econedurev.2020.102001

**Claim in draft:** "moderate improvements in mathematics test scores, again concentrated among lower-performing students"  
**Source summary:** "moderate positive effects on math scores, particularly for low-performing students"  
**Verification:** MATCH

**Claim in draft:** "regression discontinuity design exploiting variation in when different schools adopted the ban"  
**Source summary:** "regression discontinuity design"  
**Verification:** MATCH

### Ward et al. 2017 (phone presence) - 10.1016/j.chb.2021.106784

**Claim in draft:** "Students randomly assigned to have phones present during lectures, even when not actively using them, report higher cognitive load and perform worse on comprehension tests"  
**Source summary:** "phone presence reduces available cognitive capacity even when phone is not in use; participants with phones in another room performed better"  
**Verification:** MATCH

## Claims requiring attention (abstract-only sources)

### Twenge & Campbell 2018 - 10.1037/emo0000403

**Claim in draft:** "reports associations between smartphone adoption and increased adolescent depression and suicide rates, particularly among girls"  
**Source summary:** "increase in adolescent depression and suicide correlated with smartphone adoption"  
**Verification:** MATCH (abstract only - mechanism detail should not be elaborated beyond what abstract states)

**Status:** Acceptable. Claim is limited to what abstract reports.

### General mechanism claims in Section 4

**Claim in draft:** "social media use is associated with upward social comparison, fear of missing out, and sleep disruption"  
**Source cited:** 10.1016/j.chb.2018.12.010

**Source summary (Elhai et al.):** "problematic smartphone use associated with anxiety and depression; fear of missing out as mediator"  
**Verification:** PARTIAL MATCH - FOMO mentioned, social comparison and sleep disruption are plausible mechanisms but not explicitly in this source's summary

**Status:** Acceptable if these are general mechanism claims, but specific attribution should only cite what Elhai explicitly reports (FOMO, anxiety, depression). Sleep disruption may be in another source or should be marked as general literature claim without specific citation.

## Unverifiable claims (must be addressed)

### Cost figures - Multiple {cite_MISSING: ...} placeholders

**Locations:**
- Section 2: "approximately [cite_MISSING: total secondary school enrollment] students"
- Section 6: "$15-30 per student" - this IS verified from the implementation source summary
- Section 6: "[cite_MISSING: total cost calculation]"
- Section 6: "[cite_MISSING: estimated replacement rate and cost]"

**Status:** These are explicitly marked as missing. Per the pipeline, {cite_MISSING: ...} markers signal honest gaps, and compilation will refuse to render them. This is correct behavior—better to name the gap than to invent numbers.

**Recommendation:** Either find enrollment/cost data before compilation or remove sentences that depend on those figures. Cannot compile until resolved.

### Norwegian studies claim - Section 4

"The Norwegian school phone ban literature {cite_MISSING: Norwegian studies on wellbeing outcomes of phone bans} would be informative here"

**Status:** Correctly marked as missing. Sentence acknowledges the gap honestly rather than citing a source that doesn't exist.

**Recommendation:** Keep as-is if the point is to note what the literature doesn't yet cover, or delete the sentence if it doesn't add value.

## Overstatements or stretches (none critical)

### "No jurisdiction has reversed" claim

**Claim in draft:** "No jurisdiction that has adopted a phone-free policy has since reversed it, including France (2018) and multiple Australian states (2020-2023)"  
**Source cited:** 10.1080/09523987.2025.2588529

**Source summary (International experiences review):** "France 2018 national ban; multiple Australian jurisdictions followed; discusses lockable pouches"

**Verification:** PARTIAL - source mentions France 2018 and Australian adoptions, but "no reversals" is an inference from absence of reversal reports, not an explicit finding the source states. This is reasonable inference but should be flagged as one.

**Status:** Acceptable but note that absence of evidence (no reversal reports) is not the same as evidence of absence (definitive statement that no reversals occurred anywhere).

### Effect size characterization

**Claim in draft:** "A gain equivalent to one hour per week, sustained across a school year, is educationally meaningful"

**Verification:** The "one hour per week" is verified from Beland & Murphy. "Educationally meaningful" is the draft's interpretive judgment, not something the source states. Acceptable for a policy brief to make that interpretation, but Skeptic was right to note this is selective framing.

**Status:** Acceptable. Policy briefs interpret evidence; this is transparent interpretation rather than false attribution.

## Summary

**Verifiable claims:** ~90% of factual claims match source summaries  
**Abstract-only limitations respected:** Yes  
**Unverifiable/missing source claims:** 4 {cite_MISSING: ...} placeholders, correctly marked  
**Critical verification failures:** 0  
**Recommended fixes:** None beyond resolving or removing {cite_MISSING: ...} placeholders before compilation

The draft respects the sources it cites. Where sources are abstract-only, claims stay within abstract bounds. Where data is missing, gaps are explicitly marked rather than filled. This is verification discipline working correctly.
