# SkillNeed v4 expanded preregistration

Frozen before any v4 executor output is inspected.

## Question

Measure separately:

1. the installed-system effect when the agent must discover and read SkillNeed; and
2. the procedure effect when the same SkillNeed instructions are always loaded.

The arms are never pooled. The six published v3 task families and all earlier development tasks are excluded.

## Fixed package and models

- Candidate: `skillneed`
- `SKILL.md` SHA-256: `ba07fac79824f00187b0237cc0dd379d4ce2066ef38046d1bfb053795324d29e`
- `DERIVATION.json` SHA-256: `bed8349fa4538c28d61fa89970f42286f23d2c66bc38e0813e175da3434f4528`
- Executor: Claude Sonnet 4.5, Bedrock inference profiles `us.` and `global.`
- Judge: Claude Haiku 4.5, Bedrock inference profiles `us.` and `global.`
- Maximum 40 turns and $2.50 per attempt; $25 total v4 cap; no optional stopping.

## Frozen task matrix

Twenty independent task families, three samples per arm:

### Recommend one package

1. `oauth-401-proxy` → `http-error-triage`
2. `runaway-agent-cost` → `harness-first`
3. `executive-incident-update` → `top-down-comms`
4. `backend-candidate-evidence` → `people-search`
5. `product-demo-film` → `product-launch-video`
6. `social-video-crop` → `linkedin-media-prep`
7. `remove-generation-metadata` → `strip-image-ai-metadata`
8. `prelaunch-security-review` → `security-audit-checklist`
9. `multiweek-data-migration` → `workplan`
10. `cli-command-review` → `cli-ux-review`

### No extra Skill

11. `basic-percentage`
12. `italian-translation`
13. `paragraph-summary`
14. `friendly-rewrite`

### Already covered

15. `covered-http-triage`
16. `covered-workplan`
17. `covered-people-search`

### Missing prerequisite or no approved match

18. `missing-confidential-pdf`
19. `missing-service-access`
20. `no-approved-match`

Every task has a distinct fixture/catalog composition, a rubric fixed before execution, and a semantic checker calibrated against one known-bad, one short known-good, and one thorough known-good-compatible pattern. All 40 checked calibration fixtures must pass in the expected direction before execution.

## Arms and counts

- Arms: `base`, `loaded`, `skill`
- Samples: 3
- Executor attempts: 20 × 3 × 3 = 180
- Comparisons: 60 loaded/base + 60 skill/base = 120
- Blind judgments: both presentation orders for every pair = 240

`base` must never read SkillNeed. `loaded` must report a read in all 60 attempts. The installed arm's actual read rate is part of the system result; unread attempts remain in that arm and are reported as invocation failures. Corrupt or unknowable load traces invalidate only the affected pair.

## Blinding and inference

The judge receives anonymous outputs, delivered files, and observable tool summaries. It does not receive the arm, Skill path, Skill-read flag, or deterministic checker result. Each pair is judged in both orders; conflicting winner votes become a tie.

The primary estimate is the mean per-task rubric-score delta. Its two-sided 95% Student t interval is calculated over the 20 independent task-family means (`df=19`). Repeated samples reduce within-task noise and are not treated as independent tasks. Preference win value, checker score/pass rate, W/T/L, order disagreement, costs, turns, and invocation rate are secondary results. A result is supported only if its predefined interval excludes the null and no integrity gate fails.

## Integrity gates

Before aggregation, assert:

- exactly the 20 frozen task IDs and no others;
- 180 completed executor attempts;
- zero base reads and 60/60 loaded reads;
- exactly 240 judgment files, with both orders for each of 120 pairs;
- exact candidate hashes above;
- all exclusions, infrastructure failures, and capped attempts disclosed;
- redacted raw tasks, outputs, checker results, verdicts, and package identity exported.

No task replacement, sample top-up, rubric change, checker change, package change, model change, or early stop is permitted after the first executor output exists. A necessary change creates a new version and leaves v4 invalid or incomplete.
