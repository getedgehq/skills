import unittest

from ledgerctl.cli import apply_since_filter


class SinceFilterTests(unittest.TestCase):
    def test_no_filter_returns_all_rows(self):
        rows = [
            {"booked_on": "2026-01-01"},
            {"booked_on": "2026-01-15"},
        ]
        result = apply_since_filter(rows, None)
        self.assertEqual(len(result), 2)

    def test_filters_by_booked_on_date(self):
        rows = [
            {"txn_id": "a", "booked_on": "2026-01-05"},
            {"txn_id": "b", "booked_on": "2026-01-10"},
            {"txn_id": "c", "booked_on": "2026-01-15"},
        ]
        result = apply_since_filter(rows, "2026-01-10")
        self.assertEqual(len(result), 2)
        self.assertEqual([r["txn_id"] for r in result], ["b", "c"])

    def test_inclusive_of_since_date(self):
        rows = [
            {"txn_id": "a", "booked_on": "2026-01-09"},
            {"txn_id": "b", "booked_on": "2026-01-10"},
        ]
        result = apply_since_filter(rows, "2026-01-10")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["txn_id"], "b")


if __name__ == "__main__":
    unittest.main()
