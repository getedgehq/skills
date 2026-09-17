#!/usr/bin/env python3
"""End-to-end tests for the production recheck, on fixtures.

Every bug this file pins down was found by running the recheck against real
session history, not by reading it: a symlinked install that crashed the run, a
missing signature that read as a perfect score, a zero baseline that uninstalled
working skills, a theme described in ordinary words that matched every correction,
and a skill adopted the same morning being judged on half a day of sessions.

Run: python3 tests/test_recheck.py   (stdlib only, no network, no model calls)

The miner is stubbed: each test writes the corrections or failures report the
recheck would have mined, so the decisions under test are the recheck's own.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, "..", "scripts")
sys.path.insert(0, SCRIPTS)
import recheck  # noqa: E402

DAY = 86400
STUB = '''#!/usr/bin/env python3
import shutil, sys
out = sys.argv[sys.argv.index("--out") + 1]
shutil.copy({src!r}, out)
'''


def ts(offset_days):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() + offset_days * DAY))


def sessions(n, first_day, last_day):
    """n sessions spread evenly between two offsets from now, in days."""
    step = (last_day - first_day) / max(1, n - 1)
    return [{"id": f"s{i}", "ts": time.time() + (first_day + i * step) * DAY} for i in range(n)]


class KgRecheck(unittest.TestCase):
    """recheck_kg decides only when the corrections can actually answer the question."""

    def kg(self, entry_days_ago, eps, sess, rules=("never post without the list format",),
           signature="drafting a linkedin post for federico"):
        entry = {"skill": "x", "decision": "adopt", "ts": ts(-entry_days_ago),
                 "failure": {"kind": "correction", "signature": signature,
                             "user_rules": list(rules)}}
        return recheck.recheck_kg(entry, {"episodes": eps, "session_index": sess}, True)

    def test_refuses_a_skill_adopted_today(self):
        eps = [{"session": "s0", "corr": "linkedin post format is wrong"}]
        measured, why = self.kg(0.5, eps, sessions(30, -20, 0))
        self.assertIsNone(measured)
        self.assertIn("days of sessions since adoption", why)

    def test_refuses_a_theme_made_of_common_words(self):
        # Every episode contains both signature words, so matching on them says nothing.
        eps = [{"session": f"s{i}", "corr": "the linkedin post is wrong again"} for i in range(40)]
        measured, why = self.kg(30, eps, sessions(60, -60, 0),
                                rules=(), signature="linkedin post wrong again")
        self.assertIsNone(measured)
        self.assertIn("common across corrections", why)

    def test_measures_a_real_drop(self):
        sess = sessions(40, -60, 0)
        before = [s for s in sess if s["ts"] < time.time() - 30 * DAY]
        eps = [{"session": s["id"], "corr": "you used an em dash in the newsletter blurb"}
               for s in before[:6]]
        # A realistic corpus: the theme is a minority of all corrections, which is
        # what makes its words distinctive enough to count.
        noise = ["the deploy script failed again", "wrong render host for this job",
                 "check the port before starting a server", "that number is not measured",
                 "you forgot the invoice attachment"]
        eps += [{"session": s["id"], "corr": noise[i % len(noise)]}
                for i, s in enumerate(sess * 2)]
        measured, why = self.kg(30, eps, sess, rules=("never use an em dash",),
                                signature="em dash in written output")
        self.assertIsNone(why)
        self.assertGreater(measured["baseline_failure_rate"], 0)
        self.assertEqual(measured["current_failure_rate"], 0.0)
        self.assertEqual(measured["metric"], "correction_rate")

    def test_refuses_when_nothing_was_happening_before(self):
        sess = sessions(40, -60, 0)
        measured, why = self.kg(30, [], sess, rules=("never use an em dash",),
                                signature="em dash in written output")
        self.assertIsNone(measured)
        self.assertIn("no baseline signal", why)


class Uninstall(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.home = os.path.join(self.tmp, "home")
        self.real = os.path.join(self.home, ".agents", "skills", "demo")
        self.link = os.path.join(self.home, ".claude", "skills", "demo")
        os.makedirs(self.real)
        os.makedirs(os.path.dirname(self.link))
        open(os.path.join(self.real, "SKILL.md"), "w").write("---\nname: demo\n---\n")
        os.symlink(self.real, self.link)
        self._home = os.environ.get("HOME")
        os.environ["HOME"] = self.home

    def tearDown(self):
        os.environ["HOME"] = self._home
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_symlinked_install_does_not_crash_and_is_kept(self):
        root = os.path.join(self.tmp, "forge")
        done = recheck.uninstall("demo", root, dry=False)
        self.assertFalse(os.path.exists(self.link))
        self.assertFalse(os.path.exists(self.real))
        kept = [p for p in os.listdir(os.path.join(root, "revoked"))]
        self.assertEqual(len(kept), 1, "the revoked bundle is kept as evidence, not deleted")
        self.assertTrue(any("unlinked" in d for d in done))

    def test_dry_run_changes_nothing(self):
        recheck.uninstall("demo", os.path.join(self.tmp, "forge"), dry=True)
        self.assertTrue(os.path.islink(self.link))
        self.assertTrue(os.path.isfile(os.path.join(self.real, "SKILL.md")))


class MainDecisions(unittest.TestCase):
    """The tool-error path, through main(), on a ledger of fixture rows."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = os.path.join(self.tmp, "forge")
        os.makedirs(os.path.join(self.root, "mined"))
        self.miner = os.path.join(self.tmp, "miner")
        os.makedirs(self.miner)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def stub_miner(self, failures=None, corrections=None):
        for name, data in (("mine.py", failures), ("corrections.py", corrections)):
            src = os.path.join(self.tmp, name + ".json")
            json.dump(data or {}, open(src, "w"))
            open(os.path.join(self.miner, name), "w").write(STUB.format(src=src))

    def run_recheck(self, rows, *args):
        with open(os.path.join(self.root, "ledger.jsonl"), "w") as fh:
            for r in rows:
                fh.write(json.dumps(r) + "\n")
        env = dict(os.environ, FORGE_ROOT=self.root, MINER_SCRIPTS=self.miner)
        out = subprocess.run([sys.executable, os.path.join(SCRIPTS, "recheck.py"),
                              "--dry-run", *args], capture_output=True, text=True, env=env)
        self.assertEqual(out.returncode, 0, out.stderr)
        return out.stdout

    def row(self, skill, **kw):
        base = {"skill": skill, "decision": "adopt", "ts": ts(-30), "recheck_due": "2000-01-01",
                "failure": {"kind": "tool_error", "signature": "file has not been read yet"},
                "baseline_failure_rate": 0.2}
        base.update(kw)
        return base

    def test_confirms_only_on_a_real_drop(self):
        self.stub_miner(failures={"sessions_scanned": 50, "clusters": [
            {"signature": "file has not been read yet", "session_count": 1}]})
        out = self.run_recheck([self.row("dropped")])
        self.assertIn("KEEP", out)

    def test_revokes_when_the_rate_did_not_move(self):
        self.stub_miner(failures={"sessions_scanned": 50, "clusters": [
            {"signature": "file has not been read yet", "session_count": 12}]})
        out = self.run_recheck([self.row("stuck")])
        self.assertIn("REVOKE", out)

    def test_skips_without_a_signature(self):
        self.stub_miner(failures={"sessions_scanned": 50, "clusters": []})
        out = self.run_recheck([self.row("unmeasured", failure={"kind": "tool_error"})])
        self.assertIn("SKIP", out)
        self.assertNotIn("KEEP", out)

    def test_skips_on_a_zero_baseline(self):
        self.stub_miner(failures={"sessions_scanned": 50, "clusters": []})
        out = self.run_recheck([self.row("never-failed", baseline_failure_rate=0)])
        self.assertIn("SKIP", out)
        self.assertNotIn("REVOKE", out)

    def test_skips_without_a_baseline(self):
        self.stub_miner(failures={"sessions_scanned": 50, "clusters": []})
        row = self.row("nobaseline")
        del row["baseline_failure_rate"]
        out = self.run_recheck([row])
        self.assertIn("SKIP", out)

    def test_nothing_due_runs_no_miner(self):
        self.stub_miner()
        out = self.run_recheck([self.row("later", recheck_due="2099-01-01")])
        self.assertIn("no rechecks due", out)

    def test_a_decided_skill_is_not_rechecked_twice(self):
        self.stub_miner(failures={"sessions_scanned": 50, "clusters": []})
        rows = [self.row("done"), {"skill": "done", "decision": "revoked", "ts": ts(-1)}]
        out = self.run_recheck(rows)
        self.assertIn("no rechecks due", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
