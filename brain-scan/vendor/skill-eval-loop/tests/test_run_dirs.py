#!/usr/bin/env python3
"""The sample directory guard in the two runners.

Both runners refuse to start into a directory an earlier pass left behind. The
check used to cover only the agent's workdir, which is the half nothing reads: the
verdict is assembled out of <arm>.meta, and of the four files there only final.txt
survives a rerun, because nothing but the codex arm ever writes it and no arm
truncates it. So a run into a leftover .meta is judged on the previous run's answer.

These call the real scripts and assert on the refusal, which happens before any
agent binary is looked for, so nothing here needs claude, codex or harbor
installed. Stdlib only, no model calls.
"""
import json
import os
import subprocess
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(os.path.dirname(HERE), "scripts")


class SampleDirGuard(unittest.TestCase):
    runner = "run_eval.sh"

    def run_arm(self, root, arm="with", sample="1", skill=None):
        brief = os.path.join(root, "brief.json")
        with open(brief, "w") as fh:
            json.dump({"id": "b1", "prompt": "p", "verify": "true"}, fh)
        env = dict(os.environ, FORGE_ROOT=root, FORGE_SAMPLE=sample,
                   FORGE_AGENT="nosuchagent")
        return subprocess.run(["bash", os.path.join(SCRIPTS, self.runner), brief, arm,
                               skill or ""], capture_output=True, text=True, env=env)

    def sample_dir(self, root, arm="with", sample="1"):
        return os.path.join(root, "runs", "b1", "s" + sample, arm)

    def test_a_leftover_meta_dir_stops_the_run(self):
        """The half the judge reads. This is the case the old guard let through."""
        with tempfile.TemporaryDirectory() as root:
            meta = self.sample_dir(root) + ".meta"
            os.makedirs(meta)
            with open(os.path.join(meta, "final.txt"), "w") as fh:
                fh.write("a previous run's answer")
            out = self.run_arm(root)
            self.assertEqual(out.returncode, 1, out.stderr)
            self.assertIn("refusing", out.stderr)
            self.assertIn(".meta", out.stderr)

    def test_a_leftover_meta_keeps_its_contents(self):
        """Refusing, not cleaning: the earlier run's evidence is still there to read."""
        with tempfile.TemporaryDirectory() as root:
            meta = self.sample_dir(root) + ".meta"
            os.makedirs(meta)
            with open(os.path.join(meta, "final.txt"), "w") as fh:
                fh.write("a previous run's answer")
            self.run_arm(root)
            with open(os.path.join(meta, "final.txt")) as fh:
                self.assertEqual(fh.read(), "a previous run's answer")

    def test_a_leftover_workdir_stops_the_run(self):
        with tempfile.TemporaryDirectory() as root:
            os.makedirs(self.sample_dir(root))
            out = self.run_arm(root)
            self.assertEqual(out.returncode, 1, out.stderr)
            self.assertIn("refusing", out.stderr)

    def test_the_message_says_how_to_rerun(self):
        """A refusal nobody can act on gets worked around by renaming the brief, and
        then the ledger carries two ids for one question."""
        with tempfile.TemporaryDirectory() as root:
            os.makedirs(self.sample_dir(root))
            self.assertIn("delete the sample dir to rerun", self.run_arm(root).stderr)

    def test_a_fresh_sample_dir_is_not_refused(self):
        """The negative control: the guard has to let a first run through."""
        with tempfile.TemporaryDirectory() as root:
            out = self.run_arm(root)
            self.assertNotIn("refusing", out.stderr)

    def test_the_other_arm_of_the_same_sample_is_not_refused(self):
        """with and without share s<N>/ and must not see each other's dirs."""
        with tempfile.TemporaryDirectory() as root:
            os.makedirs(self.sample_dir(root, "without") + ".meta")
            out = self.run_arm(root, "with")
            self.assertNotIn("refusing", out.stderr)

    def test_the_next_sample_is_not_refused(self):
        """Sample 2 runs after sample 1 has left both dirs behind."""
        with tempfile.TemporaryDirectory() as root:
            os.makedirs(self.sample_dir(root, "with", "1") + ".meta")
            os.makedirs(self.sample_dir(root, "with", "1"))
            out = self.run_arm(root, "with", "2")
            self.assertNotIn("refusing", out.stderr)


class HarborSampleDirGuard(SampleDirGuard):
    """The same guard in the Harbor runner, which builds its verdict from the same
    .meta layout and had the same half-check."""
    runner = "run_eval_harbor.sh"


if __name__ == "__main__":
    unittest.main(verbosity=2)
