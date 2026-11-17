# Edge Skills

Edge gives your AI agent the right expert skill for the task at hand. It searches 100,000+ security-screened public skills, picks the best fit, and loads a pinned version for that task. Works in Claude Code, Codex, Cursor and the Claude app.

**Using Claude Code or Codex? Add skill discovery:**

```bash
npx skills add getedgehq/skills --skill edge-find-skills
```

**Set up Edge:** paste this into Claude Code, Codex or Cursor:

```text
Set up Edge for me: fetch https://getedge.cc/SKILL.md?ref=gh-skills with curl, read it, and follow it
```

After setup, your agent can load any skill in this repository automatically when a task needs it. Details on [getedge.cc](https://getedge.cc/?ref=gh-skills).

<!-- edge:weekly -->

## Most loaded through Edge this week

Skills ranked by how many different people loaded them through Edge in the 7 days to 2026-11-17 (external use only; no counts or identities published). Refreshed every week.

| # | Skill | By |
| --- | --- | --- |
| 1 | [kennedy-practical-ui](https://github.com/getedgehq/skills/tree/main/kennedy-practical-ui) | getedgehq |
| 2 | [cold-email](https://getedge.cc/skills/coreyhaines31/cold-email/) | coreyhaines31 |
| 3 | [email-drafter](https://github.com/github/awesome-copilot) | github |
| 4 | [frontend-design](https://github.com/anthropics/skills) | anthropics |
| 5 | [literature-review](https://github.com/affaan-m/ecc) | affaan-m |
| 6 | [pitch-deck](https://getedge.cc/skills/pitch-deck/) | getedgehq |
| 7 | [top-down-comms](https://getedge.cc/skills/top-down-comms/) | getedgehq |
| 8 | [dry-three-copy-tests](https://github.com/getedgehq/skills/tree/main/dry-three-copy-tests) | getedgehq |
| 9 | [market-research](https://github.com/affaan-m/ecc) | affaan-m |
| 10 | [prospecting](https://getedge.cc/skills/coreyhaines31/prospecting/) | coreyhaines31 |

## Add Edge to your agent

Free, no key. Edge Pro: use https://getedge.cc/mcp/pro instead.

| Agent | Setup | |
| --- | --- | --- |
| Claude Code | run `npx -y @getedge/mcp setup claude` (connector, prompt hook and one CLAUDE.md line; `--remove` undoes it) | [guide](https://getedge.cc/docs/agents/claude-code/?ref=gh-skills) |
| Codex and the ChatGPT desktop app | run `npx -y @getedge/mcp setup codex` (the Edge entry in ~/.codex/config.toml with the startup wait) | [guide](https://getedge.cc/docs/agents/codex/?ref=gh-skills) |
| Cursor | one-click install: cursor://anysphere.cursor-deeplink/mcp/install?name=edge&config=eyJjb21tYW5kIjoibnB4IiwiYXJncyI6WyIteSIsIkBnZXRlZGdlL21jcCJdfQ%3D%3D, then start a new Agent chat | [guide](https://getedge.cc/docs/agents/cursor/?ref=gh-skills) |
| Claude app (claude.ai, desktop, mobile) | add a custom connector with the URL https://getedge.cc/mcp, then Connect | [guide](https://getedge.cc/docs/agents/claude-ai/?ref=gh-skills) |
| ChatGPT | install the Edge plugin: https://chatgpt.com/plugins/plugin_asdk_app_6ac03efbe1088191a79309b2e6882ae9 | [guide](https://getedge.cc/docs/agents/chatgpt/?ref=gh-skills) |
| VS Code | add an HTTP MCP server named edge with the URL https://getedge.cc/mcp | [guide](https://getedge.cc/docs/agents/vscode/?ref=gh-skills) |
| Gemini CLI | run `gemini mcp add --scope user --transport http edge https://getedge.cc/mcp` | [guide](https://getedge.cc/docs/agents/gemini-cli/?ref=gh-skills) |
| OpenCode | run `npm install -g @getedge/mcp`, then add a local MCP server "edge" with command ["edge"] to opencode.json | [guide](https://getedge.cc/docs/agents/opencode/?ref=gh-skills) |
| Any other MCP client | remote HTTP server https://getedge.cc/mcp, or local stdio `npx -y @getedge/mcp` | [guide](https://getedge.cc/docs/agents/other/?ref=gh-skills) |

## Skills by category

Each category page on getedge.cc lists skills for that kind of work. Under each: the most installed skills with an Edge evidence page (pinned source, verified licence, passing Edge scans).

### [Design](https://getedge.cc/explore/design/?ref=gh-skills)

UI, brand, landing pages, accessibility and design systems.

| Skill | What it does |
| --- | --- |
| [Redesign Existing Projects by leonxlnx](https://getedge.cc/skills/leonxlnx/redesign-existing-projects/) | Upgrades existing websites and apps to premium quality. |
| [Minimalist UI by leonxlnx](https://getedge.cc/skills/leonxlnx/minimalist-ui/) | Clean editorial-style interfaces. |
| [Emil Design Eng by emilkowalski](https://getedge.cc/skills/emilkowalski/emil-design-eng/) | This skill encodes Emil Kowalski's philosophy on UI polish, component design, animation decisions, and the invisible... |
| [Apple Design by emilkowalski](https://getedge.cc/skills/emilkowalski/apple-design/) | Apple's approach to interface design and fluid, physical motion, translated for the web. |
| [Extract Design System by arvindrk](https://getedge.cc/skills/arvindrk/extract-design-system/) | Extract design primitives from a public website and generate starter token files for your project. |

### [Frontend](https://getedge.cc/explore/frontend/?ref=gh-skills)

React, Next.js, CSS, web performance and frontend testing.

| Skill | What it does |
| --- | --- |
| [Convex Create Component by get-convex](https://getedge.cc/skills/get-convex/convex-create-component/) | Builds reusable Convex components with isolated tables and app-facing APIs. |
| [GSAP React by greensock](https://getedge.cc/skills/greensock/gsap-react/) | Official GSAP skill for React : useGSAP hook, refs, gsap.context(), cleanup. |
| [Vue by antfu](https://getedge.cc/skills/antfu/vue/) | Vue 3 Composition API, script setup macros, reactivity system, and built-in components. |
| [Next.js on Cloudflare by cloudflare](https://getedge.cc/skills/cloudflare/nextjs-on-cloudflare/) | Build, migrate, and deploy Next.js apps on Cloudflare Workers with vinext. |
| [Next.js App Router Patterns by wshobson](https://getedge.cc/skills/wshobson/nextjs-app-router-patterns/) | Master Next.js 14+ App Router with Server Components, streaming, parallel routes, and advanced data fetching. |

### [Writing](https://getedge.cc/explore/writing/?ref=gh-skills)

Copywriting, email, blog posts, editing and communication.

| Skill | What it does |
| --- | --- |
| [Writing Beats by mattpocock](https://getedge.cc/skills/mattpocock/writing-beats/) | Writing, exploit; assemble raw material into a journey of beats, grounding each term before a beat leans on it. |
| [Writing Shape by mattpocock](https://getedge.cc/skills/mattpocock/writing-shape/) | Writing, exploit: shape raw material into an article, paragraph by paragraph. |
| [Nano Banana Edit by prime-skills](https://getedge.cc/skills/prime-skills/nano-banana-edit/) | Edit images with Google Nano Banana 2 (image-to-image edit endpoint) on RunComfy. |
| [Copywriting by coreyhaines31](https://getedge.cc/skills/coreyhaines31/copywriting/) | When the user wants to write, rewrite, or improve marketing copy for any page : including homepage, landing pages... |
| [Copy Editing by coreyhaines31](https://getedge.cc/skills/coreyhaines31/copy-editing/) | When the user wants to edit, review, or improve existing marketing copy, or refresh outdated content. |

### [Video & media](https://getedge.cc/explore/video/?ref=gh-skills)

Launch videos, animation, image generation, audio and captions.

| Skill | What it does |
| --- | --- |
| [Image to Video by prime-skills](https://getedge.cc/skills/prime-skills/image-to-video/) | Animate any still image on RunComfy : this skill is a smart router that matches the user's intent to the right i2v... |
| [Video Inpainting by prime-skills](https://getedge.cc/skills/prime-skills/video-inpainting/) | Region edits across video frames on RunComfy via the `runcomfy` CLI : remove an object that appears across many frames... |
| [Image to Code by leonxlnx](https://getedge.cc/skills/leonxlnx/image-to-code/) | Elite website image-to-code skill for Codex. |
| [General Video by heygen-com](https://getedge.cc/skills/heygen-com/general-video/) | Author or edit a custom HyperFrames composition when no specialized workflow fits, or when BRIEF.md sets flow... |
| [Review Animations by emilkowalski](https://getedge.cc/skills/emilkowalski/review-animations/) | Reviews animation and motion code against a high craft bar derived from Emil Kowalski's design engineering philosophy. |

### [Research](https://getedge.cc/explore/research/?ref=gh-skills)

Market research, literature reviews, people search, competitor analysis and web research.

| Skill | What it does |
| --- | --- |
| [Analyze Project by lllllllama](https://getedge.cc/skills/lllllllama/analyze-project/) | Rigor Analyze / Rigor Audit read-only skill for deep learning research repositories. |
| [Customer Research by coreyhaines31](https://getedge.cc/skills/coreyhaines31/customer-research/) | When the user wants to conduct, analyze, or synthesize customer research. |
| [Amazon Product Research by nexscope-ai](https://getedge.cc/skills/nexscope-ai/amazon-product-research/) | Comprehensive product research and opportunity analysis for Amazon sellers. |
| [Firecrawl Deep Research by firecrawl](https://getedge.cc/skills/firecrawl/firecrawl-deep-research/) | Produce an intensive, cited analytical report: executive summary, multi-angle findings, contrarian views, open... |
| [Firecrawl Research Papers by firecrawl](https://getedge.cc/skills/firecrawl/firecrawl-research-papers/) | Find and synthesize research papers, whitepapers, PDFs, technical reports, and academic sources with Firecrawl... |

### [Security](https://getedge.cc/explore/security/?ref=gh-skills)

Security review, secrets, dependency audits, authentication and threat models.

| Skill | What it does |
| --- | --- |
| [Firebase Auth Basics by firebase](https://getedge.cc/skills/firebase/firebase-auth-basics/) | Guide for setting up and using Firebase Authentication. |
| [Firebase Security Rules Auditor by firebase](https://getedge.cc/skills/firebase/firebase-security-rules-auditor/) | Audits Firebase (Firestore, Cloud Storage) security rules for vulnerabilities, privilege escalation, role bypasses... |
| [Security and Hardening by addyosmani](https://getedge.cc/skills/addyosmani/security-and-hardening/) | Hardens code against vulnerabilities. |
| [Convex Auth by get-convex](https://getedge.cc/skills/get-convex/convex-auth/) | Add authentication (passkeys/OAuth) to the current Convex app, including the auth.config.ts wiring. |
| [Security Requirement Extraction by wshobson](https://getedge.cc/skills/wshobson/security-requirement-extraction/) | Derive security requirements from threat models and business context. |

### [Data](https://getedge.cc/explore/data/?ref=gh-skills)

SQL, data analysis, charts, data pipelines and spreadsheets.

| Skill | What it does |
| --- | --- |
| [Analytics by coreyhaines31](https://getedge.cc/skills/coreyhaines31/analytics/) | When the user wants to set up, improve, or audit analytics tracking and measurement. |
| [Golang Data Structures by samber](https://getedge.cc/skills/samber/golang-data-structures/) | Golang data structures : slices (internals, capacity growth, preallocation, slices package), maps (internals, hash... |
| [Add Analytics Instrumentation by amplitude](https://getedge.cc/skills/amplitude/add-analytics-instrumentation/) | End-to-end analytics instrumentation workflow for a PR, branch, file, directory, or feature. |
| [Discover Analytics Patterns by amplitude](https://getedge.cc/skills/amplitude/discover-analytics-patterns/) | Discovers how analytics tracking calls are actually written in this codebase : the concrete SDK calls, function... |
| [Recipe Backup Sheet As CSV by googleworkspace](https://getedge.cc/skills/googleworkspace/recipe-backup-sheet-as-csv/) | Export a Google Sheets spreadsheet as a CSV file for local backup or processing. |

### [DevOps](https://getedge.cc/explore/devops/?ref=gh-skills)

Deploys, Docker, CI pipelines, Kubernetes and monitoring.

| Skill | What it does |
| --- | --- |
| [Azure Storage by microsoft](https://getedge.cc/skills/microsoft/azure-storage/) | Azure Storage Services including Blob Storage, File Shares, Queue Storage, Table Storage, and Data Lake. |
| [Azure Compliance by microsoft](https://getedge.cc/skills/microsoft/azure-compliance/) | Run Azure compliance and security audits with azqr plus Key Vault expiration checks. |
| [Fingerprint CI Gate by liarjsdev](https://getedge.cc/skills/liarjsdev/fingerprint-ci-gate/) | Gate a build on browser fingerprint regressions with liarjs - save a baseline scan as JSON, diff later runs against it... |
| [CI CD and Automation by addyosmani](https://getedge.cc/skills/addyosmani/ci-cd-and-automation/) | Automates CI/CD pipeline setup. |
| [Convex Deploy Guard by get-convex](https://getedge.cc/skills/get-convex/convex-deploy-guard/) | Classify + announce the target Convex deployment before any deployment-affecting command; fresh explicit consent for... |

### [Docs](https://getedge.cc/explore/docs/?ref=gh-skills)

ADRs, READMEs, API docs, specs and planning.

| Skill | What it does |
| --- | --- |
| [To Spec by mattpocock](https://getedge.cc/skills/mattpocock/to-spec/) | Turn the current conversation into a spec and publish it to the project issue tracker: no interview, just synthesis of... |
| [Claude Handoff by mattpocock](https://getedge.cc/skills/mattpocock/claude-handoff/) | Hand the current conversation off to a fresh background agent that picks up the work immediately. |
| [Executing Plans by obra](https://getedge.cc/skills/obra/executing-plans/) | Use when executing an implementation plan in the current session as the implementer yourself : your human partner chose... |
| [Gws Docs by googleworkspace](https://getedge.cc/skills/googleworkspace/gws-docs/) | Read and write Google Docs. |
| [Spec Driven Development by addyosmani](https://getedge.cc/skills/addyosmani/spec-driven-development/) | Creates specs before coding. |

### [Marketing](https://getedge.cc/explore/marketing/?ref=gh-skills)

Content marketing, SEO and GEO, launch creative, outreach and LinkedIn posts.

| Skill | What it does |
| --- | --- |
| [SEO Audit by coreyhaines31](https://getedge.cc/skills/coreyhaines31/seo-audit/) | When the user wants to audit, review, or diagnose SEO issues on their site. |
| [Programmatic SEO by coreyhaines31](https://getedge.cc/skills/coreyhaines31/programmatic-seo/) | When the user wants to create SEO-driven pages at scale using templates and data. |
| [SEO by addyosmani](https://getedge.cc/skills/addyosmani/seo/) | Optimize for search engine visibility and ranking. |
| [Firecrawl SEO Audit by firecrawl](https://getedge.cc/skills/firecrawl/firecrawl-seo-audit/) | Audit a website's SEO with Firecrawl. |
| [LinkedIn Profile Optimizer by paramchoudhary](https://getedge.cc/skills/paramchoudhary/linkedin-profile-optimizer/) | Optimize LinkedIn profile for searchability, recruiter visibility, and engagement |

<!-- /edge:weekly -->

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

This repository contains 169 top-level skill bundles, including compatibility aliases. It is the versioned source for [Edge-maintained skills](CATALOG.md). The [public database](database/edge-database.json) holds package provenance and recorded evaluations where they exist. Browse the [package catalog and evidence notes](CATALOG.md) for installation and benchmark details.

## Tracked Deck Links

Your agent publishes personal deck links and tells you who opened, what they actively read, and when another device appeared. Original system and design by **Falco Schneider**; Edge ports it into a Node + SQLite skill. See [`tracked-deck-links`](tracked-deck-links/) for setup and provenance.


Original tracking system and design by Falco Schneider. Apache-2.0 under the repository default licence; approved 2026-10-07.

## Data Globe

Turn your location data into an interactive globe with search, filters, glowing clusters, entity drilldown and mobile sheets. [`data-globe`](data-globe/) includes the reusable template and normalization tools. Explore the live reference: [Rocketmap](https://rocketlist.ai/map). Apache-2.0.

## Rocketlist Job Search

Use Rocketlist’s current startup hiring data inside your agent: role, location, stage, salary and remote filters, with direct employer links. The public dataset and Python helper need no account or API key.

| Need | Skill |
| --- | --- |
| Find current startup jobs and hiring companies | [`rocketlist-job-search`](rocketlist-job-search/) |

This bundle is licensed under [Rocketlist’s MIT license](rocketlist-job-search/LICENSE); the hiring dataset has its own upstream [data terms](https://github.com/rocketlist-ai/startup-jobs/blob/main/DATA_LICENSE.md).
