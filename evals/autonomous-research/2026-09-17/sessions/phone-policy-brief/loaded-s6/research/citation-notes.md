# Citation Database Notes

**Created:** Stage 4 (Citation Manager)
**Database:** research/citations.json
**Verification status:** All 20 DOIs verified at Crossref/DataCite (resolved=20, absent=0, unknown=0, invalid=0)

## Verification Summary

Ran `citations.py verify -d research/citations.json` immediately after build.

- **20 resolved** (all sources)
- **0 absent** 
- **0 unknown**
- **0 invalid**

All sources ready to cite. No manual intervention needed.

## DOI Status by Source

All 20 sources resolved successfully:

1. 10.1016/j.labeco.2016.04.004 - **resolved** (Beland & Murphy 2016 - headline attainment paper)
2. 10.1016/j.lanepe.2025.101211 - **resolved** (Goodyear SMART Schools 2025)
3. 10.2139/ssrn.4735240 - **resolved** (Abrahamsson 2024 Norwegian study)
4. 10.1016/j.econedurev.2020.102009 - **resolved** (Kessel Swedish study, published)
5. 10.2139/ssrn.3617386 - **resolved** (Kessel SSRN version - superseded by #4)
6. 10.1086/691462 - **resolved** (Ward brain drain 2017)
7. 10.1111/bjet.12943 - **resolved** (Selwyn & Aagaard 2020)
8. 10.1038/s41562-018-0506-1 - **resolved** (Orben & Przybylski 2019)
9. 10.1111/jcpp.13190 - **resolved** (Odgers & Jensen 2020)
10. 10.1016/j.chb.2014.05.011 - **resolved** (Gao 2014)
11. 10.1080/07380569.2023.2211062 - **resolved** (Grigic Magnusson implementation 2023)
12. 10.1080/03634523.2013.767917 - **resolved** (Kuznekoff 2013)
13. 10.1016/j.ijer.2020.101618 - **resolved** (Amez & Baert literature review 2020)
14. 10.1016/j.chbr.2021.100114 - **resolved** (Sunday meta-analysis 2021)
15. 10.1001/jamapediatrics.2025.6422 - **resolved** (Moon 2026 critical letter)
16. 10.1080/15377903.2026.2463294 - **resolved** (Whaley teacher perspectives 2026)
17. 10.3316/informit.504766316839066 - **resolved** (Usmar NZ 2024)
18. 10.58837/chelt.spm.2025.1.02 - **resolved** (Pozsonyi comparative 2025)
19. 10.3316/informit.104193324821827 - **resolved** (Swit student survey 2025)
20. 10.33225/balticste/2020.788 - **resolved** (Dobešová Cakirpaloglu 2020)

## Notes on Specific Sources

### Preprints
- **Abrahamsson (10.2139/ssrn.4735240)**: SSRN preprint, 2024. Not yet peer-reviewed but from credible Norwegian registers. Cite with caveat that it is preprint.
- **Kessel SSRN (10.2139/ssrn.3617386)**: Working paper version. **Superseded by published version** (10.1016/j.econedurev.2020.102009). Do not cite SSRN version separately; cite published journal article.

### Critical voice
- **Moon (10.1001/jamapediatrics.2025.6422)**: Letter to editor in JAMA Pediatrics challenging mental health claims. Must be cited when discussing wellbeing effects to show evidence is contested.

### Implementation sources
- **Grigic Magnusson (10.1080/07380569.2023.2211062)**: One of only two sources on enforcement/implementation complexity. Critical for implementation section.
- **Whaley (10.1080/15377903.2026.2463294)**: Teacher perspectives on implementation. The other implementation source.

## Missing from Database

**Halvorsen & Dahl (2021)**: Described in briefing notes as "single strongest paper in the pile" with "biggest effect sizes." DOI in original reading list (10.1016/j.econedurev.2019.101884) returns 404 (absent at Crossref). Searched for correct DOI but did not find it. 

**Impact:** If paper is as strong as notes claim, its absence is a gap. Brief should either:
1. Find correct DOI and add to database before final draft, OR
2. Acknowledge in limitations that one highly-cited study could not be retrieved due to incorrect DOI

## Citation Style for Brief

**Style:** Harvard (author-date)
**Format:** In-text citations as (Author, Year); bibliography at end with DOIs on every entry
**Legal requirement:** DOIs mandatory (previous annex bounced by legal for untraceable references)

All 20 sources have verified DOIs. No exceptions needed.

## Sources Without DOI

None. All 20 sources have DOIs that resolved successfully at Crossref or DataCite.

## Build Command Used

```bash
python3 scripts/citations.py build research/sources.json -o research/citations.json
```

## Verification Command Used

```bash
python3 scripts/citations.py verify -d research/citations.json
```

Result: `resolved=20 absent=0 unknown=0 invalid=0`

**Status:** Citation database ready for compilation. No manual fixes needed.
