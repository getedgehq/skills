import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]


def run_verifier(payload):
    with tempfile.TemporaryDirectory() as raw:
        root = Path(raw)
        (root / "out").mkdir()
        (root / "notes.txt").write_text((HERE / "notes.txt").read_text())
        (root / "verify.py").write_text((HERE / "verify.py").read_text())
        (root / "out/decision-ledger.json").write_text(json.dumps(payload))
        return subprocess.run([sys.executable, "verify.py"], cwd=root, capture_output=True, text=True)


class DecisionLedgerVerifierTests(unittest.TestCase):
    def test_known_good_passes(self):
        rows = [
            ["p1", "proposed", 1, "we should launch the beta on Tuesday", None, "unknown"],
            ["d1", "reversed", 2, "commit to Tuesday, September 29", None, "unknown"],
            ["p2", "proposed", 3, "onboarding should require a credit card", None, "unknown"],
            ["q1", "open", 4, "Security review is still open", None, "unknown"],
            ["d2", "decided", 7, "beta date is now Thursday, October 1", "d1", "unknown"],
            ["a1", "action", 8, "Maya will confirm the status page copy", None, "Maya"],
        ]
        records = [
            {"id": rid, "state": state, "line": line, "evidence": evidence, "supersedes": supersedes, "owner": owner, "due": "unknown"}
            for rid, state, line, evidence, supersedes, owner in rows
        ]
        result = run_verifier({"schema": "edge-decision-ledger/1.0", "records": records})
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_known_bad_and_wrong_shape_fail_cleanly(self):
        result = run_verifier([])
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
