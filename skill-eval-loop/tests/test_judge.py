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

    def test_the_load_rate_counts_the_samples_that_did_not_load(self):
        # Over valid samples only this would read 1 of 1: the sample thrown out *for*
        # never loading the skill is the one the number exists to report.
        with tempfile.TemporaryDirectory() as tmp:
            missed = self.sample("invalid", invalid=True, invalid_code="skill_never_loaded",
                                 skills_loaded={"with": []})
            hit = self.sample("with", skills_loaded={"with": ["li-post-fede"]})
            out, got = self.run_aggregate(tmp, [missed, hit])
            self.assertEqual(out.returncode, 0, out.stderr)
            self.assertEqual(got["skill_loads"], {"loaded": 1, "of": 2})

    def test_a_codex_sample_is_left_out_of_the_load_rate_entirely(self):
        # Not counted as a miss: Codex records no skill call, so counting its zero
        # would report a discovery problem that is only a transcript format.
        with tempfile.TemporaryDirectory() as tmp:
            blind = self.sample("with", skills_loaded={"with": []},
                                loads_knowable={"with": False})
            hit = self.sample("with", skills_loaded={"with": ["li-post-fede"]})
            out, got = self.run_aggregate(tmp, [blind, hit])
            self.assertEqual(got["skill_loads"], {"loaded": 1, "of": 1})


class GateFloor(unittest.TestCase):
    """Dropping invalid samples must not quietly undo the majority rule.

    Three samples exist so one lucky run cannot adopt a skill. A real 2-1 adoption on
    record survived losing both samples whose with-arm never loaded the skill, which
    left one run holding it - a majority of one.
    """

    GATE = os.path.join(SCRIPTS, "gate.py")

    def decide(self, verdict, *args):
        with tempfile.TemporaryDirectory() as tmp:
            brief = os.path.join(tmp, "brief.json")
            json.dump({"id": "b1", "prompt": "p", "verify": "true"}, open(brief, "w"))
            runs = os.path.join(tmp, "runs", "b1")
            os.makedirs(runs)
            json.dump(verdict, open(os.path.join(runs, "verdict.json"), "w"))
            skill = os.path.join(tmp, "demo-skill")
            os.makedirs(skill)
            open(os.path.join(skill, "SKILL.md"), "w").write("---\nname: demo-skill\n---\n")
            env = dict(os.environ, FORGE_ROOT=tmp, PYTHONDONTWRITEBYTECODE="1")
            out = subprocess.run([sys.executable, self.GATE, brief, skill,
                                  "--adopt-dir", os.path.join(tmp, "adopted"), *args],
                                 env=env, capture_output=True, text=True)
            self.assertEqual(out.returncode, 0, out.stderr)
            row = json.loads(open(os.path.join(tmp, "ledger.jsonl")).read().strip())
            return out.stdout, row

    def won(self, **kw):
        v = {"brief": "b1", "winner_arm": "with", "verify": {"with": 0, "without": 1},
             "tool_errors": {"with": 0, "without": 0}, "verdict": {"reasons": []},
             "samples": 3, "valid_samples": 3}
        v.update(kw)
        return v

    def test_a_win_on_one_valid_sample_is_not_adopted(self):
        out, row = self.decide(self.won(valid_samples=1))
        self.assertEqual(row["decision"], "reject")
        self.assertIn("one run is an anecdote", out)

    def test_the_same_win_on_two_valid_samples_is_adopted(self):
        out, row = self.decide(self.won(valid_samples=2))
        self.assertEqual(row["decision"], "adopt")

    def test_probation_is_refused_on_a_thin_verdict_too(self):
        # Probation installs the skill, so the floor has to hold on this path as well.
        out, row = self.decide(self.won(winner_arm="tie", valid_samples=1), "--probation")
        self.assertEqual(row["decision"], "reject")

    def test_a_verdict_written_before_the_field_existed_still_decides(self):
        v = self.won()
        del v["valid_samples"]
        out, row = self.decide(v)
        self.assertEqual(row["decision"], "adopt")

    def test_the_eval_load_rate_reaches_the_ledger(self):
        # The recheck asks this of production weeks later; the row it reads now carries
        # the eval's own answer, which is the earliest a zero can be seen coming.
        out, row = self.decide(self.won(skill_loads={"loaded": 2, "of": 3}))
        self.assertEqual(row["eval_skill_loads"], {"loaded": 2, "of": 3})



