from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from _load import load  # noqa: E402

cc = load("check_clone")

GOOD = """---
name: sam-clone
description: >-
  Work like Sam on startup tasks: decide, review and write the way they do. Use when the user asks
  for Sam's take.
---

# Sam Clone

You are Sam. Pick one answer.
"""


class CheckCloneTests(unittest.TestCase):
    def make(self, skill=GOOD, extra=None, folder="sam-clone"):
        d = tempfile.mkdtemp()
        f = Path(d) / folder
        (f / "references").mkdir(parents=True)
        (f / "SKILL.md").write_text(skill)
        if extra:
            (f / "references" / "rules.md").write_text(extra)
        return f

    def kinds(self, folder, allow=None):
        return {p["kind"] for p in cc.check(folder, allow or {"Sam"})}

    def test_good_clone_passes(self):
        self.assertEqual(self.kinds(self.make(extra="- Give one recommendation, not three options.\n")), set())

    def test_pii_is_caught(self):
        extra = ("- Email jo@example.com\n- See https://example.com\n- Call +1 415 555 0100\n"
                 "- Ask @jo_doe\n- The $40K deal\n- Read ~/private/notes.md\n- Talk to Ada Lovelace\n")
        k = self.kinds(self.make(extra=extra))
        self.assertTrue({"pii:email", "pii:url", "pii:phone", "pii:handle", "pii:amount", "pii:path",
                         "pii:name"} <= k, k)

    def test_frontmatter_problems(self):
        self.assertIn("frontmatter", {p["kind"] for p in cc.check(self.make(skill="# nothing"), set())})
        bad = GOOD.replace("name: sam-clone", "name: wrong")
        self.assertIn("frontmatter", self.kinds(self.make(skill=bad)))
        short = "---\nname: sam-clone\ndescription: too short\n---\n"
        self.assertIn("frontmatter", self.kinds(self.make(skill=short)))

    def test_placeholder_left(self):
        self.assertIn("placeholder", self.kinds(self.make(extra="- {{sections}}\n")))

    def test_missing_skill(self):
        d = Path(tempfile.mkdtemp()) / "sam-clone"
        d.mkdir()
        self.assertEqual({p["kind"] for p in cc.check(d)}, {"structure"})


if __name__ == "__main__":
    unittest.main()
