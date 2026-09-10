---
name: openpaper
description: Write a complete, source-backed research paper from one topic line, with in-text citation markers that map one-to-one to the bibliography and every printed DOI resolved at Crossref or DataCite. No API key. Use when someone asks to "write a research paper", "do a literature review", "draft a thesis chapter", "find sources on X and write it up", or names openpaper/opendraft.
---

# openpaper

Turns one topic line into a finished paper. The workflow is derived from OpenDraft
(github.com/federicodeponte/opendraft, MIT) and uses public scholarly metadata APIs.

**You are the model.** No key, no service, no account. The only network calls are
Crossref, OpenAlex and DataCite, all open endpoints.

## The one command

```
Write a paper on <topic>
```

Then run the seven phases below in order. Do not skip a phase because the topic
looks easy. Phase 4 is the one that makes this different from a chatbot writing
an essay, and phase 6 is the one that stops a broken paper from reaching anyone.

## 1. Scope

Turn the topic into a claim the paper argues, not a subject it surveys.
Pick the citation style now: numeric (IEEE, Vancouver, ACM) or author-year (APA,
Harvard, Chicago, MLA). It changes how markers render and how the bibliography
is ordered, so it cannot be decided later.

## 2. Find real sources first

```bash
python3 scripts/sources.py find "<topic>" --n 15
```

Returns DOI, title, authors, year and venue from Crossref, topped up from
OpenAlex. **Read these before writing a word.** You are writing from what exists,
not recalling what sounds right. Search two or three narrower sub-queries as well
if the first pass is thin; a paper with five sources reads like one with five
sources.

Never write a citation you did not get from this step.

## 3. Structure

Outline the argument, then assign specific sources to specific sections. A
section with no source assigned is a section you cannot write yet: go back to
phase 2 with a narrower query.

## 4. Compose with placeholder markers

Write the prose using `{cite_<doi>}` inline wherever a claim leans on a source.
Never write a rendered marker like `[3]` or `(Smith, 2020)` by hand. The
placeholder carries the DOI, so the mapping between prose and bibliography is
mechanical rather than remembered.

Each claim that rests on a source gets a marker at the point of the claim, not
gathered at the end of the paragraph.

## 5. Verify every DOI, then render

```bash
python3 scripts/sources.py verify <doi> <doi> ...
```

Three network states, and `unknown` is never quietly turned into `absent`:

- **resolved** — Crossref or DataCite returned the record. Cite it.
- **absent** — both returned 404. **Drop it.** Do not repair it, do not guess a
  replacement DOI, go back to phase 2 for a real source.
- **unknown** — a network or rate-limit failure. Retry once, then say so in the
  paper's limitations rather than pretending it resolved.

An empty DOI is `invalid`. The verification command exits nonzero for `absent`,
`unknown`, or `invalid`; only a fully resolved set exits zero.

arXiv preprints resolve at DataCite and 404 at Crossref, which is why the check
runs both. A Crossref-only check silently deletes every preprint.

Then render: number the bibliography **by first appearance in the text** for
numeric styles, alphabetically for author-year. Replace each `{cite_<doi>}` with
the rendered marker for that entry.

## 6. The integrity gate, non-negotiable

Before showing anyone the paper, check all five. Any failure means fix it, not
ship it with a caveat:

1. **Zero surviving `{cite_` placeholders** in the output.
2. **Every bibliography entry is pointed at** by at least one in-text marker.
   An entry nothing points at is padding; remove it or cite it.
3. **Every in-text marker resolves** to an entry. For numeric styles, `[n]`
   must land on entry `n`.
4. **No stranded punctuation** left where a marker was removed: ` .`, ` ,`,
   doubled spaces.
5. **Numeric bibliographies carry their numbers.** `[1]`, `[2]` in front of each
   entry. Prose citing `[1]` to `[27]` against an unnumbered alphabetical list is
   the single most common way this output becomes unusable, and it is invisible
   until you read the rendered document rather than the markdown.

## 7. State the limits in the paper

One short section, plainly worded:

- Sources without a DOI are printed unchecked.
- A resolved DOI proves the work exists. It does not prove it supports the
  sentence citing it.
- Name any source that came back `unknown`.

## What this does not do

It writes a first draft with a real literature base. It does not do your
fieldwork, replace peer review, or make you the author of something you have not
read. Read the sources before you put your name on it.

## Claims you may make about the output

Permitted, because they are enforced above: markers map one-to-one to the
bibliography; every printed DOI resolved at Crossref or DataCite; sources without
a DOI are printed unchecked.

Forbidden: "every citation is real", "no hallucinations", "verified citations",
zero errors, exhaustive research, any accuracy guarantee.
