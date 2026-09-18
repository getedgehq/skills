# GetEdge Skills

[![Catalogue](https://img.shields.io/badge/Catalogue-getedge.cc-000000?style=for-the-badge&color=154CFF)](https://getedge.cc)
[![Licence](https://img.shields.io/badge/Licence-Apache--2.0-000000?style=for-the-badge&color=154CFF)](LICENSE)

Twenty-three Agent Skills, and a loop that works out which of them are actually worth keeping.

```
npx skills add getedgehq/skills --skill skill-miner
```

`--list` shows everything without installing. A Skill is just a folder with a `SKILL.md` at its root, so cloning and copying works too:

```
git clone https://github.com/getedgehq/skills
cp -r skills/workplan ~/.claude/skills/workplan
```

Catalogue and write-ups: **[getedge.cc](https://getedge.cc)**

## The self-improvement loop

What if every time your AI agent failed, it automatically got better?

Four of these Skills form a loop that runs on your own machine, over your own session logs, and only keeps a Skill that measurably improves your own work:

1. **`skill-miner`** reads Claude Code, Codex and OpenCode session logs and finds where the agent failed you: corrections you had to type, frustration, token-heavy sessions, tool errors and hook blocks. It clusters them into themes and drafts a Skill for each, or finds an existing one.
2. **`skill-eval-loop`** turns a theme into an eval brief built from your real task, runs the agent with and without the Skill in isolated directories, has a blind judge compare the two, repeats that three times, and adopts the Skill only on a majority win where the Skill's output also passes a deterministic check. Everything else is rejected. A Skill held on probation is rechecked against later sessions and removed again if the failure it targeted did not become rarer.
3. **`agent-infra-fixer`** handles failures that are not knowledge at all: guard hooks that block legitimate work, or block with the reason on stdout so the agent never learns why. It replays every past block through the current hooks and verifies guards still catch what they must.
4. **`skill-cockpit`** is a local browser page over all of it: mined themes, runs in progress, per-sample verdicts and the adoption ledger.

Nothing leaves your machine except the calls your agent CLI already makes and, when you ask `skill-miner` to look for existing Skills, a registry search query. No session log, brief, fixture or adopted Skill from the author's own runs is in this repository.

### What it found when run on real work

The loop was developed on one person's own session logs, so these numbers are evidence about that person's tasks, not a general quality bar.

- **Generic advice Skills did not help.** Seven evals of general-purpose Skills (read before you write, preserve existing config, reuse existing assets and similar) produced five ties, one loss to the baseline and one invalid run. A capable agent already knows that advice.
- **Skills that carry the user's own rules did.** Where the theme was knowledge the agent could not have had (a reply format the user wants, their writing voice, their outreach register, which operational decisions to make without asking), six Skills won their blind comparisons, five of them 3-0 and one 2-0 with one sample invalid. Those six were adopted.
- **Two briefs were thrown out, not scored.** When both arms fail the deterministic check in every sample, the check is wrong, not the Skill. The brief writer now self-tests its check against a short good answer, a thorough good answer and a bad one before any eval runs.

## Start here

| If you want to | Install |
| --- | --- |
| Find what your agent keeps getting wrong | `skill-miner` |
| Prove a Skill helps before you keep it | `skill-eval-loop` |
| Fix hooks that block your agent silently | `agent-infra-fixer` |
| Watch the whole loop in a browser | `skill-cockpit` |
| Debug a slow or unreliable agent | `harness-first` |
| Keep long work alive across context loss | `workplan` |

## The twenty-three

| Skill | What it does |
| --- | --- |
| `agent-evals` | Builds evals for a working agent: yes/no tasks and verifiers, resettable environments, then a loop that turns production traces into new tasks. |
| `agent-infra-fixer` | Finds guard hooks that block legitimate work or hide their reason from the agent, replays every past block through the current hooks, and fixes stdout blocks so the agent sees why. |
| `autonomous-research` | Turns one topic line into a research-paper draft: eighteen agent prompts, keyless Crossref and OpenAlex lookup, and a citation-integrity gate that fails the run instead of shipping a broken bibliography. Measured in [`autonomous-research/EVALS.md`](autonomous-research/EVALS.md). |
| `cli-ux-review` | Scores a command-line tool against a fixed rubric and writes the before/after fix for each failure. |
| `domain-uptime-monitor` | Probes the domains you list with a real content check on each, so a suspended deployment or a broken build that still answers 200 is caught, and alerts only when a domain changes state. |
| `cv-job-match` | Reads a CV, works out what the person can actually do, and returns live startup roles from Rocketlist's public board with published salary, the evidence for the fit and an apply link. Rocketlist's own Skill. |
| `generate-image` | Generates images through the Codex CLI, billed to a ChatGPT subscription rather than a per-image API key. |
| `harness-first` | Diagnoses an unreliable or expensive agent by auditing its harness, traces, tools and context first, and refuses to recommend a model swap without evidence. Measured in [`harness-first/EVALS.md`](harness-first/EVALS.md). |
| `http-error-triage` | Separates a real credential problem from a CDN block, a wrong endpoint or a signature ban, before anyone concludes "the key is dead". |
| `job-board-scout` | Watches public job APIs and public Ashby, Greenhouse and Lever boards for roles matching rules you write down, dedupes against its own state, and reports the funnel so a silent zero is visible. No credential. |
| `linkedin-media-prep` | Converts, crops and compresses images and video to what LinkedIn actually accepts. |
| `pay-per-call-apis` | Gives an agent one install for hundreds of data and scraping tools: discover an endpoint, inspect its schema, run it, and report the per-call cost against a Monid balance. Monid's own Skill, not Apache-2.0. |
| `people-search` | Plans a people search, ranks supplied or public-source candidates against a brief, and discloses exactly which filters a connected provider can and can't support, without implying built-in LinkedIn access it doesn't have. |
| `product-launch-video` | Turns a product URL or launch brief into an editable, reviewed launch film using HyperFrames or Remotion with remocn primitives. |
| `reply-debt` | Ranks the mail still waiting on your reply: drops threads you already answered, bots and newsletters, keeps what asks something, orders it by wait time. Needs a Gmail connection. |
| `security-audit-checklist` | Audits app code, cloud config, containers, CI and IaC, with three bundled scanners. |
| `shadcn-first` | Builds UI from shadcn blocks and components instead of hand-written markup. |
| `skill-cockpit` | A local browser cockpit for the self-improvement loop: mined themes, running evals, per-sample verdicts and the adoption ledger. |
| `skill-eval-loop` | Runs blind A/B evals of a Skill on your own tasks, three samples each, and adopts it only on a majority win with a passing deterministic check. |
| `skill-miner` | Mines Claude Code, Codex and OpenCode session logs for corrections, frustration, token burn and failures, and drafts or finds a Skill for each theme. |
| `strip-image-ai-metadata` | Strips C2PA and AI-generation metadata so platforms stop labelling an image. Measured in [`strip-image-ai-metadata/EVALS.md`](strip-image-ai-metadata/EVALS.md). |
| `top-down-comms` | Structures a client-facing artifact the way MBB consultants do: governing thought first. Measured in [`top-down-comms/EVALS.md`](top-down-comms/EVALS.md). |
| `workplan` | Creates, updates and closes a work plan so multi-step work survives losing context. Measured in [`workplan/EVALS.md`](workplan/EVALS.md). |

### Renamed Skills

Skill names describe what a Skill does, not whose it is. On 2026-09-17 three were renamed; the old install names still work:

| Old name | New name | Creator |
| --- | --- | --- |
| `opendraft` | `autonomous-research` | OpenDraft |
| `rocketlist` | `cv-job-match` | Rocketlist |
| `monid` | `pay-per-call-apis` | Monid |

`npx skills add getedgehq/skills --skill opendraft` installs the same files as `--skill autonomous-research`, under the old name. Each old-name folder holds only a SKILL.md with the old `name:` and `metadata.internal: true` (so it stays out of `--list`) and symlinks to everything else in the renamed folder. `.github/scripts/derivation_gate.py` fails if an alias drifts from its Skill. Symlinks need a checkout that supports them, so on Windows use the new name.

## How a Skill is put together

A Skill is a folder with a `SKILL.md` at its root: a short front matter block naming the Skill and saying when to invoke it, then the instructions themselves. Agents that support Skills read the front matter to decide when a Skill applies, and the body once it does. Some of these carry scripts the instructions call.

## Every one of these is a derived copy, and each says how it was derived

Eleven are edited copies from [Federico de Ponte's](https://github.com/federicodeponte) working set; three are ports of private Floom workers that ran on a schedule before they were published; two are companies' own Skills: `pay-per-call-apis` is Monid's, published unchanged apart from its name, and `cv-job-match` is Rocketlist's, published by GetEdge; seven were written directly for this repository: `people-search`, `agent-evals`, `harness-first`, and the four Skills of the loop above. Five ship an evaluation of themselves: [`harness-first`](harness-first/EVALS.md), [`autonomous-research`](autonomous-research/EVALS.md), [`strip-image-ai-metadata`](strip-image-ai-metadata/EVALS.md), [`top-down-comms`](top-down-comms/EVALS.md) and [`workplan`](workplan/EVALS.md). Each EVALS.md says whether its result cleared our bar, which is a 95% confidence interval on the judge point delta that excludes zero. One does: `workplan`, by 13.4 points with the Skill pasted into the prompt, interval [+9.4, +17.4]. The other four are measured and unresolved. Three of them read as resolved until 2026-09-17, when we measured the interval itself against a known truth, found it was not a 95% interval at three tasks, and replaced it; the estimates did not move and the intervals widened past zero. That correction is written out in [`docs/BENCHMARK.md`](docs/BENCHMARK.md) sections 5 and 11, and every figure it took down is in [`evals/WITHDRAWN.md`](evals/WITHDRAWN.md). An unresolved cell is not a finding of no effect: at three tasks this benchmark is powered around 0.42 for a real 10-point effect, so failing to resolve is the ordinary outcome and the repair is more tasks.

Nine of them started in Federico's own working set. The original was read, never modified. What is published is a copy, edited so that it is useful to a stranger rather than only to the person who wrote it.

`autonomous-research` (formerly `opendraft`) is a port rather than a copy. Nothing in it was taken byte for byte: every file was written for this bundle against the OpenDraft engine (MIT) at a named commit, and its record maps each agent prompt and script back to the upstream file it came from, along with the upstream material deliberately left unported and why.

`domain-uptime-monitor`, `job-board-scout` (formerly the private worker `recruiter-job-scout-v1`) and `reply-debt` are ports of private Floom pure-script workers, rewritten rather than copied: nothing in them is byte-for-byte from the original. Each original was read end to end before anything was ported, to confirm it does real work against real data rather than asking a model to write something plausible, and each `DERIVATION.json` records that check, the rename where there was one, and every value that was a constant about one person or one deployment and is now required config. `reply-debt` is the one Skill in this repository that is not credential-free: it needs a Gmail connection, and says so before you install it rather than at run time.

`people-search` is neither a copy nor a port. It was written directly for this repository as part of GetEdge's September install-growth sprint, so its `DERIVATION.json` records licensing provenance only, not a source it was edited down from.

`agent-evals` was also written directly for this repository. Its structure follows a public evals masterclass by Alex Lieberman with Viv of LangChain, credited in the Skill and in its `DERIVATION.json`; no transcript or video material is included.

`cv-job-match` (formerly `rocketlist`) is Rocketlist's own Skill, published here by GetEdge. It works over Rocketlist's public job board at rocketlist.ai, and its `DERIVATION.json` records when each URL pattern and field name was checked against the live site.

`skill-miner`, `skill-eval-loop`, `agent-infra-fixer` and `skill-cockpit` were written for this repository as one loop. Their `DERIVATION.json` records the files they ship and their SHA-256; no session data from the runs reported above is included.

`harness-first` was written for this repository too. Its method comes from a public post by Mark Ajzenstadt (@mardehaym), credited in the Skill and in its `DERIVATION.json`; the post is linked, not quoted at length, and he did not review the Skill or its evaluation.

Each folder carries a `DERIVATION.json` recording that origin in full: for a working-set copy or port, the source location, every file copied, every file left behind, and the SHA-256 of each; for `people-search`, `agent-evals`, `cv-job-match` and `harness-first`, the files they ship and their SHA-256. Every folder's record also carries the licence that was added. A record cannot contain its own hash, so `DERIVATION.json` is excluded from the file list it describes.

The point of publishing the record alongside the copy is that you do not have to take the word "derived" on trust. You can read exactly what changed.

## Licence

These copies are Apache-2.0. The root `LICENSE` carries the full terms, and each bundle carries its own copy.

`pay-per-call-apis` (formerly `monid`) is the exception. It is Monid's work, not a GetEdge copy, so the Apache-2.0 grant does not cover it: it is redistributed unmodified apart from its front-matter name, in partnership with Monid, under Monid's own terms. The canonical copy is [monid.ai/SKILL.md](https://monid.ai/SKILL.md), and the Skill itself tells your agent to update from there when the Monid CLI and the Skill disagree on version. Its `DERIVATION.json` records the fetch date, the SHA-256 of the upstream file and the rename.

Apart from `cv-job-match`, the copyright holder named in those licence appendices is **Floom**, which is where these copies were first published and licensed: nine on 2026-09-07, and the paper bundle on 2026-09-09, republished in full as `opendraft` on 2026-09-10 (renamed `autonomous-research` on 2026-09-17). GetEdge publishes this repository; it did not relicense the bundles, and rewriting a dated copyright line would both misstate who granted the licence and invalidate the SHA-256 records in each `DERIVATION.json`. The licence text is upstream Apache-2.0 unmodified except for that appendix copyright line, which is what the Apache appendix instructs a licensor to fill in. `autonomous-research` also retains the MIT licence and copyright notice for the OpenDraft-derived material in `THIRD_PARTY_NOTICES.md`.

`cv-job-match` is Apache-2.0 like the rest, but it is Rocketlist's own Skill, so its licence appendix names **Rocketlist** as the copyright holder. Until 2026-09-16 that line read Floom; its `DERIVATION.json` records the change and the new SHA-256.

You may use, modify and redistribute these, subject to the licence's attribution requirement. The grant applies from the version it appears on and cannot be withdrawn from a version already fetched.

Before their recorded licence dates these copies carried no licence file at all, which under default copyright meant a stranger could read one and not modify or redistribute it. That was the wrong default for work meant to be installed by other people, and it is the one that applies when nobody chooses.

## What is not claimed

Five of these Skills have been measured against the same agent with the Skill absent, and each publishes its own page: `harness-first`, `autonomous-research`, `strip-image-ai-metadata`, `top-down-comms` and `workplan`. For the rest, no comparative evaluation has been run and no quality or safety state is asserted.

A published page is not the same as a positive result. Our rule, fixed before any of these numbers were read, is that a result counts only if the 95% confidence interval on the difference excludes zero. One of the five clears that bar, and it clears it only in the arm where the Skill is pasted into the prompt rather than left on disk for the agent to find. The other four are measured and unresolved. Each page says which it is in its opening paragraph, and the four that came down say so in a correction at the top rather than by quietly changing a number.

Ten computed figures have been withdrawn, and they are listed with their failure modes in [`evals/WITHDRAWN.md`](evals/WITHDRAWN.md). Six went because auditing the task showed the task was broken rather than the Skill. Four went because the interval they were read off was not a 95% interval, on task sets that are sound. We publish that file because a benchmark that only writes down the numbers that worked is a marketing document.

A result that clears the bar is evidence about the handful of tasks it was run on, not a general quality bar, and at three tasks per Skill this design is underpowered for effects of ordinary size. Six tasks per Skill is the requirement going forward. Every session log, grader verdict and task definition behind each page is in [`evals/`](evals/), so the numbers can be checked rather than taken. The loop results above measure the Skills the loop produced for one user, not the four loop Skills. These are working instructions, published because they were useful in practice. Package-level tests and gates are documented separately from evaluations.

Several call out to tools that must already be on your machine: `generate-image` drives the Codex CLI, `linkedin-media-prep` and `strip-image-ai-metadata` use ffmpeg and Python imaging libraries, and `security-audit-checklist` bundles three Python scanners. Read a Skill's instructions and its scripts before you run it, the same as any other code you install.

## Citation

The benchmark behind the EVALS.md pages is `edge-skill-bench@1.0`; [`docs/BENCHMARK.md`](docs/BENCHMARK.md) states its scope, its versioning rule and what it does not measure.

If you use **GetEdge Skills** in academic work, please cite it using the "Cite this repository" button on GitHub or the following BibTeX entry:

```bibtex
@software{GetEdge_Skills,
author = {De Ponte, Federico},
title = {{GetEdge Skills: measured Agent Skills and the loop that decides which ones to keep}},
year = {2026},
url = {https://github.com/getedgehq/skills}
}
```

A DOI is minted on the first Zenodo release and added to [`CITATION.cff`](CITATION.cff) and to the entry above.
