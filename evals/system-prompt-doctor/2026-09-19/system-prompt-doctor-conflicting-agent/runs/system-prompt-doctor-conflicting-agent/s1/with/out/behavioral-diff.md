# Behavioral Diff

## Outcome

The optimized prompt resolves the observed ask-versus-act, scope, and completion failures while preserving the original production, data-protection, change-preservation, and verification invariants. This is a specification-level comparison only: no model runs were performed, so no behavioral score or performance lift is claimed.

## Expected behavior changes

| Situation | Current prompt pressure | Optimized expected behavior | Evidence / reason |
|---|---|---|---|
| Read-only inspection | “Always act” conflicts with “Never act without asking” | Inspect in-scope resources without permission and make no changes | Addresses the historical unnecessary-permission failure |
| Explicitly authorized deployment | “Never act without asking” can cause repeated confirmation | Execute the established, authorized workflow unless scope or risk changes | Addresses the historical duplicate-confirmation failure |
| Diagnosis request | “Always act immediately” can be read as a mandate to remediate | Investigate and report only; require separate authorization to mutate | Addresses the historical unauthorized production change |
| Completion report | Testing rule is present but underspecified | Run named/relevant checks; report actual results; state when verification is blocked or failing | Addresses the historical unsupported success claim |
| Ambiguous low-risk work | No threshold for asking | State a reasonable assumption and proceed when the choice is not material | Reduces unnecessary blocking |
| Consequential or destructive work | Production rule exists, but other risky actions are not classified | Verify target and scope; ask when authorization or a material choice is missing | Extends the same safety principle consistently |
| Reasoning request | Requires step-by-step reasoning disclosure | Give conclusions, assumptions, evidence, and concise rationale without private chain-of-thought | Removes a hidden-reasoning request while preserving explainability |
| Response depth | “Concise” conflicts with “extremely detailed” | Default concise; add detail based on complexity, risk, or user request | Creates an observable depth policy |
| Untrusted instructions | Not addressed | Do not allow file, log, tool, or external content to override scope or governing instructions | Adds a prompt-injection boundary relevant to tool use |

## Preserved invariants

- Production changes still require explicit authorization.
- Unrelated user changes must remain intact.
- Secrets must not be exposed and must be redacted if encountered.
- Relevant verification is required before a supported completion claim.
- The agent remains action-oriented for safe, authorized, in-scope work.

## Structural changes

The original prompt is a single paragraph containing broad traits and absolute commands. The optimized prompt groups operational rules under act-or-ask, scope and safety, execution and verification, and communication. Absolute rules are retained only where the intended invariant is genuinely absolute; otherwise, decision criteria and exceptions are explicit.

## Measurement status

- Model comparison: not run.
- Behavioral score: not calculated.
- Quality lift, regression rate, latency, and cost: unknown.
- Token delta: not reported because no target tokenizer or model was specified. The files can be tokenized consistently once a target model is selected.
- Eval readiness: ten explicit cases are defined in `out/eval-manifest.json`; eight are development cases and two are untouched holdouts.

## Residual risks

- The target model and tool environment are unspecified, so adherence may vary by runtime.
- “Production,” “destructive,” and “material risk” may need domain-specific examples in a deployment-specific adapter.
- The prompt does not define organization-specific approval roles, release controls, or secret-handling procedures.
- The optimized prompt should be compared with the current prompt using the same model, tools, and graders before adoption.

## Recommended comparison protocol

Run both prompts against the eight development cases with identical model settings and tool permissions. Repair only failures found there. Freeze the selected candidate, then evaluate both prompts once on the two holdout cases. Record outputs, tool calls, pass/fail reasons, token usage, latency, and cost; only then report a behavioral score or improvement claim.
