# skills

Thirteen Skills for coding agents, published by GetEdge. Ten are edited copies from [Federico de Ponte's](https://github.com/federicodeponte) working set; three were written for this repository.

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

## Ten of these are derived copies, and each says how it was derived

Nine of them started in Federico's own working set. The original was read, never modified. What is published is a copy, edited so that it is useful to a stranger rather than only to the person who wrote it.

The tenth, `opendraft`, is a port rather than a copy. Nothing in it was taken byte for byte: every file was written for this bundle against the OpenDraft engine (MIT) at a named commit, and its record maps each agent prompt and script back to the upstream file it came from, along with the upstream material deliberately left unported and why.

Each folder carries a `DERIVATION.json` recording that edit in full: the source location, every file copied, every file left behind, the SHA-256 of each, and the licence that was added. A record cannot contain its own hash, so `DERIVATION.json` is excluded from the file list it describes.

The point of publishing the record alongside the copy is that you do not have to take the word "derived" on trust. You can read exactly what changed.

## Three are original

`scroll-video-site`, `web-hero-video` and `reference-first-design` were written from scratch for this repository on 2026-09-15. They are not copies of anything, so their `DERIVATION.json` records have no source files and no edits, only the files, their SHA-256 and the licence.

The technique they teach is inspired by the scroll video workflow [Viktor Oddy](https://x.com/viktoroddy) demonstrates publicly. No text, prompt or code from him or from motionsites.ai was used, and each of the three credits him by name.

## Licence

These copies are Apache-2.0. The root `LICENSE` carries the full terms, and each bundle carries its own copy.

The copyright holder named in those licence appendices is **Floom**, which is where these copies were first published and licensed: nine on 2026-09-07, the paper bundle on 2026-09-09, republished in full as `opendraft` on 2026-09-10, and the three original Skills on 2026-09-15. GetEdge publishes this repository; it did not relicense the bundles, and rewriting a dated copyright line would both misstate who granted the licence and invalidate the SHA-256 records in each `DERIVATION.json`. The licence text is upstream Apache-2.0 unmodified except for that appendix copyright line, which is what the Apache appendix instructs a licensor to fill in. `opendraft` also retains the MIT licence and copyright notice for the OpenDraft-derived material in `THIRD_PARTY_NOTICES.md`.

You may use, modify and redistribute these, subject to the licence's attribution requirement. The grant applies from the version it appears on and cannot be withdrawn from a version already fetched.

Before their recorded licence dates these copies carried no licence file at all, which under default copyright meant a stranger could read one and not modify or redistribute it. That was the wrong default for work meant to be installed by other people, and it is the one that applies when nobody chooses.

## What is not claimed

No evaluation has been run against any of these, and no quality or safety state is asserted.

`scroll-video-site` had one informal test before publishing, which is not an evaluation: five site briefs, each built once by the same model with the Skill and once without. All ten sites scrubbed with the scroll. The sites built with the Skill were lighter in all five, 5.6 MB against 11.4 MB at the median. Five briefs is too few to generalise from, and that test says nothing about design quality. These are working instructions, published because they were useful in practice, not because they passed a general quality bar.

Several call out to tools that must already be on your machine: `generate-image` drives the Codex CLI, `linkedin-media-prep` and `strip-image-ai-metadata` use ffmpeg and Python imaging libraries, `security-audit-checklist` bundles three Python scanners, and `scroll-video-site` and `web-hero-video` call ffmpeg and ffprobe. Read a Skill's instructions and its scripts before you run it, the same as any other code you install.

## The thirteen

| Skill | What it does |
| --- | --- |
| `cli-ux-review` | Scores a command-line tool against a fixed rubric and writes the before/after fix for each failure. |
| `generate-image` | Generates images through the Codex CLI, billed to a ChatGPT subscription rather than a per-image API key. |
| `http-error-triage` | Separates a real credential problem from a CDN block, a wrong endpoint or a signature ban, before anyone concludes "the key is dead". |
| `linkedin-media-prep` | Converts, crops and compresses images and video to what LinkedIn actually accepts. |
| `opendraft` | Turns one topic line into a research-paper draft: eighteen agent prompts, keyless Crossref and OpenAlex lookup, and a citation-integrity gate that fails the run instead of shipping a broken bibliography. |
| `reference-first-design` | Collects references and writes a design brief with explicit decisions and anti-references before any visual page is built. |
| `scroll-video-site` | Builds a site whose full-bleed background video plays forward and back with the scroll: encoding for instant seeks, text placement without an overlay, mobile and reduced-motion fallbacks, and a check script. |
| `security-audit-checklist` | Audits app code, cloud config, containers, CI and IaC, with three bundled scanners. |
| `shadcn-first` | Builds UI from shadcn blocks and components instead of hand-written markup. |
| `strip-image-ai-metadata` | Strips C2PA and AI-generation metadata so platforms stop labelling an image. |
| `top-down-comms` | Structures a client-facing artifact the way MBB consultants do: governing thought first. |
| `web-hero-video` | Plans and generates a short hero background video sized for scroll scrubbing: the shot, the camera move, where text will sit, and the prompt for a video model. |
| `workplan` | Creates, updates and closes a work plan so multi-step work survives losing context. |
