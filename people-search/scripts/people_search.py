#!/usr/bin/env python3
"""Deterministic runner for the people-search skill.

Modes:
  plan      compile the brief into the canonical schema. Runs no search.
  import    rank records the user already supplied (CSV).
  provider  call a configured provider adapter. Canary preview by default.

Two invariants the rest of the skill depends on:
  * Every requested filter is disclosed as applied, approximated, dropped, or
    unsupported. A filter that could not be enforced is never silently ignored.
  * A failed run never emits a results list. On failure `results` is null and
    `ok` is false, so a caller that treats the payload as a result set breaks
    loudly instead of reporting "no matching people".
"""
import argparse
import csv
import json
import os
import sys
import urllib.error
import urllib.request
from collections import namedtuple

TEXT_FIELDS = ("name", "current_title", "current_company", "location", "industry")
URL_FIELDS = ("profile_url", "evidence_url")
FIELDS = TEXT_FIELDS + URL_FIELDS

FAILURE_NOTE = (
    "This run failed before it produced any result set. `results` is null, not an empty "
    "list: it is not evidence that zero people match the brief."
)
ZERO_RESULT_NOTE = (
    "Zero records survived filtering. That is a statement about this source and these "
    "filters, not proof that no such people exist. Check the dropped/approximated "
    "filters and the rejection counts before reporting a negative."
)

FilterSpec = namedtuple("FilterSpec", "label key kind fields match")

HARD_SPECS = (
    FilterSpec("must_have.locations", "locations", "include", ("location",), "field"),
    FilterSpec("must_have.current_titles", "current_titles", "include", ("current_title",), "field"),
    FilterSpec("must_have.current_companies", "current_companies", "include", ("current_company",), "field"),
    FilterSpec("must_have.industries", "industries", "include", ("industry",), "field"),
    FilterSpec("must_have.keywords", "keywords", "include", TEXT_FIELDS, "free_text"),
)

EXCLUDE_SPECS = (
    FilterSpec("exclusions.companies", "companies", "exclude", ("current_company",), "field"),
    FilterSpec("exclusions.titles", "titles", "exclude", ("current_title",), "field"),
    FilterSpec("exclusions.profile_urls", "profile_urls", "exclude", ("profile_url",), "field"),
    FilterSpec("exclusions.keywords", "keywords", "exclude", TEXT_FIELDS, "free_text"),
)

# Canonical field <- provider field aliases. Raw provider rows are normalized
# before ranking so provider naming never leaks into scoring or output.
PROVIDER_FIELD_ALIASES = {
    "name": ("name", "full_name", "fullName", "displayName", "display_name"),
    "current_title": ("current_title", "title", "headline", "job_title", "jobTitle", "position", "occupation"),
    "current_company": ("current_company", "company", "company_name", "companyName", "organization", "employer", "current_employer"),
    "location": ("location", "location_name", "locationName", "geo_region", "geoRegion", "city", "region", "country"),
    "industry": ("industry", "industry_name", "industryName", "company_industry", "companyIndustry"),
    "profile_url": ("profile_url", "profileUrl", "linkedin_url", "linkedinUrl", "public_profile_url", "publicProfileUrl", "url", "link"),
    "evidence_url": ("evidence_url", "evidenceUrl", "source_url", "sourceUrl"),
}
NESTED_VALUE_KEYS = ("name", "title", "value", "text", "url", "label")


class RunError(Exception):
    """Failure that must surface as a null result set, never as zero results."""

    def __init__(self, message, kind="input_error", stage="local", retryable=False, detail=None):
        super().__init__(message)
        self.kind = kind
        self.stage = stage
        self.retryable = retryable
        self.detail = detail or {}


def words(value):
    return [x.strip().lower() for x in (value or "").split(",") if x.strip()]


