# Brain Scan release evaluation

We tested Brain Scan on three real task families reconstructed from authorized session evidence.
Each task ran three paired samples with exactly two arms: no selected Skill, and the selected
Skill's complete frozen `SKILL.md` explicitly inserted into the task context.

Both arms used Codex `gpt-5.6-sol` with the same task, fixtures, timeout, objective verifier, and
blind `gpt-6-astra` judge. The judge received each anonymous arm's final response and the readable
contents of its produced artifacts, not just filenames. Each subject ran as an unprivileged user in
a systemd filesystem namespace exposing only its own `/workspace`.

**Measured pilot: across nine valid pairs, explicit loading won 8 and lost 1. The loaded arm passed
the objective task gate 8 of 9 times versus 5 of 9 for the no-Skill arm: +33.3 percentage points
observed.**

Run date: 2026-09-20. This is publisher-authored release validation, not an independent benchmark
or a universal Skill-efficacy claim.

## Results by task family

| Redacted task family | Pairs | Loaded win / tie / loss | Objective pass, loaded / no Skill |
| --- | ---: | ---: | ---: |
| Short direct message | 3 | 3 / 0 / 0 | 3 / 0 |
| Founder post from a source corpus | 3 | 3 / 0 / 0 | 3 / 2 |
| Existing-asset launch plan | 3 | 2 / 0 / 1 | 2 / 3 |
| **Total** | **9** | **8 / 0 / 1** | **8 / 5** |

All 18 subject runs exited zero and neither arm recorded a tool error. Mean active runtime was 38.8
seconds with the Skill and 32.9 seconds without it. Runtime is descriptive; this was not a speed
benchmark.

## What this validates

- Brain Scan can reconstruct representative work, freeze it, and run the requested two-arm
  explicit-load comparison.
- Explicit loading was mechanically verified by a SHA-256 binding between each treatment prompt
  and the selected Skill. The no-Skill prompt used a different frozen hash.
- The final harness prevented the subject from reading user-level Skills, another arm, or generated
  treatment context.
- The blind judge compared actual artifact content. Hidden runner state, injected Skills, and arm
  identity were excluded symmetrically.
- The existing-asset plan's loaded arm failed one objective check, so that Skill does not pass the
  task-level adoption gate despite winning 2 of 3 blind comparisons.

## Privacy and evidence

The real inputs included private conversations and unpublished content, so raw fixtures, prompts,
transcripts, and deliverables are not public. The machine-readable
[`eval-results/summary.json`](eval-results/summary.json) publishes the protocol, per-sample verdicts,
objective results, runtimes, frozen Skill hashes, and artifact hashes. The private source record
remains available to the owner for hash verification.

## Discarded runs

Earlier attempts are excluded from every number above:

- a Codex run whose internal sandbox could not start because `bwrap` was unavailable;
- OpenCode runs that exposed ambient Skills or treatment context;
- the later isolated OpenCode result, because `opencode/big-pickle` is an undisclosed model route,
  not the requested pinned Codex subject; and
- the first verdicts over the final Codex outputs, because the judge saw filenames but not the
  contents of file-based deliverables. The same unchanged outputs were rejudged after
  artifact-content evidence was added.

These are retained as invalid-run records and are not counted.

## Limits

- Three task families and nine pairs are too small for a universal efficacy claim.
- Tasks, verifiers, and Skills came from the publisher's own session evidence.
- Explicit loading measures Skill-content effect when the content is present. It does not measure
  natural discovery or trigger quality.
- Private artifacts are hash-bound but cannot be independently inspected from this public package.
