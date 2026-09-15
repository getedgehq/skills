import json, os, pathlib, subprocess, threading, unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

ROOT = pathlib.Path(__file__).parents[1]
SCRIPT = ROOT / "scripts" / "people_search.py"
FIXTURE = ROOT / "tests" / "fixtures" / "people.csv"

class PeopleSearchTests(unittest.TestCase):
    def run_cli(self, *args, env=None):
        result = subprocess.run(["python3", str(SCRIPT), *args], capture_output=True, text=True, env=env)
        return result.returncode, json.loads(result.stdout)

    def test_import_filters_ranks_and_deduplicates(self):
        code, data = self.run_cli("--mode", "import", "--input", str(FIXTURE), "--locations", "Berlin", "--titles", "growth", "--prefer-keywords", "head,ai")
        self.assertEqual(code, 0)
        self.assertEqual([r["name"] for r in data["results"]], ["Ada Example"])
        self.assertEqual(data["cost"]["estimated_usd"], 0)

    def test_plan_never_fabricates_results(self):
        code, data = self.run_cli("--mode", "plan", "--titles", "founder")
        self.assertEqual(code, 0)
        self.assertEqual(data["results"], [])

    def test_provider_fails_closed_without_credential(self):
        code, data = self.run_cli("--mode", "provider", "--endpoint", "https://example.invalid")
        self.assertEqual(code, 2)
        self.assertIn("credential unavailable", data["error"])

    def test_provider_adapter_uses_preview_and_ranks_response(self):
        observed = {}
        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                observed["authorization"] = self.headers.get("Authorization")
                length = int(self.headers.get("Content-Length", "0"))
                observed["payload"] = json.loads(self.rfile.read(length))
                body = json.dumps({"results": [{"name": "Dana", "current_title": "Growth Lead", "current_company": "Acme AI", "location": "Berlin", "profile_url": "https://example.com/dana", "evidence_url": "https://example.com/dana"}]}).encode()
                self.send_response(200); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
            def log_message(self, *_): pass
        server = HTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        env = {**os.environ, "TEST_PEOPLE_TOKEN": "test-only-token"}
        try:
            code, data = self.run_cli("--mode", "provider", "--endpoint", f"http://127.0.0.1:{server.server_port}", "--token-env", "TEST_PEOPLE_TOKEN", "--locations", "Berlin", "--titles", "growth", env=env)
        finally:
            server.shutdown(); thread.join(); server.server_close()
        self.assertEqual(code, 0)
        self.assertEqual(data["results"][0]["name"], "Dana")
        self.assertTrue(observed["payload"]["preview"])
        self.assertEqual(observed["payload"]["limit"], 5)
        self.assertEqual(observed["authorization"], "Bearer test-only-token")

if __name__ == "__main__": unittest.main()
