"""Offline tests for build_dataset.py (standard library only; no tokenizer, no network)."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "..", "scripts", "build_dataset.py")
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
from build_dataset import sanitize, split_groups  # noqa: E402


def synthetic(n_groups=12, per=6):
    rows = []
    for g in range(n_groups):
        for k in range(per):
            rows.append({"id": f"g{g}m{k}", "group": f"thread-{g}", "synthetic": True,
                         "prompt": f"Situation number {g} {k}: a friend asks about plans",
                         "answer": f"Sure thing, thread {g} message {k} with words {' '.join(str(g * 100 + k + j) for j in range(8))}."})
    return rows


class Sanitize(unittest.TestCase):
    def test_strips_quotes_contacts_names(self):
        t = ("Lovely to hear from you Ana, call me on +49 170 1234567 or mail ana@example.com\n"
             "see https://example.com/x\n> old quoted line\nOn Mon, 3 May 2026, Ana wrote:\nquoted body")
        s = sanitize(t, ["Ana"])
        for bad in ("Ana", "1234567", "ana@example.com", "https://", "old quoted", "quoted body"):
            self.assertNotIn(bad, s)
        self.assertIn("[NAME]", s)
        self.assertIn("[EMAIL]", s)

    def test_signature_block_removed(self):
        self.assertEqual(sanitize("Thanks!\n-- \nJane Doe\nACME Corp", []), "Thanks!")


class Split(unittest.TestCase):
    def test_whole_groups_and_minimums(self):
        rows = synthetic()
        assign = split_groups(rows, "42", None)
        sizes = {"train": 0, "valid": 0, "test": 0}
        for r in rows:
            sizes[assign[r["group"]]] += 1
        self.assertGreaterEqual(sizes["test"], 12)
        self.assertGreaterEqual(sizes["valid"], 8)
        self.assertEqual(sum(sizes.values()), len(rows))

    def test_frozen_split_sends_new_groups_to_train(self):
        rows = synthetic()
        frozen = split_groups(rows, "42", None)
        new = rows + [{"group": "fb-abc", "answer": "x"}]
        self.assertEqual(split_groups(new, "42", frozen)["fb-abc"], "train")
        for g, s in frozen.items():
            self.assertEqual(split_groups(new, "42", frozen)[g], s)


class EndToEnd(unittest.TestCase):
    def run_build(self, rows, *extra):
        d = tempfile.mkdtemp()
        inp = os.path.join(d, "ex.jsonl")
        with open(inp, "w") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        p = subprocess.run([sys.executable, SCRIPT, "--input", inp, "--out", os.path.join(d, "data"), *extra],
                           capture_output=True, text=True)
        return p, d

    def test_builds_and_prints_no_text(self):
        rows = synthetic()
        p, d = self.run_build(rows)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertNotIn("Sure thing", p.stdout)
        s = json.load(open(os.path.join(d, "data", "summary.json")))
        self.assertTrue(s["trainable"])
        groups = {}
        for split in ("train", "valid", "test"):
            for line in open(os.path.join(d, "data", f"{split}.jsonl")):
                r = json.loads(line)
                groups.setdefault(r["group"], set()).add(split)
                self.assertEqual(r["messages"][-1]["role"], "assistant")
        self.assertTrue(all(len(v) == 1 for v in groups.values()), "a group leaked across splits")

    def test_duplicates_and_leaky_prompts_dropped(self):
        rows = synthetic()
        rows.append(dict(rows[0], id="dup"))
        leak = dict(rows[1], id="leak")
        leak["prompt"] = leak["answer"]
        leak["answer"] = leak["answer"] + " and something more to make it different enough from the original text here"
        rows.append(leak)
        p, d = self.run_build(rows)
        s = json.load(open(os.path.join(d, "data", "summary.json")))
        self.assertEqual(s["dropped_duplicate"], 1)
        self.assertGreaterEqual(s["dropped_prompt_leak"] + s["dropped_duplicate"], 2)

    def test_too_little_data_exits_2(self):
        p, _ = self.run_build(synthetic(n_groups=4, per=5))
        self.assertEqual(p.returncode, 2)


if __name__ == "__main__":
    unittest.main()
