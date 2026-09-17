import os
import unittest

from paystream.timesheet import read_rows, round_minutes

FIX = os.path.join(os.path.dirname(__file__), "fixtures", "mini.csv")


class RoundTests(unittest.TestCase):
    def test_rounds_down_below_the_halfway_point(self):
        self.assertEqual(round_minutes(484, 10), 480)

    def test_rounds_up_above_the_halfway_point(self):
        self.assertEqual(round_minutes(486, 10), 490)

    def test_halfway_point_rounds_up_in_employees_favor(self):
        # PS-210: 2h05 (125 min) and 2h15 (135 min) both at 10-min rounding
        self.assertEqual(round_minutes(125, 10), 130)  # 125 is exactly halfway between 120 and 130
        self.assertEqual(round_minutes(135, 10), 140)  # 135 is exactly halfway between 130 and 140
        # Generic halfway point
        self.assertEqual(round_minutes(485, 10), 490)  # exactly halfway, rounds up

    def test_exact_multiple_is_left_alone(self):
        self.assertEqual(round_minutes(480, 10), 480)
        self.assertEqual(round_minutes(2400, 15), 2400)

    def test_step_of_one_is_a_no_op(self):
        self.assertEqual(round_minutes(487, 1), 487)


class ReadTests(unittest.TestCase):
    def test_reads_every_row(self):
        rows = read_rows(FIX)
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0]["employee_id"], "E-9001")
        self.assertEqual(rows[2]["minutes"], 120)


if __name__ == "__main__":
    unittest.main()
