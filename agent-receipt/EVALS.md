# Evaluation status

Status: inconclusive against an empty baseline.

On 2026-09-19, three blind paired Harbor runs used Codex with `openai/gpt-5.6-sol`. The treatment installed this exact package. The baseline received the same task and fixtures without the package.

## Corrected result

- Valid pairs: 3
- Treatment wins: 0
- Baseline wins: 0
- Ties: 3
- Treatment verifier pass rate: 3/3
- Baseline verifier pass rate: 3/3
- Tool errors: 0 in both arms

The corrected task disclosed its flat schema and digest algorithm to both arms. The deterministic verifier compared receipt digests with the trusted fixture, checked the required public JSON and SVG artifacts, enforced privacy boundaries, preserved unknowns, and rejected false upload or deployment claims. Both arms passed every objective check, and all blind verdicts were ties. The package caused no tested regression but demonstrated no lift.

An earlier three-pair run was invalidated after independent review found an undisclosed serialization contract and digest checks that validated syntax rather than binding. Its artifacts remain under `invalid-undisclosed-schema/` and do not support any claim.

Scope: one representative task, one model, and three corrected pairs. Reproducible artifacts are in `evals/agent-receipt/2026-09-19/corrected-schema-v2/`.
