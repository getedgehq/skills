"""Integration tests using the real data files."""
import json
import os
import tempfile
import unittest

from ledgerctl.cli import main


class IntegrationTests(unittest.TestCase):
    def test_legacy_2024_file(self):
        """Verify legacy 2024 format still works exactly as before."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            out_path = f.name
        
        try:
            ret = main(['--input', 'data/legacy_2024.csv', '--out', out_path])
            self.assertEqual(ret, 0)
            
            with open(out_path) as f:
                data = json.load(f)
            
            self.assertEqual(len(data['rows']), 3)
            
            # Check first row
            row = data['rows'][0]
            self.assertEqual(row['txn_id'], 'L-2201')
            self.assertEqual(row['account'], 'assets:cash')
            self.assertEqual(row['currency'], 'EUR')
            self.assertEqual(row['amount'], '880.00')
        finally:
            if os.path.exists(out_path):
                os.unlink(out_path)
    
    def test_current_format(self):
        """Verify new format with all edge cases."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            out_path = f.name
        
        try:
            ret = main(['--input', 'data/current.csv', '--out', out_path])
            self.assertEqual(ret, 0)
            
            with open(out_path) as f:
                data = json.load(f)
            
            # Should have 9 rows after deduplication (11 raw - 2 dupes)
            self.assertEqual(len(data['rows']), 9)
            
            # Check deduplication kept the most recent
            t1002 = [r for r in data['rows'] if r['txn_id'] == 'T-1002'][0]
            self.assertEqual(t1002['amount'], '298.40')  # rebooked version
            self.assertEqual(t1002['updated_at'], '2026-08-30T10:00:00')
            
            t1003 = [r for r in data['rows'] if r['txn_id'] == 'T-1003'][0]
            self.assertEqual(t1003['amount'], '9750.00')  # credit note version
            
            # Check parentheses parsed as negative
            t1004 = [r for r in data['rows'] if r['txn_id'] == 'T-1004'][0]
            self.assertEqual(t1004['amount'], '-340.00')
            
            t1007 = [r for r in data['rows'] if r['txn_id'] == 'T-1007'][0]
            self.assertEqual(t1007['amount'], '-112.05')
            
            # Check unmapped codes are kept
            t1005 = [r for r in data['rows'] if r['txn_id'] == 'T-1005'][0]
            self.assertEqual(t1005['account'], '6300')  # unmapped, kept as-is
            
            t1008 = [r for r in data['rows'] if r['txn_id'] == 'T-1008'][0]
            self.assertEqual(t1008['account'], '7100')  # unmapped, kept as-is
        finally:
            if os.path.exists(out_path):
                os.unlink(out_path)
    
    def test_since_filter(self):
        """Verify --since filter works on booked_on date."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            out_path = f.name
        
        try:
            ret = main(['--input', 'data/current.csv', '--out', out_path, '--since', '2026-08-01'])
            self.assertEqual(ret, 0)
            
            with open(out_path) as f:
                data = json.load(f)
            
            # Should only have August transactions
            self.assertEqual(len(data['rows']), 6)
            
            # All dates should be >= 2026-08-01
            for row in data['rows']:
                self.assertGreaterEqual(row['booked_on'], '2026-08-01')
        finally:
            if os.path.exists(out_path):
                os.unlink(out_path)


if __name__ == '__main__':
    unittest.main()
