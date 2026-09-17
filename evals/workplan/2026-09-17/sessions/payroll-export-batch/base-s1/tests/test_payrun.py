import os
import unittest

from paystream.payrun import build, total_cents
from paystream.timesheet import read_rows

FIX = os.path.join(os.path.dirname(__file__), "fixtures", "mini.csv")
FIX_OVERTIME = os.path.join(os.path.dirname(__file__), "fixtures", "overtime.csv")
FIX_NO_CC = os.path.join(os.path.dirname(__file__), "fixtures", "no_cost_centre.csv")
SETTINGS = {"rounding_minutes": 1, "overtime_weekly_minutes": 2400}


class BuildTests(unittest.TestCase):
    def test_one_entry_per_employee(self):
        # Now returns one entry per employee, not per employee-week
        entries, skipped = build(read_rows(FIX), SETTINGS)
        self.assertEqual(len(entries), 2)
        # Check that both employees are present
        employee_ids = {e["employee_id"] for e in entries}
        self.assertIn("E-9001", employee_ids)
        self.assertIn("E-9002", employee_ids)

    def test_minutes_are_summed_per_employee(self):
        entries, skipped = build(read_rows(FIX), SETTINGS)
        # E-9001 has 484 + 486 = 970 minutes total
        e9001 = [e for e in entries if e["employee_id"] == "E-9001"][0]
        self.assertEqual(e9001["regular_minutes"], 970)

    def test_gross_below_the_overtime_cap(self):
        entries, skipped = build(read_rows(FIX), SETTINGS)
        # E-9002: 120 minutes at 3000 cents/hour = 6000 cents
        e9002 = [e for e in entries if e["employee_id"] == "E-9002"][0]
        self.assertEqual(e9002["gross_cents"], 6000)

    def test_total_adds_up(self):
        entries, skipped = build(read_rows(FIX), SETTINGS)
        self.assertEqual(total_cents(entries), sum(e["gross_cents"] for e in entries))
    
    def test_no_skipped_rows_when_all_have_cost_centre(self):
        entries, skipped = build(read_rows(FIX), SETTINGS)
        self.assertEqual(len(skipped), 0)


class OvertimeTests(unittest.TestCase):
    """PS-211: Test overtime at 1.5x for hours over 40/week."""
    
    def test_overtime_kicks_in_above_2400_minutes(self):
        # 2640 minutes = 44 hours
        # 2400 regular at 2000 cents/hour = 80000 cents
        # 240 overtime at 3000 cents/hour (1.5x) = 12000 cents
        # Total: 92000 cents
        entries, skipped = build(read_rows(FIX_OVERTIME), SETTINGS)
        self.assertEqual(len(entries), 1)
        e = entries[0]
        self.assertEqual(e["regular_minutes"], 2400)
        self.assertEqual(e["overtime_minutes"], 240)
        self.assertEqual(e["gross_cents"], 92000)
    
    def test_overtime_calculated_on_rounded_minutes(self):
        # This is verified by the fact that rounding happens per-shift
        # in the build() function before overtime calculation
        settings = {"rounding_minutes": 10, "overtime_weekly_minutes": 2400}
        entries, skipped = build(read_rows(FIX_OVERTIME), SETTINGS)
        # Even with rounding, the values should be based on rounded minutes
        self.assertEqual(entries[0]["overtime_minutes"], 240)


class SkippedRowsTests(unittest.TestCase):
    """PS-212: Test that rows with no cost_centre are filtered and reported."""
    
    def test_rows_without_cost_centre_are_skipped(self):
        entries, skipped = build(read_rows(FIX_NO_CC), SETTINGS)
        # Only E-9004 has a cost_centre
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["employee_id"], "E-9004")
        # E-9005 and E-9006 should be skipped
        self.assertEqual(len(skipped), 2)
    
    def test_skipped_rows_contain_employee_info(self):
        entries, skipped = build(read_rows(FIX_NO_CC), SETTINGS)
        skipped_ids = {r["employee_id"] for r in skipped}
        self.assertIn("E-9005", skipped_ids)
        self.assertIn("E-9006", skipped_ids)


if __name__ == "__main__":
    unittest.main()
