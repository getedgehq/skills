import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("build_results", HERE / "build_results.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class BuildResultsTests(unittest.TestCase):
    def test_builds_skill_result_and_machine_record(self):
        item = {
            "slug": "example",
            "title": "Example < skill",
            "description": "A result.",
            "status": "supported",
            "status_label": "Supported in this test",
            "status_explanation": "Three valid pairs.",
            "claim": "Improves one narrow behavior.",
            "method": "Blind paired test.",
            "model": "model-x",
            "package_hash": "abc",
            "stats": [{"label": "Valid pairs", "value": 3}],
            "limitations": ["One task"],
        }
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps([item]))
            site = root / "site"
            site.mkdir()
            (site / "sitemap.xml").write_text("<urlset>\n</urlset>\n")
            MODULE.build(manifest, site)
            result = (site / "evaluation/example/index.html").read_text()
            self.assertIn("Example &lt; skill", result)
            self.assertTrue((site / "skills/example/index.html").is_file())
            self.assertEqual(json.loads((site / "eval-data/example/index.json").read_text())["status"], "supported")
            self.assertIn("/evaluation/example/", (site / "result-routes.txt").read_text())
            sitemap = (site / "sitemap.xml").read_text()
            self.assertIn("https://getedge.cc/skills/example/", sitemap)
            self.assertIn("https://getedge.cc/evaluation/example/", sitemap)

    def test_escapes_repository_url_attributes(self):
        item = {
            "slug": "example",
            "title": "Example",
            "description": "A result.",
            "status": "inconclusive",
            "status_label": "Inconclusive",
            "status_explanation": "Three valid pairs.",
            "claim": "Observed one narrow behavior.",
            "method": "Blind paired test.",
            "package_hash": "abc",
            "repo_url": 'https://example.com/\" onmouseover=\"alert(1)',
            "stats": [{"label": "Valid pairs", "value": 3}],
            "limitations": ["One task"],
        }
        result = MODULE.page(item)
        self.assertNotIn('href="https://example.com/" onmouseover=', result)
        self.assertIn("&quot; onmouseover=&quot;", result)


if __name__ == "__main__":
    unittest.main()
