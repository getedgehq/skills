# Provider adapter contract

Every adapter returns its mode and provider, applied/approximated/dropped/unsupported filters, estimated and actual cost, a coverage note, and results. Provider field names must not leak into planning.

Validate identifiers and enum values before a full request. Start with a small canary and inspect count and relevance. If a provider accepts but appears to ignore a filter, mark it approximated or dropped.

Each person record preserves name, current title/company, location, stable profile URL, evidence URLs, matched criteria, missing evidence, and a transparent score breakdown. Contact data is optional and must not be inferred.

## Request

The adapter POSTs `{"query": <canonical search>, "limit": <int>, "preview": <bool>}` with the credential in an `Authorization: Bearer` header, read from the environment variable named by `--token-env`. A canary run sets `preview` true and caps `limit` at `--canary-limit`. A full run sets `preview` false, sends the requested `--limit`, and is refused unless the caller declared `--max-cost-usd`.

## Response

Accepted shapes are a bare list of records or an object with:

- `results`: list of provider records.
- `filters`: optional, either a list of canonical filter names the provider applied, or `{"applied": [...], "unsupported": [...]}`. Names may be canonical keys (`locations`) or full labels (`must_have.locations`).
- `cost`: optional `{"actual_usd": <number>}` (`cost_usd` is also read).

Records are mapped onto the canonical fields `name`, `current_title`, `current_company`, `location`, `industry`, `profile_url`, `evidence_url` through an alias table before ranking; nested objects are read via their `name`/`title`/`value`/`url` key. The mapping actually used, the canonical fields nothing filled, and the provider fields nobody consumed are reported in `provider_mapping`. Unmapped values never reach scoring.

## Filter status rules

- `applied`: the provider declared the filter applied and every returned record satisfies it on re-verification.
- `approximated`: enforced locally on retrieved records only. This covers free-text keyword filters, filters the provider declared unsupported, filters the provider never confirmed, and filters the provider claimed but contradicted with its own rows. Provider-side coverage was wider than the brief in every one of those cases, so the shortlist is filtered but the search was not.
- `dropped`: the target field is absent from every retrieved record, so the filter was not enforced at all and the result set is broader than the brief.
- `unsupported`: no search ran, which is the plan-mode case.

Each entry carries `filter`, `kind`, `values`, `fields`, `match`, `status`, `stage`, `reason`, and where relevant `provider_status` and `locally_rejected_records`.

## Failure contract

A run that fails at any stage must not emit a result set. The runner exits 2, writes a one-line reason to stderr, and prints `{"ok": false, "status": "error", "results": null, "results_valid": false, "error": {"type", "message", "stage", "retryable", "detail"}}`. `results` is null rather than `[]` so that a consumer treating the payload as a shortlist raises instead of reporting zero matches. Error types include `missing_credential`, `provider_http_error` (with the HTTP status in `detail`), `provider_unreachable`, `provider_bad_response`, `budget_not_declared`, `budget_exceeded`, and `input_error`. Only `408`, `429`, and `5xx` responses plus transport failures are marked retryable.

A successful run with no matches is a different thing: `ok` is true, `results` is `[]`, and `zero_result_note` plus `diagnostics.rejected_by_filter` show which filters removed the candidates.
