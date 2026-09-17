#!/usr/bin/env python3
"""Fixture tests for the blind judge and the sample aggregator.

Stdlib only, no network and no model calls: every test builds an arm's workdir or a
set of sample verdicts on disk and checks what the judge would show, refuse or count.

What these pin down is that the judge cannot tell the arms apart. That is the whole
basis of the loop's evidence, and it was true only for Claude Code: the file manifest
skipped .claude by name, so a Codex arm (.agents/skills) or an OpenCode arm
(.opencode/skill) would have listed the skill under test in the judge's own prompt.
"""
import json
import os
import subprocess
import sys
import shutil
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(os.path.dirname(HERE), "scripts")
sys.path.insert(0, SCRIPTS)
import judge  # noqa: E402

AGGREGATE = os.path.join(SCRIPTS, "aggregate.py")

# Where each runner installs the skill under test (run_eval.sh).
INSTALL = {"claude": ".claude/skills", "codex": ".agents/skills", "opencode": ".opencode/skill"}


def arm_dir(tmp, runner=None, skill="li-post-fede", work=("post.md",)):
    """An arm's workdir: the files the agent produced, plus the skill if it had one."""
    d = os.path.join(tmp, runner or "without")
    for name in work:
        p = os.path.join(d, name)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w").write("the agent's output\n")
    if runner:
        sk = os.path.join(d, INSTALL[runner], skill)
        os.makedirs(sk)
        open(os.path.join(sk, "SKILL.md"), "w").write("---\nname: %s\n---\nrules\n" % skill)
        open(os.path.join(sk, "reference.md"), "w").write("more rules\n")
    return d


class Blindness(unittest.TestCase):
    def test_no_runner_leaks_the_skill_into_the_file_list(self):
        for runner in INSTALL:
            with tempfile.TemporaryDirectory() as tmp:
                d = arm_dir(tmp, runner)
                trees = judge.skill_trees(d)
                files = judge.manifest(d, hide=trees.values())
                self.assertEqual(sorted(trees), ["li-post-fede"], runner)
                self.assertNotIn("li-post-fede", files, runner)
                self.assertNotIn("SKILL.md", files, runner)
                self.assertIn("post.md", files, runner)

    def test_the_old_skip_list_is_what_leaked(self):
        # The regression this replaces: skipping only .claude left the other two.
        with tempfile.TemporaryDirectory() as tmp:
            d = arm_dir(tmp, "codex")
            claude_only = [h for h in judge.skill_trees(d).values() if ".claude" in h]
            self.assertIn("li-post-fede", judge.manifest(d, hide=claude_only))

    def test_a_skill_the_agent_wrote_itself_stays_in_the_manifest(self):
        # The deliverable of a skill-writing task is not the skill under test.
        with tempfile.TemporaryDirectory() as tmp:
            d = arm_dir(tmp, None, work=("drafted-skill/SKILL.md", "notes.md"))
            trees = judge.skill_trees(d)
            self.assertEqual(trees, {})
            self.assertIn("drafted-skill/SKILL.md", judge.manifest(d, hide=trees.values()))

    def test_an_arm_that_names_the_skill_is_caught(self):
        names = ["li-post-fede", "tldr-replies"]
        self.assertEqual(judge.named_skills("Wrote it following the li-post-fede skill.", names),
                         ["li-post-fede"])
        self.assertEqual(judge.named_skills("Wrote the post. Kept it to 150 words.", names), [])

    def test_a_longer_name_does_not_match_on_a_prefix(self):
        # "fede-voice" must not fire on "fede-voice-long", or a rerun of a renamed
        # skill would be refused for naming a skill that was never installed.
        self.assertEqual(judge.named_skills("used fede-voice-long here", ["fede-voice"]), [])


