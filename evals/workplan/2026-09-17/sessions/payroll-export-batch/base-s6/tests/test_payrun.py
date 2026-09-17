import os
import unittest

from paystream.payrun import build, total_cents
from paystream.timesheet import read_rows

FIX = os.path.join(os.path.dirname(__file__), "fixtures", "mini.csv")
FIX_OT = os.path.join(os.path.dirname(__file__), "fixtures", "overtime.csv")
FIX_NO_CC = os.path.join(os.path.dirname(__file__), "fixtures", "nocostcentre.csv")
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


class OvertimeTests(unittest.TestCase):
    """PS-211: Overtime should be paid at 1.5x after 40h/week"""
    
    def test_overtime_kicks_in_after_cap(self):
        # 2520 minutes = 42h, so 2h overtime at 1.5x
        entries, skipped = build(read_rows(FIX_OT), SETTINGS)
        self.assertEqual(len(entries), 1)
        e = entries[0]
        self.assertEqual(e["minutes"], 2520)
        self.assertEqual(e["regular_minutes"], 2400)
        self.assertEqual(e["overtime_minutes"], 120)
        
        # Regular: 2400 min * 2000 cents/60 = 80000
        # Overtime: 120 min * 2000 cents * 1.5 / 60 = 6000
        # Total: 86000
        self.assertEqual(e["gross_cents"], 86000)
    
    def test_no_overtime_under_cap(self):
        entries, skipped = build(read_rows(FIX), SETTINGS)
        # Both should be under the cap
        for e in entries:
            self.assertEqual(e["overtime_minutes"], 0)


class CostCentreTests(unittest.TestCase):
    """PS-212: Rows with no cost centre should be filtered out and reported"""
    
    def test_empty_cost_centre_is_skipped(self):
        entries, skipped = build(read_rows(FIX_NO_CC), SETTINGS)
        # Should have 1 entry (E-OK01) and 1 skipped (E-BAD01)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["employee_id"], "E-OK01")
        self.assertEqual(len(skipped), 1)
        self.assertEqual(skipped[0]["employee_id"], "E-BAD01")
    
    def test_skipped_entries_have_details(self):
        entries, skipped = build(read_rows(FIX_NO_CC), SETTINGS)
        self.assertEqual(skipped[0]["name"], "No CC")
        self.assertEqual(skipped[0]["week"], "2026-W01")
        self.assertEqual(skipped[0]["day"], "Mon")


if __name__ == "__main__":
    unittest.main()
