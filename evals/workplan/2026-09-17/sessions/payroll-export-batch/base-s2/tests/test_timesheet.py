import os
import unittest

from paystream.timesheet import read_rows, round_minutes

FIX = os.path.join(os.path.dirname(__file__), "fixtures", "mini.csv")


class RoundTests(unittest.TestCase):
    def test_rounds_down_below_the_halfway_point(self):
        self.assertEqual(round_minutes(484, 10), 480)

    def test_rounds_up_above_the_halfway_point(self):
        self.assertEqual(round_minutes(486, 10), 490)
    
    def test_exact_halfway_rounds_up_in_employee_favour(self):
        # PS-210: Union agreement says halfway points go up
        self.assertEqual(round_minutes(485, 10), 490)
        self.assertEqual(round_minutes(125, 10), 130)
        self.assertEqual(round_minutes(135, 10), 140)

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
