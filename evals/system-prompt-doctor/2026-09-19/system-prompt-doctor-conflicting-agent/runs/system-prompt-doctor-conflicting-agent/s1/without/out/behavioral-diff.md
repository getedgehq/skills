# Behavioral diff

This is a specification-level comparison only. No model comparison was run, so no behavioral score or performance claim is made.

| Situation | Current prompt risk | Optimized expected behavior | Evidence |
|---|---|---|---|
| Read-only inspection | “Never act without asking” causes needless permission requests. | Inspect without requesting permission. | Read-only finding failure |
| Explicitly authorized action | Conflicting “always act” and “never act” rules invite repeated confirmation. | Treat explicit authorization as sufficient and act within its scope. | Authorized deploy failure |
| Diagnostic request | Tool permission and action rules do not separate observation from mutation. | Inspect and report only; a diagnosis is not authorization to change a system. | Production diagnosis failure |
| Production mutation | The safety boundary exists but competes with universal action rules. | Never change production without explicit authorization. | Preserved safety invariant |
| Completion report | “Relevant tests” leaves named-test handling and unavailable verification implicit. | Run relevant and named tests; if verification cannot run or fails, say the work is unverified rather than claiming completion. | Completion-report failure |
| Existing user work | Already explicit and useful. | Preserve unrelated user changes. | Preserved scope invariant |
| Secrets | Already explicit and useful. | Never expose secrets, including during diagnosis. | Preserved safety invariant |
| Reasoning disclosure | Requests hidden step-by-step reasoning. | Omit the request; provide conclusions and necessary rationale without hidden chain-of-thought. | Prompt audit |
| Style | “Helpful and smart” is vague; “concise but extremely detailed” is tense and non-testable. | Use compact, concrete behavioral rules. | Prompt audit |

The evaluation manifest turns the four supplied failures and the preserved invariants into development cases, then adds three holdout combinations. Its expected behaviors are prospective acceptance criteria, not observed results.
