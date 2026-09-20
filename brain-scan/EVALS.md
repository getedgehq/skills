# Brain Scan release evaluation

We tested the Brain Scan comparison contract on three real task families reconstructed from
authorized session evidence. Each task ran three paired samples with exactly two arms:

1. no selected Skill; and
2. the selected Skill's complete frozen `SKILL.md` explicitly inserted into the task context.

Both arms used the same task, fixtures, agent, timeout, objective verifier, and blind A/B judge.
Each subject ran as an unprivileged user in a systemd filesystem namespace that exposed only its
own `/workspace`. User homes, host temp directories, other arms, and generated treatment briefs
were inaccessible.

**Across nine valid pairs, explicit loading won 6, tied 1, and lost 2. The loaded arm passed the
objective task gate 9 of 9 times versus 4 of 9 for the no-Skill arm: an observed +55.6 percentage
points.**

Run date: 2026-09-20. This is a release validation run, not an independent benchmark and not a
claim that every Skill improves every task.

## Results by task family

| Redacted task family | Pairs | Loaded win / tie / loss | Objective pass, loaded / no Skill |
| --- | ---: | ---: | ---: |
| Short direct message | 3 | 2 / 0 / 1 | 3 / 1 |
| Founder post from a source corpus | 3 | 2 / 1 / 0 | 3 / 1 |
| Existing-asset launch plan | 3 | 2 / 0 / 1 | 3 / 2 |
| **Total** | **9** | **6 / 1 / 2** | **9 / 4** |

No run exited non-zero and neither arm recorded a tool error. Mean active runtime was 55.7 seconds
with the Skill and 18.7 seconds without it. Runtime is descriptive; the run was neither designed
nor powered as a speed benchmark.

## What this validates

- Brain Scan can reconstruct representative work, freeze it, and run the requested two-arm
  explicit-load comparison.
- Explicit loading was mechanically verified by a SHA-256 binding between each treatment prompt
  and the selected Skill. The no-Skill prompt used a different frozen hash.
- The final harness prevented the contamination found in two discarded attempts: the subject could
  not read user-level Skills, another arm, or the generated treatment brief.
- Results remain task-level. One observed treatment loss is not hidden by the aggregate.

## Privacy and evidence

The real inputs included private conversations and unpublished content, so raw fixtures, prompts,
transcripts, and deliverables are not public. The machine-readable
[`eval-results/summary.json`](eval-results/summary.json) publishes the protocol, per-sample verdicts,
objective results, runtimes, frozen Skill hashes, and artifact hashes without publishing private
content. The private source record remains available to the owner for hash verification.

## Discarded runs

Three pre-release attempts are excluded from every number above:

- a Codex run whose subject process could not create its sandbox (`bwrap` unavailable);
- an OpenCode run that retained ambient user Skills; and
- a HOME-isolated OpenCode run whose baseline could still traverse the host filesystem and find the
  generated treatment brief.

Those failures directly produced the final systemd namespace requirement. They are disclosed here
rather than silently replaced.

## Limits

- Three task families and nine pairs are too small for a universal efficacy claim.
- Tasks, verifiers, and Skills came from the publisher's own session evidence.
- The agent was OpenCode's `opencode/big-pickle` default; the blind judge used the locally configured
  Codex CLI default, whose exact model identifier was not emitted by this harness version.
- Explicit loading measures Skill-content effect when the content is present. It does not measure
  natural discovery or trigger quality.
- Private artifacts are hash-bound but cannot be independently inspected from this public package.