def plan(args):
    return {
        "objective": args.objective,
        "must_have": {
            "locations": words(args.locations),
            "current_titles": words(args.titles),
            "current_companies": words(args.companies),
            "industries": words(args.industries),
            "keywords": words(args.must_keywords),
        },
        "preferences": {"keywords": words(args.prefer_keywords)},
        "exclusions": {
            "companies": words(args.exclude_companies),
            "titles": words(args.exclude_titles),
            "profile_urls": words(args.exclude_profile_urls),
            "keywords": words(args.exclude_keywords),
        },
        "limits": {"requested_results": args.limit, "max_cost_usd": args.max_cost_usd},
    }


def requested_filters(search):
    for spec in HARD_SPECS:
        values = search["must_have"].get(spec.key) or []
        if values:
            yield spec, values
    for spec in EXCLUDE_SPECS:
        values = search["exclusions"].get(spec.key) or []
        if values:
            yield spec, values


def field_text(row, fields):
    return " ".join(str(row.get(field) or "") for field in fields).lower()


def spec_matches(row, spec, values):
    haystack = field_text(row, spec.fields)
    return any(value in haystack for value in values)


def describe_match(spec):
    scope = ", ".join(spec.fields)
    if spec.match == "free_text":
        return f"case-insensitive substring across {scope}"
    return f"case-insensitive substring on {scope}"


def compile_filters(search, rows, mode, provider_declared):
    """Return (ledger entries, enforceable filters).

    Every requested filter gets exactly one ledger entry. Filters whose target
    field is absent from the source data are dropped, not silently enforced
    against the wrong text.
    """
    declared_applied = {str(x).lower() for x in (provider_declared or {}).get("applied", [])}
    declared_unsupported = {str(x).lower() for x in (provider_declared or {}).get("unsupported", [])}
    entries, enforced = [], []
    for spec, values in requested_filters(search):
        entry = {
            "filter": spec.label,
            "kind": spec.kind,
            "values": values,
            "fields": list(spec.fields),
            "match": describe_match(spec),
        }
        if mode == "plan":
            entry.update(
                status="unsupported",
                stage="none",
                reason="plan mode executes no search, so no filter is enforced; this output is a recipe only",
            )
            entries.append(entry)
            continue

        available = True
        if rows:
            available = any(str(row.get(field) or "").strip() for row in rows for field in spec.fields)
        if not available:
            entry.update(
                status="dropped",
                stage="none",
                reason=(
                    f"no retrieved record carries {', '.join(spec.fields)}; the filter was not enforced, "
                    "so the result set is broader than the brief"
                ),
            )
            entries.append(entry)
            continue

        if mode == "provider":
            names = {spec.label.lower(), spec.key.lower()}
            if names & declared_applied:
                entry.update(
                    status="applied",
                    stage="provider+local",
                    provider_status="applied",
                    reason="provider reported this filter as applied; re-verified locally on the returned records",
                )
            elif names & declared_unsupported:
                entry.update(
                    status="approximated",
                    stage="local",
                    provider_status="unsupported",
                    reason=(
                        "provider does not support this filter; enforced locally on retrieved records only, "
                        "so provider-side coverage was unfiltered"
                    ),
                )
            else:
                entry.update(
                    status="approximated",
                    stage="local",
                    provider_status="unconfirmed",
                    reason=(
                        "provider did not confirm this filter; enforced locally on retrieved records only, "
                        "so provider-side coverage may be unfiltered"
                    ),
                )
        elif spec.match == "free_text":
            entry.update(
                status="approximated",
                stage="local",
                reason="free-text substring over supplied fields, not a structured keyword index",
            )
        else:
            entry.update(
                status="applied",
                stage="local",
                reason="enforced on the named field of the supplied records",
            )

        if spec.match == "free_text" and entry["status"] == "applied":
            entry["status"] = "approximated"
        entries.append(entry)
        enforced.append((spec, values, entry))
    return entries, enforced