class SkillActuallyLoaded(unittest.TestCase):
    """Installing a skill in an arm is not the same as the arm using it.

    Three of 39 real with-arms never called the skill they were given, in both of the
    briefs whose skill went on to be adopted. Those samples were scored as with-arm
    results; one of them was a win credited to a skill that never executed, and dropping
    the two bad samples from that brief leaves a 2-1 adoption resting on one run.
    """

    def transcript(self, tmp, lines, agent="claude"):
        meta = os.path.join(tmp, "with.meta")
        os.makedirs(meta)
        with open(os.path.join(meta, "transcript.jsonl"), "w") as fh:
            for obj in lines:
                fh.write(json.dumps(obj) + "\n")
        json.dump({"agent": agent}, open(os.path.join(meta, "run.json"), "w"))
        return meta

    def claude_call(self, name):
        return {"message": {"role": "assistant", "content": [
            {"type": "tool_use", "name": "Skill", "input": {"skill": name}}]}}

    def opencode_call(self, name):
        return {"part": {"type": "tool", "tool": "skill",
                         "state": {"status": "completed", "input": {"name": name}}}}

    def test_claude_and_opencode_spellings_are_both_read(self):
        # Read off real transcripts, not assumed: the same guess has produced the same
        # bug three times in this loop, most recently in the measurement that found it.
        for call in (self.claude_call, self.opencode_call):
            with tempfile.TemporaryDirectory() as tmp:
                meta = self.transcript(tmp, [call("li-post-fede")])
                self.assertEqual(judge.skills_loaded(meta), ({"li-post-fede"}, True))

    def test_a_plugin_invocation_counts_as_the_bare_name(self):
        # Installed, adopted and revoked under the bare name, so that is what it joins on.
        with tempfile.TemporaryDirectory() as tmp:
            meta = self.transcript(tmp, [self.claude_call("floom:li-post-fede")])
            self.assertEqual(judge.skills_loaded(meta)[0], {"li-post-fede"})

    def test_an_arm_that_loaded_nothing_reads_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            meta = self.transcript(tmp, [{"message": {"role": "assistant", "content": [
                {"type": "tool_use", "name": "Bash", "input": {"command": "ls"}}]}}])
            self.assertEqual(judge.skills_loaded(meta), (set(), True))

    def arm(self, skills=("li-post-fede",), loaded=(), knowable=True):
        return {"skills": list(skills), "loaded": list(loaded), "loads_knowable": knowable}

    def test_a_with_arm_that_skipped_its_skill_invalidates_the_pair(self):
        self.assertTrue(judge.never_used_its_skill(self.arm()))

    def test_an_arm_that_used_its_skill_is_a_real_arm(self):
        self.assertFalse(judge.never_used_its_skill(self.arm(loaded=("li-post-fede",))))

    def test_the_baseline_arm_is_not_faulted_for_loading_nothing(self):
        # The without-arm is supposed to have no skill; reading it the same way would
        # mark every single pair invalid.
        self.assertFalse(judge.never_used_its_skill(self.arm(skills=())))

    def test_an_unknowable_zero_does_not_invalidate_the_pair(self):
        self.assertFalse(judge.never_used_its_skill(self.arm(knowable=False)))

    def test_a_codex_zero_is_reported_as_unknowable(self):
        # Codex records no skill call at all, so enforcing on its zero would invalidate
        # every Codex sample the loop ever runs and quietly delete the second runner.
        with tempfile.TemporaryDirectory() as tmp:
            meta = self.transcript(tmp, [self.claude_call("li-post-fede")], agent="codex")
            self.assertEqual(judge.skills_loaded(meta, "codex"), (set(), False))

    def test_a_baseline_holding_a_rival_is_held_to_the_same_bar(self):
        # Under --rival the baseline arm is the skill already installed for this
        # trigger. A rival that was never loaded makes the baseline an empty machine
        # again, and the ledger would record a head-to-head that did not happen.
        self.assertTrue(judge.never_used_its_skill(self.arm(skills=("fede-linkedin-post",))))

    def test_a_baseline_that_loaded_its_rival_is_a_real_baseline(self):
        self.assertFalse(judge.never_used_its_skill(
            self.arm(skills=("fede-linkedin-post",), loaded=("fede-linkedin-post",))))


