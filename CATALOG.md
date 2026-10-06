# Edge Skills

Versioned skills for AI agents, with provenance for every package and complete evaluation records where a controlled benchmark exists.

[Browse on Edge](https://getedge.cc) · [How evidence works](docs/BENCHMARK.md) · [Apache 2.0 license](LICENSE)

## Public database

The skill directory and Arena records are published as one machine-readable dataset: [`database/edge-database.json`](database/edge-database.json). It includes the public skill index, tested tasks, configurations, scores, costs, provenance, and the limitations required to interpret them. See [`database/README.md`](database/README.md) for the contract and validator.

## Install a skill

```bash
npx skills add getedgehq/skills --skill workplan
```

List the available packages without installing:

```bash
npx skills add getedgehq/skills --list
```

The Edge catalog is the primary place to discover, compare, and inspect skills. This repository is the versioned package source.

## Start here

| Need | Skill |
| --- | --- |
| Keep long work alive across context loss | [`workplan`](workplan/) |
| Find and load the right skill for the task at hand, automatically | [`edge-find-skills`](edge-find-skills/) |
| Show a plan as a scannable text diagram with decisions on top | [`plan-board`](plan-board/) |
| Draft a literature review or research paper with checkable citations | [`autonomous-research`](autonomous-research/) |
| Diagnose an unreliable or expensive agent | [`harness-first`](harness-first/) |
| Decide whether another skill would help | [`skillneed`](skillneed/) |
| Find recurring failures in agent sessions | [`skill-miner`](skill-miner/) |
| Test a Skill on tasks recovered from your own sessions | [`brain-scan`](brain-scan/) |
| Discover what your agent is good and bad at | [`agent-skills-gap`](agent-skills-gap/) |
| Test whether a skill actually helps | [`skill-eval-loop`](skill-eval-loop/) |
| Release an evaluated skill end to end | [`skill-release-pipeline`](skill-release-pipeline/) |
| Turn agent work into a public-safe proof record | [`agent-receipt`](agent-receipt/) |
| Recover decisions and reversals from messy notes | [`decision-ledger`](decision-ledger/) |
| Fix hooks and agent infrastructure | [`agent-infra-fixer`](agent-infra-fixer/) |
| Inspect the improvement loop locally | [`skill-cockpit`](skill-cockpit/) |

## Packages

### Agent development

- [`agent-skills-gap`](agent-skills-gap/) analyzes supplied Claude or Codex sessions and creates an evidence-backed skills profile plus share card.
- [`brain-scan`](brain-scan/) mines authorized sessions and measures no Skill versus the selected Skill explicitly loaded on reconstructed real tasks.
- [`skill-evals`](skill-evals/) builds repeatable agent evaluations and verifiers.
- [`agent-infra-fixer`](agent-infra-fixer/) diagnoses and repairs broken agent guardrails.
- [`harness-first`](harness-first/) audits the harness before recommending a model change.
- [`skill-cockpit`](skill-cockpit/) provides a local view of mined failures and evaluation runs.
- [`skill-eval-loop`](skill-eval-loop/) runs controlled with-skill and without-skill comparisons.
- [`skill-release-pipeline`](skill-release-pipeline/) takes a concrete failure through package creation, evaluation, evidence binding, and publication.
- [`skill-battle`](skill-battle/) defines the disclosure and integrity contract for public skill comparisons.
- [`skill-miner`](skill-miner/) finds recurring failures in Claude Code, Codex, and OpenCode sessions.
- [`skillneed`](skillneed/) decides whether a task needs specialist procedure and recommends at most one exact package.
- [`system-prompt-doctor`](system-prompt-doctor/) audits and tests user-owned agent instructions against representative tasks.
- [`invocation-doctor`](invocation-doctor/) repairs skill descriptions using train and held-out trigger cases.
- [`workplan`](workplan/) keeps multi-step work durable across context loss.
- [`edge-find-skills`](edge-find-skills/) tells your agent to search Edge at the start of specialist work and load the best fitting skill on demand.
- [`plan-board`](plan-board/) shows plans and status as one-line-per-item text diagrams, with decisions first and an optional board that collects approvals.

### Research and communication

- [`fede-voice`](fede-voice/) writes DMs and posts in Federico’s documented style as a finished, privacy-safe example.
- [`clone-my-voice`](clone-my-voice/) builds a private local writing skill from the user’s own samples.
- [`personal-model-builder`](personal-model-builder/) takes someone from "create my model" to a Claude style card and, on a capable computer, a small open model fine-tuned on their own writing that runs offline, with a blind "which sounds like you?" check.
- [`fede-clone`](fede-clone/) works like Federico on startup tasks: how he decides, judges work and reports, as a finished, privacy-safe example. Pairs with `fede-voice` for writing.
- [`clone-yourself`](clone-yourself/) builds a private local `<your-name>-clone` skill from the user’s own agent rules, notes and writing: their voice plus how they decide, judge and report.
- [`client-comms`](client-comms/) drafts concise, actionable client messages and handles complaints promptly.
- [`inbound-triage`](inbound-triage/) ranks mixed inbox threads by consequence and identifies what needs a reply, delegation, or no action.

- [`autonomous-research`](autonomous-research/) (formerly OpenDraft) drafts a literature review, research paper, or thesis chapter from one topic line. It finds sources at Crossref and OpenAlex, drafts each section against them, and its integrity gate checks that every printed DOI resolved at Crossref or DataCite. No API key or account. Install: `npx skills add getedgehq/skills --skill autonomous-research`.
- [`people-search`](people-search/) plans and documents evidence-backed people searches.
- [`top-down-comms`](top-down-comms/) structures executive and client communication around a governing thought.
- [`decision-ledger`](decision-ledger/) converts messy notes into evidence-linked decisions, reversals, proposals, open questions, and actions.
- [`negotiation-prep`](negotiation-prep/) prepares a negotiation with BATNA/ZOPA analysis, scores draft messages on six dimensions before they are sent, and keeps a concession ledger across rounds. Inspired by the negotiation preparation approach taught in the CEMS Negotiation Strategy course at Nova SBE. Install: `npx skills add getedgehq/skills --skill negotiation-prep`.

### Engineering and operations

- [`cli-ux-review`](cli-ux-review/) reviews command-line interfaces for clear states and recovery paths.
- [`domain-uptime-monitor`](domain-uptime-monitor/) monitors real page content, not only HTTP status.
- [`http-error-triage`](http-error-triage/) separates credential failures from endpoint, CDN, and client failures.
- [`job-board-scout`](job-board-scout/) watches public job boards against saved rules.
- [`security-audit-checklist`](security-audit-checklist/) audits code, cloud configuration, containers, CI, and IaC.
- [`agent-governance-gap-analysis`](agent-governance-gap-analysis/) scores AI agent governance against Cakewalk's 25 read-only checks and writes a 30/60/90 plan. By [Cakewalk](https://www.cakewalk.security/), Apache-2.0.
- [`shadcn-first`](shadcn-first/) builds interfaces from existing shadcn components and blocks.

### Media and workflow

- [`ai-dna`](ai-dna/) turns your own local ChatGPT, Claude Code, and Codex histories into a luminous helix still and 12-second film, with an optional portrait intro.

- [`generate-image`](generate-image/) generates images through an authenticated Codex CLI.
- [`linkedin-media-prep`](linkedin-media-prep/) prepares images and video for LinkedIn.
- [`ai-festival-poster`](ai-festival-poster/) paints a festival lineup poster from real AI usage in local agent logs.
- [`procedural-painter`](procedural-painter/) paints finished painterly images entirely with Python: no image model, no reference images.
- [`product-launch-video`](product-launch-video/) turns a product brief into an editable launch film.
- [`launch-film`](launch-film/) makes a short, result-first launch film for a product, feature or skill: one object carried across beats cut on a music grid, an original synthesized score and your brand kit, rendered from HTML to MP4 with no video editor. Made the Edge skill films.
- [`linkedin-year-audit`](linkedin-year-audit/) reads your own LinkedIn analytics export and tells you what worked over the year: totals, follower growth, how much a few posts carried, and which kinds of posts reached people versus which got reactions, with the number behind every claim. Runs on your computer; nothing is uploaded.
- [`subscription-billing-reconciliation`](subscription-billing-reconciliation/) reconciles what a subscription contract says should have been billed for a period against what invoices actually billed: proration, invoice-export revisions, credit notes, merged and parent/child accounts, FX and one-time rounding.
- [`ar-aging-and-cash-application`](ar-aging-and-cash-application/) builds an accounts receivable aging report and applies incoming cash to invoices: due dates from terms, allocation order, settlement discounts, partial payments, credit memos, disputes and unapplied cash.
- [`crawler-access-audit`](crawler-access-audit/) audits crawler access from server logs and robots.txt: RFC 9309 group selection and precedence, versioned robots.txt, crawler impersonation, real client IP behind proxies and AI crawler tokens.
- [`interview-reel-motion`](interview-reel-motion/) layers the graphic beats on an already-cut 9:16 interview short with HyperFrames (npx, no app install) from a beat map (cover frame, phrase captions, stickers, counters, a speed ramp, a clean end hold), then gates the render for face zones, safe zones, readability and caption sync.
- [`muse-gadget-setup`](muse-gadget-setup/) gets a Meta Muse gadget working from one sentence ("I have [hardware]. I want Muse to [thing]."): picks Home Link, Linux SDK or ESP32 SDK, then gives setup, flashing, pairing and debugging steps from the official muse-gadget-sdk docs. Not affiliated with Meta.
- [`record-mac-demo`](record-mac-demo/) has your agent screen-record a real demo on your own Mac (even overnight) or a second Mac, with zero clicks and a timed action log for captions.
- [`reply-debt`](reply-debt/) identifies mail that is still waiting on a reply.
- [`repo-to-launch`](repo-to-launch/) turns repository facts into a grounded launch package without inventing product claims.
- [`strip-image-ai-metadata`](strip-image-ai-metadata/) removes C2PA and AI-generation metadata.
- [`vlog-edit`](vlog-edit/) edits phone footage into a captioned 9:16 short with a hook, full-frame data cards, maps and b-roll, then judges the cut before anyone watches it.

### Evidence and publishing

- [`agent-receipt`](agent-receipt/) produces a public-safe, hash-bound result record from a private run manifest.
- [`skill-battle`](skill-battle/) packages controlled comparison results without silently escalating disclosure.
- [`skill-release-pipeline`](skill-release-pipeline/) enforces the release contract and exact package hashes.

### Founder guides

- [`founders-handbook`](founders-handbook/) answers founder questions (co-founders, cap tables, SAFEs, Series A, secondaries, M&A, QSBS) from 1984 Ventures' public Founders Handbook and links the chapter behind every answer.
- [`pitch-lensing`](pitch-lensing/) structures and reviews an investor deck with the lensing method pitch designer Chris Laughlin presented in a public Emerson Collective talk (June 2024): a lens note per partner, a four-slide context opener instead of Problem / Solution, raise timing and a fast-rules review table. Restated in our own words with credit; not endorsed by him. Install: `npx skills add getedgehq/skills --skill pitch-lensing`.
- [`german-taxes-elster`](german-taxes-elster/) prepares German taxes with an agent for founders and small UG/GmbH companies: UStVA and annual USt (including section 13b reverse charge on EU and US SaaS and the `DE000000000` placeholder VAT ID trap), KSt, GewSt, E-Bilanz, Einspruch with AdV and Verböserung check, Vorauszahlungen, deadlines, and certificate-based Mein ELSTER filing. The agent prepares; a human approves every submission. Not tax advice. Install: `npx skills add getedgehq/skills --skill german-taxes-elster`.

### Web and 3D, by Meng To

Four skills by [Meng To](https://github.com/MengTo), republished unchanged from [MengTo/skills](https://github.com/MengTo/skills) under his MIT licence.

- [`threejs`](threejs/) builds and debugs interactive 3D scenes on the web with Three.js.
- [`threejs-scroll-worlds`](threejs-scroll-worlds/) builds one persistent 3D world that the camera travels through as the page scrolls.
- [`awwwards-sites`](awwwards-sites/) art-directs and builds motion-rich marketing, editorial and portfolio sites with GSAP and one smooth-scroll engine.
- [`realistic-water`](realistic-water/) adds an ultra-realistic open ocean to a Three.js scene: waves, sun glitter, foam and a ship wake.

### Expressive UI, by Jakub Antalik

One skill by [Jakub Antalik](https://github.com/Jakubantalik), republished unchanged from [Jakubantalik/Libraries.dev](https://github.com/Jakubantalik/Libraries.dev) under his MIT licence.

- [`libraries-dev`](libraries-dev/) adds expressive UI effects (border beam, thinking orbs, gooey, voice glow, bot avatars, liquid metal, image reveal) from the Libraries.dev packages, and finds where they fit in a project.

### Founder ideas, by Garry Tan

One skill by [Garry Tan](https://github.com/garrytan), republished unchanged from [garrytan/gstack](https://github.com/garrytan/gstack) under his MIT licence.

- [`office-hours`](office-hours/) runs YC-style office hours on a product idea: six forcing questions about demand, the status quo and the smallest version, then a design doc, before any code.

### Web design

- [`website-inspiration`](website-inspiration/) checks 17 curated design galleries (full pages, hero sections, pricing, footers, app flows, fonts) for real references before the agent designs a page.

### Partner packages

- [`cv-job-match`](cv-job-match/) matches a CV to live roles from Rocketlist.
- [`rocketlist`](rocketlist/) searches current startup jobs and hiring companies through Rocketlist's public MCP.
- [`pay-per-call-apis`](pay-per-call-apis/) exposes Monid's paid data and scraping tools through one CLI.
- [`geo-domination`](geo-domination/) (GEO Domination, by RadarKit) finds the AI prompts your buyers ask, then shows how to own the answers in ChatGPT, Perplexity, Gemini and Google AI.

## Evidence status

Fourteen skills currently publish controlled comparisons against the same agent without the skill. Six
use the frozen `edge-skill-bench@1.0` environment; `agent-skills-gap` publishes a separate direct
Codex A/B evaluation, `brain-scan` publishes a separate explicit-load release validation, five packages publish isolated Harbor A/B evaluations, and `german-taxes-elster` publishes a `skill-eval-loop` headless A/B pilot. Each is labelled
accordingly.

| Skill | Status | Record |
| --- | --- | --- |
| `brain-scan` | Measured pilot: 8 wins, 0 ties, 1 loss; +33.3pp objective completion observed | [`EVALS.md`](brain-scan/EVALS.md) |
| `agent-receipt` | Measured in Harbor, inconclusive | [`EVALS.md`](agent-receipt/EVALS.md) |
| `decision-ledger` | Measured in Harbor, inconclusive | [`EVALS.md`](decision-ledger/EVALS.md) |
| `agent-skills-gap` | Supported in its recorded direct A/B eval; outside `edge-skill-bench@1.0` | [`EVALS.md`](agent-skills-gap/EVALS.md) |
| `invocation-doctor` | Measured in Harbor, inconclusive | [`EVALS.md`](invocation-doctor/EVALS.md) |
| `repo-to-launch` | Measured in Harbor, inconclusive | [`EVALS.md`](repo-to-launch/EVALS.md) |
| `system-prompt-doctor` | Measured in Harbor, negative | [`EVALS.md`](system-prompt-doctor/EVALS.md) |
| `workplan` | Supported in the recorded benchmark | [`EVALS.md`](workplan/EVALS.md) |
| `autonomous-research` | Measured, inconclusive | [`EVALS.md`](autonomous-research/EVALS.md) |
| `harness-first` | Measured, inconclusive | [`EVALS.md`](harness-first/EVALS.md) |
| `skillneed` | Measured, inconclusive | [`EVALS.md`](skillneed/EVALS.md) |
| `strip-image-ai-metadata` | Supported in the recorded benchmark | [`EVALS.md`](strip-image-ai-metadata/EVALS.md) |
| `top-down-comms` | Supported in the recorded benchmark | [`EVALS.md`](top-down-comms/EVALS.md) |
| `german-taxes-elster` | Measured pilot, inconclusive: 2 wins, 1 tie, 0 losses; verifier 3/3 vs 2/3 | [`EVALS.md`](german-taxes-elster/EVALS.md) |

“Published,” “featured,” and “benchmarked” are different states. A benchmark result is supported only when its stated confidence interval excludes zero. An inconclusive result is not presented as a win.

Read the full protocol in [`docs/BENCHMARK.md`](docs/BENCHMARK.md). Withdrawn figures and their failure modes remain visible in [`evals/WITHDRAWN.md`](evals/WITHDRAWN.md).

## Package structure

Every package has a `SKILL.md` at its root. Packages may also include scripts, references, assets, tests, and an `agents/openai.yaml` interface definition.

Each package includes `DERIVATION.json`, which records its origin, shipped files, hashes, and licensing provenance. Read package instructions and executable files before installing, as you would with any agent extension.

## Renamed packages

| Previous name | Current name |
| --- | --- |
| `opendraft` | `autonomous-research` |
| `rocketlist` | `cv-job-match` |
| `monid` | `pay-per-call-apis` |
| `radarkit-prompt-discovery` | `geo-domination` |

The previous install names remain as compatibility aliases. New integrations should use the current names.

## License and attribution

Most packages are Apache-2.0 and carry their own license and provenance record. Partner-owned packages may use different terms; their package directories state those terms explicitly.

`founders-handbook` summarizes the [Founders Handbook by 1984 Ventures](https://1984.vc/docs/founders-handbook) chapter by chapter, with each chapter linked and its authors credited. The handbook content belongs to 1984 Ventures, so the package is not covered by the repository's Apache-2.0 grant; see [`founders-handbook/THIRD_PARTY_NOTICES.md`](founders-handbook/THIRD_PARTY_NOTICES.md). It is not affiliated with or endorsed by 1984 Ventures.

`geo-domination` (GEO Domination) is RadarKit's own Skill, provided by RadarKit for Edge and published unchanged apart from its front-matter `name:`. No licence was stated with it, so it is not covered by the repository's Apache-2.0 grant; see [`geo-domination/THIRD_PARTY_NOTICES.md`](geo-domination/THIRD_PARTY_NOTICES.md).

For academic citation, use [`CITATION.cff`](CITATION.cff). The benchmark identifier is `edge-skill-bench@1.0`.

`threejs`, `threejs-scroll-worlds`, `awwwards-sites` and `realistic-water` are Meng To's work, copied from [MengTo/skills](https://github.com/MengTo/skills) at a pinned commit. They are MIT-licensed (Copyright (c) 2026 Meng To), not covered by the repository's Apache-2.0 grant, and each folder carries his LICENSE. The only change is the front-matter `name:` plus an author and source credit, recorded in each `DERIVATION.json`. They are not affiliated with or endorsed by Meng To.

`libraries-dev` is Jakub Antalik's work, copied from [Jakubantalik/Libraries.dev](https://github.com/Jakubantalik/Libraries.dev) at a pinned commit. It is MIT-licensed (Copyright (c) 2026 Jakub Antalik), not covered by the repository's Apache-2.0 grant, and the folder carries his LICENSE. The only change is an author and source credit in the front matter, recorded in `DERIVATION.json`. It is not affiliated with or endorsed by Jakub Antalik.

`office-hours` is Garry Tan's work, copied from [garrytan/gstack](https://github.com/garrytan/gstack) at a pinned commit. It is MIT-licensed (Copyright (c) 2026 Garry Tan), not covered by the repository's Apache-2.0 grant, and the folder carries his LICENSE. The only change is an author and source credit in the front matter, recorded in `DERIVATION.json`. It is not affiliated with or endorsed by Garry Tan or Y Combinator.
