import os
import unittest

from paystream.payrun import build, total_cents
from paystream.timesheet import read_rows

FIX = os.path.join(os.path.dirname(__file__), "fixtures", "mini.csv")
FIX_OT = os.path.join(os.path.dirname(__file__), "fixtures", "overtime.csv")
SETTINGS = {"rounding_minutes": 1, "overtime_weekly_minutes": 2400}


class BuildTests(unittest.TestCase):
    def test_one_entry_per_employee_week(self):
        entries, skipped = build(read_rows(FIX), SETTINGS)
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0]["employee_id"], "E-9001")
        self.assertEqual(entries[0]["week"], "2026-W01")

    def test_minutes_are_summed_per_week(self):
        entries, skipped = build(read_rows(FIX), SETTINGS)
        self.assertEqual(entries[0]["minutes"], 970)

    def test_gross_below_the_overtime_cap(self):
        entries, skipped = build(read_rows(FIX), SETTINGS)
        # 120 minutes at 3000 cents/hour
        self.assertEqual(entries[1]["gross_cents"], 6000)

    def test_total_adds_up(self):
        entries, skipped = build(read_rows(FIX), SETTINGS)
        self.assertEqual(total_cents(entries), sum(e["gross_cents"] for e in entries))
    
    def test_overtime_paid_at_time_and_half(self):
        # PS-211: overtime should be 1.5x
        entries, skipped = build(read_rows(FIX_OT), SETTINGS)
        # 2520 minutes total, 2400 regular + 120 overtime
        # Regular: 2400 min * 2000 cents/hour / 60 = 80000 cents
        # Overtime: 120 min * 2000 * 1.5 / 60 = 6000 cents
        # Total: 86000 cents
        self.assertEqual(entries[0]["gross_cents"], 86000)
        self.assertEqual(entries[0]["regular_minutes"], 2400)
        self.assertEqual(entries[0]["overtime_minutes"], 120)
    
    def test_rows_without_cost_centre_are_skipped(self):
        # PS-212: rows with empty cost_centre should be filtered out
        entries, skipped = build(read_rows(FIX_OT), SETTINGS)
        self.assertEqual(len(entries), 1)
        self.assertEqual(len(skipped), 1)
        self.assertEqual(skipped[0]["employee_id"], "E-9999")


if __name__ == "__main__":
    unittest.main()