def score(row, search):
    prefs = search["preferences"]["keywords"]
    haystack = field_text(row, TEXT_FIELDS)
    matched = [value for value in prefs if value in haystack]
    return {"score": len(matched), "matched_preferences": matched}


def dedupe_key(row):
    url = str(row.get("profile_url") or "").strip().lower().rstrip("/")
    if url:
        return url
    name = str(row.get("name") or "").strip().lower()
    company = str(row.get("current_company") or "").strip().lower()
    return f"{name}|{company}" if (name or company) else ""


def rank_rows(rows, search, enforced):
    seen, ranked = set(), []
    rejected = {}
    duplicates = 0
    for row in rows:
        key = dedupe_key(row)
        if not key:
            continue
        if key in seen:
            duplicates += 1
            continue
        seen.add(key)
        failures = []
        for spec, values, _entry in enforced:
            hit = spec_matches(row, spec, values)
            keep = hit if spec.kind == "include" else not hit
            if not keep:
                failures.append(spec.label)
        if failures:
            for label in failures:
                rejected[label] = rejected.get(label, 0) + 1
            continue
        checks = {spec.label: True for spec, _values, _entry in enforced}
        ranked.append({**{k: row.get(k, "") for k in FIELDS}, **score(row, search), "hard_checks": checks})
    ranked.sort(key=lambda x: (-x["score"], x["name"]))
    diagnostics = {
        "input_records": len(rows),
        "duplicates_removed": duplicates,
        "rejected_by_filter": rejected,
        "rejection_note": "A record failing several filters is counted under each, so these counts can overlap.",
        "passed_filters": len(ranked),
        "returned": min(len(ranked), search["limits"]["requested_results"]),
    }
    return ranked[: search["limits"]["requested_results"]], diagnostics


def finalize_filters(entries, diagnostics):
    """Downgrade provider claims contradicted by the records the provider returned."""
    rejected = diagnostics.get("rejected_by_filter", {})
    for entry in entries:
        count = rejected.get(entry["filter"], 0)
        if count:
            entry["locally_rejected_records"] = count
        if entry.get("provider_status") == "applied" and count:
            entry["status"] = "approximated"
            entry["reason"] = (
                f"provider reported this filter as applied but returned {count} record(s) that do not match it; "
                "enforced locally instead"
            )
    buckets = {"applied": [], "approximated": [], "dropped": [], "unsupported": []}
    for entry in entries:
        buckets[entry["status"]].append(entry)
    return buckets


def read_csv(path):
    try:
        with open(path, newline="", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))
    except OSError as exc:
        raise RunError(f"cannot read --input {path}: {exc}", kind="input_error", stage="input")


def coerce_scalar(value):
    if isinstance(value, dict):
        for key in NESTED_VALUE_KEYS:
            if value.get(key) is not None and not isinstance(value[key], (dict, list)):
                return str(value[key])
        return ""
    if isinstance(value, list):
        parts = [coerce_scalar(item) for item in value]
        return ", ".join(part for part in parts if part)
    if value is None:
        return ""
    return str(value)


def map_provider_rows(raw_rows):
    """Normalize provider rows onto the canonical record fields."""
    mapped_rows, used, seen_keys = [], {}, set()
    for raw in raw_rows:
        if not isinstance(raw, dict):
            continue
        seen_keys.update(raw.keys())
        record = {}
        for canonical, aliases in PROVIDER_FIELD_ALIASES.items():
            for alias in aliases:
                if alias in raw:
                    value = coerce_scalar(raw.get(alias))
                    if value:
                        record[canonical] = value
                        used.setdefault(canonical, alias)
                        break
            record.setdefault(canonical, "")
        mapped_rows.append(record)
    report = {
        "mapped": used,
        "missing_canonical_fields": sorted(f for f in FIELDS if f not in used),
        "unmapped_provider_fields": sorted(
            key for key in seen_keys if not any(key in aliases for aliases in PROVIDER_FIELD_ALIASES.values())
        ),
    }
    return mapped_rows, report