class RivalBaseline(unittest.TestCase):
    """What the win was against has to be read off the run, not off the flag.

    Every arm the loop has ever run had exactly one skill installed on the with side
    and none on the without side, while adoption puts the skill into a fleet of 314
    where several others answer the same trigger. --rival makes the baseline the
    incumbent; these pin down that a row cannot claim that comparison unless it
    happened.
    """

    GATE = os.path.join(SCRIPTS, "gate.py")

    def run_gate(self, verdict, *args):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        brief = os.path.join(tmp, "brief.json")
        json.dump({"id": "b1", "prompt": "p", "verify": "true"}, open(brief, "w"))
        runs = os.path.join(tmp, "runs", "b1")
        os.makedirs(runs)
        json.dump(verdict, open(os.path.join(runs, "verdict.json"), "w"))
        skill = os.path.join(tmp, "demo-skill")
        os.makedirs(skill)
        open(os.path.join(skill, "SKILL.md"), "w").write("---\nname: demo-skill\n---\n")
        env = dict(os.environ, FORGE_ROOT=tmp, PYTHONDONTWRITEBYTECODE="1")
        out = subprocess.run([sys.executable, self.GATE, brief, skill,
                              "--adopt-dir", os.path.join(tmp, "adopted"), *args],
                             env=env, capture_output=True, text=True)
        ledger = os.path.join(tmp, "ledger.jsonl")
        row = (json.loads(open(ledger).read().strip())
               if os.path.exists(ledger) and open(ledger).read().strip() else None)
        return out, row

    def won(self, **kw):
        v = {"brief": "b1", "winner_arm": "with", "verify": {"with": 0, "without": 1},
             "tool_errors": {"with": 0, "without": 0}, "verdict": {"reasons": []},
             "samples": 3, "valid_samples": 3}
        v.update(kw)
        return v

    def test_a_rival_that_never_reached_the_arm_stops_the_gate(self):
        out, row = self.run_gate(self.won(), "--rival", "fede-linkedin-post")
        self.assertNotEqual(out.returncode, 0)
        self.assertIn("ran with no skill installed", out.stderr)
        self.assertIsNone(row)

    def test_the_rival_the_baseline_really_had_reaches_the_ledger(self):
        out, row = self.run_gate(
            self.won(skills_installed={"with": ["demo-skill"], "without": ["fede-linkedin-post"]}),
            "--rival", "fede-linkedin-post")
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(row["baseline_skills"], ["fede-linkedin-post"])
        self.assertIn("over fede-linkedin-post", out.stdout)

    def test_an_empty_baseline_is_recorded_as_empty_and_said_out_loud(self):
        # The honest reading of every row written before the field existed. A reader
        # who sees "ADOPTED" with nothing beside it would otherwise assume a contest.
        out, row = self.run_gate(self.won())
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(row["baseline_skills"], [])
        self.assertIn("over an empty baseline", out.stdout)
        self.assertIn("beats nothing", out.stdout)

    def test_a_baseline_skill_is_recorded_even_without_the_flag(self):
        # The row describes the run, so the field follows what was installed rather
        # than what was asked for; a caller who forgets the flag still gets the truth.
        out, row = self.run_gate(
            self.won(skills_installed={"with": ["demo-skill"], "without": ["fede-linkedin-post"]}))
        self.assertEqual(row["baseline_skills"], ["fede-linkedin-post"])
        self.assertNotIn("beats nothing", out.stdout)


