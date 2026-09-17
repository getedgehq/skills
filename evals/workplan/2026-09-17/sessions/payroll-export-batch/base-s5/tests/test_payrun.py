import os
import tempfile
import unittest

from paystream.payrun import build, total_cents
from paystream.timesheet import read_rows, round_minutes

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


class OvertimeTests(unittest.TestCase):
    """Test PS-211: overtime at 1.5x"""
    
    def test_overtime_paid_at_one_point_five_rate(self):
        # 2500 minutes (41h 40m) at 3000 cents/hour
        # Regular: 2400 min * 3000/60 = 120,000
        # Overtime: 100 min * 3000 * 1.5 / 60 = 7,500
        # Total: 127,500
        test_rows = [
            {
                "employee_id": "E-OT",
                "name": "Overtime Test",
                "cost_centre": "CC-TEST",
                "week": "2026-W37",
                "day": "Mon",
                "minutes": 2500,
                "rate_cents": 3000
            }
        ]
        entries, excluded = build(test_rows, SETTINGS)
        self.assertEqual(entries[0]["regular_minutes"], 2400)
        self.assertEqual(entries[0]["overtime_minutes"], 100)
        self.assertEqual(entries[0]["gross_cents"], 127500)
    
    def test_no_overtime_below_cap(self):
        test_rows = [
            {
                "employee_id": "E-REG",
                "name": "Regular Test",
                "cost_centre": "CC-TEST",
                "week": "2026-W37",
                "day": "Mon",
                "minutes": 2400,
                "rate_cents": 3000
            }
        ]
        entries, excluded = build(test_rows, SETTINGS)
        self.assertEqual(entries[0]["regular_minutes"], 2400)
        self.assertEqual(entries[0]["overtime_minutes"], 0)
        self.assertEqual(entries[0]["gross_cents"], 120000)


class CostCentreFilterTests(unittest.TestCase):
    """Test PS-212: rows with missing cost_centre are excluded"""
    
    def test_empty_cost_centre_rows_excluded(self):
        test_rows = [
            {
                "employee_id": "E-VALID",
                "name": "Valid",
                "cost_centre": "CC-TEST",
                "week": "2026-W37",
                "day": "Mon",
                "minutes": 480,
                "rate_cents": 2400
            },
            {
                "employee_id": "E-INVALID",
                "name": "Invalid",
                "cost_centre": "",
                "week": "2026-W37",
                "day": "Mon",
                "minutes": 480,
                "rate_cents": 2400
            }
        ]
        entries, excluded = build(test_rows, SETTINGS)
        self.assertEqual(len(entries), 1)
        self.assertEqual(len(excluded), 1)
        self.assertEqual(entries[0]["employee_id"], "E-VALID")
        self.assertEqual(excluded[0]["employee_id"], "E-INVALID")


class RoundingTests(unittest.TestCase):
    """Test PS-210: halfway rounding in employee's favour"""
    
    def test_halfway_rounds_up(self):
        # With step 10: 125 (2h05) should round to 130 (2h10)
        self.assertEqual(round_minutes(125, 10), 130)
        self.assertEqual(round_minutes(135, 10), 140)
        self.assertEqual(round_minutes(485, 10), 490)
    
    def test_below_halfway_rounds_down(self):
        self.assertEqual(round_minutes(124, 10), 120)
        self.assertEqual(round_minutes(484, 10), 480)
    
    def test_above_halfway_rounds_up(self):
        self.assertEqual(round_minutes(126, 10), 130)
        self.assertEqual(round_minutes(486, 10), 490)


if __name__ == "__main__":
    unittest.main()
