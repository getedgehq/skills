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

    def test_total_adds_up(self):
        entries, excluded = build(read_rows(FIX), SETTINGS)
        self.assertEqual(total_cents(entries), sum(e["gross_cents"] for e in entries))


if __name__ == "__main__":
    unittest.main()


class OvertimeTests(unittest.TestCase):
    """PS-211: Overtime calculation at 1.5x rate."""
    
    def test_overtime_kicks_in_after_40_hours(self):
        fix = os.path.join(os.path.dirname(__file__), "fixtures", "overtime.csv")
        settings = {"rounding_minutes": 1, "overtime_weekly_minutes": 2400}
        entries, excluded = build(read_rows(fix), settings)
        
        # 2700 minutes total: 2400 regular + 300 overtime
        self.assertEqual(entries[0]["regular_minutes"], 2400)
        self.assertEqual(entries[0]["overtime_minutes"], 300)
        
        # Gross = (2400 * 2000 / 60) + (300 * 2000 * 1.5 / 60)
        #       = 80000 + 15000 = 95000 cents
        self.assertEqual(entries[0]["gross_cents"], 95000)


class ExcludedRowsTests(unittest.TestCase):
    """PS-212: Rows with no cost centre should be excluded and reported."""
    
    def test_missing_cost_centre_rows_are_excluded(self):
        fix = os.path.join(os.path.dirname(__file__), "fixtures", "missing_cost_centre.csv")
        settings = {"rounding_minutes": 1, "overtime_weekly_minutes": 2400}
        entries, excluded = build(read_rows(fix), settings)
        
        # Only E-9001 should be in entries
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["employee_id"], "E-9001")
        
        # E-9002 rows should be excluded
        self.assertEqual(len(excluded), 2)
        self.assertEqual(excluded[0]["employee_id"], "E-9002")
        self.assertEqual(excluded[1]["employee_id"], "E-9002")
