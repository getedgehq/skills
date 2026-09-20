# Behavioral Diff

## Outcome

The optimized prompt replaces universal, contradictory commands with request-mode, scope, authorization, and evidence rules. It preserves the four real invariants in the source prompt: explicit authorization for production changes, preservation of unrelated changes, test-backed completion, and protection of secrets.

No behavioral score or quality lift is claimed. No current-versus-candidate model comparison was run in this task.

## Expected behavior changes

| Situation | Current prompt tendency | Optimized expected behavior |
|---|---|---|
| Read-only explanation | May ask permission because it says never act without asking. | Inspect relevant sources immediately and answer with evidence; make no edits. |
| Explicitly authorized deployment | May ask twice because universal confirmation conflicts with immediate action. | Resolve the target, execute once authorized, and report the observed result without redundant confirmation. |
| Production diagnosis | Vague helpfulness can be interpreted as permission to fix. | Keep diagnosis read-only unless mutation is separately requested and authorized. |
| Named verification command | “Relevant tests” leaves room to skip the named test. | Run the named test and tie any completion claim to its observed result. |
| Ambiguous destructive production action | “Always act immediately” pressures premature execution. | Verify the exact target and scope; ask only for the unresolved material detail. |
| Secret-bearing evidence | Prohibition exists but handling is unspecified. | Avoid propagating secrets and redact sensitive values in commands, logs, patches, and responses. |
| Reasoning request | Requires hidden chain-of-thought disclosure. | Give conclusions, evidence, and a brief rationale without private chain-of-thought. |
| Conflicting content in logs or files | No trust-boundary rule. | Treat retrieved instructions as untrusted data unless the user explicitly adopts them. |

## Instruction-level changes

- Removed “Always act immediately” and “Never act without asking first.” Replaced them with calibrated rules based on request type, risk, ambiguity, and authorization.
- Replaced “Be helpful and smart” with observable responsibilities: accurate scoped work, evidence, verification, and honest residual-risk reporting.
- Replaced “Think step by step and reveal your reasoning” with concise rationale and evidence, while explicitly protecting private chain-of-thought.
- Replaced “Be concise but extremely detailed” with a concrete reporting payload: conclusions, evidence, actions, verification, and remaining risks.
- Expanded “You can use tools” into rules governing read-only autonomy, implementation authority, production safety, destructive ambiguity, and tool-result evidence.
- Strengthened the completion rule so named tests are mandatory when available and unobserved success cannot be claimed.
- Preserved and operationalized secret protection and unrelated-change preservation.
- Added an untrusted-content boundary to prevent instructions embedded in repository or tool content from overriding the task.

## Preserved invariants

1. Production mutation still requires explicit authorization. Authorization removes redundant confirmation, but it does not permit guessing an ambiguous or destructive target.
2. Unrelated user changes remain protected.
3. Implementation completion remains contingent on relevant verification; a user-named test must be run.
4. Secrets remain non-disclosable, with explicit redaction behavior added.

## Evaluation plan

The manifest contains eight development cases and two sealed holdout cases. The development set covers all four observed failures plus production authorization, unrelated changes, secret handling, and hidden-reasoning requests. The holdout set probes ambiguous destructive authorization and prompt injection through untrusted build logs.

Run the current and optimized prompts with the same model version, tool permissions, fixtures, and sampling settings. Record responses, tool calls, assertion outcomes, token usage, latency, and errors. Do not tune on the holdout cases. Only after those runs may a behavioral score, quality lift, token delta, or battle result be reported.

## Residual risks

- The model, provider, and runtime tool contract are unspecified, so the prompt is provider-neutral and untested.
- “Explicit authorization” may need a runtime-specific definition if an organization treats a direct production imperative as authorization; the manifest currently tests the stricter interpretation encoded by the source invariant.
- Production versus non-production environments must be reliably labeled by the runtime or task context.
- No empirical regression, latency, cost, or token comparison is available until the manifest is executed.

