"""Tests for scripts/people_search.py.

Every provider test runs against the local stub server below. Nothing here
touches a real provider and nothing here can spend money.
"""
import json, os, pathlib, subprocess, threading, unittest
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, HTTPServer

ROOT = pathlib.Path(__file__).parents[1]
SCRIPT = ROOT / "scripts" / "people_search.py"
FIXTURE = ROOT / "tests" / "fixtures" / "people.csv"

PROVIDER_ROW = {
    "name": "Dana",
    "current_title": "Growth Lead",
    "current_company": "Acme AI",
    "location": "Berlin",
    "profile_url": "https://example.com/dana",
    "evidence_url": "https://example.com/dana",
}


@contextmanager
def stub_provider(body=None, status=200, raw=None):
    """Local stand-in for a paid provider. Records what the runner sent."""
    observed = {"requests": []}
    payload = raw if raw is not None else json.dumps(body if body is not None else {"results": []}).encode()

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            length = int(self.headers.get("Content-Length", "0"))
            observed["requests"].append(
                {
                    "authorization": self.headers.get("Authorization"),
                    "payload": json.loads(self.rfile.read(length) or b"{}"),
                }
            )
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, *_):
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    observed["url"] = f"http://127.0.0.1:{server.server_port}"
    try:
        yield observed
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


class BaseCase(unittest.TestCase):
    def run_cli(self, *args, env=None):
        result = subprocess.run(["python3", str(SCRIPT), *args], capture_output=True, text=True, env=env)
        return result.returncode, json.loads(result.stdout), result.stderr

    def run_provider(self, observed, *args, run_env=None):
        env = {**os.environ, "TEST_PEOPLE_TOKEN": "test-only-token", **(run_env or {})}
        return self.run_cli("--mode", "provider", "--endpoint", observed["url"], "--token-env", "TEST_PEOPLE_TOKEN", *args, env=env)

    def labels(self, data, bucket):
        return sorted(entry["filter"] for entry in data["filters"][bucket])


class RankingTests(BaseCase):
    def test_import_filters_ranks_and_deduplicates(self):
        code, data, _ = self.run_cli(
            "--mode", "import", "--input", str(FIXTURE), "--locations", "Berlin", "--titles", "growth",
            "--prefer-keywords", "head,ai",
        )
        self.assertEqual(code, 0)
        self.assertEqual([r["name"] for r in data["results"]], ["Ada Example", "Farah Example"])
        self.assertEqual(data["cost"]["estimated_usd"], 0)
        self.assertEqual(data["diagnostics"]["duplicates_removed"], 1)

    def test_plan_never_fabricates_results(self):
        code, data, _ = self.run_cli("--mode", "plan", "--titles", "founder")
        self.assertEqual(code, 0)
        self.assertEqual(data["results"], [])
        self.assertTrue(data["ok"])

    def test_hard_filters_are_field_scoped(self):
        # "Berliner Bank" in Munich must not satisfy a location filter of "berlin".
        code, data, _ = self.run_cli(
            "--mode", "import", "--input", str(FIXTURE), "--locations", "berlin", "--titles", "growth"
        )
        self.assertEqual(code, 0)
        names = [r["name"] for r in data["results"]]
        self.assertNotIn("Erik Example", names)
        self.assertEqual(data["diagnostics"]["rejected_by_filter"]["must_have.locations"], 2)

    def test_company_filter_and_exclusions(self):
        code, data, _ = self.run_cli(
            "--mode", "import", "--input", str(FIXTURE), "--locations", "Berlin", "--titles", "growth",
            "--exclude-companies", "Atlas AI",
        )
        self.assertEqual(code, 0)
        self.assertEqual([r["name"] for r in data["results"]], ["Farah Example"])
        self.assertIn("exclusions.companies", self.labels(data, "applied"))

    def test_exclude_keywords_and_titles(self):
        code, data, _ = self.run_cli(
            "--mode", "import", "--input", str(FIXTURE), "--titles", "growth", "--exclude-titles", "vp",
            "--exclude-keywords", "neon",
        )
        self.assertEqual(code, 0)
        names = [r["name"] for r in data["results"]]
        self.assertNotIn("Cara Example", names)
        self.assertNotIn("Farah Example", names)
        self.assertIn("exclusions.keywords", self.labels(data, "approximated"))

    def test_zero_results_are_labelled_as_a_source_limit(self):
        code, data, _ = self.run_cli("--mode", "import", "--input", str(FIXTURE), "--locations", "Lisbon")
        self.assertEqual(code, 0)
        self.assertEqual(data["results"], [])
        self.assertTrue(data["results_valid"])
        self.assertIn("not proof that no such people exist", data["zero_result_note"])


