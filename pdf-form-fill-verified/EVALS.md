# Evaluation evidence and limits

The repository's adoption bar has **not been established**: the available evidence is a small historical comparison, without a randomized same-agent no-skill control or a prespecified 95% confidence interval on judge point delta. “Verified” describes the helper's saved-PDF check, not a universal reliability rating.

## Source evaluation

A private local report (`REPORT.md`, fingerprinted in `DERIVATION.json`) records ten fresh agent trials with this skill explicitly invoked: five on W-9 revision March 2024 and five on W-4 2026. Each trial received the raw form and task, without the expected field mapping. The skill and helper were frozen before scoring. The three original runtime files are copied byte for byte into this package.

| Form | Historical public-skill runs passing | Verified-skill runs passing |
| --- | ---: | ---: |
| W-9 | 1/5 | 5/5 |
| W-4 | 4/7 | 5/5 |
| Combined | 5/12 | 10/10 |

A run passed only when every intended checkbox on that form was visibly marked. The new outputs contained 15/15 intended ticks, and all explicitly unchecked choices were correct. Per-run and per-checkbox denominators are different and must not be combined.

An audit rerendered every saved page with Poppler, checked checkbox interior ink and saved `/V` and `/AS`, and compared against fixed expected mappings. The report records visual inspection of checkbox crops and representative first pages. The audit used the helper's raster detector, so it was independent of the subjects' selected mappings but not an independent detector.

Runtime: Python 3.12.3, pypdf 6.13.2, PyMuPDF 1.27.1, Pillow 10.4.0, numpy 2.4.2, Poppler 24.02.0; Codex CLI 0.160.0 with gpt-6.1-sol and medium reasoning.

## Public reproduction and privacy

Run the synthetic regression suite from this directory after installing `scripts/requirements.txt` and system Poppler (`pdftoppm`):

```sh
python3 -m unittest discover -s tests -v
```

The five tests cover nonstandard export values with interactive and flattened output, repair of an invisible appearance, rejection of metadata-only selection, rejection of an unintended tick, and invalid field/export rejection. They create their own synthetic forms in temporary directories and require no private files or network access. These are correctness tests, not a comparative skill evaluation.

Private prompts, filled tax forms, mappings, page images, trial logs, and the original report are intentionally omitted because they contain personal or task-specific details. Their source fingerprints identify the evidence reviewed; they do not make the historical trial results publicly reproducible. The report also records successful W-9 and W-4 flattening smoke checks.

These results do not measure automatic discovery, other PDF families, signing, or tax advice. Pixel checks establish visible ink, not whether the chosen label matches the user's intent. Human inspection of labels and text remains part of the skill.
