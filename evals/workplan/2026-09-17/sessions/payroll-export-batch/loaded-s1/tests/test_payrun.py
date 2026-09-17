import os
import unittest

from paystream.payrun import build, total_cents
from paystream.timesheet import read_rows

FIX = os.path.join(os.path.dirname(__file__), "fixtures", "mini.csv")
SETTINGS = {"rounding_minutes": 1, "overtime_weekly_minutes": 2400}


class BuildTests(unittest.TestCase):
    def test_one_entry_per_employee_week(self):
        entries, filtered = build(read_rows(FIX), SETTINGS)
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0]["employee_id"], "E-9001")
        self.assertEqual(entries[0]["week"], "2026-W01")

    def test_minutes_are_summed_per_week(self):
        entries, filtered = build(read_rows(FIX), SETTINGS)
        self.assertEqual(entries[0]["minutes"], 970)

    def test_gross_below_the_overtime_cap(self):
        entries, filtered = build(read_rows(FIX), SETTINGS)
        # 120 minutes at 3000 cents/hour
        self.assertEqual(entries[1]["gross_cents"], 6000)

    def test_overtime_paid_at_1_5x(self):
        # PS-211: Overtime over 40h/week paid at 1.5x
        rows = [
            {"employee_id": "E-OT", "name": "Test OT", "cost_centre": "CC-1",
             "week": "2026-W01", "day": "Mon", "minutes": 2500, "rate_cents": 3000}
        ]
        entries, filtered = build(rows, SETTINGS)
        # 2400 regular @ 3000 cents/hr = 2400 * 3000 / 60 = 120000
        # 100 overtime @ 4500 cents/hr = 100 * 4500 / 60 = 7500
        # Total = 127500
        self.assertEqual(entries[0]["regular_minutes"], 2400)
        self.assertEqual(entries[0]["overtime_minutes"], 100)
        self.assertEqual(entries[0]["gross_cents"], 127500)

    def test_filters_rows_with_empty_cost_centre(self):
        # PS-212: Rows with empty cost_centre are excluded
        rows = [
            {"employee_id": "E-1", "name": "Good", "cost_centre": "CC-1",
             "week": "2026-W01", "day": "Mon", "minutes": 100, "rate_cents": 2000},
            {"employee_id": "E-2", "name": "Bad", "cost_centre": "",
             "week": "2026-W01", "day": "Tue", "minutes": 200, "rate_cents": 2000},
        ]
        entries, filtered = build(rows, SETTINGS)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["employee_id"], "E-1")
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["employee_id"], "E-2")

    def test_total_adds_up(self):
        entries, filtered = build(read_rows(FIX), SETTINGS)
        self.assertEqual(total_cents(entries), sum(e["gross_cents"] for e in entries))


if __name__ == "__main__":
    unittest.main()
