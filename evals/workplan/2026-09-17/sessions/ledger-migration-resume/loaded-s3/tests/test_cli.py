import json
import os
import tempfile
import unittest

from ledgerctl.cli import main


class CliTests(unittest.TestCase):
    def test_since_filter(self):
        """Test that --since filters on booked_on date."""
        fixture = os.path.join(os.path.dirname(__file__), "fixtures", "simple.csv")
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            out_path = f.name
        
        try:
            # Filter to only rows booked on or after 2026-01-03
            main([
                "--input", fixture,
                "--out", out_path,
                "--since", "2026-01-03"
            ])
            
            with open(out_path) as f:
                data = json.load(f)
            
            # Should only have S-2 (booked 2026-01-03), not S-1 (booked 2026-01-02)
            self.assertEqual(len(data["rows"]), 1)
            self.assertEqual(data["rows"][0]["txn_id"], "S-2")
        finally:
            if os.path.exists(out_path):
                os.unlink(out_path)


if __name__ == "__main__":
    unittest.main()
