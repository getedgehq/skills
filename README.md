# Edge Skills

Edge gives your AI agent the right expert skill for the task at hand. It searches 100,000+ security-screened public skills, picks the best fit, and loads a pinned version for that task. Works in Claude Code, Codex, Cursor and the Claude app.

**Set up Edge:** paste `set up https://getedge.cc/SKILL.md` into your agent. Details on [getedge.cc](https://getedge.cc/).

## Benchmarks

Explore [Edge's benchmark evidence](benchmarks/): published results, study protocols, task manifests and reanalysis scripts, alongside credited external research. Browse the [interactive benchmarks](https://getedge.cc/benchmarks/) for outcomes and method details.

## What can Edge find?

These are examples returned by production `find_skill` on 2026-09-29; they are third-party catalog results, not packages maintained in this repository. Results can change.

| Your task | Skill Edge returned first |
| --- | --- |
| Write a CFO outbound email sequence | `onewave-ai/claude-skills@cold-email-sequence-generator` |
| Create an investor pitch deck | `manojbajaj95/claude-gtm-plugin@pitch-deck-creation` |
| Analyze a sales CSV | `claude-office-skills/skills@data-analysis` |
| Write a competitor positioning brief | `phuryn/pm-skills@competitor-analysis` |

Edge scans packages, mirrors available third-party scanner reports, and loads pinned revisions. A scan reports findings within its stated scope; it is not a safety guarantee. Browse the [skill evidence hub](https://getedge.cc/skill-evidence/) or individual pages for [product launch video](https://getedge.cc/skills/product-launch-video/), [autonomous research](https://getedge.cc/skills/autonomous-research/), and [workplan](https://getedge.cc/skills/workplan/).

[Browse on Edge](https://getedge.cc) · [How evidence works](docs/BENCHMARK.md) · [Apache 2.0 license](LICENSE)

## In this repository

This is the versioned source for [Edge-maintained skills](CATALOG.md). The [public database](database/edge-database.json) holds package provenance and recorded evaluations where they exist. Browse the [package catalog and evidence notes](CATALOG.md) for installation and benchmark details.

## Tracked Deck Links

Your agent publishes personal deck links and tells you who opened, what they actively read, and when another device appeared. Original system and design by **Falco Schneider**; Edge ports it into a Node + SQLite skill. See [`tracked-deck-links`](tracked-deck-links/) for setup and provenance.


Original tracking system and design by Falco Schneider. Apache-2.0 under the repository default licence; approved 2026-10-07.

## Data Globe

Turn your location data into an interactive globe with search, filters, glowing clusters, entity drilldown and mobile sheets. [`data-globe`](data-globe/) includes the reusable template and normalization tools. Apache-2.0.
