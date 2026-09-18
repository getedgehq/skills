#!/usr/bin/env python3
"""Read-only job discovery across public job feeds and public ATS boards.

Every source, filter, score and path comes from a JSON config file. The script
itself hardcodes no employer, no search term and no output location. It performs
public HTTPS GET requests only: it never applies, never logs into a board, never
sends a message and never writes to a third-party service.

Usage
-----
  python scripts/job_board_scout.py --config examples/config.example.json \
      --state .job-board-scout/state.json --out out

  python scripts/job_board_scout.py --config c.json --out out --dry-run
      Run the whole pipeline without recording anything as seen, so the next
      real run still queues the same roles.

Exit codes: 0 success, 1 failure (nothing written), 2 bad config/arguments.
A run in which every source fails exits 1 rather than reporting an empty queue.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib import error, request
from urllib.parse import urlsplit, urlunsplit

DEFAULT_USER_AGENT = "job-board-scout/1.0 (+https://github.com/getedgehq/skills)"
DEFAULT_TIMEOUT_SECONDS = 25
DEFAULT_MAX_NEW_ROLES = 40
MAX_NEW_ROLES = 500
MAX_SEEN_KEYS = 5000
STATE_SCHEMA_VERSION = 2

ATS_ENDPOINTS = {
    "ashby": "https://api.ashbyhq.com/posting-api/job-board/{board}",
    "greenhouse": "https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true",
    "lever": "https://api.lever.co/v0/postings/{board}?mode=json",
}
FEED_ADAPTERS = ("arbeitnow", "himalayas", "jobicy", "remotive")


# --------------------------------------------------------------------------- #
# config
# --------------------------------------------------------------------------- #
class ConfigError(ValueError):
    """The config file is missing something the run cannot invent a value for."""


def load_config(path: Path) -> dict[str, Any]:
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ConfigError(f"config file not found: {path}") from None
    except json.JSONDecodeError as exc:
        raise ConfigError(f"config file is not valid JSON: {exc}") from None
    if not isinstance(config, dict):
        raise ConfigError("config file must contain a JSON object")

    feeds = config.get("feeds") or []
    watchlist = config.get("ats_watchlist") or []
    if not isinstance(feeds, list) or not isinstance(watchlist, list):
        raise ConfigError("'feeds' and 'ats_watchlist' must be lists")
    if not feeds and not watchlist:
        raise ConfigError("config declares no sources: add at least one entry to "
                          "'feeds' or 'ats_watchlist'")

    for feed in feeds:
        if not isinstance(feed, dict) or not feed.get("url") or not feed.get("adapter"):
            raise ConfigError("every 'feeds' entry needs 'adapter' and 'url'")
        if feed["adapter"] not in FEED_ADAPTERS:
            raise ConfigError(f"unknown feed adapter {feed['adapter']!r}; "
                              f"supported: {', '.join(FEED_ADAPTERS)}")
    for entry in watchlist:
        if not isinstance(entry, dict) or not entry.get("provider") or not entry.get("board"):
            raise ConfigError("every 'ats_watchlist' entry needs 'provider' and 'board'")
        if str(entry["provider"]).lower() not in ATS_ENDPOINTS:
            raise ConfigError(f"unknown ATS provider {entry['provider']!r}; "
                              f"supported: {', '.join(sorted(ATS_ENDPOINTS))}")

    filters = config.get("filters") or {}
    if not isinstance(filters, dict):
        raise ConfigError("'filters' must be an object")
    if not filters.get("title_terms"):
        raise ConfigError("filters.title_terms is required: the scout has no idea "
                          "which roles you want and will not guess")
    return config


def source_configs(config: dict[str, Any]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for feed in config.get("feeds") or []:
        adapter = feed["adapter"]
        out.append({"source": feed.get("name") or adapter.title(), "adapter": adapter,
                    "url": feed["url"], "kind": "feed", "company": ""})
    for entry in config.get("ats_watchlist") or []:
        provider = str(entry["provider"]).lower()
        board = str(entry["board"])
        out.append({"source": f"{provider}:{board}", "adapter": provider,
                    "url": ATS_ENDPOINTS[provider].format(board=board),
                    "kind": "direct_ats", "company": str(entry.get("company") or "")})
    return out


# --------------------------------------------------------------------------- #
# normalisation
# --------------------------------------------------------------------------- #
def text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        return " ".join(text(item) for item in value)
    return html.unescape(str(value)).replace("\x00", " ")


def strip_html(value: Any) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text(value))).strip()


def clean_url(value: Any) -> str:
    parts = urlsplit(str(value or "").strip())
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        return ""
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(),
                       parts.path.rstrip("/"), "", ""))


def boolish(value: Any) -> bool:
    return value is True or str(value).lower().strip() in {"true", "yes", "1", "remote"}


GREENHOUSE_EMPLOYMENT_LABELS = {
    "employment", "employment type", "type of employment", "job type",
    "contract", "contract type", "work type", "worker type", "engagement type",
}
MAX_GREENHOUSE_EMPLOYMENT_VALUE_LENGTH = 120


def concise_greenhouse_employment_metadata(value: Any) -> str:
    """Greenhouse metadata is a free-form list; keep only the employment labels."""
    if not isinstance(value, list):
        return ""
    values: list[str] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        label = re.sub(r"\s+", " ", strip_html(item.get("name"))).casefold().strip()
        if label not in GREENHOUSE_EMPLOYMENT_LABELS:
            continue
        candidate = re.sub(r"\s+", " ", strip_html(item.get("value"))).strip()
        if (candidate and len(candidate) <= MAX_GREENHOUSE_EMPLOYMENT_VALUE_LENGTH
                and candidate not in values):
            values.append(candidate)
    return "; ".join(values)


def normalise(adapter: str, source: str, record: dict[str, Any]) -> dict[str, Any]:
    """Map a source-specific record onto the common shape. Conservative by design:
    a field the source does not provide stays empty rather than being inferred."""
    if adapter == "arbeitnow":
        return {"source": source, "source_id": text(record.get("slug")),
                "title": text(record.get("title")), "company": text(record.get("company_name")),
                "url": clean_url(record.get("url")), "location": text(record.get("location")),
                "employment_type": text(record.get("job_types")),
                "published_at": text(record.get("created_at")),
                "description": strip_html(record.get("description")),
                "tags": text(record.get("tags")), "remote_hint": boolish(record.get("remote"))}
    if adapter == "himalayas":
        return {"source": source, "source_id": text(record.get("guid")),
                "title": text(record.get("title")), "company": text(record.get("companyName")),
                "url": clean_url(record.get("applicationLink")),
                "location": text(record.get("locationRestrictions")),
                "employment_type": text(record.get("employmentType")),
                "published_at": text(record.get("pubDate")),
                "description": strip_html(record.get("description")),
                "tags": text(record.get("categories")) + " " + text(record.get("parentCategories")),
                "remote_hint": True}
    if adapter == "jobicy":
        return {"source": source, "source_id": text(record.get("id")),
                "title": text(record.get("jobTitle")), "company": text(record.get("companyName")),
                "url": clean_url(record.get("url")), "location": text(record.get("jobGeo")),
                "employment_type": text(record.get("jobType")),
                "published_at": text(record.get("pubDate")),
                "description": strip_html(record.get("jobDescription"))
                or strip_html(record.get("jobExcerpt")),
                "tags": text(record.get("jobIndustry")) + " " + text(record.get("jobLevel")),
                "remote_hint": True}
    if adapter == "remotive":
        return {"source": source, "source_id": text(record.get("id")),
                "title": text(record.get("title")), "company": text(record.get("company_name")),
                "url": clean_url(record.get("url")),
                "location": text(record.get("candidate_required_location")),
                "employment_type": text(record.get("job_type")),
                "published_at": text(record.get("publication_date")),
                "description": strip_html(record.get("description")),
                "tags": text(record.get("tags")) + " " + text(record.get("category")),
                "remote_hint": True}
    if adapter == "ashby":
        location = text(record.get("location"))
        return {"source": source, "source_id": text(record.get("id")),
                "title": text(record.get("title")), "company": text(record.get("companyName")),
                "url": clean_url(record.get("jobUrl") or record.get("url")),
                "location": location, "employment_type": text(record.get("employmentType")),
                "published_at": text(record.get("publishedAt") or record.get("createdAt")),
                "description": strip_html(record.get("descriptionPlain")
                                          or record.get("descriptionHtml")),
                "tags": text(record.get("department")) + " " + text(record.get("team")),
                "remote_hint": boolish(record.get("isRemote")) or "remote" in location.casefold(),
                "is_listed": boolish(record.get("isListed", True))}
    if adapter == "greenhouse":
        metadata_text = concise_greenhouse_employment_metadata(record.get("metadata"))
        raw_location = record.get("location")
        location = (text(raw_location.get("name")) if isinstance(raw_location, dict)
                    else text(raw_location))
        description = strip_html(record.get("content"))
        return {"source": source, "source_id": text(record.get("id")),
                "title": text(record.get("title")), "company": text(record.get("company_name")),
                "url": clean_url(record.get("absolute_url")), "location": location,
                "employment_type": metadata_text, "published_at": text(record.get("updated_at")),
                "description": description, "tags": metadata_text,
                "remote_hint": "remote" in f"{location} {metadata_text} {description}".casefold()}
    if adapter == "lever":
        categories = record.get("categories") if isinstance(record.get("categories"), dict) else {}
        location = text(categories.get("location"))
        description = strip_html(record.get("descriptionPlain") or record.get("description"))
        created_at = record.get("createdAt")
        published_at = (datetime.fromtimestamp(created_at / 1000, tz=timezone.utc)
                        .isoformat().replace("+00:00", "Z")
                        if isinstance(created_at, (int, float)) else text(created_at))
        return {"source": source, "source_id": text(record.get("id")),
                "title": text(record.get("text")), "company": text(record.get("company")),
                "url": clean_url(record.get("hostedUrl")), "location": location,
                "employment_type": text(categories.get("commitment")),
                "published_at": published_at, "description": description,
                "tags": text(categories.get("team")) + " " + text(categories.get("department")),
                "remote_hint": text(record.get("workplaceType")).casefold() == "remote"
                or "remote" in f"{location} {description}".casefold()}
    raise ConfigError(f"unsupported adapter: {adapter}")


def records_for(adapter: str, payload: Any) -> list[dict[str, Any]]:
    if adapter == "lever":
        records = payload if isinstance(payload, list) else []
    elif adapter == "arbeitnow":
        records = payload.get("data", []) if isinstance(payload, dict) else []
    else:
        records = payload.get("jobs", []) if isinstance(payload, dict) else []
    return [row for row in records if isinstance(row, dict)] if isinstance(records, list) else []


# --------------------------------------------------------------------------- #
# filtering
# --------------------------------------------------------------------------- #
def compile_geography(geography: dict[str, Any]) -> Callable[[str], bool]:
    """Return a predicate over the source's stated location restriction.

    This is a geography filter over what the posting says, not an assertion about
    anyone's right to work. When it is disabled, every location passes.
    """
    if not geography or not geography.get("enabled", True):
        return lambda _location: True
    patterns = [re.compile(p, re.IGNORECASE) for p in geography.get("allow_patterns", [])]
    terms = [str(t).casefold() for t in geography.get("allow_terms", [])]
    allow_unknown = bool(geography.get("allow_unstated", False))

    def predicate(location: str) -> bool:
        normalized = re.sub(r"\s+", " ", location.casefold()).strip()
        if not normalized:
            return allow_unknown
        if any(p.search(normalized) for p in patterns):
            return True
        return any(re.search(rf"\b{re.escape(term)}\b", normalized) for term in terms)

    return predicate


def rejection_reason(job: dict[str, Any], filters: dict[str, Any],
                     geography_ok: Callable[[str], bool]) -> str | None:
    title = str(job["title"]).casefold()
    searchable = " ".join(str(job.get(key, "")).casefold()
                          for key in ("title", "description", "tags", "employment_type"))
    location = str(job["location"]).casefold()
    title_terms = [str(t).casefold() for t in filters.get("title_terms", [])]
    exclude_terms = [str(t).casefold() for t in filters.get("exclude_terms", [])]
    non_remote_terms = [str(t).casefold() for t in filters.get("non_remote_terms", [])]

    if not str(job["title"]).strip() or not str(job["company"]).strip() or not str(job["url"]).strip():
        return "missing required job identity"
    if job.get("is_listed") is False:
        return "no longer listed by ATS"
    if not any(term in title for term in title_terms):
        return "title does not match filters.title_terms"
    if any(term in searchable for term in exclude_terms):
        return "matched filters.exclude_terms"
    if filters.get("require_remote", True):
        if any(term in f"{title} {location}" for term in non_remote_terms):
            return "matched filters.non_remote_terms"
        if not bool(job["remote_hint"]) and "remote" not in f"{title} {location} {str(job['description']).casefold()}":
            return "no remote signal"
    if not geography_ok(str(job["location"])):
        return "location outside filters.geography"
    return None


# --------------------------------------------------------------------------- #
# identity, scoring, ordering
# --------------------------------------------------------------------------- #
def identity_text(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text(value).casefold()).strip()


def role_key(job: dict[str, Any]) -> str:
    """Cross-source fingerprint, deliberately independent of the ATS URL so the
    same posting syndicated to three feeds is queued once."""
    seed = "|".join(identity_text(job[key]) for key in ("company", "title", "location"))
    if not seed.replace("|", ""):
        seed = f"{job['source']}:{job['source_id']}"
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()


def published_sort_value(job: dict[str, Any]) -> str:
    return str(job.get("published_at", "")).strip()


def score_job(job: dict[str, Any], scoring: dict[str, Any]) -> tuple[int, list[str]]:
    """Deterministic review-order score with an auditable reason for every point."""
    title = str(job["title"]).casefold()
    searchable = " ".join(str(job.get(key, "")).casefold()
                          for key in ("title", "description", "tags", "employment_type"))
    score, reasons = 0, []
    for tier in scoring.get("title_tiers", []):
        phrase, points = str(tier["phrase"]).casefold(), int(tier["points"])
        if phrase in title:
            score += points
            reasons.append(f"+{points} {tier.get('label', phrase)}")
            break  # highest matching tier only; tiers are ordered by the config
    for signal in scoring.get("signal_terms", []):
        phrase, points = str(signal["phrase"]).casefold(), int(signal["points"])
        present = (re.search(rf"\b{re.escape(phrase)}\b", searchable) is not None
                   if signal.get("word_boundary") else phrase in searchable)
        if present:
            score += points
            reasons.append(f"+{points} {signal.get('label', phrase)}")
    bonus = int(scoring.get("direct_ats_bonus", 0))
    if bonus and str(job["source"]).split(":", 1)[0] in ATS_ENDPOINTS:
        score += bonus
        reasons.append(f"+{bonus} direct employer ATS")
    return score, reasons


def prefer_candidate(current: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    """Deterministic duplicate tie-breaker: score, direct board, freshness, URL."""
    def rank(job: dict[str, Any]) -> tuple[int, int, str, str]:
        is_direct = int(str(job["source"]).split(":", 1)[0] in ATS_ENDPOINTS)
        return (int(str(job.get("score", "0"))), is_direct,
                published_sort_value(job), str(job["url"]))
    return incoming if rank(incoming) > rank(current) else current


# --------------------------------------------------------------------------- #
# state
# --------------------------------------------------------------------------- #
def normalise_state(value: Any) -> dict[str, Any]:
    seen = value.get("seen_role_keys", []) if isinstance(value, dict) else []
    keys = [str(k) for k in seen if str(k)][-MAX_SEEN_KEYS:] if isinstance(seen, list) else []
    return {"schema_version": STATE_SCHEMA_VERSION, "seen_role_keys": keys,
            "last_run_at": value.get("last_run_at") if isinstance(value, dict) else None}


def load_state(path: Path) -> dict[str, Any]:
    try:
        return normalise_state(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError):
        return normalise_state({})


def atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent,
                                     prefix=f".{path.name}.", delete=False) as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
        temporary = Path(handle.name)
    os.replace(temporary, path)


# --------------------------------------------------------------------------- #
# fetching
# --------------------------------------------------------------------------- #
def make_fetcher(user_agent: str, timeout: int) -> Callable[[str], Any]:
    def fetch_json(url: str) -> Any:
        req = request.Request(url, headers={"Accept": "application/json",
                                            "User-Agent": user_agent})
        with request.urlopen(req, timeout=timeout) as response:
            if response.status != 200:
                raise RuntimeError(f"HTTP {response.status}")
            return json.loads(response.read().decode("utf-8"))
    return fetch_json


def fetch_all(config: dict[str, Any],
              fetcher: Callable[[str], Any]) -> tuple[list[dict[str, Any]], dict[str, str], dict[str, int]]:
    jobs: list[dict[str, Any]] = []
    status: dict[str, str] = {}
    counts: dict[str, int] = {}
    for source in source_configs(config):
        name, adapter = source["source"], source["adapter"]
        try:
            rows = records_for(adapter, fetcher(source["url"]))
            normalised = [normalise(adapter, name, row) for row in rows]
            if source.get("company"):
                normalised = [{**job, "company": str(job["company"]) or source["company"]}
                              for job in normalised]
            jobs.extend(normalised)
            status[name] = f"ok ({len(rows)} records)"
            counts[name] = len(rows)
        except (OSError, ValueError, RuntimeError, TypeError, KeyError, OverflowError,
                error.URLError, json.JSONDecodeError) as exc:
            status[name] = f"failed ({type(exc).__name__})"
            counts[name] = 0
    return jobs, status, counts


# --------------------------------------------------------------------------- #
# report
# --------------------------------------------------------------------------- #
def markdown_queue(new_jobs: list[dict[str, Any]], source_status: dict[str, str],
                   rejected: dict[str, int], telemetry: dict[str, Any], dry_run: bool) -> str:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    lines = ["# Job review queue", "", f"Generated: {now}",
             f"New roles for review: {len(new_jobs)}"]
    if dry_run:
        lines.append("Dry run: nothing was recorded as seen, so the next real run "
                     "will queue these again.")
    lines += ["", "This is a review queue only. This script cannot apply, send messages, "
              "or alter any external system.", "", "## New roles", ""]
    if not new_jobs:
        lines.append("No new matching roles were found in this run.")
    for index, job in enumerate(new_jobs, start=1):
        lines += [f"### {index}. {str(job['title']).strip()} at {str(job['company']).strip()}",
                  f"- Source: {job['source']}",
                  f"- Location scope: {job['location'] or 'Not stated by source'}",
                  f"- Employment: {job['employment_type'] or 'Not stated'}",
                  f"- Posted: {job['published_at'] or 'Not stated'}",
                  f"- Score: {job.get('score', '0')} "
                  f"({job.get('score_reasons') or 'no scoring rule matched'})",
                  f"- Link: {job['url']}", ""]
    lines += ["## Source status", ""]
    lines += [f"- {source}: {value}" for source, value in sorted(source_status.items())]
    lines += ["", "## Filter counts", ""]
    lines += [f"- {reason}: {count}" for reason, count in sorted(rejected.items())] or ["- none"]
    lines += ["", "## Funnel telemetry", ""]
    for key in ("records_fetched", "title_fit", "passed_hard_gates", "unique_candidates",
                "cross_source_duplicates", "previously_seen", "selected"):
        lines.append(f"- {key.replace('_', ' ')}: {telemetry.get(key, 0)}")
    warnings = telemetry.get("coverage_warnings", [])
    if warnings:
        lines += ["", "## Coverage warnings", ""]
        lines += [f"- {warning}" for warning in warnings]
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- #
# run
# --------------------------------------------------------------------------- #
def run(config: dict[str, Any], state_path: Path, output_dir: Path,
        max_new_roles: int | None = None, fetcher: Callable[[str], Any] | None = None,
        dry_run: bool = False) -> dict[str, Any]:
    filters = config.get("filters") or {}
    scoring = config.get("scoring") or {}
    limit = int(max_new_roles if max_new_roles is not None
                else config.get("max_new_roles", DEFAULT_MAX_NEW_ROLES))
    if not 1 <= limit <= MAX_NEW_ROLES:
        raise ConfigError(f"max_new_roles must be between 1 and {MAX_NEW_ROLES}")
    fetcher = fetcher or make_fetcher(
        str(config.get("user_agent") or DEFAULT_USER_AGENT),
        int(config.get("timeout_seconds") or DEFAULT_TIMEOUT_SECONDS))

    all_jobs, source_status, fetched_counts = fetch_all(config, fetcher)
    if source_status and not any(v.startswith("ok") for v in source_status.values()):
        raise RuntimeError("every configured source failed; refusing to report an empty "
                           "queue as a clean run: " + json.dumps(source_status, sort_keys=True))

    geography_ok = compile_geography(filters.get("geography") or {})
    title_terms = [str(t).casefold() for t in filters.get("title_terms", [])]
    rejected: dict[str, int] = {}
    candidates: dict[str, dict[str, Any]] = {}
    title_fit_by_source = {source: 0 for source in source_status}
    passed_hard_gates = 0
    cross_source_duplicates = 0

    for job in all_jobs:
        if any(term in str(job["title"]).casefold() for term in title_terms):
            key = str(job["source"])
            title_fit_by_source[key] = title_fit_by_source.get(key, 0) + 1
        reason = rejection_reason(job, filters, geography_ok)
        if reason:
            rejected[reason] = rejected.get(reason, 0) + 1
            continue
        passed_hard_gates += 1
        score, reasons = score_job(job, scoring)
        scored = {**job, "score": str(score), "score_reasons": " | ".join(reasons)}
        key = role_key(scored)
        if key in candidates:
            cross_source_duplicates += 1
            candidates[key] = prefer_candidate(candidates[key], scored)
        else:
            candidates[key] = scored

    ordered = sorted(candidates.items(),
                     key=lambda row: (int(str(row[1].get("score", "0"))),
                                      published_sort_value(row[1]),
                                      str(row[1]["title"]), str(row[1]["company"])),
                     reverse=True)

    state = load_state(state_path)
    seen = set(state["seen_role_keys"])
    unseen = [(key, job) for key, job in ordered if key not in seen]
    selected = unseen[:limit]
    new_jobs = [job for _, job in selected]
    if not dry_run:
        state["seen_role_keys"] = (state["seen_role_keys"]
                                   + [key for key, _ in selected])[-MAX_SEEN_KEYS:]
        state["last_run_at"] = (datetime.now(timezone.utc).replace(microsecond=0)
                                .isoformat().replace("+00:00", "Z"))
        atomic_write_json(state_path, state)

    telemetry = {
        "records_fetched": sum(fetched_counts.values()),
        "title_fit": sum(title_fit_by_source.values()),
        "passed_hard_gates": passed_hard_gates,
        "unique_candidates": len(candidates),
        "cross_source_duplicates": cross_source_duplicates,
        "previously_seen": len(ordered) - len(unseen),
        "selected": len(new_jobs),
        "coverage_warnings": [
            f"{source} returned {count} records but zero title fits. Check the source "
            f"scope or filters.title_terms."
            for source, count in sorted(fetched_counts.items())
            if count and title_fit_by_source.get(source, 0) == 0],
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "queue.md").write_text(
        markdown_queue(new_jobs, source_status, rejected, telemetry, dry_run), encoding="utf-8")
    atomic_write_json(output_dir / "state.json", state)
    return {"new_roles": len(new_jobs), "source_status": source_status,
            "rejected": rejected, "telemetry": telemetry, "state": state,
            "queue_path": str(output_dir / "queue.md"), "dry_run": dry_run}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", required=True, type=Path,
                        help="JSON config: sources, filters, scoring. No defaults are "
                             "supplied for what to search for.")
    parser.add_argument("--state", type=Path, default=Path(".job-board-scout/state.json"),
                        help="deduplication state file (created on first run)")
    parser.add_argument("--out", type=Path, default=Path("out"),
                        help="directory for queue.md and state.json")
    parser.add_argument("--max-new", type=int, default=None,
                        help="override config.max_new_roles for this run")
    parser.add_argument("--dry-run", action="store_true",
                        help="run everything but do not record anything as seen")
    parser.add_argument("--json", action="store_true",
                        help="print the run summary as JSON on stdout")
    args = parser.parse_args(argv)

    try:
        config = load_config(args.config)
    except ConfigError as exc:
        print(f"config error: {exc}", file=sys.stderr)
        return 2

    try:
        result = run(config, args.state, args.out, args.max_new, dry_run=args.dry_run)
    except ConfigError as exc:
        print(f"config error: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001 - one failure mode, reported not swallowed
        print(f"job-board-scout failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps({k: v for k, v in result.items() if k != "state"},
                         sort_keys=True, indent=2))
    else:
        print(f"{result['new_roles']} new role(s) -> {result['queue_path']}")
        for source, status in sorted(result["source_status"].items()):
            print(f"  {source}: {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
