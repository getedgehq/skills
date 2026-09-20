import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "scripts" / "refresh_derivation.py"
SPEC = importlib.util.spec_from_file_location("refresh_derivation", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class RefreshDerivationTests(unittest.TestCase):
    def test_refresh_is_exact_and_stable(self):
        with tempfile.TemporaryDirectory() as raw:
            bundle = Path(raw)
            (bundle / "DERIVATION.json").write_text('{"slug":"example"}\n')
            (bundle / "SKILL.md").write_text("hello\n")
            (bundle / "__pycache__").mkdir()
            (bundle / "__pycache__" / "ignored.pyc").write_bytes(b"ignored")

            first = MODULE.refresh(bundle)
            second = MODULE.refresh(bundle)

            self.assertEqual(first, second)
            self.assertEqual([entry["path"] for entry in first["copy_files"]], ["SKILL.md"])
            saved = json.loads((bundle / "DERIVATION.json").read_text())
            self.assertEqual(saved["copy_files_sha256"], first["copy_files_sha256"])


if __name__ == "__main__":
    unittest.main()
