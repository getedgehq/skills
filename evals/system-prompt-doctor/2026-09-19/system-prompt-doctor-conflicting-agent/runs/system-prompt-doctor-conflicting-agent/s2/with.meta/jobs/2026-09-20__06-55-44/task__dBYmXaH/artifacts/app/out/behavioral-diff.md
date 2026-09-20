# Behavioral diff

No model comparison was run in this task. The changes below are intended behavioral effects, not measured results, and no behavioral score is claimed.

| Area | Current prompt | Optimized prompt | Intended effect / evidence |
|---|---|---|---|
| Ask versus act | Says both “Always act immediately” and “Never act without asking first.” | Read-only work needs no permission; requested changes proceed unless scope or authorization is missing. | Avoids needless permission for inspection and duplicate confirmation after authorization, matching two recorded failures. |
| Diagnosis boundary | Immediate action can be read as permission to mutate. | “Diagnose without change.” | Prevents remediation when the user requested diagnosis only. |
| Production safety | Requires explicit authorization. | Preserves the same explicit-authorization boundary. | Maintains the material production safeguard. |
| Completion | Requires relevant tests but leaves named-test and blocked-test reporting implicit. | Requires relevant and named tests; otherwise the work must be reported as unverified. | Directly addresses the false completion claim in `failures.json`. |
| Existing work | Protects unrelated user changes. | Preserves that invariant. | Avoids collateral edits or rollback of user work. |
| Secrets | Prohibits exposing secrets. | Preserves secret protection. | Maintains the confidentiality boundary. |
| Reasoning | Demands step-by-step revealed reasoning. | Requests concise conclusions, not private reasoning. | Removes a hidden-reasoning request while retaining useful conclusions. |
| Style | “Helpful and smart” is vague; “concise but extremely detailed” conflicts. | Uses one concise-output instruction. | Makes the output requirement observable and removes a contradiction. |
| Tools | Merely states that tools may be used. | Omits redundant capability text. | Leaves capabilities to the runtime and focuses the prompt on action boundaries. |

## Verification plan

Run the current and optimized prompts against the same manifest, model/version, tool permissions, and clean fixtures. Tune only with train and validation cases. Use the two holdout cases once for the final comparison, recording outputs, tool calls, mutations, test evidence, token usage, latency, and cost.

## Residual risks

- The runtime must enforce actual production and secret access controls; prose alone is not a security boundary.
- “Relevant tests” still requires task-specific judgment when the user names none.
- Ambiguous conversational authorization may require clarification.
- Until the manifest is executed, none of the intended effects is a demonstrated behavioral improvement.
