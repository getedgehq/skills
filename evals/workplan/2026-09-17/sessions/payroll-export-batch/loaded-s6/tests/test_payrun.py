import os
import unittest

from paystream.payrun import build, total_cents
from paystream.timesheet import read_rows

FIX = os.path.join(os.path.dirname(__file__), "fixtures", "mini.csv")
SETTINGS = {"rounding_minutes": 1, "overtime_weekly_minutes": 2400}


class BuildTests(unittest.TestCase):
    def test_one_entry_per_employee_week(self):
        entries, excluded = build(read_rows(FIX), SETTINGS)
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0]["employee_id"], "E-9001")
        self.assertEqual(entries[0]["week"], "2026-W01")

    def test_minutes_are_summed_per_week(self):
        entries, excluded = build(read_rows(FIX), SETTINGS)
        self.assertEqual(entries[0]["minutes"], 970)

    def test_gross_below_the_overtime_cap(self):
        entries, excluded = build(read_rows(FIX), SETTINGS)
        # 120 minutes at 3000 cents/hour
        self.assertEqual(entries[1]["gross_cents"], 6000)

    def test_overtime_paid_at_1_5x(self):
        # PS-211: overtime (>40h/week = 2400 min) paid at 1.5x
        rows = [
            {"employee_id": "E-OT", "name": "Overtime Test", "cost_centre": "CC-TEST",
             "week": "2026-W01", "day": "Mon", "minutes": 2880, "rate_cents": 3000}
        ]
        entries, excluded = build(rows, SETTINGS)
        # 2880 minutes = 2400 regular + 480 overtime
        # Regular: 2400 * 3000 / 60 = 120000 cents
        # Overtime: 480 * 3000 * 1.5 / 60 = 36000 cents
        # Total: 156000 cents
        self.assertEqual(entries[0]["regular_minutes"], 2400)
        self.assertEqual(entries[0]["overtime_minutes"], 480)
        self.assertEqual(entries[0]["gross_cents"], 156000)

    def test_missing_cost_centre_excluded(self):
        # PS-212: rows with empty cost_centre should be excluded and reported
        rows = [
            {"employee_id": "E-GOOD", "name": "Good Employee", "cost_centre": "CC-TEST",
             "week": "2026-W01", "day": "Mon", "minutes": 480, "rate_cents": 2000},
            {"employee_id": "E-BAD", "name": "Missing CC", "cost_centre": "",
             "week": "2026-W01", "day": "Tue", "minutes": 490, "rate_cents": 2000},
        ]
        entries, excluded = build(rows, SETTINGS)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["employee_id"], "E-GOOD")
        self.assertEqual(len(excluded), 1)
        self.assertEqual(excluded[0]["employee_id"], "E-BAD")
        self.assertEqual(excluded[0]["minutes"], 490)

    def test_total_adds_up(self):
        entries, excluded = build(read_rows(FIX), SETTINGS)
        self.assertEqual(total_cents(entries), sum(e["gross_cents"] for e in entries))


if __name__ == "__main__":
    unittest.main()
