# Edge Skills

Versioned skills for AI agents, with provenance for every package and complete evaluation records where a controlled benchmark exists.

[Browse on Edge](https://getedge.cc) · [How evidence works](docs/BENCHMARK.md) · [Apache 2.0 license](LICENSE)

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

### Research and communication

- [`autonomous-research`](autonomous-research/) produces source-grounded research with citation checks.
- [`people-search`](people-search/) plans and documents evidence-backed people searches.
- [`top-down-comms`](top-down-comms/) structures executive and client communication around a governing thought.
- [`decision-ledger`](decision-ledger/) converts messy notes into evidence-linked decisions, reversals, proposals, open questions, and actions.

### Engineering and operations

- [`cli-ux-review`](cli-ux-review/) reviews command-line interfaces for clear states and recovery paths.
- [`domain-uptime-monitor`](domain-uptime-monitor/) monitors real page content, not only HTTP status.
- [`http-error-triage`](http-error-triage/) separates credential failures from endpoint, CDN, and client failures.
- [`job-board-scout`](job-board-scout/) watches public job boards against saved rules.
- [`security-audit-checklist`](security-audit-checklist/) audits code, cloud configuration, containers, CI, and IaC.
- [`shadcn-first`](shadcn-first/) builds interfaces from existing shadcn components and blocks.

### Media and workflow

- [`generate-image`](generate-image/) generates images through an authenticated Codex CLI.
- [`linkedin-media-prep`](linkedin-media-prep/) prepares images and video for LinkedIn.
- [`product-launch-video`](product-launch-video/) turns a product brief into an editable launch film.
- [`reply-debt`](reply-debt/) identifies mail that is still waiting on a reply.
- [`repo-to-launch`](repo-to-launch/) turns repository facts into a grounded launch package without inventing product claims.
- [`strip-image-ai-metadata`](strip-image-ai-metadata/) removes C2PA and AI-generation metadata.

### Evidence and publishing

- [`agent-receipt`](agent-receipt/) produces a public-safe, hash-bound result record from a private run manifest.
- [`skill-battle`](skill-battle/) packages controlled comparison results without silently escalating disclosure.
- [`skill-release-pipeline`](skill-release-pipeline/) enforces the release contract and exact package hashes.

### Partner packages

- [`cv-job-match`](cv-job-match/) matches a CV to live roles from Rocketlist.
- [`pay-per-call-apis`](pay-per-call-apis/) exposes Monid's paid data and scraping tools through one CLI.

## Evidence status

Thirteen skills currently publish controlled comparisons against the same agent without the skill. Six
use the frozen `edge-skill-bench@1.0` environment; `agent-skills-gap` publishes a separate direct
Codex A/B evaluation, `brain-scan` publishes a separate explicit-load release validation, and five packages publish isolated Harbor A/B evaluations. Each is labelled
accordingly.

| Skill | Status | Record |
| --- | --- | --- |
| `brain-scan` | Release validation: 6 wins, 1 tie, 2 losses; +55.6pp objective completion observed | [`EVALS.md`](brain-scan/EVALS.md) |
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

The previous install names remain as compatibility aliases. New integrations should use the current names.

## License and attribution

Most packages are Apache-2.0 and carry their own license and provenance record. Partner-owned packages may use different terms; their package directories state those terms explicitly.

For academic citation, use [`CITATION.cff`](CITATION.cff). The benchmark identifier is `edge-skill-bench@1.0`.