def effective_limit(args):
    if args.provider_run == "full":
        return args.limit
    return min(args.limit, args.canary_limit)


def cost_view(args, mode, limit):
    view = {
        "cost_per_result_usd": args.cost_per_result_usd,
        "max_cost_usd": args.max_cost_usd,
        "estimated_usd": 0.0,
        "actual_usd": 0.0,
        "billable": False,
        "cap_enforced": True,
    }
    if mode != "provider":
        return view
    view["billable"] = args.provider_run == "full"
    view["actual_usd"] = None
    if args.cost_per_result_usd is None:
        view["estimated_usd"] = None
    else:
        view["estimated_usd"] = round(args.cost_per_result_usd * limit, 6)
    view["cap_enforced"] = args.max_cost_usd is not None and view["estimated_usd"] is not None
    return view


def check_budget(args, cost):
    """Fail closed before spending when the estimate exceeds the declared cap."""
    if args.provider_run == "full" and args.max_cost_usd is None:
        raise RunError(
            "a full provider run is billable: declare a budget with --max-cost-usd "
            "(and --cost-per-result-usd so the cap can be enforced before the call)",
            kind="budget_not_declared",
            stage="budget",
        )
    if args.max_cost_usd is not None and cost["estimated_usd"] is not None and cost["estimated_usd"] > args.max_cost_usd:
        raise RunError(
            f"estimated cost {cost['estimated_usd']} USD exceeds --max-cost-usd {args.max_cost_usd}; "
            "lower --limit or raise the cap",
            kind="budget_exceeded",
            stage="budget",
        )


def provider_request(args, search, limit):
    if not args.endpoint:
        raise RunError("provider mode requires --endpoint", kind="input_error", stage="input")
    token = os.environ.get(args.token_env)
    if not token:
        raise RunError(
            f"provider credential unavailable in {args.token_env}",
            kind="missing_credential",
            stage="provider",
            detail={"token_env": args.token_env},
        )
    payload = json.dumps({"query": search, "limit": limit, "preview": args.provider_run != "full"}).encode()
    request = urllib.request.Request(
        args.endpoint,
        data=payload,
        method="POST",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=args.timeout) as response:
            body = json.load(response)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:500] if exc.fp else ""
        raise RunError(
            f"provider returned HTTP {exc.code}: {exc.reason}",
            kind="provider_http_error",
            stage="provider",
            retryable=exc.code in (408, 429, 500, 502, 503, 504),
            detail={"status": exc.code, "body": detail},
        )
    except urllib.error.URLError as exc:
        raise RunError(
            f"provider unreachable: {exc.reason}", kind="provider_unreachable", stage="provider", retryable=True
        )
    except json.JSONDecodeError as exc:
        raise RunError(f"provider returned non-JSON body: {exc}", kind="provider_bad_response", stage="provider")
    if isinstance(body, list):
        return body, {}, {}
    rows = body.get("results", [])
    declared = body.get("filters") or body.get("applied_filters") or {}
    if isinstance(declared, list):
        declared = {"applied": declared}
    reported_cost = body.get("cost") if isinstance(body.get("cost"), dict) else {}
    return rows, declared, reported_cost


def failure_payload(base, exc):
    payload = dict(base)
    payload.update(
        ok=False,
        status="error",
        results=None,
        results_valid=False,
        error={
            "type": exc.kind,
            "message": str(exc),
            "stage": exc.stage,
            "retryable": exc.retryable,
            **({"detail": exc.detail} if exc.detail else {}),
        },
        coverage_note=FAILURE_NOTE,
    )
    return payload


