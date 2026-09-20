# Sources / closest existing primitives

## 1. Sentry `prompt-optimizer`

- Repo: `getsentry/skills`
- Path: `skills/prompt-optimizer/`
- License: Apache-2.0
- Why it matters: closest public skill to the proposed idea. It explicitly optimizes system, developer, and agent prompts with an eval-first workflow, candidate beam, holdout validation, model-family notes, and prompt compaction.
- Reuse: contract capture, external-context inventory, candidate-beam pattern, failure clustering, holdout validation, prompt compaction.

## 2. Promptfoo prompt optimization

- Docs: `https://www.promptfoo.dev/docs/usage/prompt-optimization/`
- Why it matters: provides an executable baseline → candidate suggestions → evaluation → held-out validation loop via `promptfoo optimize`.
- Reuse: optimization runner and validation split rather than inventing our own optimizer search.

## 3. Promptfoo eval/red-team Agent Skills

- Docs: `https://www.promptfoo.dev/docs/integrations/agent-skill/`
- Why it matters: ready-made eval and red-team skills, calibrated grading guidance, CI-friendly result output.
- Reuse: eval authoring, deterministic assertions first, evidence discipline, red-team setup.

## 4. Anthropic agent-development skill

- Repo: `anthropics/claude-code`
- Path: `plugins/plugin-dev/skills/agent-development/SKILL.md`
- Why it matters: concrete system prompt structure: role, responsibilities, analysis process, quality standards, output format, edge cases; advises keeping system prompts under 10k characters.
- Reuse: structural audit checklist, not a universal scoring rubric.

## 5. `claude-md-optimizer`

- Repo: `wrsmith108/claude-md-optimizer`
- Why it matters: specifically optimizes oversized `CLAUDE.md` / `AGENTS.md` / Copilot instruction files using progressive disclosure and validates information preservation.
- Reuse: instruction-file compaction / progressive-disclosure path when the bottleneck is context bloat rather than behavioral wording.

## 6. Anthropic `skill-creator`

- Repo: `anthropics/skills`
- Why it matters: train/held-out optimization and repeated trigger trials demonstrate how to optimize agent instructions without tuning to the test set.
- Reuse: train/heldout discipline and iterative improvement logs.

## Edge-specific addition

None of the above makes the output a consumer social object. Edge adds:

- current vs optimized Battle
- result cloud sync
- share card
- community prompt-battle data (only for user-owned/public prompts)
- model/version-specific results
- token-cost tradeoff
- opt-in insights for future recommendations

