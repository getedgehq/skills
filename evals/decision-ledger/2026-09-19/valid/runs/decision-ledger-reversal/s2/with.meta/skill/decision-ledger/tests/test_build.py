from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("build", HERE / "scripts" / "build.py")
build = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(build)


class BuildTests(unittest.TestCase):
    def test_evidence_must_match_line(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "notes.txt"
            source.write_text("We decided to ship Friday.\n")
            with self.assertRaisesRegex(ValueError, "evidence mismatch"):
                build.validate(source, [{"id": "d1", "state": "decided", "line": 1, "evidence": "ship Monday"}])

    def test_unknown_fields_are_explicit(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "notes.txt"
            source.write_text("We decided to ship Friday.\n")
            result = build.validate(source, [{"id": "d1", "state": "decided", "line": 1, "evidence": "ship Friday"}])
            self.assertEqual(result["records"][0]["owner"], "unknown")


if __name__ == "__main__":
    unittest.main()
