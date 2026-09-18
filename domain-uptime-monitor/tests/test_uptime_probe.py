"""Tests for uptime_probe. No network: every test supplies its own http callable."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import uptime_probe as up  # noqa: E402


def fake_http(routes):
    """routes: {url: (status, body_bytes)}. Anything unrouted is a DNS failure."""
    def http(url, method="GET", data=None, extra_headers=None):
        key = f"{method} {url}" if f"{method} {url}" in routes else url
        return routes.get(key, (None, b"ERR:URLError:not routed"))
    return http


def cfg(*domains, **over):
    base = {"domains": list(domains)}
    base.update(over)
    return base


# --------------------------------------------------------------------------- #
# the point of the skill: a 200 that is really off
# --------------------------------------------------------------------------- #
def test_marker_check_fails_on_a_200_with_the_wrong_body(tmp_path):
    config = cfg({"host": "a.test", "tier": "critical",
                  "check": {"type": "marker", "path": "/", "marker": "Real Product"}})
    http = fake_http({"https://a.test/": (200, b"<h1>This deployment is disabled</h1>")})
    result = up.run(config, tmp_path / "s.json", tmp_path / "r.md", "", "",
                    http=http, send=False)
    assert result["critical_down"] == ["a.test"]
    assert "marker" in result["results"]["a.test"]["detail"]
    assert "missing" in result["results"]["a.test"]["detail"]


def test_marker_check_passes_when_the_marker_is_present(tmp_path):
    config = cfg({"host": "a.test", "tier": "critical",
                  "check": {"type": "marker", "marker": "Real Product"}})
    http = fake_http({"https://a.test/": (200, b"<title>Real Product</title>")})
    result = up.run(config, tmp_path / "s.json", tmp_path / "r.md", "", "",
                    http=http, send=False)
    assert result["critical_down"] == []


def test_json_check_reads_a_nested_field(tmp_path):
    config = cfg({"host": "api.test", "tier": "critical",
                  "check": {"type": "json", "path": "/healthz",
                            "field": "checks.db", "contains": "ok"}})
    body = json.dumps({"checks": {"db": "ok (degraded)"}}).encode()
    result = up.run(config, tmp_path / "s.json", tmp_path / "r.md", "", "",
                    http=fake_http({"https://api.test/healthz": (200, body)}), send=False)
    assert result["critical_down"] == []


def test_json_check_fails_when_the_field_disagrees(tmp_path):
    config = cfg({"host": "api.test", "tier": "critical",
                  "check": {"type": "json", "path": "/health",
                            "field": "database", "equals": "connected"}})
    body = json.dumps({"database": "disconnected"}).encode()
    result = up.run(config, tmp_path / "s.json", tmp_path / "r.md", "", "",
                    http=fake_http({"https://api.test/health": (200, body)}), send=False)
    assert result["critical_down"] == ["api.test"]


def test_json_check_fails_on_200_with_html_instead_of_json(tmp_path):
    config = cfg({"host": "api.test", "tier": "critical",
                  "check": {"type": "json", "path": "/health", "field": "database"}})
    result = up.run(config, tmp_path / "s.json", tmp_path / "r.md", "", "",
                    http=fake_http({"https://api.test/health": (200, b"<html>502</html>")}),
                    send=False)
    assert result["critical_down"] == ["api.test"]
    assert "not JSON" in result["results"]["api.test"]["detail"]


def test_allowed_401_is_up(tmp_path):
    config = cfg({"host": "gated.test", "tier": "critical",
                  "check": {"type": "status", "allow": [200, 401]}})
    result = up.run(config, tmp_path / "s.json", tmp_path / "r.md", "", "",
                    http=fake_http({"https://gated.test/": (401, b"")}), send=False)
    assert result["critical_down"] == []


def test_dns_failure_is_down_not_an_exception(tmp_path):
    config = cfg({"host": "gone.test", "tier": "critical"})
    result = up.run(config, tmp_path / "s.json", tmp_path / "r.md", "", "",
                    http=fake_http({}), send=False)
    assert result["critical_down"] == ["gone.test"]


# --------------------------------------------------------------------------- #
# post_check
# --------------------------------------------------------------------------- #
def test_post_check_fails_the_domain_on_the_declared_signature(tmp_path):
    config = cfg({"host": "app.test", "tier": "critical",
                  "check": {"type": "marker", "marker": "Sign in"},
                  "post_check": {"path": "/api/auth/sync", "origin": "https://app.test",
                                 "body": {"probe": 1}, "ok_status": [200, 401],
                                 "fail_if": {"status": 403, "body_contains": "csrf"}}})
    http = fake_http({"https://app.test/": (200, b"Sign in"),
                      "POST https://app.test/api/auth/sync": (403, b'{"error":"CSRF token"}')})
    result = up.run(config, tmp_path / "s.json", tmp_path / "r.md", "", "",
                    http=http, send=False)
    assert result["critical_down"] == ["app.test"]
    assert "failure signature" in result["results"]["app.test"]["detail"]


def test_post_check_ok_status_keeps_the_domain_up(tmp_path):
    config = cfg({"host": "app.test", "tier": "critical",
                  "check": {"type": "marker", "marker": "Sign in"},
                  "post_check": {"path": "/api/auth/sync", "ok_status": [200, 401],
                                 "fail_if": {"status": 403, "body_contains": "csrf"}}})
    http = fake_http({"https://app.test/": (200, b"Sign in"),
                      "POST https://app.test/api/auth/sync": (401, b"unauthorized")})
    result = up.run(config, tmp_path / "s.json", tmp_path / "r.md", "", "",
                    http=http, send=False)
    assert result["critical_down"] == []


# --------------------------------------------------------------------------- #
# tiers and alerting
# --------------------------------------------------------------------------- #
def test_a_standard_domain_down_does_not_alert_or_fail_the_run(tmp_path):
    config = cfg({"host": "blog.test", "tier": "standard"})
    result = up.run(config, tmp_path / "s.json", tmp_path / "r.md", "", "",
                    http=fake_http({}), send=False)
    assert result["critical_down"] == [] and result["standard_down"] == ["blog.test"]
    assert result["state_changes"] == []


def test_first_sighting_of_a_down_domain_is_not_a_transition(tmp_path):
    config = cfg({"host": "a.test", "tier": "critical"})
    result = up.run(config, tmp_path / "s.json", tmp_path / "r.md", "", "",
                    http=fake_http({}), send=False)
    assert result["critical_down"] == ["a.test"]
    assert result["state_changes"] == []


def test_alerts_fire_once_on_down_and_once_on_recovery(tmp_path):
    config = cfg({"host": "a.test", "tier": "critical"})
    state, report = tmp_path / "s.json", tmp_path / "r.md"
    ok = fake_http({"https://a.test/": (200, b"hi")})
    down = fake_http({})

    assert up.run(config, state, report, "", "", http=ok, send=False)["state_changes"] == []
    assert up.run(config, state, report, "", "", http=down, send=False)["state_changes"] == ["DOWN:a.test"]
    # Still down: no second alert.
    assert up.run(config, state, report, "", "", http=down, send=False)["state_changes"] == []
    assert up.run(config, state, report, "", "", http=ok, send=False)["state_changes"] == ["RECOVERED:a.test"]


def test_a_send_failure_does_not_mask_detection(tmp_path, monkeypatch):
    monkeypatch.delenv("RESEND_API_KEY", raising=False)
    config = cfg({"host": "a.test", "tier": "critical"})
    state, report = tmp_path / "s.json", tmp_path / "r.md"
    up.run(config, state, report, "ops@example.test", "Uptime <u@example.test>",
           http=fake_http({"https://a.test/": (200, b"hi")}), send=True)
    result = up.run(config, state, report, "ops@example.test", "Uptime <u@example.test>",
                    http=fake_http({}), send=True)
    assert result["critical_down"] == ["a.test"]
    assert result["state_changes"] == ["DOWN:a.test"]
    assert "RESEND_API_KEY not set" in result["email"]


# --------------------------------------------------------------------------- #
# config: no personal default ever
# --------------------------------------------------------------------------- #
def test_missing_notify_email_is_a_config_error():
    with pytest.raises(up.ConfigError, match="no alert recipient"):
        up.resolve_notify({"domains": []}, None, None, False)


def test_missing_email_from_is_a_config_error():
    with pytest.raises(up.ConfigError, match="no alert sender"):
        up.resolve_notify({"notify_email": "a@b.test"}, None, None, False)


def test_no_email_needs_no_address():
    assert up.resolve_notify({}, None, None, True) == ("", "")


def test_empty_domains_is_a_config_error(tmp_path):
    path = tmp_path / "c.json"
    path.write_text(json.dumps({"domains": []}))
    with pytest.raises(up.ConfigError, match="non-empty list"):
        up.load_config(path)


def test_marker_check_without_a_marker_is_a_config_error(tmp_path):
    path = tmp_path / "c.json"
    path.write_text(json.dumps({"domains": [{"host": "a.test",
                                             "check": {"type": "marker"}}]}))
    with pytest.raises(up.ConfigError, match="needs 'marker'"):
        up.load_config(path)


def test_cli_exits_2_without_a_recipient(tmp_path, capsys):
    path = tmp_path / "c.json"
    path.write_text(json.dumps({"domains": [{"host": "a.test"}]}))
    assert up.main(["--config", str(path)]) == 2
    assert "no alert recipient" in capsys.readouterr().err


def test_two_entries_with_the_same_label_are_a_config_error(tmp_path):
    path = tmp_path / "c.json"
    path.write_text(json.dumps({"domains": [
        {"host": "a.test", "check": {"type": "marker", "marker": "Home"}},
        {"host": "a.test", "check": {"type": "marker", "marker": "Checkout"}}]}))
    with pytest.raises(up.ConfigError, match="share the label"):
        up.load_config(path)


def test_a_name_lets_you_probe_one_host_twice(tmp_path):
    """Without distinct labels the second result silently overwrote the first."""
    config = cfg(
        {"host": "a.test", "name": "a.test home", "tier": "critical",
         "check": {"type": "marker", "path": "/", "marker": "Home"}},
        {"host": "a.test", "name": "a.test checkout", "tier": "critical",
         "check": {"type": "marker", "path": "/buy", "marker": "Add to cart"}})
    http = fake_http({"https://a.test/": (200, b"Home"),
                      "https://a.test/buy": (200, b"upgrade your plan")})
    result = up.run(config, tmp_path / "s.json", tmp_path / "r.md", "", "",
                    http=http, send=False)
    assert sorted(result["results"]) == ["a.test checkout", "a.test home"]
    assert result["critical_down"] == ["a.test checkout"]


# --------------------------------------------------------------------------- #
# transfer encoding: a healthy site must not fail its own marker check
# --------------------------------------------------------------------------- #
class Headers(dict):
    def get(self, key, default=None):  # case-insensitive, like http.client
        for k, v in self.items():
            if k.lower() == key.lower():
                return v
        return default


def test_a_gzipped_body_is_decoded_before_the_marker_is_looked_for():
    """www.python.org gzips even when the request asks for identity. Without this,
    a live healthy site reads as DOWN."""
    import gzip as _gzip
    raw = _gzip.compress(b"<title>Real Product</title>")
    assert b"Real Product" not in raw
    assert b"Real Product" in up.decode_body(raw, Headers({"Content-Encoding": "gzip"}))


def test_a_deflate_body_is_decoded():
    import zlib as _zlib
    raw = _zlib.compress(b"<title>Real Product</title>")
    assert b"Real Product" in up.decode_body(raw, Headers({"Content-Encoding": "deflate"}))


def test_an_undecodable_encoding_is_left_alone_rather_than_faked():
    raw = b"\x01\x02brotli-ish"
    assert up.decode_body(raw, Headers({"Content-Encoding": "br"})) == raw


def test_an_unencoded_body_is_untouched():
    assert up.decode_body(b"plain", Headers({})) == b"plain"


def test_report_is_written_every_run(tmp_path):
    config = cfg({"host": "a.test", "tier": "critical",
                  "check": {"type": "marker", "marker": "Hi"}})
    report = tmp_path / "out" / "report.md"
    up.run(config, tmp_path / "s.json", report, "", "",
           http=fake_http({"https://a.test/": (200, b"Hi there")}), send=False)
    text = report.read_text()
    assert "| a.test | critical | UP |" in text and "1/1 up" in text
