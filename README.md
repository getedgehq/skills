# skills

Sixteen Skills for agents, published by GetEdge. Eleven are edited copies from [Federico de Ponte's](https://github.com/federicodeponte) working set; two are companies' own Skills: `monid` is Monid's, published unchanged, and `rocketlist` is Rocketlist's, published by GetEdge; three, `people-search`, `agent-evals` and `harness-first`, were written directly for this repository. `harness-first` is the only one measured so far: it ships an evaluation of itself in [`harness-first/EVALS.md`](harness-first/EVALS.md).

A Skill is a folder with a `SKILL.md` at its root: a short front matter block naming the Skill and saying when to invoke it, then the instructions themselves. Agents that support Skills read the front matter to decide when a Skill applies, and the body once it does. Some of these carry scripts the instructions call.

## Installing one

```
npx skills add getedgehq/skills --skill workplan
```

`--list` shows everything available without installing. Each Skill is also a plain folder, so copying it into wherever your agent reads Skills from works just as well:

```
git clone https://github.com/getedgehq/skills
cp -r skills/workplan ~/.claude/skills/workplan
```

## Every one of these is a derived copy, and each says how it was derived

Nine of them started in Federico's own working set. The original was read, never modified. What is published is a copy, edited so that it is useful to a stranger rather than only to the person who wrote it.

`opendraft` is a port rather than a copy. Nothing in it was taken byte for byte: every file was written for this bundle against the OpenDraft engine (MIT) at a named commit, and its record maps each agent prompt and script back to the upstream file it came from, along with the upstream material deliberately left unported and why.

`people-search` is neither a copy nor a port. It was written directly for this repository as part of GetEdge's September install-growth sprint, so its `DERIVATION.json` records licensing provenance only, not a source it was edited down from.

`agent-evals` was also written directly for this repository. Its structure follows a public evals masterclass by Alex Lieberman with Viv of LangChain, credited in the Skill and in its `DERIVATION.json`; no transcript or video material is included.

`rocketlist` is Rocketlist's own Skill, published here by GetEdge. It works over Rocketlist's public job board at rocketlist.ai, and its `DERIVATION.json` records when each URL pattern and field name was checked against the live site.

`harness-first` was written for this repository too. Its method comes from a public post by Mark Ajzenstadt (@mardehaym), credited in the Skill and in its `DERIVATION.json`; the post is linked, not quoted at length, and he did not review the Skill or its evaluation.

Each folder carries a `DERIVATION.json` recording that origin in full: for a working-set copy or port, the source location, every file copied, every file left behind, and the SHA-256 of each; for `people-search`, `agent-evals`, `rocketlist` and `harness-first`, the files they ship and their SHA-256. Every folder's record also carries the licence that was added. A record cannot contain its own hash, so `DERIVATION.json` is excluded from the file list it describes.

The point of publishing the record alongside the copy is that you do not have to take the word "derived" on trust. You can read exactly what changed.

## Licence

These copies are Apache-2.0. The root `LICENSE` carries the full terms, and each bundle carries its own copy.

`monid` is the exception. It is Monid's work, not a GetEdge copy, so the Apache-2.0 grant does not cover it: it is redistributed unmodified, in partnership with Monid, under Monid's own terms. The canonical copy is [monid.ai/SKILL.md](https://monid.ai/SKILL.md), and the Skill itself tells your agent to update from there when the Monid CLI and the Skill disagree on version. Its `DERIVATION.json` records the fetch date and SHA-256.

Apart from `rocketlist`, the copyright holder named in those licence appendices is **Floom**, which is where these copies were first published and licensed: nine on 2026-09-07, and the paper bundle on 2026-09-09, republished in full as `opendraft` on 2026-09-10. GetEdge publishes this repository; it did not relicense the bundles, and rewriting a dated copyright line would both misstate who granted the licence and invalidate the SHA-256 records in each `DERIVATION.json`. The licence text is upstream Apache-2.0 unmodified except for that appendix copyright line, which is what the Apache appendix instructs a licensor to fill in. `opendraft` also retains the MIT licence and copyright notice for the OpenDraft-derived material in `THIRD_PARTY_NOTICES.md`.

`rocketlist` is Apache-2.0 like the rest, but it is Rocketlist's own Skill, so its licence appendix names **Rocketlist** as the copyright holder. Until 2026-09-16 that line read Floom; its `DERIVATION.json` records the change and the new SHA-256.

You may use, modify and redistribute these, subject to the licence's attribution requirement. The grant applies from the version it appears on and cannot be withdrawn from a version already fetched.

Before their recorded licence dates these copies carried no licence file at all, which under default copyright meant a stranger could read one and not modify or redistribute it. That was the wrong default for work meant to be installed by other people, and it is the one that applies when nobody chooses.

## What is not claimed

With one exception, no comparative model evaluation has been run against any of these, and no general quality or safety state is asserted. The exception is `harness-first`: [`harness-first/EVALS.md`](harness-first/EVALS.md) reports a single run comparing the same agent with and without that Skill loaded, on three tasks, with the confidence interval and the one task where it did not help stated there. That is evidence about those three tasks, not a general quality bar. These are working instructions, published because they were useful in practice. Package-level tests and gates are documented separately from evaluations.

Several call out to tools that must already be on your machine: `generate-image` drives the Codex CLI, `linkedin-media-prep` and `strip-image-ai-metadata` use ffmpeg and Python imaging libraries, and `security-audit-checklist` bundles three Python scanners. Read a Skill's instructions and its scripts before you run it, the same as any other code you install.

## The sixteen

| Skill | What it does |
| --- | --- |
| `agent-evals` | Builds evals for a working agent: yes/no tasks and verifiers, resettable environments, then a loop that turns production traces into new tasks. |
| `cli-ux-review` | Scores a command-line tool against a fixed rubric and writes the before/after fix for each failure. |
| `generate-image` | Generates images through the Codex CLI, billed to a ChatGPT subscription rather than a per-image API key. |
| `harness-first` | Diagnoses an unreliable or expensive agent by auditing its harness, traces, tools and context first, and refuses to recommend a model swap without evidence. Measured in [`harness-first/EVALS.md`](harness-first/EVALS.md). |
| `http-error-triage` | Separates a real credential problem from a CDN block, a wrong endpoint or a signature ban, before anyone concludes "the key is dead". |
| `linkedin-media-prep` | Converts, crops and compresses images and video to what LinkedIn actually accepts. |
| `monid` | Gives an agent one install for hundreds of data and scraping tools: discover an endpoint, inspect its schema, run it, and report the per-call cost against a Monid balance. Monid's own Skill, not Apache-2.0. |
| `opendraft` | Turns one topic line into a research-paper draft: eighteen agent prompts, keyless Crossref and OpenAlex lookup, and a citation-integrity gate that fails the run instead of shipping a broken bibliography. |
| `people-search` | Plans a people search, ranks supplied or public-source candidates against a brief, and discloses exactly which filters a connected provider can and can't support — without implying built-in LinkedIn access it doesn't have. |
| `product-launch-video` | Turns a product URL or launch brief into an editable, reviewed launch film using HyperFrames or Remotion with remocn primitives. |
| `rocketlist` | Reads a CV, works out what the person can actually do, and returns live startup roles from Rocketlist's public board with published salary, the evidence for the fit and an apply link. Rocketlist's own Skill. |
| `security-audit-checklist` | Audits app code, cloud config, containers, CI and IaC, with three bundled scanners. |
| `shadcn-first` | Builds UI from shadcn blocks and components instead of hand-written markup. |
| `strip-image-ai-metadata` | Strips C2PA and AI-generation metadata so platforms stop labelling an image. |
| `top-down-comms` | Structures a client-facing artifact the way MBB consultants do: governing thought first. |
| `workplan` | Creates, updates and closes a work plan so multi-step work survives losing context. |
