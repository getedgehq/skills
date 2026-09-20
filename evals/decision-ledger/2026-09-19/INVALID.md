# Excluded Decision Ledger attempts

Only `valid/` contributes to the published result.

- `invalid/v2/`: six concurrent arms saturated AX41 memory and swap. Four interrupted arms exited 137. The remaining pair used the original contradictory verifier.
- `invalid/v3/` and `invalid/v4/`: rendered before the corrected verifier replaced the stale verifier embedded in the brief setup.
- `invalid/v5/`: parallel arms raced while copying one shared fixture tree, so one arm never ran.
- `invalid/v6/`: ran while the verifier still required an extra cancellation-event record not required by the task. It was excluded before judgment.

The final `valid/` run used a fixture-backed brief, a verifier tested on known-good and known-bad outputs, and file-locked shared task rendering. Invalid attempts are preserved as infrastructure evidence and excluded from all win and pass counts.
