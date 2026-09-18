#!/usr/bin/env python3
"""Fixture tests for the Harbor task renderer.

Stdlib only, no Docker and no model calls: every test renders a brief and checks
what the generated task would and would not tell an agent.

Most of these pin blindness, because that is what moving to Harbor is for. The
local runner installed the skill by hand into a path it had to know per runner,
got that path wrong, and put the skill's name in the judge's prompt on two of the
three runners. Under Harbor the without arm's container is never given the files,
which only holds while the generated task keeps its hands off two things:
environment.skills_dir, and the instruction text.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(os.path.dirname(HERE), "scripts")
sys.path.insert(0, SCRIPTS)
import harbor_task  # noqa: E402

RUNNER = os.path.join(SCRIPTS, "run_eval_harbor.sh")

BRIEF = {
    "id": "li-post-fede-001",
    "prompt": "Write a LinkedIn post about the release. Save it as post.md.",
    "verify": "test -s post.md",
}


def render(tmp, **over):
    brief = dict(BRIEF, **over)
    out = os.path.join(tmp, "task")
    harbor_task.render(brief, out)
    return out


def read(out, *parts):
    return open(os.path.join(out, *parts)).read()


class Blindness(unittest.TestCase):
    def test_the_task_never_sets_skills_dir(self):
        # With it set, Trial._resolve_effective_skills_dir() returns a path in
        # both arms, so the without arm gets an empty skills directory the with
        # arm has content in. Left unset, the without arm has no such directory.
        with tempfile.TemporaryDirectory() as tmp:
            self.assertNotIn("skills_dir", read(render(tmp), "task.toml"))

    def test_the_instruction_is_the_prompt_and_says_nothing_about_skills(self):
        # Harbor's hello-skills example opens with "You have a skill installed
        # called generate-greeting". That sentence in a blind pair is the leak.
        with tempfile.TemporaryDirectory() as tmp:
            text = read(render(tmp), "instruction.md")
            self.assertEqual(text, BRIEF["prompt"])
            self.assertNotIn("skill", text.lower())

    def test_the_image_carries_no_skill(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = render(tmp, setup="mkdir -p /app/fixtures")
            self.assertNotIn("skill", read(out, "environment", "Dockerfile").lower())
            self.assertFalse(os.path.exists(os.path.join(out, "environment", "skills")))

    def test_both_arms_render_the_same_bytes(self):
        # The renderer takes no arm argument, and nothing about it may depend on
        # one: the only difference between the arms is Harbor's --skill flag.
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            for part in (("task.toml",), ("instruction.md",),
                         ("environment", "Dockerfile")):
                self.assertEqual(read(render(a), *part), read(read_b := render(b), *part))
            self.assertTrue(read_b)


class Rendering(unittest.TestCase):
    def test_setup_is_baked_into_the_image(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = render(tmp, setup="pip install ruff\nmkdir -p /app/src")
            docker = read(out, "environment", "Dockerfile")
            self.assertIn("RUN pip install ruff", docker)
            self.assertIn("RUN mkdir -p /app/src", docker)

    def test_a_brief_with_no_setup_still_builds(self):
        with tempfile.TemporaryDirectory() as tmp:
            docker = read(render(tmp), "environment", "Dockerfile")
            self.assertIn("WORKDIR /app", docker)
            self.assertNotIn("RUN \n", docker)

    def test_the_workdir_is_pulled_back_as_an_artifact(self):
        # Without this the arm's workdir arrives empty and the judge compares
        # two runs by their final messages alone.
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIn('source = "/app"', read(render(tmp), "task.toml"))

    def test_the_task_name_survives_an_awkward_brief_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = render(tmp, id="Theme 12: DMs / voice")
            self.assertIn("skill-forge/theme-12--dms---voice", read(out, "task.toml"))

    def test_the_verifier_scores_nothing_rather_than_a_pass(self):
        # The objective gate is the brief's verify, run on the host by judge.py.
        # A Harbor reward of 1 here would be a second, different gate.
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIn("echo 0 > /logs/verifier/reward.txt",
                          read(render(tmp), "tests", "test.sh"))

    def test_a_brief_without_a_prompt_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "b.json")
            json.dump({"id": "x"}, open(path, "w"))
            out = subprocess.run([sys.executable, harbor_task.__file__, path,
                                  os.path.join(tmp, "task")],
                                 capture_output=True, text=True)
            self.assertNotEqual(out.returncode, 0)
            self.assertIn("no prompt", out.stderr)


class RunnerContract(unittest.TestCase):
    """The runner must stay a drop-in for run_eval.sh, or judge.py cannot read it."""

    def setUp(self):
        self.text = open(RUNNER).read()

    def test_it_writes_the_layout_judge_expects(self):
        for token in ('DIR="$BASE/$ARM"', 'META="$BASE/$ARM.meta"',
                      "transcript.jsonl", "run.json"):
            self.assertIn(token, self.text)

    def test_the_skill_is_dereferenced_before_upload(self):
        # Deployed skills are symlinks; Harbor uploads the directory as it finds
        # it, so a link arrives dangling and the with arm has no skill at all.
        self.assertIn("cp -rL", self.text)

    def test_the_token_is_never_an_argument(self):
        # It goes through the environment. In argv it would reach the process
        # list, and from a failed run into the log we keep.
        self.assertNotIn("--token", self.text)
        # Naming the variable in an error message is how the operator learns what
        # to set; expanding it is the leak. Only the expansion is a failure.
        for line in self.text.splitlines():
            printed = ("echo" in line or "printf" in line)
            if printed and ("$CLAUDE_CODE_OAUTH_TOKEN" in line
                            or "${CLAUDE_CODE_OAUTH_TOKEN" in line):
                self.fail(f"token reaches a log: {line.strip()}")

    def test_a_sudo_run_hands_the_job_tree_back(self):
        # Harbor under sudo writes its jobs tree as root; the pull-back step runs as
        # the invoking user and died on PermissionError reading the agent's own
        # session log, after a full container run had been paid for.
        self.assertIn('chown -R "$(id -u):$(id -g)" "$META/jobs"', self.text)
        chown = self.text.index("chown -R")
        self.assertLess(chown, self.text.index("Harbor writes one trial per job"),
                        "the chown has to come before anything reads the tree")

    def test_sudo_passes_named_variables_not_the_whole_environment(self):
        self.assertIn("sudo -n env", self.text)
        self.assertNotIn("sudo -nE", self.text)
        self.assertNotIn("sudo -E", self.text)


class RivalArm(unittest.TestCase):
    """--skill follows what the arm was handed, not the arm's name.

    The two runners have to agree about this or a rival baseline silently becomes an
    empty one on Harbor. A stub harbor records its argv; nothing here starts a
    container or spends a token.
    """

    def harbor_argv(self, arm, skill=None):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        bin_ = os.path.join(tmp, "bin")
        os.makedirs(bin_)
        log = os.path.join(tmp, "argv.txt")
        stub = os.path.join(bin_, "harbor")
        open(stub, "w").write('#!/usr/bin/env bash\nprintf "%s\\n" "$@" > ' + log + "\nexit 1\n")
        os.chmod(stub, 0o755)
        task = os.path.join(tmp, "task")
        os.makedirs(task)
        if skill:
            skill = os.path.join(tmp, skill)
            os.makedirs(skill)
            open(os.path.join(skill, "SKILL.md"), "w").write("---\nname: rival\n---\n")
        brief = os.path.join(tmp, "brief.json")
        json.dump({"id": "b1", "prompt": "p", "verify": "true"}, open(brief, "w"))
        # opencode: the claude path reaches for a subscription token before it ever
        # builds the argv, and this test is about the argv.
        env = dict(os.environ, FORGE_ROOT=os.path.join(tmp, "forge"), FORGE_TASK_DIR=task,
                   FORGE_SAMPLE="1", FORGE_AGENT="opencode",
                   PATH=bin_ + os.pathsep + os.environ["PATH"], PYTHONDONTWRITEBYTECODE="1")
        out = subprocess.run(["bash", RUNNER, brief, arm, skill or ""],
                             env=env, capture_output=True, text=True)
        self.assertTrue(os.path.exists(log),
                        "harbor was never invoked, so the argv proves nothing: "
                        + out.stderr)
        return open(log).read().split()

    def test_a_baseline_handed_a_rival_gets_the_skill_flag(self):
        argv = self.harbor_argv("without", "incumbent")
        self.assertIn("--skill", argv)
        self.assertTrue(any(a.endswith("/incumbent") for a in argv), argv)

    def test_a_baseline_handed_nothing_still_gets_no_skill_flag(self):
        # This is what keeps the Harbor blind: no flag, no skills directory in the
        # container, nothing for the agent to notice.
        self.assertNotIn("--skill", self.harbor_argv("without"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
