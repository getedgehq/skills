---
name: people-search
description: Find and rank professional people for recruiting, partnerships, sales, or research from user-provided data, public web sources, an authenticated search session, or a connected provider. Use for people discovery, LinkedIn or Sales Navigator search design, profile-list ranking, or provider filter translation.
---

# People Search

Produce an auditable shortlist without pretending the skill itself grants LinkedIn data access.

## Choose the data mode

Use the strongest mode already available: provided CSV/profiles/export; public web search; an authorized authenticated session; or a connected provider such as HarvestAPI or Apify. If no discovery source is available, return a normalized search plan, ready-to-run filters, and an input template. Never fabricate profiles.

## Workflow

1. Translate the request into [the canonical schema](references/search-schema.md).
2. Separate hard requirements from ranking preferences. Treat vague criteria as preferences unless explicitly mandatory.
3. State the selected mode and its coverage limits.
4. Map canonical filters to provider fields and disclose every applied, approximated, dropped, or unsupported filter.
5. Run the cheapest useful canary before a paid/full search. Stop on invalid, silently empty, or off-target results.
6. Deduplicate by stable profile URL, then normalized name plus current company.
7. Rank against the original brief, preserve evidence URLs, and distinguish sourced facts from inference.
8. Return the shortlist, search recipe, caveats, and highest-value refinement.

## Boundaries

- A skill is orchestration, not a data license. Never imply built-in LinkedIn access.
- Never expose, embed, or persist provider credentials.
- Make the cost-bearing mode clear before paid search; prefer previews and staged expansion.
- Never interpret zero results as no matching people until request validity and filter support are checked.
- Do not send connection requests or messages without separate authorization.

For adapter behavior and result contracts, read [references/provider-contract.md](references/provider-contract.md).

## Deterministic runner

Use `scripts/people_search.py` for plan-only, CSV import/ranking, and provider-canary execution. Provider credentials must enter through the named environment variable at process scope; never pass a token as an argument.
