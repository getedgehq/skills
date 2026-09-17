import os
import unittest
from decimal import Decimal

from ledgerctl.normalize import dedupe, parse_amount, parse_currency, read_rows

FIX = os.path.join(os.path.dirname(__file__), "fixtures", "simple.csv")


class ParseTests(unittest.TestCase):
    def test_plain_amount(self):
        self.assertEqual(parse_amount("1234.50"), Decimal("1234.50"))

    def test_currency_prefix_stripped(self):
        self.assertEqual(parse_amount("EUR 1234.50"), Decimal("1234.50"))

    def test_thousands_separator(self):
        self.assertEqual(parse_amount("EUR 1,234.50"), Decimal("1234.50"))

    def test_currency_uppercased(self):
        self.assertEqual(parse_currency("eur"), "EUR")

    def test_parentheses_are_negative(self):
        self.assertEqual(parse_amount("(EUR 340.00)"), Decimal("-340.00"))
        self.assertEqual(parse_amount("(112.05)"), Decimal("-112.05"))


class ReadTests(unittest.TestCase):
    def test_reads_every_row(self):
        rows = read_rows(FIX)
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0]["currency"], "EUR")
        self.assertEqual(rows[1]["amount"], Decimal("20.00"))

    def test_dedupe_collapses_repeated_ids(self):
        rows = dedupe(read_rows(FIX))
        self.assertEqual(len(rows), 2)
        self.assertEqual(sorted(r["txn_id"] for r in rows), ["S-1", "S-2"])

    def test_dedupe_keeps_most_recently_updated(self):
        rows = [
            {"txn_id": "T1", "updated_at": "2026-01-02T09:00:00", "memo": "old"},
            {"txn_id": "T2", "updated_at": "2026-01-03T09:00:00", "memo": "ok"},
            {"txn_id": "T1", "updated_at": "2026-01-04T09:00:00", "memo": "new"},
        ]
        result = dedupe(rows)
        self.assertEqual(len(result), 2)
        t1 = [r for r in result if r["txn_id"] == "T1"][0]
        self.assertEqual(t1["memo"], "new")


if __name__ == "__main__":
    unittest.main()
