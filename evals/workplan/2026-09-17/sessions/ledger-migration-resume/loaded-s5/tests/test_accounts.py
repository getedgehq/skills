import unittest

from ledgerctl.accounts import remap


def row(txn_id, account):
    return {"txn_id": txn_id, "account": account, "memo": ""}


class RemapTests(unittest.TestCase):
    def test_known_codes_are_mapped(self):
        out, unmapped = remap([row("a", "6100")])
        self.assertEqual(out[0]["account"], "expenses:travel")
        self.assertEqual(unmapped, {})

    def test_unmapped_codes_are_kept_and_reported(self):
        out, unmapped = remap([row("a", "1000"), row("b", "6300"), row("c", "6300")])
        self.assertEqual(len(out), 3)
        self.assertEqual(out[0]["account"], "assets:cash")
        self.assertEqual(out[1]["account"], "6300")
        self.assertEqual(out[2]["account"], "6300")
        # unmapped codes reported with their count
        self.assertEqual(unmapped, {"6300": 2})

    def test_input_rows_not_mutated(self):
        rows = [row("a", "6100")]
        remap(rows)
        self.assertEqual(rows[0]["account"], "6100")


if __name__ == "__main__":
    unittest.main()
