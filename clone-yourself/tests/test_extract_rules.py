from __future__ import annotations

import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from _load import load  # noqa: E402

er = load("extract_rules")

SAMPLE = """---
name: example
description: a memory file
---
# Rules
- Never ship on an agent's word; run the tests yourself.
- Always lead with the result, keep it under five lines.
- Give me one recommendation, not three options.
- Never write em dashes in messages.
- Always email Jordan Keller at jordan@acme.example about the $50K deal, call +49 170 1234567.
- Never ship on an agent's word, run the tests yourself!
- I hate a boring hook, it annoys me more than anything.
This line is just a description of a project and has no rule in it at all.

**Why:** Last week a client lost money because of it.
**How to apply:** Check the existing docs before you build anything.
"""


class ExtractTests(unittest.TestCase):
    def run_on(self, text, *args):
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "CLAUDE.md"
            src.write_text(text)
            out = Path(d) / "out"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = er.main([str(src), "--no-defaults", "--out", str(out), *args])
            data = json.loads((out / "rules.json").read_text())
            return rc, buf.getvalue(), data

    def test_extracts_buckets_dedupes_and_redacts(self):
        rc, stdout, data = self.run_on(SAMPLE)
        self.assertEqual(rc, 0)
        texts = [r["text"] for r in data["rules"]]
        joined = "\n".join(texts)
        self.assertIn("Check the existing docs before you build anything.", texts)
        self.assertNotIn("jordan@acme.example", joined)
        self.assertNotIn("Jordan Keller", joined)
        self.assertNotIn("50K", joined)
        self.assertNotIn("client lost money", joined)          # Why: lines are skipped
        self.assertNotIn("description of a project", joined)   # not a rule
        dup = [r for r in data["rules"] if r["text"].startswith("Never ship on an agent")]
        self.assertEqual(len(dup), 1)
        self.assertEqual(dup[0]["count"], 2)
        buckets = {r["text"][:20]: r["bucket"] for r in data["rules"]}
        self.assertEqual(buckets["Never write em dashe"], "format")
        self.assertEqual(buckets["I hate a boring hook"], "persona")
        self.assertTrue(all(r["confirmed"] is False for r in data["rules"]))
        self.assertGreaterEqual(data["redactions"].get("dropped_rules", 0), 1)

    def test_stdout_has_counts_not_text_unless_show(self):
        _, stdout, _ = self.run_on(SAMPLE)
        self.assertNotIn("Check the existing docs", stdout)
        self.assertIn("rules kept:", stdout)
        _, shown, _ = self.run_on(SAMPLE, "--show")
        self.assertIn("Check the existing docs", shown)

    def test_redact_patterns(self):
        cases = {
            "see https://example.com/a": "[url]",
            "mail a.b@example.org now": "[email]",
            "ask @someone_1 first": "[handle]",
            "call +1 415 555 0100 today": "[phone]",
            "a €1,234 invoice": "[amount]",
            "read ~/notes/plan.md first": "[path]",
            "loop in Ada Lovelace": "[name]",
            "read ~/context first": "[path]",
            "ssh 10.0.0.12 first": "[ip]",
            "board 69261198 is the source": "[number]",
            "post it on example.dev": "[url]",
        }
        for text, token in cases.items():
            self.assertIn(token, er.redact(text), text)
        self.assertEqual(er.redact("Use Opus for complex lanes"), "Use Opus for complex lanes")

    def test_aggressive_and_redact_words(self):
        try:
            er.OPTIONS.update(aggressive=True, words=set())
            self.assertEqual(er.redact("Ask Jordan before you ship to Claude"), "Ask [word] before you ship to Claude")
            er.OPTIONS.update(aggressive=False, words={"acme"})
            self.assertEqual(er.redact("never pitch acme or Acme"), "never pitch [word] or [word]")
            self.assertEqual(er.redact("ship acme-api and acme_sync"), "ship [word]-api and [word]_sync")
        finally:
            er.OPTIONS.update(aggressive=False, words=set())

    def test_defaults_use_given_home(self):
        with tempfile.TemporaryDirectory() as d:
            home = Path(d)
            mem = home / ".claude/projects/p/memory"
            mem.mkdir(parents=True)
            (mem / "feedback_x.md").write_text("- Never send a message without approval.\n")
            paths = er.default_paths(home, home / "nowhere")
            files, rules, _ = er.extract(paths)
            self.assertEqual(len(files), 1)
            self.assertEqual(rules[0]["sources"], ["feedback_x.md"])


if __name__ == "__main__":
    unittest.main()
