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


def sessions(n, first_day, last_day, turns=8, prefix="s", skills=("x",)):
    """n sessions spread evenly between two offsets from now, in days.

    `turns` is what the miner records for each: the number of turns the human typed.
    The default is well over recheck.MIN_TURNS, so a test that does not care about
    session length gets a corpus that is uniform in it and cannot trip the guard.
    `prefix` keeps two windows built by two calls from sharing session ids, which would
    otherwise credit one window's corrections to the other.
    `skills` is what each session loaded, defaulting to the skill every fixture here is
    named after, so a test about rates is testing rates: the usage guard only has
    something to say when a test deliberately empties it.
    """
    step = (last_day - first_day) / max(1, n - 1)
    return [{"id": f"{prefix}{i}", "ts": time.time() + (first_day + i * step) * DAY,
             "turns": turns, "skills": list(skills)} for i in range(n)]


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


class SkillActuallyRan(unittest.TestCase):
    """A rate that fell while the skill was never loaded is not about the skill.

    Every other guard in recheck.py asks whether the rate moved. None of them asked
    whether the thing under test ever ran, and a skill only reaches the model when it is
    loaded - so the one verdict the rate alone gets backwards is the one that writes
    down a win. On this machine all seven adopted skills had zero production loads on
    the day they were adopted, and the only Skill calls naming them were the eval arms.
    """

    def kg(self, sess, eps, skill="x"):
        entry = {"skill": skill, "decision": "adopt", "ts": ts(-30),
                 "failure": {"kind": "correction", "signature": "em dash in written output",
                             "user_rules": ["never use an em dash"]}}
        return recheck.recheck_kg(entry, {"episodes": eps, "session_index": sess}, True)

    def corpus(self, skills):
        """The clean drop from test_measures_a_real_drop, with usage varied."""
        sess = sessions(40, -60, -31, skills=("x",)) + sessions(20, -29, 0, prefix="a", skills=skills)
        before = [s for s in sess if s["ts"] < time.time() - 30 * DAY]
        eps = [{"session": s["id"], "corr": "you used an em dash in the newsletter blurb"}
               for s in before[:6]]
        noise = ["the deploy script failed again", "wrong render host for this job",
                 "check the port before starting a server", "that number is not measured"]
        eps += [{"session": s["id"], "corr": noise[i % len(noise)]}
                for i, s in enumerate(sess * 2)]
        return sess, eps

    def test_counts_only_loads_inside_the_window(self):
        sess = sessions(6, -60, -31) + sessions(4, -29, 0, prefix="a")
        self.assertEqual(recheck.loads("x", sess, time.time() - 30 * DAY, time.time() + DAY), 4)

    def test_a_skill_the_window_never_loaded_counts_zero(self):
        sess = sessions(4, -29, 0, skills=("something-else",))
        self.assertEqual(recheck.loads("x", sess, time.time() - 30 * DAY, time.time() + DAY), 0)

    def test_the_count_rides_on_a_measurement_that_was_taken(self):
        sess, eps = self.corpus(("x",))
        measured, why = self.kg(sess, eps)
        self.assertIsNone(why)
        self.assertEqual(measured["loads_after"], 20)

    def test_a_drop_with_no_loads_is_not_confirmed(self):
        sess, eps = self.corpus(("something-else",))
        measured, why = self.kg(sess, eps)
        # The measurement still happens - the rate really did fall - and the refusal to
        # call it a win belongs to main(), which is what the next test checks.
        self.assertIsNone(why)
        self.assertEqual(measured["loads_after"], 0)
        self.assertLess(measured["current_failure_rate"],
                        measured["baseline_failure_rate"] * recheck.IMPROVED)

    def test_an_index_without_the_usage_field_is_refused_rather_than_read_as_zero(self):
        # Read as zero, an old index would block every confirmation instead of the ones
        # that deserve it, which is the same mistake in the opposite direction.
        sess, eps = self.corpus(("x",))
        for s in sess:
            del s["skills"]
        measured, why = self.kg(sess, eps)
        self.assertIsNone(measured)
        self.assertIn("predates the skill-usage index", why)


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

    def test_installed_finds_both_a_real_directory_and_a_symlink(self):
        self.assertEqual(len(recheck.installed("demo")), 2)

    def test_installed_is_empty_for_a_skill_that_is_not_there(self):
        # The two causes of zero loads: this one is plumbing, and reads differently in
        # the SKIP message than a skill the sessions could reach and passed over.
        self.assertEqual(recheck.installed("never-installed"), [])


