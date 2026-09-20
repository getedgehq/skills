from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class LaunchToolTests(unittest.TestCase):
    def test_inspector_ignores_dependency_tree(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary) / "product"
            repo.mkdir()
            (repo / "README.md").write_text("# Clear Product\n\nDoes one useful thing.\n")
            (repo / "main.py").write_text("print('ok')\n")
            ignored = repo / "node_modules" / "x"
            ignored.mkdir(parents=True)
            (ignored / "junk.js").write_text("junk")
            out = Path(temporary) / "facts.json"
            subprocess.check_call([sys.executable, str(ROOT / "scripts" / "inspect_repo.py"), str(repo), "--out", str(out)])
            facts = json.loads(out.read_text())
            self.assertEqual(facts["title"], "Clear Product")
            self.assertEqual(facts["file_count"], 2)

    def test_validator_requires_every_launch_asset(self):
        with tempfile.TemporaryDirectory() as temporary:
            run = subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_pack.py"), temporary], capture_output=True, text=True)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("facts.json", run.stderr)


if __name__ == "__main__":
    unittest.main()
