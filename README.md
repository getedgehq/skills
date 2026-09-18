# GetEdge Skills

[![Catalogue](https://img.shields.io/badge/Catalogue-getedge.cc-000000?style=for-the-badge&color=154CFF)](https://getedge.cc)
[![Licence](https://img.shields.io/badge/Licence-Apache--2.0-000000?style=for-the-badge&color=154CFF)](LICENSE)

GetEdge Skills is a set of Agent Skills from [GetEdge](https://getedge.cc), published together with the loop that decides which of them are worth keeping. You can use it to:

- Install a single Skill into Claude Code, Codex, OpenCode or anything else that reads a `SKILL.md`.
- Mine your own session logs for what your agent keeps getting wrong.
- Prove a Skill helps on your own tasks, with a blind A/B eval, before you adopt it.
- Read the measured result for a Skill that ships one, in that Skill's own `EVALS.md`.

The full catalogue, a write-up per Skill, and what the loop found when it was run on real work are at [getedge.cc](https://getedge.cc).

## Installation

```bash
npx skills add getedgehq/skills --skill skill-miner
```

`--list` prints every Skill without installing one. A Skill is just a folder with a `SKILL.md` at its root, so a clone and a copy works too:

```bash
git clone https://github.com/getedgehq/skills
cp -r skills/workplan ~/.claude/skills/workplan
```

## The self-improvement loop

Four of these Skills form a loop that runs on your own machine, over your own session logs, and keeps a Skill only when it measurably improves your own work:

1. `skill-miner` reads Claude Code, Codex and OpenCode session logs for corrections you had to type, frustration, token burn, tool errors and hook blocks, clusters them into themes, and drafts a Skill for each or finds an existing one.
2. `skill-eval-loop` turns a theme into an eval brief built from your real task, runs the agent with and without the Skill in isolated directories, has a blind judge compare the two, repeats that three times, and adopts the Skill only on a majority win whose output also passes a deterministic check.
3. `agent-infra-fixer` handles the failures that are not knowledge at all: guard hooks that block legitimate work, or block without telling the agent why.
4. `skill-cockpit` is a local browser page over all of it: mined themes, runs in progress, per-sample verdicts and the adoption ledger.

Nothing leaves your machine except the calls your agent CLI already makes and, when you ask `skill-miner` to look for an existing Skill, a registry search query. No session log, brief, fixture or adopted Skill from the author's own runs is in this repository.

## Start here

| If you want to | Install |
| --- | --- |
| Find what your agent keeps getting wrong | `skill-miner` |
| Prove a Skill helps before you keep it | `skill-eval-loop` |
| Fix hooks that block your agent silently | `agent-infra-fixer` |
| Watch the whole loop in a browser | `skill-cockpit` |
| Debug a slow or unreliable agent | `harness-first` |
| Keep long work alive across context loss | `workplan` |

The other fourteen Skills, from security audits to launch films, are listed at [getedge.cc](https://getedge.cc) and by `npx skills add getedgehq/skills --list`.

## Provenance and results

Every Skill folder carries a `DERIVATION.json` recording where it came from: the source it was copied or ported from, every file shipped and the SHA-256 of each, every file deliberately left behind, and the licence that was added. You do not have to take the word "derived" on trust, you can read exactly what changed.

Five Skills ship an evaluation of themselves: [`harness-first`](harness-first/EVALS.md), [`autonomous-research`](autonomous-research/EVALS.md), [`strip-image-ai-metadata`](strip-image-ai-metadata/EVALS.md), [`top-down-comms`](top-down-comms/EVALS.md) and [`workplan`](workplan/EVALS.md). Our bar, fixed before any of those numbers were read, is a 95% confidence interval on the judge point delta that excludes zero. Each page says in its opening paragraph whether its result cleared that bar, and two of the five did not. Every session log, grader verdict and task definition behind them is in [`evals/`](evals/), so the numbers can be checked rather than taken. For the Skills without a page, no comparative evaluation has been run and no quality or safety claim is made.

Several Skills call out to tools that must already be on your machine, such as the Codex CLI, ffmpeg or Python imaging libraries. Read a Skill's instructions and its scripts before you run it, the same as any other code you install.

## Licence

Apache-2.0, in the root [`LICENSE`](LICENSE) and again in each Skill folder. The copyright holder named in those appendices is Floom, where these copies were first published and licensed, except for `cv-job-match`, which is Rocketlist's own Skill and names Rocketlist. `autonomous-research` also retains the MIT notice for its OpenDraft-derived material in its `THIRD_PARTY_NOTICES.md`.

`pay-per-call-apis` is the one exception to that grant. It is Monid's work, not a GetEdge copy, redistributed unmodified apart from its front-matter name and under Monid's own terms, with [monid.ai/SKILL.md](https://monid.ai/SKILL.md) as the canonical copy.

Three Skills were renamed on 2026-09-17 and the old install names still resolve: `opendraft` is now `autonomous-research`, `rocketlist` is `cv-job-match`, and `monid` is `pay-per-call-apis`. The old-name folders are alias shells built from symlinks, so on Windows use the new name.

## Citation

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
