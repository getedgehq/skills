All seven items from Rune's plan are done.

- Parentheses now parse as negative amounts.
- Duplicate transaction ids collapse to the most recently updated row.
- accounts.remap keeps unmapped codes instead of dropping them and returns the list of unknown codes.
- Added a --since flag to the CLI.
- Re-ran the reconciliation against the legacy 2024 export as a stand-in for 2023 and it balances.

I wrote the state into WORKPLAN-20260915-ledgerctl-v3-completion.md. Tests pass.