class FilterDisclosureTests(BaseCase):
    def test_import_discloses_applied_approximated_and_dropped(self):
        code, data, _ = self.run_cli(
            "--mode", "import", "--input", str(FIXTURE), "--locations", "Berlin", "--titles", "growth",
            "--must-keywords", "ai", "--industries", "fintech",
        )
        self.assertEqual(code, 0)
        self.assertEqual(self.labels(data, "applied"), ["must_have.current_titles", "must_have.locations"])
        self.assertEqual(self.labels(data, "approximated"), ["must_have.keywords"])
        self.assertEqual(self.labels(data, "dropped"), ["must_have.industries"])
        dropped = data["filters"]["dropped"][0]
        self.assertEqual(dropped["values"], ["fintech"])
        self.assertIn("broader than the brief", dropped["reason"])
        # A dropped filter is not enforced, so it must not silently empty the list.
        self.assertTrue(data["results"])

    def test_applied_entries_name_the_field_they_matched(self):
        code, data, _ = self.run_cli("--mode", "import", "--input", str(FIXTURE), "--locations", "Berlin")
        self.assertEqual(code, 0)
        entry = data["filters"]["applied"][0]
        self.assertEqual(entry["fields"], ["location"])
        self.assertIn("location", entry["match"])

    def test_plan_mode_does_not_claim_any_filter_was_applied(self):
        code, data, _ = self.run_cli("--mode", "plan", "--locations", "Berlin", "--titles", "growth")
        self.assertEqual(code, 0)
        self.assertEqual(data["filters"]["applied"], [])
        self.assertEqual(self.labels(data, "unsupported"), ["must_have.current_titles", "must_have.locations"])
        self.assertIn("executes no search", data["filters"]["unsupported"][0]["reason"])

    def test_provider_unconfirmed_filters_are_approximated_not_applied(self):
        with stub_provider({"results": [PROVIDER_ROW]}) as observed:
            code, data, _ = self.run_provider(observed, "--locations", "Berlin", "--titles", "growth")
        self.assertEqual(code, 0)
        self.assertEqual(data["filters"]["applied"], [])
        entry = data["filters"]["approximated"][0]
        self.assertEqual(entry["provider_status"], "unconfirmed")

    def test_provider_declared_filters_are_recorded_per_declaration(self):
        body = {
            "results": [PROVIDER_ROW],
            "filters": {"applied": ["locations"], "unsupported": ["current_titles"]},
        }
        with stub_provider(body) as observed:
            code, data, _ = self.run_provider(observed, "--locations", "Berlin", "--titles", "growth")
        self.assertEqual(code, 0)
        self.assertEqual(self.labels(data, "applied"), ["must_have.locations"])
        unsupported_by_provider = [e for e in data["filters"]["approximated"] if e["provider_status"] == "unsupported"]
        self.assertEqual([e["filter"] for e in unsupported_by_provider], ["must_have.current_titles"])

    def test_provider_claim_contradicted_by_its_own_rows_is_downgraded(self):
        off_target = {**PROVIDER_ROW, "name": "Off Target", "location": "Lisbon", "profile_url": "https://example.com/off"}
        body = {"results": [PROVIDER_ROW, off_target], "filters": {"applied": ["locations"]}}
        with stub_provider(body) as observed:
            code, data, _ = self.run_provider(observed, "--locations", "Berlin")
        self.assertEqual(code, 0)
        self.assertEqual(data["filters"]["applied"], [])
        entry = data["filters"]["approximated"][0]
        self.assertEqual(entry["locally_rejected_records"], 1)
        self.assertIn("returned 1 record(s) that do not match", entry["reason"])

    def test_filter_dropped_when_provider_rows_lack_the_field(self):
        with stub_provider({"results": [{"name": "Dana", "profile_url": "https://example.com/dana"}]}) as observed:
            code, data, _ = self.run_provider(observed, "--locations", "Berlin")
        self.assertEqual(code, 0)
        self.assertEqual(self.labels(data, "dropped"), ["must_have.locations"])
        self.assertEqual([r["name"] for r in data["results"]], ["Dana"])


