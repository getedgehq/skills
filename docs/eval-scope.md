# Eval scope for `edge-skill-bench@1.0`

Which Skills in this repository are measured by the benchmark, which are deliberately not, and
why. The method itself is in [`BENCHMARK.md`](BENCHMARK.md).

A Skill being out of scope is not a judgement on the Skill. It means a number for it would not
mean what a reader would take it to mean.

## The arithmetic

Ignoring the support directories `.github/` and `docs/`, the repository root holds
**29 product directories**. Of those, **28 contain a `SKILL.md`** and are Skills;
**1 does not** and is data.

```
29 product directories
  1  evals/                  raw eval material, not a Skill
 28  Skills
      3  alias shells        ship the canonical Skill's bytes, not separately measurable
     25  canonical Skills
          6  meta-tooling    benchmark machinery or separately evaluated, out of scope
         19  measurable      in scope for edge-skill-bench@1.0
```

Verify it in the clone:

```sh
for d in */; do d=${d%/}; [ -f "$d/SKILL.md" ] && echo "SKILL   $d" || echo "NOSKILL $d"; done
grep -l "alias_of" */SKILL.md
```

---

## In scope: 19 measurable Skills

These are the 19 the research report is built around. Each does work with a deliverable a
deterministic checker can inspect or execute, and each can be given a task a competent agent
without it might get wrong.

| Skill | Eval status |
| --- | --- |
| `autonomous-research` | Measured, unresolved. Ships [`EVALS.md`](../autonomous-research/EVALS.md) |
| `cli-ux-review` | Result withdrawn, task rebuilt, re-running |
| `cv-job-match` | Tasks authored and calibrated, first run in flight |
| `domain-uptime-monitor` | Not measured yet |
| `generate-image` | Tasks authored and calibrated, first run in flight |
| `harness-first` | Measured, unresolved. Ships [`EVALS.md`](../harness-first/EVALS.md) |
| `http-error-triage` | Result withdrawn, task rebuilt, re-running |
| `job-board-scout` | Not measured yet |
| `linkedin-media-prep` | Result withdrawn, task rebuilt, re-running |
| `pay-per-call-apis` | Tasks authored and calibrated, first run in flight |
| `people-search` | Result withdrawn, task rebuilt, re-running |
| `product-launch-video` | Tasks authored and calibrated, first run in flight |
| `reply-debt` | Not measured yet |
| `security-audit-checklist` | Result withdrawn, task rebuilt, re-running |
| `shadcn-first` | Result withdrawn, task rebuilt, re-running |
| `skillneed` | Measured, unresolved. Ships [`EVALS.md`](../skillneed/EVALS.md) |
| `strip-image-ai-metadata` | Measured, resolved. Ships [`EVALS.md`](../strip-image-ai-metadata/EVALS.md) |
| `top-down-comms` | Measured, resolved in `loaded`, unresolved in `skill`. Ships [`EVALS.md`](../top-down-comms/EVALS.md) |
| `workplan` | Measured, resolved. Ships [`EVALS.md`](../workplan/EVALS.md) |

Statuses are updated through 2026-09-19. Six of the 19 have published sessions, grader
verdicts and task definitions under [`evals/`](../evals/). For the other thirteen, no comparative
evaluation has landed and no quality claim is made. "Not measured yet" is the published state, not
an implied zero.

Two constraints on how some of these are testable at all, disclosed because a reader would
otherwise assume otherwise:

- **`pay-per-call-apis`** is a Skill about not overspending on metered APIs, so its tasks are built
  so that no attempt can make a real paid call. No credential appears in any task input, every
  catalog record, run record and spend dump is a recorded fixture, and each deliverable is a plan
  or a decision rather than an execution. The spending decision is priced deterministically by the
  checker from the agent's own parameters. It is never performed.
- **`generate-image`** needed a stand-in to be testable at all, because its real backend is a CLI
  billed to a subscription that cannot exist inside a sandbox. The task installs a deterministic
  offline renderer and writes a prompt-derived signature into the pixels, so the checker can tell a
  real render from a locally drawn image carrying forged metadata. This measures whether the agent
  prompts the tool correctly, not whether the real model draws well.

---

## Out of scope: 6 meta-tooling Skills

| Skill | What it is |
| --- | --- |
| `agent-skills-gap` | Session-profile product with a separate direct A/B evaluation, outside this frozen benchmark |
| `agent-evals` | Authoring and running agent evaluations |
| `agent-infra-fixer` | Fixing guard hooks that block legitimate agent work |
| `skill-cockpit` | The local browser page over mined themes, runs and the adoption ledger |
| `skill-eval-loop` | Turning a theme into an eval brief and running the with-and-without comparison |
| `skill-miner` | Reading session logs for corrections, frustration and tool errors, and drafting a Skill |

