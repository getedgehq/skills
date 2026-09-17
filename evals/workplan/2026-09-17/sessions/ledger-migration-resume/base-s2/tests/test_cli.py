import json
import os
import tempfile
import unittest

from ledgerctl.cli import main


class CLITests(unittest.TestCase):
    def test_since_filter(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as out:
            out_path = out.name
        
        try:
            # Use simple.csv which has dates 2026-01-02, 2026-01-03
            main(['--input', 'tests/fixtures/simple.csv', '--out', out_path, '--since', '2026-01-03'])
            
            with open(out_path) as f:
                data = json.load(f)
            
            # Should only get S-2 which is booked on 2026-01-03
            # S-1 is booked on 2026-01-02 so should be filtered out
            self.assertEqual(len(data['rows']), 1)
            self.assertEqual(data['rows'][0]['txn_id'], 'S-2')
        finally:
            if os.path.exists(out_path):
                os.unlink(out_path)


if __name__ == "__main__":
    unittest.main()