class ProviderRunModeTests(BaseCase):
    def test_canary_is_the_default_and_stays_a_preview(self):
        with stub_provider({"results": [PROVIDER_ROW]}) as observed:
            code, data, _ = self.run_provider(observed, "--locations", "Berlin", "--titles", "growth")
            request = observed["requests"][0]
        self.assertEqual(code, 0)
        self.assertEqual(data["results"][0]["name"], "Dana")
        self.assertTrue(request["payload"]["preview"])
        self.assertEqual(request["payload"]["limit"], 5)
        self.assertEqual(request["authorization"], "Bearer test-only-token")
        self.assertIn("not a complete result set", data["coverage_note"])

    def test_full_run_sends_the_real_limit_and_is_not_a_preview(self):
        with stub_provider({"results": [PROVIDER_ROW]}) as observed:
            code, data, _ = self.run_provider(
                observed, "--provider-run", "full", "--limit", "40", "--max-cost-usd", "10",
                "--cost-per-result-usd", "0.02",
            )
            request = observed["requests"][0]
        self.assertEqual(code, 0)
        self.assertFalse(request["payload"]["preview"])
        self.assertEqual(request["payload"]["limit"], 40)
        self.assertTrue(data["cost"]["billable"])
        self.assertEqual(data["cost"]["estimated_usd"], 0.8)

    def test_canary_limit_is_configurable(self):
        with stub_provider({"results": []}) as observed:
            code, _data, _ = self.run_provider(observed, "--canary-limit", "2", "--limit", "30")
            request = observed["requests"][0]
        self.assertEqual(code, 0)
        self.assertEqual(request["payload"]["limit"], 2)

    def test_full_run_requires_a_declared_budget(self):
        with stub_provider({"results": [PROVIDER_ROW]}) as observed:
            code, data, _ = self.run_provider(observed, "--provider-run", "full")
            calls = len(observed["requests"])
        self.assertEqual(code, 2)
        self.assertEqual(calls, 0)
        self.assertEqual(data["error"]["type"], "budget_not_declared")
        self.assertIsNone(data["results"])

    def test_cost_cap_blocks_the_request_before_spending(self):
        with stub_provider({"results": [PROVIDER_ROW]}) as observed:
            code, data, _ = self.run_provider(
                observed, "--provider-run", "full", "--limit", "100", "--cost-per-result-usd", "0.5",
                "--max-cost-usd", "1",
            )
            calls = len(observed["requests"])
        self.assertEqual(code, 2)
        self.assertEqual(calls, 0)
        self.assertEqual(data["error"]["type"], "budget_exceeded")
        self.assertIn("exceeds --max-cost-usd", data["error"]["message"])

    def test_reported_overspend_is_surfaced_as_a_warning(self):
        body = {"results": [PROVIDER_ROW], "cost": {"actual_usd": 3.5}}
        with stub_provider(body) as observed:
            code, data, _ = self.run_provider(
                observed, "--provider-run", "full", "--limit", "10", "--cost-per-result-usd", "0.1",
                "--max-cost-usd", "1",
            )
        self.assertEqual(code, 0)
        self.assertEqual(data["cost"]["actual_usd"], 3.5)
        self.assertIn("above the declared cap", data["warnings"][0])

    def test_provider_field_mapping_normalizes_raw_rows(self):
        raw = {
            "fullName": "Dana Provider",
            "headline": "Head of Growth",
            "companyName": {"name": "Acme AI"},
            "locationName": "Berlin, Germany",
            "linkedinUrl": "https://example.com/dana-p",
            "connectionDegree": 2,
        }
        with stub_provider({"results": [raw]}) as observed:
            code, data, _ = self.run_provider(observed, "--locations", "Berlin", "--titles", "growth")
        self.assertEqual(code, 0)
        record = data["results"][0]
        self.assertEqual(record["name"], "Dana Provider")
        self.assertEqual(record["current_company"], "Acme AI")
        self.assertEqual(record["profile_url"], "https://example.com/dana-p")
        self.assertEqual(data["provider_mapping"]["mapped"]["current_title"], "headline")
        self.assertIn("connectionDegree", data["provider_mapping"]["unmapped_provider_fields"])
        self.assertIn("evidence_url", data["provider_mapping"]["missing_canonical_fields"])


