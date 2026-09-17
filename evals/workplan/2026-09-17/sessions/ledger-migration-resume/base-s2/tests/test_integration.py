"""Integration tests for the full pipeline."""
import json
import os
import tempfile
import unittest

from ledgerctl.cli import main


class IntegrationTests(unittest.TestCase):
    def test_legacy_csv_still_works(self):
        """Verify legacy_2024.csv still processes correctly."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as out:
            out_path = out.name
        
        try:
            main(['--input', 'data/legacy_2024.csv', '--out', out_path])
            
            with open(out_path) as f:
                data = json.load(f)
            
            rows = data['rows']
            self.assertEqual(len(rows), 3)
            
            # Check that accounts are remapped
            accounts = [r['account'] for r in rows]
            self.assertIn('assets:cash', accounts)
            self.assertIn('expenses:cogs', accounts)
            self.assertIn('income:sales', accounts)
            
            # Check currencies are uppercased
            for r in rows:
                self.assertEqual(r['currency'], 'EUR')
        finally:
            if os.path.exists(out_path):
                os.unlink(out_path)
    
    def test_current_csv_with_all_features(self):
        """Verify current.csv processes with deduplication, negatives, etc."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as out:
            out_path = out.name
        
        try:
            result = main(['--input', 'data/current.csv', '--out', out_path])
            
            with open(out_path) as f:
                data = json.load(f)
            
            rows = data['rows']
            
            # Should have 9 unique transactions after deduplication
            self.assertEqual(len(rows), 9)
            
            # Check deduplication kept most recent
            t1002 = [r for r in rows if r['txn_id'] == 'T-1002'][0]
            self.assertEqual(t1002['updated_at'], '2026-08-30T10:00:00')
            self.assertEqual(t1002['amount'], '298.40')
            
            t1003 = [r for r in rows if r['txn_id'] == 'T-1003'][0]
            self.assertEqual(t1003['updated_at'], '2026-08-12T16:20:00')
            self.assertEqual(t1003['amount'], '9750.00')
            
            # Check negative amounts from parentheses
            t1004 = [r for r in rows if r['txn_id'] == 'T-1004'][0]
            self.assertEqual(t1004['amount'], '-340.00')
            
            t1007 = [r for r in rows if r['txn_id'] == 'T-1007'][0]
            self.assertEqual(t1007['amount'], '-112.05')
            
            # Check unmapped codes are kept
            unmapped = [r for r in rows if r['account'] in ['6300', '7100']]
            self.assertEqual(len(unmapped), 2)
            
            # Check all currencies uppercased
            for r in rows:
                self.assertEqual(r['currency'], 'EUR')
        finally:
            if os.path.exists(out_path):
                os.unlink(out_path)


if __name__ == "__main__":
    unittest.main()