class Verdicts(unittest.TestCase):
    def test_a_reply_that_keeps_talking_still_parses(self):
        text = 'Here it is:\n{"winner": "A", "reasons": ["clearer"]}\nHappy to expand.'
        self.assertEqual(judge.first_object(text)["winner"], "A")

    def test_a_reply_with_no_object_is_none(self):
        self.assertIsNone(judge.first_object("I cannot judge these runs."))

    def test_the_obvious_wrappers_are_read_not_refused(self):
        for said, want in (("A", "A"), ("b", "B"), ("Run A", "A"), (" tie ", "tie"),
                           ("draw", "tie")):
            self.assertEqual(judge.winner_slot({"winner": said}), want, said)

    def test_an_unreadable_winner_is_refused_not_called_a_tie(self):
        # The defect: slots.get(winner, "tie") turned this into a tie, and a tie is
        # enough for gate.py --probation to install the skill.
        for said in ("Run A (with the skill)", "neither run is complete", "", None):
            self.assertIsNone(judge.winner_slot({"winner": said}), said)


class Aggregation(unittest.TestCase):
    def run_aggregate(self, tmp, verdicts):
        brief = os.path.join(tmp, "brief.json")
        json.dump({"id": "b1", "prompt": "p", "verify": "true"}, open(brief, "w"))
        for i, v in enumerate(verdicts, 1):
            d = os.path.join(tmp, "runs", "b1", f"s{i}")
            os.makedirs(d)
            json.dump(v, open(os.path.join(d, "verdict.json"), "w"))
        env = dict(os.environ, FORGE_ROOT=tmp, PYTHONDONTWRITEBYTECODE="1")
        out = subprocess.run([sys.executable, AGGREGATE, brief], env=env,
                             capture_output=True, text=True)
        path = os.path.join(tmp, "runs", "b1", "verdict.json")
        got = json.load(open(path)) if os.path.exists(path) else None
        return out, got

    def sample(self, arm, **kw):
        v = {"winner_arm": arm, "verify": {"with": 0, "without": 0}, "verdict": {"reasons": []}}
        v.update(kw)
        return v

    def test_three_wins_aggregate_to_a_win(self):
        with tempfile.TemporaryDirectory() as tmp:
            out, got = self.run_aggregate(tmp, [self.sample("with")] * 3)
            self.assertEqual(out.returncode, 0, out.stderr)
            self.assertEqual(got["winner_arm"], "with")
            self.assertEqual(got["wins"]["with"], 3)

    def test_an_unreadable_sample_stops_the_tally_instead_of_counting_as_a_tie(self):
        with tempfile.TemporaryDirectory() as tmp:
            out, got = self.run_aggregate(
                tmp, [self.sample("with"), self.sample("Run A"), self.sample("with")])
            self.assertNotEqual(out.returncode, 0)
            self.assertIn("rejudge that sample", out.stderr)
            self.assertIsNone(got)

    def test_a_non_blind_sample_is_dropped_and_named(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = self.sample("invalid", invalid=True,
                              invalid_reason="an arm named the skill under test in its "
                                             "final message (li-post-fede), so this pair "
                                             "was not judged blind")
            out, got = self.run_aggregate(tmp, [bad, bad])
            self.assertEqual(out.returncode, 0, out.stderr)
            self.assertTrue(got["invalid"])
            self.assertIn("named the skill", got["invalid_reason"])
            self.assertNotIn("fix the brief", got["invalid_reason"])

    def test_one_non_blind_sample_does_not_sink_the_other_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = self.sample("invalid", invalid=True, invalid_reason="not judged blind")
            out, got = self.run_aggregate(tmp, [bad, self.sample("with"), self.sample("with")])
            self.assertEqual(out.returncode, 0, out.stderr)
            self.assertEqual(got["valid_samples"], 2)
            self.assertEqual(got["winner_arm"], "with")



class UnpassableBrief(unittest.TestCase):
    """A brief that keeps failing its own gate should not cost the full three samples.

    The first real one was a design brief whose verify demanded a flawless final
    message: both arms failed it, and the loop went on spending half an hour per arm
    twice more. But one such sample does not prove the gate is unpassable, only that
    this pair did not pass it, and stopping on the first would throw away the verdict a
    second sample might have produced under a strict but passable gate. Two in a row is
    what stops the run.
    """

    FORGE = os.path.join(SCRIPTS, "forge.sh")

    def build(self, tmp, codes):
        """A copy of forge.sh next to stubs, so the real loop body runs on fake spend.

        `codes` is one entry per sample: an invalid_code, or None for a clean verdict.
        """
        here = os.path.join(tmp, "scripts")
        os.makedirs(here)
        shutil.copy(self.FORGE, os.path.join(here, "forge.sh"))
        counter = os.path.join(tmp, "runs.txt")
        with open(os.path.join(here, "run_eval.sh"), "w") as fh:
            fh.write('#!/usr/bin/env bash\necho "$2" >> %s\n' % counter)
        bodies = [json.dumps({"brief": "b1", "winner_arm": "invalid",
                              "verify": {"with": 1}, "invalid_code": c} if c else
                             {"brief": "b1", "winner_arm": "with", "verify": {"with": 0}})
                  for c in codes]
        with open(os.path.join(here, "judge.py"), "w") as fh:
            fh.write("#!/usr/bin/env python3\nimport sys\n"
                     "n = int(sys.argv[sys.argv.index('--sample') + 1])\n"
                     "print(%r[n - 1])\n" % (bodies,))
        for stub in ("aggregate.py", "gate.py"):
            with open(os.path.join(here, stub), "w") as fh:
                fh.write("#!/usr/bin/env python3\n")
        brief = os.path.join(tmp, "brief.json")
        with open(brief, "w") as fh:
            json.dump({"id": "b1", "prompt": "p", "verify": "true"}, fh)
        skill = os.path.join(tmp, "skill")
        os.makedirs(skill)
        return here, brief, skill, counter

    def samples_run(self, *codes):
        with tempfile.TemporaryDirectory() as tmp:
            here, brief, skill, counter = self.build(tmp, codes)
            env = dict(os.environ, FORGE_ROOT=os.path.join(tmp, "forge"),
                       FORGE_SKIP_SCORE="1", PYTHONDONTWRITEBYTECODE="1")
            out = subprocess.run(["bash", os.path.join(here, "forge.sh"), "--brief", brief,
                                  "--skill-dir", skill, "--samples", str(len(codes))],
                                 env=env, capture_output=True, text=True)
            self.assertEqual(out.returncode, 0, out.stderr)
            with open(counter) as fh:
                arms = fh.read().split() if os.path.exists(counter) else []
            return len(arms) // 2, out.stderr

    BOTH = "both_arms_failed_verify"

    def test_two_failed_gates_running_stop_the_brief(self):
        n, err = self.samples_run(self.BOTH, self.BOTH, self.BOTH)
        self.assertEqual(n, 2, "the third sample was going to repeat the other two")
        self.assertIn("twice running", err)

    def test_one_failed_gate_does_not_stop_the_brief(self):
        # A strict gate can fail one pair and pass the next, and that next sample is a
        # verdict. Stopping on the first would have thrown it away to save an hour.
        n, err = self.samples_run(self.BOTH, None, None)
        self.assertEqual(n, 3)
        self.assertNotIn("twice running", err)

    def test_the_count_is_consecutive_not_cumulative(self):
        # Needs a fourth sample to be able to fail: over three, a running count and a
        # cumulative one both reach two only on the last one, which has already run.
        n, _ = self.samples_run(self.BOTH, None, self.BOTH, None)
        self.assertEqual(n, 4, "a clean sample in between clears the count")

    def test_a_pair_that_was_not_blind_does_not_stop_the_run(self):
        # Chance, not a property of the brief: the next sample may well be blind.
        n, _ = self.samples_run(*(["skill_named_in_final"] * 3))
        self.assertEqual(n, 3)

    def test_a_normal_verdict_runs_every_sample(self):
        n, _ = self.samples_run(None, None, None)
        self.assertEqual(n, 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
