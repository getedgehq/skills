from __future__ import annotations

import importlib.util
import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("check_copy", HERE / "scripts" / "check_copy.py")
cc = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(cc)


def rules(text, mode="any"):
    return {f["rule"] for f in cc.check(text, mode) if f["severity"] == "error"}


class CheckCopyTests(unittest.TestCase):
    def test_clean_linkedin_post_passes(self):
        post = "We gave Claude $1 and 2,000 tools to test.\n\nIt found 10 customers.\n\nTotal spend: 40 cents."
        self.assertEqual(rules(post, "linkedin"), set())

    def test_em_and_en_dash_and_entities(self):
        self.assertIn("dash", rules("fast \u2014 and cheap"))
        self.assertIn("dash", rules("2020\u20132026"))
        self.assertIn("dash", rules("<p>fast &mdash; cheap</p>", "page"))

    def test_banned_phrases(self):
        self.assertIn("banned-phrase", rules("Excited to announce our launch"))
        self.assertIn("banned-phrase", rules("this is truly insane"))
        self.assertNotIn("banned-phrase", rules("this is actually insane"))

    def test_disclaimer(self):
        self.assertIn("disclaimer", rules("Visuals are AI-generated."))

    def test_hook_gate(self):
        self.assertIn("hook-question", rules("Have you ever shipped 3 products in one week?", "linkedin"))
        self.assertIn("hook-digit", rules("We shipped a whole product in one single week.", "linkedin"))
        self.assertIn("hook-length", rules("We shipped 3 products.", "linkedin"))

    def test_hook_gate_only_in_linkedin_mode(self):
        self.assertEqual(rules("Have you tried it?", "dm"), set())

    def test_swearing_and_emoji(self):
        self.assertIn("swearing", rules("what the fuck"))
        self.assertNotIn("swearing", rules("what the f*ck"))
        self.assertIn("emoji", rules("lfg \U0001F64C"))

    def test_dm_warnings_do_not_fail_unless_strict(self):
        dm = "Hey Sam,\nlooks useful\nBest,"
        found = {f["rule"] for f in cc.check(dm, "dm")}
        self.assertTrue({"dm-greeting", "dm-signoff"} <= found)

    def test_cli_exit_codes_and_json(self):
        import tempfile, os
        with tempfile.TemporaryDirectory() as d:
            bad = os.path.join(d, "bad.txt"); open(bad, "w").write("Excited to announce \u2014 v2")
            good = os.path.join(d, "good.txt"); open(good, "w").write("looks useful\nwant me to test it?")
            buf = io.StringIO()
            with redirect_stdout(buf):
                self.assertEqual(cc.main(["--json", bad]), 1)
            data = json.loads(buf.getvalue())
            self.assertFalse(data["ok"])
            self.assertEqual({f["rule"] for f in data["findings"]}, {"dash", "banned-phrase"})
            with redirect_stdout(io.StringIO()):
                self.assertEqual(cc.main(["--mode", "dm", good]), 0)
                dm = os.path.join(d, "dm.txt"); open(dm, "w").write("Hi Sam\nlooks good")
                self.assertEqual(cc.main(["--mode", "dm", dm]), 0)
                self.assertEqual(cc.main(["--mode", "dm", "--strict", dm]), 1)


if __name__ == "__main__":
    unittest.main()
