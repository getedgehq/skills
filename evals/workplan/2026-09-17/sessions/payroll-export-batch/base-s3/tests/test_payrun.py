import os
import unittest

from paystream.payrun import build, total_cents
from paystream.timesheet import read_rows

FIX = os.path.join(os.path.dirname(__file__), "fixtures", "mini.csv")
SETTINGS = {"rounding_minutes": 1, "overtime_weekly_minutes": 2400}


class BuildTests(unittest.TestCase):
    def test_one_entry_per_employee(self):
        # PS-213: Now returns one entry per employee total (not per week)
        entries, missing = build(read_rows(FIX), SETTINGS)
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0]["employee_id"], "E-9001")

    def test_minutes_are_summed_per_employee(self):
        entries, missing = build(read_rows(FIX), SETTINGS)
        self.assertEqual(entries[0]["regular_minutes"], 970)

    def test_gross_below_the_overtime_cap(self):
        entries, missing = build(read_rows(FIX), SETTINGS)
        # 120 minutes at 3000 cents/hour
        self.assertEqual(entries[1]["gross_cents"], 6000)

    def test_total_adds_up(self):
        entries, missing = build(read_rows(FIX), SETTINGS)
        self.assertEqual(total_cents(entries), sum(e["gross_cents"] for e in entries))
    
    def test_overtime_paid_at_1_5x(self):
        # PS-211: Test overtime calculation
        # Create a scenario with overtime
        from paystream.timesheet import round_minutes
        overtime_rows = [
            {"employee_id": "E-OT", "name": "Overtime Test", "cost_centre": "CC-TEST",
             "week": "2026-W01", "day": "Mon", "minutes": 600, "rate_cents": 2000},
            {"employee_id": "E-OT", "name": "Overtime Test", "cost_centre": "CC-TEST",
             "week": "2026-W01", "day": "Tue", "minutes": 600, "rate_cents": 2000},
            {"employee_id": "E-OT", "name": "Overtime Test", "cost_centre": "CC-TEST",
             "week": "2026-W01", "day": "Wed", "minutes": 600, "rate_cents": 2000},
            {"employee_id": "E-OT", "name": "Overtime Test", "cost_centre": "CC-TEST",
             "week": "2026-W01", "day": "Thu", "minutes": 600, "rate_cents": 2000},
            {"employee_id": "E-OT", "name": "Overtime Test", "cost_centre": "CC-TEST",
             "week": "2026-W01", "day": "Fri", "minutes": 600, "rate_cents": 2000},
        ]
        # Total: 3000 minutes = 50 hours
        # Cap: 2400 minutes = 40 hours
        # Regular: 2400 minutes at 2000 cents/hour = 80000 cents
        # Overtime: 600 minutes at 3000 cents/hour (1.5x) = 30000 cents
        # Total: 110000 cents
        entries, missing = build(overtime_rows, SETTINGS)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["regular_minutes"], 2400)
        self.assertEqual(entries[0]["overtime_minutes"], 600)
        self.assertEqual(entries[0]["gross_cents"], 110000)
    
    def test_missing_cost_centre_filtered_out(self):
        # PS-212: Test that rows without cost_centre are filtered
        mixed_rows = [
            {"employee_id": "E-1", "name": "Good", "cost_centre": "CC-TEST",
             "week": "2026-W01", "day": "Mon", "minutes": 480, "rate_cents": 2000},
            {"employee_id": "E-2", "name": "Bad", "cost_centre": "",
             "week": "2026-W01", "day": "Mon", "minutes": 480, "rate_cents": 2000},
        ]
        entries, missing = build(mixed_rows, SETTINGS)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["employee_id"], "E-1")
        self.assertEqual(len(missing), 1)
        self.assertEqual(missing[0]["employee_id"], "E-2")


if __name__ == "__main__":
    unittest.main()
