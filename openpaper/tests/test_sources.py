import importlib.util
import subprocess
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).parents[1] / "scripts" / "sources.py"
SPEC = importlib.util.spec_from_file_location("openpaper_sources", SCRIPT)
SOURCES = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SOURCES)


class VerifyTests(unittest.TestCase):
    def test_empty_doi_is_invalid_without_network_call(self):
        with patch.object(SOURCES, "_get") as get:
            result = SOURCES.verify("   ")

        get.assert_not_called()
        self.assertEqual(
            result,
            {
                "doi": "",
                "status": "invalid",
                "agency": None,
                "error": "DOI is empty",
            },
        )

    def test_empty_doi_command_exits_nonzero(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "verify", "   "],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn('"status": "invalid"', result.stdout)


class FindTests(unittest.TestCase):
    def test_openalex_doi_is_not_returned_when_it_does_not_resolve(self):
        openalex_result = {
            "doi": "https://doi.org/10.9999/unverified",
            "title": "Unverified result",
            "authorships": [{"author": {"display_name": "Ada Lovelace"}}],
            "publication_year": 2026,
            "primary_location": {"source": {"display_name": "Example"}},
            "type": "article",
        }
        calls = []

        def fake_get(url, timeout=20):
            calls.append(url)
            if url.startswith("https://api.crossref.org/works?"):
                return {"message": {"items": []}}
            if url.startswith("https://api.openalex.org/works?"):
                return {"results": [openalex_result]}
            raise urllib.error.HTTPError(url, 404, "not found", {}, None)

        with patch.object(SOURCES, "_get", side_effect=fake_get), patch.object(
            SOURCES.time, "sleep", return_value=None
        ):
            result = SOURCES.find("example", n=1)

        self.assertEqual(result, [])
        self.assertTrue(
            any("api.crossref.org/works/10.9999/unverified" in url for url in calls)
        )
        self.assertTrue(
            any("api.datacite.org/dois/10.9999/unverified" in url for url in calls)
        )


if __name__ == "__main__":
    unittest.main()
