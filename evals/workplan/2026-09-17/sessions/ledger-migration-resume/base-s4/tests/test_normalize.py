import os
import unittest
from decimal import Decimal

from ledgerctl.normalize import dedupe, parse_amount, parse_currency, read_rows, filter_since

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

    def test_parentheses_parse_as_negative(self):
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

    def test_dedupe_keeps_most_recent_updated_at(self):
        rows = dedupe(read_rows(FIX))
        s1 = [r for r in rows if r["txn_id"] == "S-1"][0]
        # Should keep the 2026-01-04 version (corrected), not the 2026-01-02 one
        self.assertEqual(s1["updated_at"], "2026-01-04T09:00:00")
        self.assertEqual(s1["amount"], Decimal("11.00"))
        self.assertEqual(s1["memo"], "one corrected")


class FilterTests(unittest.TestCase):
    def test_filter_since_keeps_matching_and_later(self):
        rows = [
            {"txn_id": "a", "booked_on": "2026-01-01"},
            {"txn_id": "b", "booked_on": "2026-01-05"},
            {"txn_id": "c", "booked_on": "2026-01-10"},
        ]
        filtered = filter_since(rows, "2026-01-05")
        self.assertEqual(len(filtered), 2)
        self.assertEqual([r["txn_id"] for r in filtered], ["b", "c"])

    def test_filter_since_none_returns_all(self):
        rows = [{"txn_id": "a", "booked_on": "2026-01-01"}]
        filtered = filter_since(rows, None)
        self.assertEqual(len(filtered), 1)


if __name__ == "__main__":
    unittest.main()
