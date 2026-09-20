from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "summarize.py"


class SummarizeTests(unittest.TestCase):
    def test_confusion_matrix_accuracy(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            before, after, out = root / "before.json", root / "after.json", root / "out.json"
            before.write_text(json.dumps({"tp": 4, "tn": 4, "fp": 1, "fn": 3}))
            after.write_text(json.dumps({"tp": 6, "tn": 4, "fp": 1, "fn": 1}))
            subprocess.check_call([sys.executable, str(SCRIPT), str(before), str(after), "--out", str(out)])
            result = json.loads(out.read_text())
            self.assertAlmostEqual(result["before_accuracy"], 8 / 12)
            self.assertAlmostEqual(result["after_accuracy"], 10 / 12)


if __name__ == "__main__":
    unittest.main()
