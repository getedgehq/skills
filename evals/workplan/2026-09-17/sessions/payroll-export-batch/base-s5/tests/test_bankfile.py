import os
import tempfile
import unittest

from paystream import bankfile


class AggregationTests(unittest.TestCase):
    """Test PS-213: one row per employee (not per week)"""
    
    def test_aggregates_multiple_weeks_per_employee(self):
        entries = [
            {
                "employee_id": "E-001",
                "week": "2026-W37",
                "gross_cents": 10000,
                "cost_centre": "CC-TEST",
            },
            {
                "employee_id": "E-001",
                "week": "2026-W38",
                "gross_cents": 12000,
                "cost_centre": "CC-TEST",
            },
            {
                "employee_id": "E-002",
                "week": "2026-W37",
                "gross_cents": 8000,
                "cost_centre": "CC-TEST",
            },
        ]
        
        aggregated = bankfile.aggregate_by_employee(entries)
        
        self.assertEqual(len(aggregated), 2)
        self.assertEqual(aggregated[0]["employee_id"], "E-001")
        self.assertEqual(aggregated[0]["gross_cents"], 22000)  # 10000 + 12000
        self.assertEqual(aggregated[1]["employee_id"], "E-002")
        self.assertEqual(aggregated[1]["gross_cents"], 8000)
    
    def test_preserves_employee_order(self):
        entries = [
            {"employee_id": "E-003", "week": "2026-W37", "gross_cents": 1000, "cost_centre": "CC-A"},
            {"employee_id": "E-001", "week": "2026-W37", "gross_cents": 2000, "cost_centre": "CC-B"},
            {"employee_id": "E-002", "week": "2026-W37", "gross_cents": 3000, "cost_centre": "CC-C"},
            {"employee_id": "E-001", "week": "2026-W38", "gross_cents": 1500, "cost_centre": "CC-B"},
        ]
        
        aggregated = bankfile.aggregate_by_employee(entries)
        
        self.assertEqual(len(aggregated), 3)
        self.assertEqual(aggregated[0]["employee_id"], "E-003")
        self.assertEqual(aggregated[1]["employee_id"], "E-001")
        self.assertEqual(aggregated[2]["employee_id"], "E-002")


class WriteTests(unittest.TestCase):
    
    def test_write_returns_number_of_employees(self):
        entries = [
            {"employee_id": "E-001", "week": "2026-W37", "gross_cents": 10000, "cost_centre": "CC-TEST"},
            {"employee_id": "E-001", "week": "2026-W38", "gross_cents": 12000, "cost_centre": "CC-TEST"},
            {"employee_id": "E-002", "week": "2026-W37", "gross_cents": 8000, "cost_centre": "CC-TEST"},
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            path = f.name
        
        try:
            n = bankfile.write(entries, path, "TEST-RUN")
            self.assertEqual(n, 2)  # 2 unique employees
            
            # Verify file contents
            with open(path, 'r') as f:
                lines = f.readlines()
                self.assertEqual(len(lines), 3)  # header + 2 employees
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
