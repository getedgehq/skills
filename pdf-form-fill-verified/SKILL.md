---
name: pdf-form-fill-verified
description: Fill PDF AcroForms, including checkboxes with nonstandard export values, and verify saved checkmarks from page PNGs before delivery. Supports optional flattening. Use for interactive PDF forms, not scanned documents or digital signing.
---

# Verified PDF form filling

Use the bundled `scripts/form_fill.py`; resolve its path relative to this SKILL.md. Requires Python 3 with `scripts/requirements.txt`, plus system `pdftoppm` (Poppler). Keep original PDFs unchanged. No uploads or publishing are needed.

1. Run `python3 <skill>/scripts/form_fill.py list blank.pdf > fields.json`. This lists **every field**, including containers and non-widget fields, and every page widget with its full name, page, rectangle, type, current value, and checkbox/radio **on_values**. Inspect page text and render the blank page to map opaque field names to printed labels. Do not infer meaning from array indices alone.
2. Write `data.json` with `{"fields": {"FULL.FIELD.NAME": "text", "p1:w7": "6", "p1:w8": false}}`. Use full names or widget IDs from the inventory. For a button, use its actual on-value without the initial slash, or `false`/`"Off"`. `true` is accepted only for a single unambiguous checkbox. Never substitute `"Yes"`, `"On"`, or the JSON string `"true"` for an export value. For each choice group, explicitly include unselected alternatives as `false`. For radio groups, pass the group name and selected export value; repeated text names need manual handling. Unknown, ambiguous, read-only, unsupported, and invalid button values fail closed.
3. Run `python3 <skill>/scripts/form_fill.py fill blank.pdf filled.pdf --data data.json --evidence evidence/` and optionally append `--flatten`. The script sets `/V` and `/AS`, uses existing `/AP /N` export appearances, creates a missing Off appearance, regenerates text appearances, and sets `/NeedAppearances false`. Hybrid XFA XML is removed from the output so it cannot override the verified AcroForm view. On a failed render check it retries once with font-independent vector X appearance streams. Flattening bakes widgets into PDF page content before final verification.
4. Success requires `evidence/verification.json` to say `passed: true`. Every saved page is rendered to PNG with **Poppler**, independent of the PDF writer. Each intended box is cropped and compared to an otherwise identical all-intended-boxes-Off reference. Only new dark ink inside the border with adequate horizontal/vertical extent counts as a visible tick. Explicit unchecked choices are checked too. Unflattened outputs also require saved `/V` and `/AS` agreement. Inspect the checkbox crops and filled page PNGs to confirm label selection, text placement, and that no unintended options are selected. Pixel checks establish visible ink, not semantic correctness; the chosen label must still match the request.
5. Deliver only the verified PDF. Keep the mapping, page PNGs, crops and report as local evidence. A failed run exits nonzero and does not copy its candidate to the output path. Do not deliver an old output left from an earlier run. After two failures, inspect the recorded candidates and stop to diagnose; never report success from field metadata alone.

To recheck an existing PDF (including a flattened one):

```sh
python3 <skill>/scripts/form_fill.py verify blank.pdf filled.pdf --data data.json --evidence recheck/
```

Use a fresh evidence directory per invocation. Preserve signatures, dates and employer sections as requested; this tool does not sign. Do not guess missing tax classification or filing status. Form revisions can change field names and amounts: inspect the supplied form instructions. XFA-only PDFs are unsupported; hybrid PDFs retain page content and AcroForm fields but lose XFA XML. Scanned forms and custom drawn boxes need a separately validated workflow. Very small or out-of-page boxes fail rather than bypass verification. The raster check is a conservative ink detector, not a universal image understanding model; unusual appearances may require diagnosis.