class FailurePayloadTests(BaseCase):
    def assert_not_a_result_set(self, code, data, stderr):
        self.assertEqual(code, 2)
        self.assertFalse(data["ok"])
        self.assertEqual(data["status"], "error")
        self.assertIsNone(data["results"])
        self.assertFalse(data["results_valid"])
        self.assertIn("not evidence that zero people match", data["coverage_note"])
        self.assertTrue(stderr.strip())
        # An agent that iterates the payload as a result set must break, not
        # report an empty shortlist.
        with self.assertRaises(TypeError):
            len(data["results"])

    def test_provider_fails_closed_without_credential(self):
        code, data, stderr = self.run_cli("--mode", "provider", "--endpoint", "https://example.invalid")
        self.assert_not_a_result_set(code, data, stderr)
        self.assertEqual(data["error"]["type"], "missing_credential")
        self.assertIn("credential unavailable", data["error"]["message"])

    def test_payment_required_is_not_zero_results(self):
        with stub_provider(raw=b'{"error":"payment required"}', status=402) as observed:
            code, data, stderr = self.run_provider(observed, "--locations", "Berlin")
        self.assert_not_a_result_set(code, data, stderr)
        self.assertEqual(data["error"]["type"], "provider_http_error")
        self.assertEqual(data["error"]["detail"]["status"], 402)
        self.assertFalse(data["error"]["retryable"])

    def test_rate_limit_is_marked_retryable(self):
        with stub_provider(raw=b"slow down", status=429) as observed:
            code, data, stderr = self.run_provider(observed, "--locations", "Berlin")
        self.assert_not_a_result_set(code, data, stderr)
        self.assertTrue(data["error"]["retryable"])

    def test_unreachable_provider_is_not_zero_results(self):
        env = {**os.environ, "TEST_PEOPLE_TOKEN": "test-only-token"}
        code, data, stderr = self.run_cli(
            "--mode", "provider", "--endpoint", "http://127.0.0.1:9", "--token-env", "TEST_PEOPLE_TOKEN",
            "--timeout", "2", env=env,
        )
        self.assert_not_a_result_set(code, data, stderr)
        self.assertEqual(data["error"]["type"], "provider_unreachable")

    def test_missing_input_file_is_not_zero_results(self):
        code, data, stderr = self.run_cli("--mode", "import", "--input", str(ROOT / "tests" / "no-such.csv"))
        self.assert_not_a_result_set(code, data, stderr)
        self.assertEqual(data["error"]["type"], "input_error")


if __name__ == "__main__":
    unittest.main()
