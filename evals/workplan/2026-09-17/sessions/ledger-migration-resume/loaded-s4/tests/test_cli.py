import json
import os
import tempfile
import unittest

from ledgerctl.cli import filter_since, main


class FilterSinceTests(unittest.TestCase):
    def test_no_filter_returns_all(self):
        rows = [
            {"booked_on": "2026-01-01"},
            {"booked_on": "2026-02-01"},
        ]
        result = filter_since(rows, None)
        self.assertEqual(len(result), 2)

    def test_filters_before_date(self):
        rows = [
            {"booked_on": "2026-01-15"},
            {"booked_on": "2026-02-01"},
            {"booked_on": "2026-02-15"},
        ]
        result = filter_since(rows, "2026-02-01")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["booked_on"], "2026-02-01")
        self.assertEqual(result[1]["booked_on"], "2026-02-15")


class IntegrationTests(unittest.TestCase):
    def test_current_csv_pipeline(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            outpath = f.name
        try:
            result = main(["--input", "data/current.csv", "--out", outpath])
            self.assertEqual(result, 0)
            
            with open(outpath) as f:
                data = json.load(f)
            
            # Should have 9 rows after deduplication
            self.assertEqual(len(data["rows"]), 9)
            
            # Check negatives parsed correctly
            negatives = [r for r in data["rows"] if float(r["amount"]) < 0]
            self.assertEqual(len(negatives), 2)
            
        finally:
            if os.path.exists(outpath):
                os.unlink(outpath)

    def test_legacy_csv_still_works(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            outpath = f.name
        try:
            result = main(["--input", "data/legacy_2024.csv", "--out", outpath])
            self.assertEqual(result, 0)
            
            with open(outpath) as f:
                data = json.load(f)
            
            self.assertEqual(len(data["rows"]), 3)
            
        finally:
            if os.path.exists(outpath):
                os.unlink(outpath)

    def test_since_filter(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            outpath = f.name
        try:
            result = main([
                "--input", "data/current.csv",
                "--out", outpath,
                "--since", "2026-08-01"
            ])
            self.assertEqual(result, 0)
            
            with open(outpath) as f:
                data = json.load(f)
            
            # Should have fewer rows
            self.assertLess(len(data["rows"]), 9)
            
            # All should be >= 2026-08-01
            for row in data["rows"]:
                self.assertGreaterEqual(row["booked_on"], "2026-08-01")
            
        finally:
            if os.path.exists(outpath):
                os.unlink(outpath)


if __name__ == "__main__":
    unittest.main()
