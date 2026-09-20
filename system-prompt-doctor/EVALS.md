# Evaluation status

Status: negative against an empty baseline.

On 2026-09-19, three blind paired Harbor runs used Codex with `openai/gpt-5.6-sol` on an agent prompt containing conflicting instructions. Both arms had to diagnose the prompt and produce a compact replacement without dropping required behavior or presenting a heuristic audit as a quality score.

## Result

- Valid pairs: 3
- Treatment verifier passes: 1/3
- Baseline verifier passes: 2/3
- Blind verdicts: 1 treatment win, 2 baseline wins
- Tool errors: 0 in both arms

The tested skill reduced performance on this task. Two treatment outputs failed because the replacement prompt was not compact enough, omitted required behavior, and framed the audit as a score. This package should not carry an efficacy claim until its method is revised and a new held-out evaluation succeeds.

The result is narrow: one prompt-repair task, one model, and three paired samples. Reproducible artifacts are in `evals/system-prompt-doctor/2026-09-19/`.
