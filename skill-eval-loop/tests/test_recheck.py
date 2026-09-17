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


def sessions(n, first_day, last_day, turns=8, prefix="s"):
    """n sessions spread evenly between two offsets from now, in days.

    `turns` is what the miner records for each: the number of turns the human typed.
    The default is well over recheck.MIN_TURNS, so a test that does not care about
    session length gets a corpus that is uniform in it and cannot trip the guard.
    `prefix` keeps two windows built by two calls from sharing session ids, which would
    otherwise credit one window's corrections to the other.
    """
    step = (last_day - first_day) / max(1, n - 1)
    return [{"id": f"{prefix}{i}", "ts": time.time() + (first_day + i * step) * DAY,
             "turns": turns} for i in range(n)]


class KgRecheck(unittest.TestCase):
    """recheck_kg decides only when the corrections can actually answer the question."""

    def kg(self, entry_days_ago, eps, sess, rules=("never post without the list format",),
           signature="drafting a linkedin post for federico", derived_from=None):
        failure = {"kind": "correction", "signature": signature, "user_rules": list(rules)}
        if derived_from:
            failure["derived_from"] = derived_from
        entry = {"skill": "x", "decision": "adopt", "ts": ts(-entry_days_ago),
                 "failure": failure}
        return recheck.recheck_kg(entry, {"episodes": eps, "session_index": sess}, True)

    def test_refuses_a_signature_lifted_from_the_skills_own_description(self):
        # Same corpus and the same clean drop as test_measures_a_real_drop below. The
        # only difference is where the signature came from, and that alone has to be
        # enough: extending the stopword list narrowed real skill_md signatures from
        # 35-42 words to 18-20, under the width cap, so width can no longer catch them.
        sess = sessions(40, -60, 0)
        before = [s for s in sess if s["ts"] < time.time() - 30 * DAY]
        eps = [{"session": s["id"], "corr": "you used an em dash in the newsletter blurb"}
               for s in before[:6]]
        eps += [{"session": s["id"], "corr": "the deploy script failed again"} for s in sess]
        measured, why = self.kg(30, eps, sess, rules=("never use an em dash",),
                                signature="em dash in written output",
                                derived_from="skill_md:/home/u/.agents/skills/x/SKILL.md")
        self.assertIsNone(measured, "a prose-derived matcher must never carry a verdict")
        self.assertIn("lifted from the skill's own description", why)

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


class SessionLength(unittest.TestCase):
    """The denominator holds only sessions that could have carried a correction.

    Found by measuring, not by reading: across the real adoption date the share of
    single-turn sessions fell from 70% of the window to 6%, taking the raw correction
    rate from 22% to 75% with no skill involved. The shipped verdict would have read
    that as every adopted skill making the agent worse.
    """

    def test_a_session_too_short_to_hold_an_episode_is_not_in_the_denominator(self):
        short = sessions(4, -10, -1, turns=1)
        long = sessions(4, -10, -1, turns=9)
        kept = recheck.eligible(short + long)
        self.assertEqual([s["id"] for s in kept], [s["id"] for s in long])

    def test_an_index_without_turns_is_refused_rather_than_guessed(self):
        sess = [{"id": s["id"], "ts": s["ts"]} for s in sessions(40, -60, 0)]
        eps = [{"session": s["id"], "corr": "you used an em dash in the blurb"} for s in sess[:6]]
        entry = {"skill": "x", "decision": "adopt", "ts": ts(-30),
                 "failure": {"kind": "correction", "signature": "em dash in written output",
                             "user_rules": ["never use an em dash"]}}
        measured, why = recheck.recheck_kg(entry, {"episodes": eps, "session_index": sess}, True)
        self.assertIsNone(measured)
        self.assertIn("predates the session-length control", why)

    def shift(self, before, after, eps):
        t = time.time() - 30 * DAY
        return recheck.length_shift(before + after, eps, t, time.time() + DAY)

    def test_windows_of_the_same_shape_do_not_shift(self):
        before = sessions(30, -60, -31, turns=9)
        after = sessions(10, -29, 0, turns=9, prefix="a")
        eps = [{"session": s["id"], "corr": "wrong"} for s in (before + after)[::3]]
        self.assertAlmostEqual(self.shift(before, after, eps), 1.0, places=6)

    def test_a_window_that_got_longer_shifts_and_is_refused(self):
        # The real pattern: short exchanges for weeks, then a day of deep work. Both
        # windows clear the floor, so this is the residue the floor does not remove.
        before = sessions(30, -60, -31, turns=2)
        after = sessions(10, -29, 0, turns=30, prefix="a")
        eps = [{"session": s["id"], "corr": "wrong"} for s in before[:6] + after[:9]]
        shift = self.shift(before, after, eps)
        self.assertGreater(shift, 1 / recheck.IMPROVED,
                           "length alone explains the whole rate change here")

    def test_a_before_window_with_no_signal_is_unbounded_not_comparable(self):
        # 0.0 expected before and a real rate after is the widest shift there is. Reading
        # a zero denominator as "no shift" would wave through exactly the worst case.
        before = sessions(30, -60, -31, turns=2)
        after = sessions(10, -29, 0, turns=30, prefix="a")
        eps = [{"session": s["id"], "corr": "wrong"} for s in after]
        self.assertEqual(self.shift(before, after, eps), float("inf"))
        self.assertEqual(self.shift(before, after, []), 1.0,
                         "two quiet windows are comparable, they are just both quiet")

    def test_the_guard_refuses_through_recheck_kg(self):
        # Both windows clear the floor and both are large enough to compare, so the only
        # thing left to refuse on is the shape: short exchanges before, deep work after.
        before = sessions(30, -60, -31, turns=2)
        after = sessions(14, -29, 0, turns=30, prefix="a")
        sess = before + after
        eps = [{"session": s["id"], "corr": "you used an em dash in the blurb"}
               for s in before[:6]]
        eps += [{"session": s["id"], "corr": "the deploy script failed again"}
                for s in after[:12]]
        entry = {"skill": "x", "decision": "adopt", "ts": ts(-30),
                 "failure": {"kind": "correction", "signature": "em dash in written output",
                             "user_rules": ["never use an em dash"]}}
        measured, why = recheck.recheck_kg(entry, {"episodes": eps, "session_index": sess}, True)
        self.assertIsNone(measured, "a verdict here would be about the shape of the work")
        self.assertIn("shape of the work", why)

    def test_the_guard_is_tied_to_the_verdict_threshold(self):
        # Not an independent tunable: the guard allows exactly what the verdict cannot
        # turn on, so raising one without the other is impossible by construction.
        self.assertEqual(recheck.IMPROVED, 0.7)


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
