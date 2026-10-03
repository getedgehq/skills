"""Offline tests for the blind-pick sheet/score, regurgitation check and the hard-rule parser."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EV = os.path.join(HERE, "..", "scripts", "evaluate.py")
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))


def write(path, rows):
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


class BlindPick(unittest.TestCase):
    def test_sheet_and_score(self):
        d = tempfile.mkdtemp()
        mine = [{"id": f"f{i}", "kind": "fresh", "arm": "mine", "prompt": f"q{i}", "reply": f"mine {i} <b>"} for i in range(10)]
        card = [dict(r, arm="card", reply=f"card {i}") for i, r in enumerate(mine)]
        write(f"{d}/m.jsonl", mine); write(f"{d}/c.jsonl", card)
        subprocess.run([sys.executable, EV, "sheet", "--first", f"{d}/m.jsonl", "--second", f"{d}/c.jsonl",
                        "--out", f"{d}/compare.html", "--key", f"{d}/key.json"], check=True, capture_output=True)
        page = open(f"{d}/compare.html").read()
        self.assertIn("&lt;b&gt;", page)          # replies are escaped
        key = json.load(open(f"{d}/key.json"))
        picks = {i: next(s for s, arm in k.items() if arm == "mine") for i, k in list(key.items())[:7]}
        picks.update({i: "neither" for i in list(key)[7:]})
        json.dump(picks, open(f"{d}/picks.json", "w"))
        out = subprocess.run([sys.executable, EV, "score", "--picks", f"{d}/picks.json", "--key", f"{d}/key.json"],
                             check=True, capture_output=True, text=True).stdout
        t = json.loads(out)
        self.assertEqual((t["mine"], t["neither"], t["accepted"]), (7, 3, True))


class Regurgitation(unittest.TestCase):
    def test_flags_long_copy_only(self):
        d = tempfile.mkdtemp()
        secret = "The spare key is under the blue flowerpot next to the garage door, always."
        write(f"{d}/train.jsonl", [{"messages": [{"role": "user", "content": "q"}, {"role": "assistant", "content": secret}]}])
        write(f"{d}/out.jsonl", [{"id": "a", "arm": "mine", "prompt": "where?", "reply": "Oh! " + secret},
                                 {"id": "b", "arm": "mine", "prompt": "hi", "reply": "Something else entirely."}])
        out = json.loads(subprocess.run([sys.executable, EV, "regurg", "--outputs", f"{d}/out.jsonl", "--train", f"{d}/train.jsonl"],
                                        check=True, capture_output=True, text=True).stdout)
        self.assertEqual([h["id"] for h in out["hits"]], ["a"])


class HardRules(unittest.TestCase):
    def test_banned_phrases(self):
        from common import banned_phrases
        card = 'You write short.\nNever write: "XOXO", "Best regards"\nnever use "per my last email"'
        self.assertEqual(banned_phrases(card), ["XOXO", "Best regards", "per my last email"])


if __name__ == "__main__":
    unittest.main()