`agent-skills-gap` publishes its own direct Codex A/B record and is explicitly not an
`edge-skill-bench@1.0` result. **The other five are machinery that runs the evaluation, so
measuring them with themselves is circular.** A number produced for `skill-eval-loop` by an evaluation loop, or
for `agent-evals` by an eval harness, is the instrument reporting on itself. It would be graded by
criteria the Skill under test supplies the vocabulary for, and a reader could not tell an effect
from an echo. There is no blinding that fixes that, so no number is published for them rather than
a number published with a caveat.

This exclusion is about the benchmark, not about evidence in general. These packages can still be
judged the ordinary way, by whether the loop they run finds real defects and whether its adoption
decisions hold up. That is a different claim from a measured point delta and it is not made here.

---

## Out of scope: 3 alias shells

Renamed on 2026-09-17, with the old install names still resolving. Each declares its target in its
own front matter as `metadata.alias_of`.

| Alias slug | Canonical Skill | Confirmed by |
| --- | --- | --- |
| `monid` | `pay-per-call-apis` | `alias_of: pay-per-call-apis` |
| `opendraft` | `autonomous-research` | `alias_of: autonomous-research` |
| `rocketlist` | `cv-job-match` | `alias_of: cv-job-match` |

They are not separately measurable because they are not separate Skills. Every file in an alias
folder is a symlink to the canonical folder except `SKILL.md`, which is a real file differing only
in the `name:` field and the added `metadata: {internal: true, alias_of: ...}` block. Verify with
`git ls-files -s monid opendraft rocketlist`: mode `120000` is a symlink, `100644` a real file.

Counting a rename as its own Skill would measure the same bytes twice and inflate the coverage
figure. The 22 packages the platform lists are 19 distinct measurable Skills plus these 3 renames.

**One caution about `opendraft`, because the published package and the repository folder are not
the same thing.** In this repository `opendraft/SKILL.md` is byte-identical to
`autonomous-research/SKILL.md` apart from the name and metadata block. The package published to the
platform was an older copy, 396 lines against 560, so a reader who downloaded `opendraft` from the
platform got a Skill well behind the one beside it. That is a catalog defect rather than a
measurement defect, and the result in the report belongs to the 560-line text.

Separately, the published runs for `autonomous-research` were recorded under the `opendraft` run
slug, on 2 tasks rather than the usual 3. When reading
[`evals/autonomous-research/`](../evals/autonomous-research/), the `skill` field says `opendraft`
and the result is `autonomous-research`'s.

---

## Not a Skill: `evals/`

[`evals/`](../evals/) has no `SKILL.md`. It is the raw material behind the published numbers: per
run, the session logs turn by turn, every file the agents wrote, every grader verdict with its
reasoning, the task definitions, and the per-run summaries.

It currently holds directories for the six Skills with published evaluations:
`autonomous-research`, `harness-first`, `skillneed`, `strip-image-ai-metadata`,
`top-down-comms`, `workplan`.

If a summary anywhere disagrees with an artifact in `evals/`, the artifact is right.

---

## Task suites that exist but are not in scope

The harness working tree carries task suites for slugs that are not published Skills in this
repository: `duckdb-first`, `handoff-brief`, `spec-before-code`, and `opendraft` (the alias slug
under which `autonomous-research` was run). Numbers from those suites are not `edge-skill-bench`
results, because the benchmark measures Skills this repository publishes.

Task counts also vary from the 3-per-skill rule in the harness tree: `http-error-triage` has 5 task
directories and `strip-image-ai-metadata` has 6, while every published summary draws on 3 tasks per
skill (2 for `autonomous-research`). Which subset a given run used is recorded in that run's
`summary.json` under `pairs[].task_id`, and that record is the authority, not the directory count.

`NOT YET SPECIFIED:` how a task suite is admitted to `edge-skill-bench@1.0`. There is no written
rule stating that the benchmark's task set is exactly the 3 calibrated tasks per in-scope Skill, no
rule for which subset is used when more task directories exist, and no rule for what happens to the
version when a suite is added. Section 8 of [`BENCHMARK.md`](BENCHMARK.md) records the same gap
from the other side.

---

## A counting discrepancy in the root `README.md`

The root `README.md` describes "four" loop Skills and "the other fourteen Skills", which sums to
18. The repository holds 20 canonical Skills. The loop list of four omits `agent-evals`, and the
remainder is 16 rather than 14.

Noted here rather than fixed, because `README.md` is out of this document's scope. The counts that
`edge-skill-bench@1.0` uses are the ones verified against the filesystem at the top of this page:
29 product directories, 28 Skills, 25 canonical, 19 measurable.
