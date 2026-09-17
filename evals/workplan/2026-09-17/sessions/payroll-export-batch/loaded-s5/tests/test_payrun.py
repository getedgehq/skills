import os
import unittest

from paystream.payrun import build, total_cents
from paystream.timesheet import read_rows

FIX = os.path.join(os.path.dirname(__file__), "fixtures", "mini.csv")
FIX_EMPTY = os.path.join(os.path.dirname(__file__), "fixtures", "with_empty_cost_centre.csv")
FIX_OVERTIME = os.path.join(os.path.dirname(__file__), "fixtures", "overtime.csv")
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

    def test_total_adds_up(self):
        entries, excluded = build(read_rows(FIX), SETTINGS)
        self.assertEqual(total_cents(entries), sum(e["gross_cents"] for e in entries))
    
    def test_excludes_empty_cost_centre(self):
        entries, excluded = build(read_rows(FIX_EMPTY), SETTINGS)
        self.assertEqual(len(entries), 1)
        self.assertEqual(len(excluded), 1)
        self.assertEqual(entries[0]["employee_id"], "E-1001")
        self.assertEqual(excluded[0]["employee_id"], "E-1002")
    
    def test_overtime_paid_at_1_5x(self):
        entries, excluded = build(read_rows(FIX_OVERTIME), SETTINGS)
        self.assertEqual(len(entries), 1)
        # 2700 minutes total = 2400 regular + 300 overtime
        # 2400 min at 3000 cents/hr = 2400 * 3000 / 60 = 120000
        # 300 min at 4500 cents/hr (1.5x) = 300 * 4500 / 60 = 22500
        # Total = 142500
        self.assertEqual(entries[0]["regular_minutes"], 2400)
        self.assertEqual(entries[0]["overtime_minutes"], 300)
        self.assertEqual(entries[0]["gross_cents"], 142500)


if __name__ == "__main__":
    unittest.main()
