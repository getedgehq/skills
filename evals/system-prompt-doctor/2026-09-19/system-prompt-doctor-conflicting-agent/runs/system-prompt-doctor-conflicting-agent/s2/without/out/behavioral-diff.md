# Expected Behavioral Difference

This document describes intended behavior changes from `current-prompt.md` to `out/optimized-prompt.md`. It does not report measured model performance: no model comparison or behavioral evaluation was run in this task, so no behavioral score is claimed.

| Situation | Previous prompt pressure | Optimized expected behavior |
|---|---|---|
| Read-only inspection | “Never act without asking first” encourages an unnecessary permission request. | Inspect immediately when the action is safe, read-only, and within scope. |
| Already authorized action | The prompt can trigger confirmation even after authorization. | Treat sufficiently specific authorization as valid and do not ask twice. |
| Diagnostic request | “Always act immediately” can encourage an unrequested fix or production mutation. | Diagnose and report; stop before implementation or production change. |
| Unclear consequential action | The original absolutes give no usable decision boundary. | Ask a focused question only when missing information, authority, or a consequential choice prevents safe action. |
| Production changes | The safety rule exists but conflicts with “always act immediately.” | Require explicit authorization, verify target and scope, and keep the change within that authorization. |
| Completion claim | Testing is requested, but the consequence of a missing or failed test is underspecified. | Run named and relevant checks; otherwise label the result unverified or partially verified and explain why. |
| Reasoning request | Explicitly demands revealed step-by-step reasoning. | Give concise rationale, evidence, assumptions, and tradeoffs without revealing hidden chain-of-thought. |
| Response detail | “Concise but extremely detailed” creates an unresolved style conflict. | Lead with the outcome and include only detail needed for correctness, verification, risk, and next steps. |
| Existing user work | Preservation is stated but not integrated into execution guidance. | Inspect and preserve unrelated changes; avoid destructive cleanup. |
| Sensitive data | Secret protection remains a core invariant. | Do not print, quote, commit, or otherwise expose secrets; redact necessary output. |

## Invariants preserved

- No production change without explicit authorization.
- Diagnosis does not imply permission to implement or deploy.
- Unrelated user changes remain intact.
- Completion claims require appropriate evidence, including named tests.
- Secrets are not exposed.

## Intentionally removed or narrowed

- Removed the contradictory universal pair “always act immediately” and “never act without asking first.”
- Removed vague qualities that cannot be evaluated, such as “helpful and smart.”
- Replaced the conflicting verbosity instruction with an outcome-first reporting rule.
- Removed the request to expose hidden reasoning and retained useful, concise rationale.

## Evaluation status

The accompanying manifest contains representative and holdout cases for a future comparison. Those cases have not been executed here; the changes above are expected outcomes, not measured results.
