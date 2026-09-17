import os
import tempfile
import unittest

from ledgerctl.cli import filter_since, main


class FilterTests(unittest.TestCase):
    def test_no_filter_returns_all(self):
        rows = [
            {'txn_id': '1', 'booked_on': '2026-07-01'},
            {'txn_id': '2', 'booked_on': '2026-08-01'},
        ]
        result = filter_since(rows, None)
        self.assertEqual(len(result), 2)

    def test_filter_excludes_before_date(self):
        rows = [
            {'txn_id': '1', 'booked_on': '2026-07-01'},
            {'txn_id': '2', 'booked_on': '2026-08-01'},
            {'txn_id': '3', 'booked_on': '2026-08-15'},
        ]
        result = filter_since(rows, '2026-08-01')
        self.assertEqual(len(result), 2)
        self.assertEqual([r['txn_id'] for r in result], ['2', '3'])

    def test_filter_includes_exact_date(self):
        rows = [
            {'txn_id': '1', 'booked_on': '2026-07-31'},
            {'txn_id': '2', 'booked_on': '2026-08-01'},
        ]
        result = filter_since(rows, '2026-08-01')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['txn_id'], '2')


class IntegrationTests(unittest.TestCase):
    def test_current_csv_with_since_filter(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            out_path = f.name
        
        try:
            input_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'current.csv')
            ret = main(['--input', input_path, '--out', out_path, '--since', '2026-08-01'])
            self.assertEqual(ret, 0)
            
            # Verify file was created
            self.assertTrue(os.path.exists(out_path))
            
            # Verify content
            import json
            with open(out_path) as fh:
                data = json.load(fh)
                self.assertEqual(len(data['rows']), 6)
                # All rows should be >= 2026-08-01
                for row in data['rows']:
                    self.assertGreaterEqual(row['booked_on'], '2026-08-01')
        finally:
            if os.path.exists(out_path):
                os.unlink(out_path)


if __name__ == '__main__':
    unittest.main()
