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
            MODULE.build(manifest, root / "site")
            result = (root / "site/evaluation/example/index.html").read_text()
            self.assertIn("Example &lt; skill", result)
            self.assertTrue((root / "site/skills/example/index.html").is_file())
            self.assertEqual(json.loads((root / "site/eval-data/example/index.json").read_text())["status"], "supported")
            self.assertIn("/evaluation/example/", (root / "site/result-routes.txt").read_text())


if __name__ == "__main__":
    unittest.main()
