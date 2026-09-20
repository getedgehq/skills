# Evaluation status

Status: adopted against an empty baseline for the tested receipt task.

On 2026-09-19, three blind paired Harbor runs used Codex with `openai/gpt-5.6-sol`. The treatment installed this exact package. The baseline received the same task and fixtures without the package.

## Result

- Valid pairs: 3
- Treatment wins: 3
- Baseline wins: 0
- Ties: 0
- Treatment verifier pass rate: 3/3
- Baseline verifier pass rate: 0/3
- Tool errors: 0 in both arms

The deterministic verifier checked the required public JSON and SVG artifacts, schema validity, evidence hashing, privacy boundaries, unknown preservation, and the absence of false upload or deployment claims. The blind judge could not inspect every rendered detail from its view, so this result supports task completion and public-safety compliance, not a broad visual-quality claim.

Scope: this is a small pilot on one representative task and one model. It is evidence for adoption over no skill, not proof of universal improvement.

Reproducible artifacts are in `evals/agent-receipt/2026-09-19/agent-receipt-public-safe/`.
