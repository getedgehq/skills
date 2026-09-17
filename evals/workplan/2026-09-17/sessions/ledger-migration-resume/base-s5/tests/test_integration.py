import json
import os
import tempfile
import unittest

from ledgerctl.cli import main


class IntegrationTests(unittest.TestCase):
    """End-to-end tests using the real data files."""

    def setUp(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        self.current_csv = os.path.join(self.data_dir, "current.csv")
        self.legacy_csv = os.path.join(self.data_dir, "legacy_2024.csv")

    def test_current_csv_full_pipeline(self):
        """Test processing the new bank export format."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            out_path = f.name

        try:
            ret = main(["--input", self.current_csv, "--out", out_path])
            self.assertEqual(ret, 0)

            with open(out_path) as f:
                data = json.load(f)

            rows = data["rows"]
            # After deduplication, should have 9 unique transactions
            self.assertEqual(len(rows), 9)

            # Check that deduplication kept the most recent version
            t1002 = [r for r in rows if r["txn_id"] == "T-1002"][0]
            self.assertEqual(t1002["amount"], "298.40")  # rebooked amount
            self.assertEqual(t1002["updated_at"], "2026-08-30T10:00:00")

            t1003 = [r for r in rows if r["txn_id"] == "T-1003"][0]
            self.assertEqual(t1003["amount"], "9750.00")  # with credit note
            self.assertEqual(t1003["updated_at"], "2026-08-12T16:20:00")

            # Check negative amounts (parentheses)
            t1004 = [r for r in rows if r["txn_id"] == "T-1004"][0]
            self.assertEqual(t1004["amount"], "-340.00")

            t1007 = [r for r in rows if r["txn_id"] == "T-1007"][0]
            self.assertEqual(t1007["amount"], "-112.05")

            # Check account mapping
            t1001 = [r for r in rows if r["txn_id"] == "T-1001"][0]
            self.assertEqual(t1001["account"], "assets:cash")

            # Check unmapped codes are kept
            t1005 = [r for r in rows if r["txn_id"] == "T-1005"][0]
            self.assertEqual(t1005["account"], "6300")  # unmapped, kept as-is

            # All currencies should be uppercase
            for r in rows:
                self.assertEqual(r["currency"], "EUR")

        finally:
            if os.path.exists(out_path):
                os.unlink(out_path)

    def test_legacy_csv_still_works(self):
        """Test that the 2024 legacy format still processes correctly."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            out_path = f.name

        try:
            ret = main(["--input", self.legacy_csv, "--out", out_path])
            self.assertEqual(ret, 0)

            with open(out_path) as f:
                data = json.load(f)

            rows = data["rows"]
            self.assertEqual(len(rows), 3)

            # Check a sample row
            l2201 = [r for r in rows if r["txn_id"] == "L-2201"][0]
            self.assertEqual(l2201["account"], "assets:cash")
            self.assertEqual(l2201["amount"], "880.00")
            self.assertEqual(l2201["currency"], "EUR")

        finally:
            if os.path.exists(out_path):
                os.unlink(out_path)

    def test_since_filter(self):
        """Test the --since filter."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            out_path = f.name

        try:
            ret = main([
                "--input", self.current_csv,
                "--out", out_path,
                "--since", "2026-08-01"
            ])
            self.assertEqual(ret, 0)

            with open(out_path) as f:
                data = json.load(f)

            rows = data["rows"]
            self.assertEqual(len(rows), 6)

            # All rows should be from August or later
            for r in rows:
                self.assertGreaterEqual(r["booked_on"], "2026-08-01")

            # Should not include July transactions
            txn_ids = [r["txn_id"] for r in rows]
            self.assertNotIn("T-1001", txn_ids)  # July 3
            self.assertIn("T-1004", txn_ids)  # August 2

        finally:
            if os.path.exists(out_path):
                os.unlink(out_path)


if __name__ == "__main__":
    unittest.main()
