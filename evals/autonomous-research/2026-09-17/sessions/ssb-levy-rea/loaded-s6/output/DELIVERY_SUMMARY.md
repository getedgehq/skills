# Delivery Summary: SDIL Extension REA

## Delivered File
**output/ssb_levy_rea.md** - Ready for Treasury consultation response

## Specifications Met

### Word Count
- **Main text:** 2,468 words (target: 2,200-2,600 ✓, hard ceiling: 2,600 ✓)
- **Key findings box:** 117 words (max: 120 ✓)
- **Total:** Within specification

### References
- **Count:** 20 sources (minimum: 16 ✓)
- **Verification:** All 20 DOIs resolved ✓
- **Style:** Harvard author-date with DOI on every reference ✓
- **One-to-one mapping:** Every in-text marker → bibliography entry ✓

### Required Elements
- ✓ Key findings box (120w max)
- ✓ Study characteristics table (Study/Setting/Design/Outcome/Effect columns)
- ✓ Harvard citations with DOIs
- ✓ All sections present per brief

### Evidence Coverage
- ✓ UK SDIL evidence (9 sources)
- ✓ International comparators (8 sources: Mexico, US, South Africa)
- ✓ Systematic review/meta-analysis (1 source)
- ✓ Equity and economics (2 sources)
- ✓ Dental outcomes addressed
- ✓ Purchases-versus-intake question addressed
- ✓ Both consultation questions covered:
  - Extension to milk-based drinks
  - Threshold reduction to 4g/100ml

### Evidence Gaps Disclosed
Five gaps explicitly stated in Limitations section:
1. No empirical milk-based drinks evidence (extrapolated from soft drinks)
2. No empirical threshold-change evidence (inferred from 5g behavior)
3. UK intake data limited (international confirms purchases→intake link)
4. Dental benefits modeled not empirically demonstrated for UK levy
5. Long-term health outcomes beyond child obesity not yet observed

## Critical Issue Resolved: Retracted Paper

**Marcus's steer note cited Pell et al. (2021) BMJ (10.1136/bmj.n254) as the key UK purchasing study.**

This paper has been **RETRACTED**.

### Action Taken
Replaced with:
- Rogers et al. (2025) BMJ Nutrition, Prevention & Health (10.1136/bmjnph-2024-000981) - the proper published purchasing analysis
- Rogers et al. (2020) PLOS Medicine (10.1371/journal.pmed.1003269) - anticipatory effects

Both verified and resolved. Retracted paper does not appear in delivered REA.

See **output/RETRACTION_NOTE.md** for full details.

## Evidence Base Quality
- 20/20 sources peer-reviewed or published reports
- Dominated by controlled interrupted time series (robust quasi-experimental design)
- Recent evidence (2016-2026 publication years)
- Includes most recent UK levy impacts (Rogers 2023, 2025; Watt 2024)
- International evidence spans multiple jurisdictions and tax designs

## Position and Evidence
- **Board position (July 2024):** Support extension to milk-based drinks and threshold reduction
- **REA role:** Evidence base for that position
- **Intellectual honesty:** Gaps disclosed where evidence is extrapolated vs observed
- **Tone:** Balanced evidence synthesis, not advocacy

## Consultation Questions Addressed

### 1. Extending levy to milk-based drinks
**Evidence support:** Extrapolated from soft drinks reformulation mechanism (disclosed as gap)
**Rationale:** Same economic incentive, technical feasibility, closes substitution gap
**Key finding:** Extension logical based on mechanism, though not directly observed

### 2. Lowering threshold from 5g to 4g
**Evidence support:** Inferred from manufacturer clustering at 5g (disclosed as gap)
**Rationale:** Economic logic - manufacturers reformulate below thresholds
**Key finding:** 4g threshold would likely drive further reformulation like 5g did

### Equity considerations
**Evidence support:** Strong empirical base (Rogers 2023, 2025; Lal 2017; Colchero 2016)
**Finding:** Financially regressive, health-progressive, net progressive when health valued
**UK specific:** Largest obesity reductions in most deprived areas

## Files Delivered

1. **output/ssb_levy_rea.md** - Final REA with compiled citations
2. **output/RETRACTION_NOTE.md** - Critical alert about retracted paper
3. **research/sources.json** - 20 verified sources
4. **research/sources.md** - Human-readable source list
5. **research/summaries.md** - Detailed source summaries
6. **research/citations.json** - Citation database (all resolved)
7. **research/gaps.md** - Evidence gaps analysis
8. **research/citation-notes.md** - Notes including retraction alert

## Quality Checks Passed

```bash
# All 20 DOIs verified
python3 scripts/citations.py verify -d research/citations.json
# Output: resolved=20 absent=0 unknown=0 invalid=0

# Integrity gate passed
python3 scripts/integrity.py final.md -d research/citations.json -b research/brief.json
# Output: exit_code=0 (no errors)

# Word count verified
python3 scripts/integrity.py final.md --stats
# Output: main text words: 2468, abstract words: 117, reference entries: 20
```

## Ready for Use
The REA is ready to attach as an evidence annex to the Treasury consultation response. Key findings box (117 words) can be lifted to executive summary if needed. Study table provides transparency for technical reviewers.

## Recommendations
1. Inform Marcus about the Pell 2021 retraction
2. Consider whether to note the retraction explicitly in limitations or covering letter
3. Key findings box is under 120w and could be used standalone if Treasury has a summary format requirement
4. Study table is dense but comprehensive - no further abbreviation recommended

---

Delivered by opendraft pipeline: 18 stages, 20 verified sources, zero hallucinated citations.
