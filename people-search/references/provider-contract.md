# Provider adapter contract

Every adapter returns its mode and provider, applied/approximated/dropped/unsupported filters, estimated and actual cost, a coverage note, and results. Provider field names must not leak into planning.

Validate identifiers and enum values before a full request. Start with a small canary and inspect count and relevance. If a provider accepts but appears to ignore a filter, mark it approximated or dropped.

Each person record preserves name, current title/company, location, stable profile URL, evidence URLs, matched criteria, missing evidence, and a transparent score breakdown. Contact data is optional and must not be inferred.
