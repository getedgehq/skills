from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("receipt", HERE / "scripts" / "receipt.py")
receipt = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(receipt)


class ReceiptTests(unittest.TestCase):
    def test_public_result_hashes_but_does_not_copy_evidence(self):
        result = receipt.build_receipt({
            "project": "Example",
            "agent": "Codex",
            "tests_passed": 4,
            "tests_total": 4,
            "evidence": [{"private_path": "/secret/customer.txt"}],
        })
        self.assertEqual(result["evidence_count"], 1)
        self.assertNotIn("evidence", result)
        self.assertNotIn("/secret/customer.txt", str(result))
        self.assertEqual(result["privacy"], "summary_only")

    def test_impossible_test_count_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "cannot exceed"):
            receipt.build_receipt({"project": "X", "agent": "Y", "tests_passed": 2, "tests_total": 1})


if __name__ == "__main__":
    unittest.main()
