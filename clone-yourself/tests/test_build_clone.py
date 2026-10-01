from __future__ import annotations

import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from _load import load  # noqa: E402

bc = load("build_clone")

RULES = {"rules": [
    {"id": "r001", "bucket": "decide", "text": "Give one recommendation, not three options.", "count": 3, "confirmed": True},
    {"id": "r002", "bucket": "judge", "text": "Every number needs a source.", "count": 2, "confirmed": True},
    {"id": "r003", "bucket": "bans", "text": "Never write I hope this helps.", "count": 1, "confirmed": True},
    {"id": "r004", "bucket": "report", "text": "Unconfirmed rule that must not appear.", "count": 9, "confirmed": False},
]}
PERSONA = {"talk": ["short, lowercase in chat"], "phrases": ["ship it"], "annoys": ["boring hooks"],
           "cares": ["shipping today"]}


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.root = Path(self.d.name)
        self.rules = self.root / "rules.json"
        self.rules.write_text(json.dumps(RULES))
        self.persona = self.root / "persona.json"
        self.persona.write_text(json.dumps(PERSONA))

    def tearDown(self):
        self.d.cleanup()

    def run_main(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = bc.main(list(args))
        return rc, out.getvalue() + err.getvalue()

    def test_builds_confirmed_rules_only_and_passes_check(self):
        rc, log = self.run_main("--rules", str(self.rules), "--name", "Sam", "--persona", str(self.persona),
                                "--tasks", "startup tasks", "--out", str(self.root / "skills"))
        self.assertEqual(rc, 0, log)
        dest = self.root / "skills" / "sam-clone"
        skill = (dest / "SKILL.md").read_text()
        rules = (dest / "references" / "rules.md").read_text()
        persona = (dest / "references" / "persona.md").read_text()
        self.assertIn("name: sam-clone", skill)
        self.assertIn("You are Sam.", skill)
        self.assertIn("Give one recommendation", skill)
        self.assertNotIn("Unconfirmed", skill + rules)
        self.assertIn("## How I decide", rules)
        self.assertIn("- boring hooks", persona)
        self.assertNotIn("{{", skill + rules + persona)

    def test_refuses_without_confirmed_rules_and_on_overwrite(self):
        none = self.root / "none.json"
        none.write_text(json.dumps({"rules": [dict(RULES["rules"][3])]}))
        rc, log = self.run_main("--rules", str(none), "--name", "Sam", "--out", str(self.root / "s"))
        self.assertEqual(rc, 2)
        self.assertIn("no confirmed rules", log)
        args = ("--rules", str(self.rules), "--name", "Sam", "--out", str(self.root / "s2"))
        self.assertEqual(self.run_main(*args)[0], 0)
        rc, log = self.run_main(*args)
        self.assertEqual(rc, 2)
        self.assertIn("--force", log)
        self.assertEqual(self.run_main(*args, "--force")[0], 0)

    def test_rejects_bad_name(self):
        rc, log = self.run_main("--rules", str(self.rules), "--name", "../x", "--out", str(self.root / "s"))
        self.assertEqual(rc, 2)

    def test_pronouns(self):
        dest = bc.build(self.rules, "Ana", self.root / "p", pronoun="she", tasks="design reviews")
        self.assertIn("the way she does", (dest / "SKILL.md").read_text())


if __name__ == "__main__":
    unittest.main()