class UsageReport(unittest.TestCase):
    """--usage asks the load question early, while a zero is still fixable."""

    def entry(self, skill, day=-20):
        return {"skill": skill, "decision": "adopt", "ts": ts(day)}

    def test_counts_loads_only_after_the_adoption(self):
        sess = sessions(10, -40, -21, skills=("s",)) + sessions(4, -10, 0, prefix="a", skills=("s",))
        out = recheck.usage_report([self.entry("s")], sess, roots=())
        self.assertIn("s ", out)
        # the ten before adoption loaded it too and none of them count
        self.assertRegex(out, r"\bs\s+4\s+4\b")

    def test_a_skill_nothing_loaded_is_reported_as_zero_not_dropped(self):
        sess = sessions(6, -10, 0, skills=("other",))
        out = recheck.usage_report([self.entry("quiet")], sess, roots=())
        self.assertRegex(out, r"\bquiet\s+0\s+6\b")
        self.assertIn("never loaded once", out)

    def test_the_zeros_sort_first(self):
        sess = sessions(6, -10, 0, skills=("busy",))
        out = recheck.usage_report([self.entry("busy"), self.entry("quiet")], sess, roots=())
        body = [l for l in out.splitlines() if l.startswith(("busy", "quiet"))]
        self.assertEqual(body[0].split()[0], "quiet")

    def test_an_entry_with_no_readable_adoption_time_is_left_out(self):
        sess = sessions(6, -10, 0, skills=("s",))
        out = recheck.usage_report([{"skill": "undated", "decision": "adopt"}], sess, roots=())
        self.assertIn("no open entries", out)

    def test_the_report_names_the_root_the_skill_is_installed_in(self):
        sess = sessions(6, -10, 0, skills=("s",))
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, True)
        os.makedirs(os.path.join(tmp, "demo"))
        out = recheck.usage_report([self.entry("demo"), self.entry("absent")], sess, roots=(tmp,))
        self.assertIn(f"{tmp}", out)
        self.assertIn("not installed here", out)


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

    def run_recheck(self, rows, *args, **envkw):
        with open(os.path.join(self.root, "ledger.jsonl"), "w") as fh:
            for r in rows:
                fh.write(json.dumps(r) + "\n")
        env = dict(os.environ, FORGE_ROOT=self.root, MINER_SCRIPTS=self.miner, **envkw)
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

    def kg_corpus(self, skills):
        sess = sessions(40, -60, -31, skills=("kg",)) + sessions(20, -29, 0, prefix="a", skills=skills)
        before = [s for s in sess if s["ts"] < time.time() - 30 * DAY]
        eps = [{"session": s["id"], "corr": "you used an em dash in the newsletter blurb"}
               for s in before[:6]]
        noise = ["the deploy script failed again", "wrong render host for this job",
                 "check the port before starting a server", "that number is not measured"]
        eps += [{"session": s["id"], "corr": noise[i % len(noise)]}
                for i, s in enumerate(sess * 2)]
        return {"episodes": eps, "session_index": sess}

    def kg_row(self):
        return self.row("kg", failure={"kind": "correction",
                                       "signature": "em dash in written output",
                                       "user_rules": ["never use an em dash"]})

    def test_a_drop_confirms_when_the_skill_was_actually_loaded(self):
        self.stub_miner(corrections=self.kg_corpus(("kg",)))
        out = self.run_recheck([self.kg_row()])
        self.assertIn("KEEP", out)

    def test_the_same_drop_does_not_confirm_when_the_skill_never_loaded(self):
        # Same corpus, same drop, same threshold. The only difference is that nothing in
        # the window loaded the skill, and that alone has to be enough to withhold a win.
        self.stub_miner(corrections=self.kg_corpus(("something-else",)))
        out = self.run_recheck([self.kg_row()])
        self.assertIn("never loaded", out)
        self.assertNotIn("KEEP", out)
        self.assertNotIn("REVOKE", out, "a skill that never ran has had no chance, not a failure")

    def test_a_zero_that_is_really_an_install_path_says_so(self):
        # Zero loads for a skill no root here carries says nothing about the skill. On the
        # live machine every adopted skill sat under root's home while the sessions being
        # measured were the user's, so the count was reporting a path, not a description.
        self.stub_miner(corrections=self.kg_corpus(("something-else",)))
        home = os.path.join(self.tmp, "empty-home")
        os.makedirs(home)
        out = self.run_recheck([self.kg_row()], HOME=home)
        self.assertIn("not installed in any root", out)

    def test_a_zero_with_the_skill_installed_points_at_the_description(self):
        self.stub_miner(corrections=self.kg_corpus(("something-else",)))
        home = os.path.join(self.tmp, "full-home")
        os.makedirs(os.path.join(home, ".agents", "skills", "kg"))
        out = self.run_recheck([self.kg_row()], HOME=home)
        self.assertIn("description is not matching", out)
        self.assertNotIn("not installed in any root", out)
        self.assertNotIn("REVOKE", out)

    def test_usage_reports_without_deciding_anything(self):
        self.stub_miner(corrections=self.kg_corpus(("something-else",)))
        out = self.run_recheck([self.kg_row()], "--usage")
        self.assertIn("never loaded once", out)
        for verdict in ("KEEP", "REVOKE", "SKIP"):
            self.assertNotIn(verdict, out)

    def test_usage_covers_entries_no_date_has_come_due_for(self):
        self.stub_miner(corrections=self.kg_corpus(("something-else",)))
        row = self.kg_row()
        row["recheck_due"] = "2099-01-01"
        out = self.run_recheck([row], "--usage")
        self.assertNotIn("no rechecks due", out)
        self.assertIn("kg", out)

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
