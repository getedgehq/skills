# Behavioral diff

This is a prospective, specification-level diff. No model comparison was run, so it reports intended behavior changes and no behavioral score.

| Situation | Current prompt risk | Optimized expected behavior |
|---|---|---|
| Read-only inspection | “Never act without asking” can trigger needless permission requests. | Inspect without asking when the work is safe, read-only, and in scope. |
| Explicitly authorized production action | The ask/act contradiction can cause repeated confirmation. | Treat explicit authorization as sufficient for the specified production action and proceed without asking again. |
| Diagnosis-only request | “Always act immediately” can blur diagnosis into remediation. | Diagnose without changing anything unless the user requests a fix; production still requires explicit authorization. |
| Completion report | A generic test instruction can be satisfied loosely or ignored. | Run relevant named tests before reporting completion; otherwise identify what remains unverified. |
| Existing user edits | Already protected. | Continue preserving unrelated user changes. |
| Secrets | Already protected. | Continue prohibiting secret disclosure. |
| Explanation quality | Requests hidden step-by-step reasoning and combines vague, conflicting style demands. | Provide observable outcomes and useful reporting without requesting hidden reasoning. |

## Removed or narrowed language

- Removed “helpful and smart” because it is subjective and not behaviorally testable.
- Replaced both absolute action rules with risk- and scope-based authorization rules.
- Removed the hidden-reasoning disclosure request.
- Removed the “concise but extremely detailed” tension; the replacement favors explicit operational rules.
- Narrowed completion claims to evidence from relevant named tests, with an honest unverified state when tests cannot run.

## Preserved invariants

- Production changes require explicit authorization.
- Unrelated user changes are preserved.
- Secrets are never exposed.
- Relevant tests gate completion claims.

The cases in `eval-manifest.json` are designed to measure these expectations later, including two held-out cases. Their presence is an evaluation design, not evidence of improved behavior.
