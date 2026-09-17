import json
import os
import tempfile
import unittest

from ledgerctl.cli import main


class CLITests(unittest.TestCase):
    def test_since_filter(self):
        """Test that --since filters rows by booked_on date."""
        current = os.path.join(os.path.dirname(__file__), "..", "data", "current.csv")
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tf:
            try:
                ret = main(["--input", current, "--out", tf.name, "--since", "2026-08-01"])
                self.assertEqual(ret, 0)
                
                with open(tf.name) as f:
                    data = json.load(f)
                
                rows = data["rows"]
                # Should only include rows booked on or after 2026-08-01
                for r in rows:
                    self.assertGreaterEqual(r["booked_on"], "2026-08-01")
                
                # Verify we filtered out earlier rows
                self.assertTrue(all(r["booked_on"] >= "2026-08-01" for r in rows))
                # Current.csv has rows from July and August; should have fewer than total
                self.assertLess(len(rows), 11)  # Total would be less after deduping
                
            finally:
                os.unlink(tf.name)


if __name__ == "__main__":
    unittest.main()
