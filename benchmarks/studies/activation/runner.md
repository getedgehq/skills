# Reanalysis and execution boundary

Run `python3 scripts/verify_studies.py` from the benchmarks folder to reconcile the approved completed trial exports. `python3 scripts/sync_studies.py` regenerates the study register and analysis JSON without model calls.

Subject execution adapters, private fixtures and raw transcripts are withheld. These exports support independent reanalysis, not a complete subject rerun. Pending studies contain no completed result.
