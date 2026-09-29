# Edge Skills

Edge finds a task-fit agent skill, shows available evidence, and loads a pinned version into your agent for the current task.

**Set up Edge:** `set up https://getedge.cc/SKILL.md` — paste this exact line into your agent, as shown on [getedge.cc](https://getedge.cc/).

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
