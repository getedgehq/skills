import os
import tempfile
import unittest

from paystream import bankfile


class CollapseTests(unittest.TestCase):
    def test_collapses_multiple_weeks_per_employee(self):
        # PS-213: one row per employee, not per week
        entries = [
            {"employee_id": "E-1001", "week": "2026-W37", "gross_cents": 10000, "cost_centre": "CC-A"},
            {"employee_id": "E-1001", "week": "2026-W38", "gross_cents": 15000, "cost_centre": "CC-A"},
            {"employee_id": "E-1002", "week": "2026-W37", "gross_cents": 8000, "cost_centre": "CC-B"},
        ]
        collapsed = bankfile.collapse_by_employee(entries)
        self.assertEqual(len(collapsed), 2)
        self.assertEqual(collapsed[0]["employee_id"], "E-1001")
        self.assertEqual(collapsed[0]["gross_cents"], 25000)
        self.assertEqual(collapsed[1]["employee_id"], "E-1002")
        self.assertEqual(collapsed[1]["gross_cents"], 8000)
    
    def test_write_outputs_collapsed_rows(self):
        entries = [
            {"employee_id": "E-1001", "week": "2026-W37", "gross_cents": 10000, "cost_centre": "CC-A"},
            {"employee_id": "E-1001", "week": "2026-W38", "gross_cents": 15000, "cost_centre": "CC-A"},
        ]
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            path = f.name
        
        try:
            n = bankfile.write(entries, path, "TEST001")
            # Should return 1 (one employee, collapsed from 2 weeks)
            self.assertEqual(n, 1)
            
            # Verify file content
            with open(path) as f:
                lines = f.readlines()
            self.assertEqual(len(lines), 2)  # header + 1 data row
            self.assertIn("E-1001", lines[1])
            self.assertIn("25000", lines[1])
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
