# Citation notes and manual record-keeping

This file records citation-related decisions, removed sources, and anything requiring manual judgment that the automated citation database cannot capture.

## Removed DOIs (verification failures)

### 10.1016/j.econedurev.2019.101884
**Title (from reading list):** Phone-free schools and classroom concentration: evidence from a Norwegian reform  
**Authors:** Halvorsen, Marit; Dahl, Sigrid  
**Year:** 2021  
**Venue:** Economics of Education Review  
**Status:** absent (404 from both Crossref and DataCite)  
**Reason for removal:** DOI in original reading list does not resolve. Searched for correct DOI via Crossref ("Halvorsen Dahl Economics Education Review phone") but paper not found. This may be:
1. Incorrect DOI in reading list (transcription error)
2. Paper not yet published despite 2021 date in notes
3. Paper published under different title/authors
4. Pre-publication information that did not materialize

**Action taken:** Removed from database. Brief notes stated this was "strongest paper in the pile, biggest effects" and a key Norwegian study. Without verifiable DOI, cannot cite. Will need to adjust arguments that relied on this source.

**All placeholders removed:** All instances of {cite_10.1016/j.econedurev.2019.101884} must be removed from summaries.md, gaps.md, and any drafted sections.

**Impact on source count:** Reduces verified pool from 18 to 17 sources. Brief specified 17-18 minimum, so still within target range, but close to floor.

## Sources without DOIs

None. All 18 sources in original pool had DOIs; one (above) failed verification.

## Verification summary (post-removal)

**Total sources in pool:** 17  
**Resolved:** 17  
**Absent:** 0 (removed above)  
**Unknown:** 0  
**Invalid:** 0

All remaining sources have verified DOIs pointing to retrievable metadata at Crossref or DataCite.

## Preprints in database

### 10.2139/ssrn.4735240 (Abrahamsson 2024)
**Status:** resolved (SSRN preprint)  
**Note:** Recent preprint (2024), awaiting peer review. SSRN DOIs resolve at DataCite. Flagged as preprint in sources.md and will be marked as such in citations. Acceptable given recency (under 12 months old) and unique contribution (Norwegian administrative data on both outcomes and mental health).

## Notes on author names

All author names preserved as returned by Crossref/OpenAlex:
- Family and given name structure maintained
- Empty `given` fields (where only family name was deposited) left empty, not filled in
- No initials invented for missing given names
- Special characters (e.g., ö, å, ø in Nordic names) preserved exactly as in metadata

## Notes for Architect (stage 5) and Crafter (stage 7)

**Impact of Halvorsen & Dahl removal:**
- gaps.md references this source in multiple places as evidence for "biggest effect sizes" and "strongest paper"
- These claims now unsupported and must be removed or hedged
- Norwegian evidence base reduced to Abrahamsson 2024 preprint alone
- Attainment section word budget may need adjustment if this was planned as major source

**Recommendation:** Proceed with 17 verified sources. This meets minimum (brief specified 17-18, paper-types.md specifies 15+ for evidence brief). If Halvorsen & Dahl paper is critical, option to return to stage 1 for replacement Norwegian/Nordic attainment study, but 17 sources is sufficient to proceed.

## Citation style notes

Style will be determined at stage 6 (Formatter). Brief specifies Harvard author-date. All 17 sources have complete author lists in database, so Harvard (Author Year) format is fully supported.

## Integrity pre-check

Before stage 7 begins drafting, all files referencing the removed DOI must be updated:
- `research/sources.md`: Remove source entry #3
- `research/summaries.md`: Remove summary entry #3  
- `research/gaps.md`: Remove or qualify any claims resting on Halvorsen & Dahl as "strongest paper"

These files will be updated after this stage completes, before proceeding to stage 5.