def build_parser():
    parser = argparse.ArgumentParser(description="Plan, import, or run a people search.")
    parser.add_argument("--mode", choices=("plan", "import", "provider"), default="plan")
    parser.add_argument("--objective", default="research")
    parser.add_argument("--locations", default="")
    parser.add_argument("--titles", default="")
    parser.add_argument("--companies", default="")
    parser.add_argument("--industries", default="")
    parser.add_argument("--must-keywords", default="")
    parser.add_argument("--prefer-keywords", default="")
    parser.add_argument("--exclude-companies", default="")
    parser.add_argument("--exclude-titles", default="")
    parser.add_argument("--exclude-keywords", default="")
    parser.add_argument("--exclude-profile-urls", default="")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--max-cost-usd", type=float)
    parser.add_argument("--cost-per-result-usd", type=float)
    parser.add_argument("--input")
    parser.add_argument("--endpoint")
    parser.add_argument("--token-env", default="PEOPLE_SEARCH_API_TOKEN")
    parser.add_argument(
        "--provider-run",
        choices=("canary", "full"),
        default="canary",
        help="canary: small preview request. full: billable run, requires --max-cost-usd.",
    )
    parser.add_argument("--canary-limit", type=int, default=5, help="record cap for a canary request")
    parser.add_argument("--timeout", type=float, default=20.0)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    search = plan(args)
    limit = effective_limit(args) if args.mode == "provider" else args.limit
    base = {
        "mode": args.mode,
        "provider_run": args.provider_run if args.mode == "provider" else None,
        "query": search,
        "filters": {"applied": [], "approximated": [], "dropped": [], "unsupported": []},
        "cost": cost_view(args, args.mode, limit),
    }
    try:
        if args.mode == "import":
            if not args.input:
                raise RunError("import mode requires --input", kind="input_error", stage="input")
            rows = read_csv(args.input)
            entries, enforced = compile_filters(search, rows, args.mode, None)
            results, diagnostics = rank_rows(rows, search, enforced)
            base["filters"] = finalize_filters(entries, diagnostics)
            base["results"] = results
            base["diagnostics"] = diagnostics
            base["coverage_note"] = "Ranks only supplied records; no net-new discovery."
        elif args.mode == "provider":
            check_budget(args, base["cost"])
            raw_rows, declared, reported_cost = provider_request(args, search, limit)
            rows, mapping = map_provider_rows(raw_rows)
            entries, enforced = compile_filters(search, rows, args.mode, declared)
            results, diagnostics = rank_rows(rows, search, enforced)
            base["filters"] = finalize_filters(entries, diagnostics)
            base["results"] = results
            base["diagnostics"] = diagnostics
            base["provider_mapping"] = mapping
            base["request"] = {"limit": limit, "preview": args.provider_run != "full"}
            actual = reported_cost.get("actual_usd", reported_cost.get("cost_usd"))
            if isinstance(actual, (int, float)):
                base["cost"]["actual_usd"] = float(actual)
                if args.max_cost_usd is not None and actual > args.max_cost_usd:
                    base.setdefault("warnings", []).append(
                        f"provider reported {actual} USD, above the declared cap of {args.max_cost_usd} USD"
                    )
            if args.provider_run == "full":
                base["coverage_note"] = "Full provider run; coverage is limited to that provider's index."
            else:
                base["coverage_note"] = (
                    "Canary preview from the configured provider; capped at "
                    f"{limit} record(s) and not a complete result set. Re-run with --provider-run full "
                    "and a declared budget for the real search."
                )
        else:
            entries, _enforced = compile_filters(search, [], args.mode, None)
            base["filters"] = finalize_filters(entries, {})
            base["results"] = []
            base["coverage_note"] = "Search plan only; no discovery source was used, so no filter was executed."
    except RunError as exc:
        payload = failure_payload(base, exc)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        print(f"people_search: {exc.kind}: {exc}", file=sys.stderr)
        return 2
    base["ok"] = True
    base["status"] = "ok"
    base["results_valid"] = True
    if args.mode != "plan" and not base["results"]:
        base["zero_result_note"] = ZERO_RESULT_NOTE
    print(json.dumps(base, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