class SilentArm(unittest.TestCase):
    """The never-loaded check runs on whichever arm had a skill, candidate or rival.

    End to end through judge.py with a stub model, because the rule that matters lives
    in main(): a rival the baseline never loaded turns the head-to-head the ledger is
    about to record back into the walkover --rival exists to replace.
    """

    JUDGE = os.path.join(SCRIPTS, "judge.py")

    def arm_files(self, runs, arm, skill=None, loaded=None):
        work = os.path.join(runs, arm)
        meta = work + ".meta"
        os.makedirs(work)
        os.makedirs(meta)
        open(os.path.join(work, "post.md"), "w").write("the agent's output\n")
        if skill:
            sk = os.path.join(work, ".claude", "skills", skill)
            os.makedirs(sk)
            open(os.path.join(sk, "SKILL.md"), "w").write("---\nname: %s\n---\n" % skill)
        lines = [{"message": {"role": "assistant", "content": [{"type": "text", "text": "done"}]}}]
        if loaded:
            lines.insert(0, {"message": {"role": "assistant", "content": [
                {"type": "tool_use", "name": "Skill", "input": {"skill": loaded}}]}})
        with open(os.path.join(meta, "transcript.jsonl"), "w") as fh:
            for obj in lines:
                fh.write(json.dumps(obj) + "\n")
        json.dump({"agent": "claude", "exit": 0}, open(os.path.join(meta, "run.json"), "w"))

    def judge_pair(self, without_skill=None, without_loaded=None):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        stub = os.path.join(tmp, "stub")
        os.makedirs(stub)
        open(os.path.join(stub, "forge_llm.py"), "w").write(
            "def call_model(prompt, model=None):\n"
            "    return '{\"winner\": \"A\", \"reasons\": []}', 'stub'\n")
        brief = os.path.join(tmp, "brief.json")
        json.dump({"id": "b1", "prompt": "p", "verify": "true"}, open(brief, "w"))
        runs = os.path.join(tmp, "runs", "b1", "s1")
        self.arm_files(runs, "with", skill="demo-skill", loaded="demo-skill")
        self.arm_files(runs, "without", skill=without_skill, loaded=without_loaded)
        env = dict(os.environ, FORGE_ROOT=tmp, PYTHONPATH=stub, PYTHONDONTWRITEBYTECODE="1")
        out = subprocess.run([sys.executable, self.JUDGE, brief, "--sample", "1"],
                             env=env, capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        return json.load(open(os.path.join(runs, "verdict.json")))

    def test_an_empty_baseline_is_still_a_valid_pair(self):
        v = self.judge_pair()
        self.assertFalse(v.get("invalid"), v.get("invalid_reason"))

    def test_a_baseline_that_never_loaded_its_rival_invalidates_the_pair(self):
        v = self.judge_pair(without_skill="fede-linkedin-post")
        self.assertEqual(v["invalid_code"], "skill_never_loaded")
        self.assertIn("the without-arm never loaded fede-linkedin-post", v["invalid_reason"])
        self.assertEqual(v["winner_arm"], "invalid")

    def test_a_baseline_that_loaded_its_rival_is_a_real_comparison(self):
        v = self.judge_pair(without_skill="fede-linkedin-post",
                            without_loaded="fede-linkedin-post")
        self.assertFalse(v.get("invalid"), v.get("invalid_reason"))
        self.assertEqual(v["skills_installed"]["without"], ["fede-linkedin-post"])


class ArmInstall(unittest.TestCase):
    """Which arm gets a skill is decided by what it was handed, not by its name.

    The baseline arm was hardcoded to install nothing, so every verdict the loop has
    ever written compares a candidate against an empty machine. A stub agent on PATH
    stands in for the CLI: nothing here spends a model call.
    """

    RUN = os.path.join(SCRIPTS, "run_eval.sh")

    def run_arm(self, arm, skill_dir="", skill="fede-linkedin-post"):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        bin_ = os.path.join(tmp, "bin")
        os.makedirs(bin_)
        stub = os.path.join(bin_, "claude")
        open(stub, "w").write("#!/usr/bin/env bash\nexit 0\n")
        os.chmod(stub, 0o755)
        if skill_dir:
            skill_dir = os.path.join(tmp, skill_dir)
            os.makedirs(skill_dir)
            open(os.path.join(skill_dir, "SKILL.md"), "w").write("---\nname: %s\n---\n" % skill)
        brief = os.path.join(tmp, "brief.json")
        json.dump({"id": "b1", "prompt": "p", "verify": "true"}, open(brief, "w"))
        root = os.path.join(tmp, "forge")
        env = dict(os.environ, FORGE_ROOT=root, FORGE_SAMPLE="1",
                   PATH=bin_ + os.pathsep + os.environ["PATH"], PYTHONDONTWRITEBYTECODE="1")
        out = subprocess.run(["bash", self.RUN, brief, arm, skill_dir],
                             env=env, capture_output=True, text=True)
        return out, os.path.join(root, "runs", "b1", "s1", arm, ".claude", "skills")

    def test_a_baseline_handed_a_rival_installs_it(self):
        out, skills = self.run_arm("without", "rival")
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertTrue(os.path.exists(os.path.join(skills, "rival", "SKILL.md")))

    def test_a_baseline_handed_nothing_stays_empty(self):
        out, skills = self.run_arm("without")
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertFalse(os.path.exists(skills))

    def test_a_with_arm_still_refuses_to_run_without_a_skill(self):
        # The one asymmetry that survives: a candidate arm with no candidate in it is
        # not a cheaper eval, it is a pair of identical runs scored as a comparison.
        out, _ = self.run_arm("with")
        self.assertNotEqual(out.returncode, 0)
        self.assertIn("with-arm needs a skill dir", out.stderr)

    def test_a_skill_dir_that_does_not_exist_stops_the_arm(self):
        out, _ = self.run_arm("without", skill_dir="")  # baseline with nothing is fine
        self.assertEqual(out.returncode, 0)
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        brief = os.path.join(tmp, "brief.json")
        json.dump({"id": "b1", "prompt": "p", "verify": "true"}, open(brief, "w"))
        env = dict(os.environ, FORGE_ROOT=os.path.join(tmp, "forge"), FORGE_SAMPLE="1",
                   PYTHONDONTWRITEBYTECODE="1")
        out = subprocess.run(["bash", self.RUN, brief, "without", os.path.join(tmp, "gone")],
                             env=env, capture_output=True, text=True)
        self.assertNotEqual(out.returncode, 0)
        self.assertIn("no such skill dir", out.stderr)


class RivalPlumbing(unittest.TestCase):
    """--rival has to reach both the baseline arm and the ledger, or it is decoration."""

    FORGE = os.path.join(SCRIPTS, "forge.sh")

    def run_forge(self, *extra):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        here = os.path.join(tmp, "scripts")
        os.makedirs(here)
        shutil.copy(self.FORGE, os.path.join(here, "forge.sh"))
        arms = os.path.join(tmp, "arms.txt")
        gate = os.path.join(tmp, "gate.txt")
        open(os.path.join(here, "run_eval.sh"), "w").write(
            '#!/usr/bin/env bash\necho "$2|${3:-}" >> %s\n' % arms)
        open(os.path.join(here, "judge.py"), "w").write(
            "#!/usr/bin/env python3\nprint('%s')\n"
            % json.dumps({"brief": "b1", "winner_arm": "with", "verify": {"with": 0}}))
        open(os.path.join(here, "aggregate.py"), "w").write("#!/usr/bin/env python3\n")
        open(os.path.join(here, "gate.py"), "w").write(
            "#!/usr/bin/env python3\nimport sys\n"
            "open(%r, 'w').write(' '.join(sys.argv[1:]))\n" % gate)
        brief = os.path.join(tmp, "brief.json")
        json.dump({"id": "b1", "prompt": "p", "verify": "true"}, open(brief, "w"))
        skill = os.path.join(tmp, "demo-skill")
        os.makedirs(skill)
        env = dict(os.environ, FORGE_ROOT=os.path.join(tmp, "forge"),
                   FORGE_SKIP_SCORE="1", PYTHONDONTWRITEBYTECODE="1")
        out = subprocess.run(["bash", os.path.join(here, "forge.sh"), "--brief", brief,
                              "--skill-dir", skill, "--samples", "1", *extra],
                             env=env, capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        return open(arms).read().split(), open(gate).read(), skill

    def test_without_a_rival_the_baseline_arm_is_handed_nothing(self):
        armlog, gateargs, skill = self.run_forge()
        self.assertEqual(armlog, ["without|", "with|" + skill])
        self.assertNotIn("--rival", gateargs)

    def test_a_rival_reaches_the_baseline_arm_and_the_gate(self):
        armlog, gateargs, skill = self.run_forge("--rival", "/skills/incumbent")
        self.assertEqual(armlog, ["without|/skills/incumbent", "with|" + skill])
        self.assertIn("--rival /skills/incumbent", gateargs)


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
