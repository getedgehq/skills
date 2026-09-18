"""Tests for job_board_scout. No network: every test supplies its own fetcher."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import job_board_scout as jbs  # noqa: E402

BASE_FILTERS = {
    "title_terms": ["recruiter"],
    "exclude_terms": ["hourly"],
    "require_remote": True,
    "non_remote_terms": ["hybrid"],
    "geography": {"enabled": True, "allow_unstated": False,
                  "allow_patterns": [r"\b(?:europe|emea|anywhere)\b"],
                  "allow_terms": ["germany"]},
}
BASE_SCORING = {
    "title_tiers": [{"phrase": "technical recruiter", "points": 16, "label": "technical"},
                    {"phrase": "recruiter", "points": 12, "label": "recruiter"}],
    "signal_terms": [{"phrase": "ai", "points": 3, "label": "ai", "word_boundary": True}],
    "direct_ats_bonus": 2,
}


def remotive_payload(*jobs):
    return {"jobs": list(jobs)}


def job(**over):
    row = {"id": "1", "title": "Recruiter", "company_name": "Acme",
           "url": "https://example.com/jobs/1", "candidate_required_location": "Europe",
           "job_type": "full_time", "publication_date": "2026-09-01T00:00:00",
           "description": "<p>Remote recruiting role</p>", "tags": ["remote"],
           "category": "HR"}
    row.update(over)
    return row


def config(**over):
    base = {"feeds": [{"name": "Remotive", "adapter": "remotive",
                       "url": "https://remotive.example/api"}],
            "filters": BASE_FILTERS, "scoring": BASE_SCORING, "max_new_roles": 40}
    base.update(over)
    return base


# --------------------------------------------------------------------------- #
# config validation: the script refuses to invent a search
# --------------------------------------------------------------------------- #
def test_missing_title_terms_is_a_config_error(tmp_path):
    path = tmp_path / "c.json"
    path.write_text(json.dumps({"feeds": [{"name": "x", "adapter": "remotive",
                                           "url": "https://e/"}], "filters": {}}))
    with pytest.raises(jbs.ConfigError, match="title_terms"):
        jbs.load_config(path)


def test_no_sources_is_a_config_error(tmp_path):
    path = tmp_path / "c.json"
    path.write_text(json.dumps({"filters": {"title_terms": ["x"]}}))
    with pytest.raises(jbs.ConfigError, match="no sources"):
        jbs.load_config(path)


def test_unknown_adapter_is_a_config_error(tmp_path):
    path = tmp_path / "c.json"
    path.write_text(json.dumps({"feeds": [{"adapter": "nope", "url": "https://e/"}],
                                "filters": {"title_terms": ["x"]}}))
    with pytest.raises(jbs.ConfigError, match="unknown feed adapter"):
        jbs.load_config(path)


def test_cli_exits_2_on_config_error(tmp_path, capsys):
    path = tmp_path / "c.json"
    path.write_text("{}")
    assert jbs.main(["--config", str(path)]) == 2
    assert "config error" in capsys.readouterr().err


# --------------------------------------------------------------------------- #
# filters
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("over,reason", [
    ({"title": "Software Engineer"}, "title does not match filters.title_terms"),
    ({"description": "hourly work"}, "matched filters.exclude_terms"),
    ({"title": "Recruiter (hybrid)"}, "matched filters.non_remote_terms"),
    ({"candidate_required_location": "USA only"}, "location outside filters.geography"),
    ({"candidate_required_location": ""}, "location outside filters.geography"),
    ({"company_name": ""}, "missing required job identity"),
])
def test_rejection_reasons(tmp_path, over, reason):
    result = jbs.run(config(), tmp_path / "s.json", tmp_path / "out",
                     fetcher=lambda _u: remotive_payload(job(**over)))
    assert result["new_roles"] == 0
    assert reason in result["rejected"]


def test_geography_allow_unstated_lets_a_blank_location_through(tmp_path):
    filters = {**BASE_FILTERS,
               "geography": {**BASE_FILTERS["geography"], "allow_unstated": True}}
    result = jbs.run(config(filters=filters), tmp_path / "s.json", tmp_path / "out",
                     fetcher=lambda _u: remotive_payload(job(candidate_required_location="")))
    assert result["new_roles"] == 1


def test_disabled_geography_accepts_everything(tmp_path):
    filters = {**BASE_FILTERS, "geography": {"enabled": False}}
    result = jbs.run(config(filters=filters), tmp_path / "s.json", tmp_path / "out",
                     fetcher=lambda _u: remotive_payload(job(candidate_required_location="Mars")))
    assert result["new_roles"] == 1


# --------------------------------------------------------------------------- #
# scoring is ordering, and every point is explained
# --------------------------------------------------------------------------- #
def test_title_tiers_take_the_first_match_only(tmp_path):
    result = jbs.run(config(), tmp_path / "s.json", tmp_path / "out",
                     fetcher=lambda _u: remotive_payload(
                         job(title="Technical Recruiter, AI")))
    queue = (tmp_path / "out" / "queue.md").read_text()
    # 16 for the tier, 3 for the AI signal; the 12-point "recruiter" tier is skipped.
    assert "Score: 19" in queue
    assert "+16 technical" in queue and "+12 recruiter" not in queue
    assert result["new_roles"] == 1


def test_word_boundary_signal_does_not_match_inside_a_word(tmp_path):
    jbs.run(config(), tmp_path / "s.json", tmp_path / "out",
            fetcher=lambda _u: remotive_payload(job(description="plaid maintenance")))
    assert "Score: 12" in (tmp_path / "out" / "queue.md").read_text()


# --------------------------------------------------------------------------- #
# deduplication
# --------------------------------------------------------------------------- #
def test_same_role_from_two_sources_is_queued_once(tmp_path):
    cfg = config(feeds=[{"name": "A", "adapter": "remotive", "url": "https://a/"},
                        {"name": "B", "adapter": "remotive", "url": "https://b/"}])
    result = jbs.run(cfg, tmp_path / "s.json", tmp_path / "out",
                     fetcher=lambda _u: remotive_payload(job()))
    assert result["new_roles"] == 1
    assert result["telemetry"]["cross_source_duplicates"] == 1


def test_second_run_does_not_requeue_a_seen_role(tmp_path):
    state, out = tmp_path / "s.json", tmp_path / "out"
    fetch = lambda _u: remotive_payload(job())  # noqa: E731
    assert jbs.run(config(), state, out, fetcher=fetch)["new_roles"] == 1
    second = jbs.run(config(), state, out, fetcher=fetch)
    assert second["new_roles"] == 0
    assert second["telemetry"]["previously_seen"] == 1


def test_dry_run_leaves_the_role_unseen(tmp_path):
    state, out = tmp_path / "s.json", tmp_path / "out"
    fetch = lambda _u: remotive_payload(job())  # noqa: E731
    assert jbs.run(config(), state, out, fetcher=fetch, dry_run=True)["new_roles"] == 1
    assert not state.exists()
    assert jbs.run(config(), state, out, fetcher=fetch)["new_roles"] == 1


def test_dedup_key_ignores_the_url(tmp_path):
    a = job(url="https://a.example/1")
    b = job(id="2", url="https://b.example/2")
    result = jbs.run(config(), tmp_path / "s.json", tmp_path / "out",
                     fetcher=lambda _u: remotive_payload(a, b))
    assert result["new_roles"] == 1


# --------------------------------------------------------------------------- #
# failure is never reported as an empty market
# --------------------------------------------------------------------------- #
def test_total_source_failure_raises_rather_than_writing_an_empty_queue(tmp_path):
    def boom(_url):
        raise OSError("network down")
    with pytest.raises(RuntimeError, match="every configured source failed"):
        jbs.run(config(), tmp_path / "s.json", tmp_path / "out", fetcher=boom)
    assert not (tmp_path / "out" / "queue.md").exists()


def test_partial_source_failure_still_produces_a_queue(tmp_path):
    cfg = config(feeds=[{"name": "Good", "adapter": "remotive", "url": "https://good/"},
                        {"name": "Bad", "adapter": "remotive", "url": "https://bad/"}])

    def fetch(url):
        if "bad" in url:
            raise OSError("boom")
        return remotive_payload(job())
    result = jbs.run(cfg, tmp_path / "s.json", tmp_path / "out", fetcher=fetch)
    assert result["new_roles"] == 1
    assert result["source_status"]["Bad"].startswith("failed")


def test_coverage_warning_when_a_source_returns_records_but_no_title_fits(tmp_path):
    result = jbs.run(config(), tmp_path / "s.json", tmp_path / "out",
                     fetcher=lambda _u: remotive_payload(job(title="Chef")))
    assert result["telemetry"]["coverage_warnings"]
    assert "zero title fits" in result["telemetry"]["coverage_warnings"][0]


# --------------------------------------------------------------------------- #
# ATS adapters
# --------------------------------------------------------------------------- #
def test_ashby_unlisted_posting_is_rejected(tmp_path):
    cfg = config(feeds=[], ats_watchlist=[{"provider": "ashby", "board": "demo"}])
    payload = {"jobs": [{"id": "1", "title": "Recruiter", "companyName": "Demo",
                         "jobUrl": "https://jobs.ashbyhq.com/demo/1", "location": "Europe",
                         "isRemote": True, "isListed": False, "descriptionPlain": "x"}]}
    result = jbs.run(cfg, tmp_path / "s.json", tmp_path / "out", fetcher=lambda _u: payload)
    assert result["rejected"] == {"no longer listed by ATS": 1}


def test_greenhouse_metadata_keeps_only_employment_labels():
    record = {"id": 1, "title": "Recruiter", "absolute_url": "https://example.com/1",
              "location": {"name": "Remote - Europe"}, "content": "x",
              "metadata": [{"name": "Employment Type", "value": "Full time"},
                           {"name": "Internal notes", "value": "y" * 400}]}
    row = jbs.normalise("greenhouse", "greenhouse:demo", record)
    assert row["employment_type"] == "Full time"


def test_lever_epoch_becomes_an_iso_timestamp():
    record = {"id": "1", "text": "Recruiter", "hostedUrl": "https://jobs.lever.co/d/1",
              "categories": {"location": "Remote - EMEA", "commitment": "Full-time"},
              "createdAt": 1750000000000, "workplaceType": "remote"}
    row = jbs.normalise("lever", "lever:demo", record)
    assert row["published_at"].startswith("2025-") and row["published_at"].endswith("Z")


def test_ats_url_is_built_from_the_provider_and_board():
    cfg = {"ats_watchlist": [{"provider": "greenhouse", "board": "demo"}]}
    assert jbs.source_configs(cfg)[0]["url"] == (
        "https://boards-api.greenhouse.io/v1/boards/demo/jobs?content=true")
