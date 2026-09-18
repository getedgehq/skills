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

    # The Harbor runner never installs into the workdir: it resolves the skill into
    # <arm>.meta/skill/<name> and hands that to the container. Scanning the workdir
    # alone reported every Harbor with-arm as having no skill installed, which is what
    # the first real Harbor pair recorded, and with no installed name neither the
    # never-loaded check nor the blindness check can fire.

    def harbor_meta(self, tmp, name="tldr-replies"):
        meta = os.path.join(tmp, "with.meta")
        handed = os.path.join(meta, "skill", name)
        os.makedirs(handed)
        with open(os.path.join(handed, "SKILL.md"), "w") as fh:
            fh.write("---\nname: %s\n---\n" % name)
        return meta

    def test_the_skill_handed_to_a_container_counts_as_installed(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = arm_dir(tmp, None, work=("post.md",))
            self.assertEqual(judge.skill_trees(d), {})
            trees = judge.skill_trees(d, self.harbor_meta(tmp))
            self.assertEqual(sorted(trees), ["tldr-replies"])

    def test_the_handed_skill_never_reaches_the_file_list(self):
        # It lives outside the workdir, so the manifest cannot leak it either way.
        with tempfile.TemporaryDirectory() as tmp:
            d = arm_dir(tmp, None, work=("post.md",))
            trees = judge.skill_trees(d, self.harbor_meta(tmp))
            self.assertNotIn("tldr-replies", judge.manifest(d, hide=trees.values()))

    def test_a_meta_dir_with_no_skill_adds_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = arm_dir(tmp, None, work=("post.md",))
            meta = os.path.join(tmp, "with.meta")
            os.makedirs(meta)
            self.assertEqual(judge.skill_trees(d, meta), {})

    def test_a_handed_dir_without_a_skill_md_is_not_a_skill(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = arm_dir(tmp, None, work=("post.md",))
            meta = os.path.join(tmp, "with.meta")
            os.makedirs(os.path.join(meta, "skill", "not-a-skill"))
            self.assertEqual(judge.skill_trees(d, meta), {})

    def test_the_workdir_copy_wins_over_the_handed_one(self):
        # The local runner installs into the workdir and that is the tree the agent
        # actually read; the handed copy is a second record of the same skill.
        with tempfile.TemporaryDirectory() as tmp:
            d = arm_dir(tmp, "claude")
            trees = judge.skill_trees(d, self.harbor_meta(tmp, "li-post-fede"))
            self.assertIn(".claude", trees["li-post-fede"])

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

    def test_a_verdict_that_cannot_say_is_not_a_verdict_that_says_nothing(self):
        # The two readings of a missing field, and the refusal above answers only one
        # of them. Every verdict aggregate.py wrote before it carried this field was
        # the other, so the operator was sent to rerun an eval that was already right.
        out, row = self.run_gate(self.won(), "--rival", "fede-linkedin-post")
        self.assertNotEqual(out.returncode, 0)
        self.assertIn("does not record what either arm was given", out.stderr)
        self.assertIn("spends no eval", out.stderr)
        self.assertNotIn("ran with no skill installed", out.stderr)
        self.assertIsNone(row)

    def test_a_baseline_the_runner_really_left_empty_is_still_refused(self):
        # And the other reading keeps its own message: the field is there and says the
        # baseline got nothing, which no amount of re-aggregating will change. This
        # replaces a test that asserted the same message for a verdict carrying no
        # field at all - the conflation itself, written down and passing.
        out, row = self.run_gate(
            self.won(skills_installed={"with": ["demo-skill"], "without": []}),
            "--rival", "fede-linkedin-post")
        self.assertNotEqual(out.returncode, 0)
        self.assertIn("ran with no skill installed", out.stderr)
        self.assertIsNone(row)


class RivalEndToEnd(unittest.TestCase):
    """aggregate.py and gate.py run together, over sample verdicts judge.py wrote.

    Every test above hands gate.py a verdict dict the test built. That is how a
    guard that refused 100% of the head-to-heads it was given passed its whole suite
    for eleven PRs: the fixtures carried skills_installed and the producer did not.
    These run the real chain, so a field one script stops writing fails here rather
    than in a queue log at 03:24.
    """

    def chain(self, samples, *gate_args):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        brief = os.path.join(tmp, "brief.json")
        json.dump({"id": "b1", "prompt": "p", "verify": "true"}, open(brief, "w"))
        for i, v in enumerate(samples, 1):
            d = os.path.join(tmp, "runs", "b1", f"s{i}")
            os.makedirs(d)
            json.dump(v, open(os.path.join(d, "verdict.json"), "w"))
        skill = os.path.join(tmp, "li-post-fede")
        os.makedirs(skill)
        open(os.path.join(skill, "SKILL.md"), "w").write("---\nname: li-post-fede\n---\n")
        env = dict(os.environ, FORGE_ROOT=tmp, PYTHONDONTWRITEBYTECODE="1")
        agg = subprocess.run([sys.executable, AGGREGATE, brief], env=env,
                             capture_output=True, text=True)
        if agg.returncode != 0:
            return agg, None, None
        gate = subprocess.run([sys.executable, os.path.join(SCRIPTS, "gate.py"), brief, skill,
                               "--adopt-dir", os.path.join(tmp, "adopted"), *gate_args],
                              env=env, capture_output=True, text=True)
        ledger = os.path.join(tmp, "ledger.jsonl")
        row = (json.loads(open(ledger).read().strip())
               if os.path.exists(ledger) and open(ledger).read().strip() else None)
        return agg, gate, row

    def sample(self, without=("fede-linkedin-post",), **kw):
        v = {"winner_arm": "with", "verify": {"with": 0, "without": 0},
             "verdict": {"reasons": []}, "tool_errors": {"with": 0, "without": 0},
             "skills_installed": {"with": ["li-post-fede"], "without": list(without)},
             "skills_loaded": {"with": ["li-post-fede"], "without": list(without)}}
        v.update(kw)
        return v

    def test_the_head_to_head_the_samples_record_reaches_the_ledger(self):
        # The live case: three samples, the rival installed and loaded in the baseline
        # of each, 3-0 to the candidate. This exited 1 at the gate.
        agg, gate, row = self.chain([self.sample()] * 3, "--rival", "fede-linkedin-post")
        self.assertEqual(agg.returncode, 0, agg.stderr)
        self.assertEqual(gate.returncode, 0, gate.stderr)
        self.assertEqual(row["baseline_skills"], ["fede-linkedin-post"])
        self.assertIn("over fede-linkedin-post", gate.stdout)
        self.assertNotIn("beats nothing", gate.stdout)

    def test_a_walkover_still_reads_as_a_walkover(self):
        agg, gate, row = self.chain([self.sample(without=())] * 3)
        self.assertEqual(gate.returncode, 0, gate.stderr)
        self.assertEqual(row["baseline_skills"], [])
        self.assertIn("beats nothing", gate.stdout)

    def test_an_invalid_sample_still_says_what_it_was_given(self):
        # Read off every sample, not the valid ones: an unreadable pair answers what
        # the runner installed as well as a readable one. All three invalid is what
        # separates the two, because with any valid sample left the field survives
        # either way - here, reading only the valid ones leaves nothing to read, and
        # the gate sends the operator to rerun an aggregate that would change nothing.
        dud = self.sample(winner_arm="invalid", invalid=True, invalid_reason="not blind")
        agg, gate, row = self.chain([dud] * 3, "--rival", "fede-linkedin-post")
        self.assertEqual(agg.returncode, 0, agg.stderr)
        self.assertEqual(gate.returncode, 0, gate.stderr)
        self.assertNotIn("does not record what either arm was given", gate.stderr)
        self.assertEqual(row["baseline_skills"], ["fede-linkedin-post"])
        self.assertEqual(row["decision"], "reject")

    def test_one_bad_sample_does_not_cost_the_other_two_their_contest(self):
        dud = self.sample(winner_arm="invalid", invalid=True, invalid_reason="not blind")
        agg, gate, row = self.chain([dud, self.sample(), self.sample()],
                                    "--rival", "fede-linkedin-post")
        self.assertEqual(gate.returncode, 0, gate.stderr)
        self.assertEqual(row["baseline_skills"], ["fede-linkedin-post"])

    def test_samples_given_different_baselines_are_not_one_comparison(self):
        agg, gate, row = self.chain([self.sample(), self.sample(without=())],
                                    "--rival", "fede-linkedin-post")
        self.assertNotEqual(agg.returncode, 0)
        self.assertIn("not given the same skills in every sample", agg.stderr)
        self.assertIn("s2", agg.stderr)
        self.assertIsNone(gate)

    def test_samples_that_never_recorded_it_leave_the_field_out(self):
        # Rather than writing an empty list, which gate.py would read as a baseline
        # that really ran empty and refuse with the one message re-aggregating cannot
        # fix. Pre-#36 samples are the ones this describes.
        old = {"winner_arm": "with", "verify": {"with": 0, "without": 0},
               "verdict": {"reasons": []}}
        agg, gate, row = self.chain([old] * 3, "--rival", "fede-linkedin-post")
        self.assertEqual(agg.returncode, 0, agg.stderr)
        self.assertNotEqual(gate.returncode, 0)
        self.assertIn("does not record what either arm was given", gate.stderr)


def stub_claude(tmp):
    """A fake claude CLI on PATH, and the file that records whether it was called.

    forge_llm shells out to the CLI, so shadowing the module through PYTHONPATH does
    nothing: judge.py's own script directory is sys.path[0] and the real forge_llm
    wins. Two end-to-end judge tests were quietly spending a real model call each
    because of that. Intercepting the CLI is also what lets a test assert the judge
    was never reached.
    """
    bin_ = os.path.join(tmp, "bin")
    os.makedirs(bin_, exist_ok=True)
    marker = os.path.join(tmp, "judge-calls.txt")
    path = os.path.join(bin_, "claude")
    with open(path, "w") as fh:
        fh.write("#!/usr/bin/env bash\n"
                 "echo called >> %s\n"
                 "printf '%%s' '{\"result\": \"{\\\"winner\\\": \\\"A\\\", "
                 "\\\"reasons\\\": []}\"}'\n" % marker)
    os.chmod(path, 0o755)
    return bin_, marker


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

    def judge_pair(self, without_skill=None, without_loaded=None, verify="true",
                   with_loaded="demo-skill"):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        bin_, marker = stub_claude(tmp)
        brief = os.path.join(tmp, "brief.json")
        json.dump({"id": "b1", "prompt": "p", "verify": verify}, open(brief, "w"))
        runs = os.path.join(tmp, "runs", "b1", "s1")
        self.arm_files(runs, "with", skill="demo-skill", loaded=with_loaded)
        self.arm_files(runs, "without", skill=without_skill, loaded=without_loaded)
        env = dict(os.environ, FORGE_ROOT=tmp, FORGE_ENGINE="claude",
                   PATH=bin_ + os.pathsep + os.environ["PATH"], PYTHONDONTWRITEBYTECODE="1")
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

    # The first Harbor pair. Both arms failed the brief's 150-word gate and the verdict
    # read "fix the brief, not the loop" - over a brief the local runner had passed
    # three times out of three on the with side. The with-arm wrote 194 words because
    # it never loaded the skill, and that skill's whole job is to make the reply short.

    def test_a_silent_arm_outranks_a_gate_both_arms_failed(self):
        v = self.judge_pair(verify="false", with_loaded=None)
        self.assertEqual(v["invalid_code"], "skill_never_loaded")

    def test_the_failed_gate_is_still_in_the_record(self):
        """Dropping it would hide that the gate is unmeasured, not that it is fine."""
        v = self.judge_pair(verify="false", with_loaded=None)
        self.assertIn("also failed verify", v["invalid_reason"])
        self.assertIn("never loaded demo-skill", v["invalid_reason"])
        self.assertEqual(v["verify"], {"with": 1, "without": 1})

    def test_a_gate_nobody_passed_with_both_arms_loaded_is_still_the_brief(self):
        """The negative control: with nothing silent, the brief is still implicated."""
        v = self.judge_pair(verify="false")
        self.assertEqual(v["invalid_code"], "both_arms_failed_verify")

    def test_a_silent_arm_that_passed_its_gate_says_nothing_about_verify(self):
        v = self.judge_pair(with_loaded=None)
        self.assertEqual(v["invalid_code"], "skill_never_loaded")
        self.assertNotIn("also failed verify", v["invalid_reason"])


class DeadArm(unittest.TestCase):
    """An arm whose agent never started is a runner fault, not a broken brief.

    The Harbor binary was not on the sudo PATH, so both arms exited 127 in two seconds
    with empty transcripts, and judge.py recorded "both arms failed verify - fix the
    brief, not the loop" over two empty workdirs - twice, with a model call spent each
    time. The stub CLI records every call, so these tests assert the check runs before
    the judge does and not merely that the code is right.
    """

    JUDGE = os.path.join(SCRIPTS, "judge.py")

    def judge_pair(self, with_run=None, without_run=None, transcripts=True, verify="true",
                   finals=None):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        bin_, self.marker = stub_claude(tmp)
        brief = os.path.join(tmp, "brief.json")
        json.dump({"id": "b1", "prompt": "p", "verify": verify}, open(brief, "w"))
        runs = os.path.join(tmp, "runs", "b1", "s1")
        for arm, run in (("with", with_run), ("without", without_run)):
            work = os.path.join(runs, arm)
            meta = work + ".meta"
            os.makedirs(work)
            os.makedirs(meta)
            if (finals or {}).get(arm):
                open(os.path.join(meta, "final.txt"), "w").write(finals[arm])
            with open(os.path.join(meta, "transcript.jsonl"), "w") as fh:
                if transcripts:
                    fh.write(json.dumps({"message": {"role": "assistant", "content": [
                        {"type": "text", "text": "done"}]}}) + "\n")
            json.dump(run or {"agent": "claude", "exit": 0},
                      open(os.path.join(meta, "run.json"), "w"))
        env = dict(os.environ, FORGE_ROOT=tmp, FORGE_ENGINE="claude",
                   PATH=bin_ + os.pathsep + os.environ["PATH"], PYTHONDONTWRITEBYTECODE="1")
        out = subprocess.run([sys.executable, self.JUDGE, brief, "--sample", "1"],
                             env=env, capture_output=True, text=True)
        path = os.path.join(runs, "verdict.json")
        verdict = json.load(open(path)) if os.path.exists(path) else None
        return out, verdict, runs

    def judged(self):
        return os.path.exists(self.marker)

    def dead(self, error="env: 'harbor': No such file or directory"):
        return {"agent": "claude", "exit": 127, "runner": "harbor", "error": error}

    def test_a_pair_that_never_started_is_a_runner_fault_not_a_brief_fault(self):
        out, v, _ = self.judge_pair(with_run=self.dead(), without_run=self.dead(),
                                    transcripts=False, verify="false")
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(v["invalid_code"], "arm_never_ran")
        self.assertEqual(v["winner_arm"], "invalid")
        # The whole point: the old code sent the brief back for a rewrite.
        self.assertNotIn("fix the brief", v["invalid_reason"])
        self.assertIn("harbor", v["invalid_reason"])
        self.assertIn("produced no transcript", v["invalid_reason"])
        self.assertFalse(self.judged(), "a model call was spent on two empty workdirs")

    def test_one_dead_arm_is_enough(self):
        _, v, _ = self.judge_pair(without_run=self.dead(), transcripts=False)
        self.assertEqual(v["invalid_code"], "arm_never_ran")
        self.assertIn("the without-arm", v["invalid_reason"])

    def test_no_blind_mapping_is_written_for_a_pair_that_never_ran(self):
        # The rerun after the fix has to draw its own slots. A mapping left behind here
        # would be reused, and it was drawn for a pair that produced nothing.
        _, _, runs = self.judge_pair(with_run=self.dead(), without_run=self.dead(),
                                     transcripts=False)
        self.assertFalse(os.path.exists(os.path.join(runs, "mapping.private.json")))

    def test_a_nonzero_exit_with_a_transcript_is_still_judged(self):
        # A timeout after real work exits non-zero and has plenty to compare.
        out, v, _ = self.judge_pair(with_run=self.dead(error=""), transcripts=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertNotEqual(v.get("invalid_code"), "arm_never_ran")
        self.assertTrue(self.judged())

    AUTH = "Failed to authenticate: OAuth session expired and could not be refreshed"

    def test_a_final_message_that_is_the_runners_error_is_not_an_answer(self):
        # The real shape, off the first rival pair. The CLI failed to authenticate,
        # wrote its init line to the transcript and wrote the failure as the final
        # message, so none of the three original tests fired. With a working judge
        # this would have been scored as two agents answering with the same sentence.
        run = {"agent": "claude", "exit": 1, "error": self.AUTH}
        out, v, _ = self.judge_pair(with_run=run, without_run=run, transcripts=True,
                                    finals={"with": self.AUTH, "without": self.AUTH})
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(v["invalid_code"], "arm_never_ran")
        self.assertIn("authenticate", v["invalid_reason"])
        self.assertIn("final message is the runner's own error", v["invalid_reason"])
        self.assertNotIn("produced no transcript", v["invalid_reason"])
        self.assertFalse(self.judged(), "a model call was spent judging two error strings")

    def test_a_truncated_error_still_matches_its_own_final_message(self):
        # run.json keeps 300 characters of the error; final.txt keeps all of it.
        long = self.AUTH + " " + "x" * 400
        run = {"agent": "claude", "exit": 1, "error": long[:300]}
        _, v, _ = self.judge_pair(with_run=run, transcripts=True, finals={"with": long})
        self.assertEqual(v["invalid_code"], "arm_never_ran")

    def test_an_agent_answer_after_a_failed_exit_is_still_an_answer(self):
        # A timeout after real work: the error comes from stderr and the final message
        # is the agent's own. Condemning this would throw away real comparisons.
        run = {"agent": "claude", "exit": 124, "error": "timeout"}
        out, v, _ = self.judge_pair(with_run=run, transcripts=True,
                                    finals={"with": "Here is the post you asked for."})
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertNotEqual(v.get("invalid_code"), "arm_never_ran")
        self.assertTrue(self.judged())

    def test_an_empty_transcript_alone_does_not_condemn_an_arm(self):
        # Exit 0 and nothing in the transcript is a runner that writes none, not a
        # runner that failed, and judging it is the right call.
        self.judge_pair(transcripts=False)
        self.assertTrue(self.judged())


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

    def test_a_skill_that_keeps_not_loading_does_not_retire_the_brief(self):
        # Which code comes out decides whether the brief survives, and on the first
        # Harbor pair the two competed: both arms failed the gate because the with-arm
        # never loaded the skill whose job was to pass it. Filed as a broken brief,
        # two such samples would stop the run and the log would blame a brief the
        # local runner passes three times out of three. Loading is chance - the model
        # picks the skill from its description against whatever else is installed -
        # so the next sample may well load it.
        n, err = self.samples_run(*(["skill_never_loaded"] * 3))
        self.assertEqual(n, 3)
        self.assertNotIn("twice running", err)

    def test_a_dead_runner_stops_the_brief_on_the_first_sample(self):
        # Not the two-in-a-row rule: a runner that could not launch an agent will not
        # launch one next time either, and each repeat costs another container build.
        n, err = self.samples_run("arm_never_ran", None, None)
        self.assertEqual(n, 1, "samples 2 and 3 would have reproduced the same fault")
        self.assertIn("never started", err)
        self.assertIn("nothing here is the brief's fault", err)

    def test_a_contaminated_baseline_stops_the_brief_on_the_first_sample(self):
        # Same reason: the skill is installed on the host or in the image, so it is
        # there for samples 2 and 3 too and none of them can measure anything.
        n, err = self.samples_run("baseline_had_the_skill", None, None)
        self.assertEqual(n, 1)
        self.assertIn("could reach the skill under test", err)

    LATE = "arm_timed_out"

    def test_two_cut_off_samples_running_stop_the_brief(self):
        # Not the first one: which arm runs long can vary between samples. But a brief
        # that cannot finish inside the cap twice will not finish inside it on the
        # third, and proving that again costs two more arms of wall clock.
        n, err = self.samples_run(self.LATE, self.LATE, self.LATE)
        self.assertEqual(n, 2)
        self.assertIn("ran out of time twice running", err)
        self.assertIn("FORGE_TIMEOUT", err)

    def test_one_cut_off_sample_does_not_stop_the_brief(self):
        n, err = self.samples_run(self.LATE, None, None)
        self.assertEqual(n, 3)
        self.assertNotIn("twice running", err)

    def test_a_cut_off_sample_does_not_count_as_a_failed_gate(self):
        # Counting it would blame the brief for the clock: these two are exactly the
        # pair of samples edge-launch produced, and they stopped the brief with a
        # message telling the operator to rewrite it.
        n, err = self.samples_run(self.BOTH, self.LATE, None)
        self.assertEqual(n, 3)
        self.assertNotIn("failed its own verify in both arms twice running", err)

    def test_a_cut_off_sample_does_not_clear_a_real_failed_gate(self):
        # The other half of the same rule, and the one an else-branch gets wrong: a
        # sample that says nothing about the gate must leave the verify count where it
        # stood, not reset it. Sample 4 is the second consecutive gate failure.
        n, err = self.samples_run(self.BOTH, self.LATE, self.BOTH, None)
        self.assertEqual(n, 3, "the gate failed twice with only a timeout in between")
        self.assertIn("failed its own verify in both arms twice running", err)


class LeakyBaseline(unittest.TestCase):
    """A baseline that could reach the candidate's skill is not a baseline.

    Every other check in judge.py reads what the harness installed, so all of them agree
    with each other by construction. This one reads what the agent was offered, which is
    the only place an ambient copy shows up: a skill already on the host, or baked into
    the container image, is advertised to both arms and installed by neither. The
    measurement that motivates it is in advertised_skills: 53 real without-arms on AX41,
    none contaminated today, and the loop's own four skills deployed to ~/.agents/skills
    exactly the way an adopted skill will be.
    """

    JUDGE = os.path.join(SCRIPTS, "judge.py")

    def arm_files(self, runs, arm, skill=None, loaded=None, advertised=None, shape="init"):
        work = os.path.join(runs, arm)
        meta = work + ".meta"
        os.makedirs(work)
        os.makedirs(meta)
        open(os.path.join(work, "post.md"), "w").write("the agent's output\n")
        if skill:
            sk = os.path.join(work, ".claude", "skills", skill)
            os.makedirs(sk)
            open(os.path.join(sk, "SKILL.md"), "w").write("---\nname: %s\n---\n" % skill)
        lines = []
        if advertised is not None:
            # The host CLI's shape and the SDK CLI's shape, both live in runs/ today.
            lines.append({"type": "system", "subtype": "init", "skills": list(advertised)}
                         if shape == "init" else
                         {"type": "attachment", "attachment": {
                             "type": "skill_listing", "names": list(advertised),
                             "skillCount": len(advertised)}})
        if loaded:
            lines.append({"message": {"role": "assistant", "content": [
                {"type": "tool_use", "name": "Skill", "input": {"skill": loaded}}]}})
        lines.append({"message": {"role": "assistant",
                                  "content": [{"type": "text", "text": "done"}]}})
        with open(os.path.join(meta, "transcript.jsonl"), "w") as fh:
            for obj in lines:
                fh.write(json.dumps(obj) + "\n")
        json.dump({"agent": "claude", "exit": 0}, open(os.path.join(meta, "run.json"), "w"))

    def judge_pair(self, offered=None, shape="init", without_skill=None,
                   without_loaded=None, with_loaded="demo-skill"):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        bin_, marker = stub_claude(tmp)
        brief = os.path.join(tmp, "brief.json")
        json.dump({"id": "b1", "prompt": "p", "verify": "true"}, open(brief, "w"))
        runs = os.path.join(tmp, "runs", "b1", "s1")
        self.arm_files(runs, "with", skill="demo-skill", loaded=with_loaded)
        self.arm_files(runs, "without", skill=without_skill, loaded=without_loaded,
                       advertised=offered, shape=shape)
        env = dict(os.environ, FORGE_ROOT=tmp, FORGE_ENGINE="claude",
                   PATH=bin_ + os.pathsep + os.environ["PATH"], PYTHONDONTWRITEBYTECODE="1")
        out = subprocess.run([sys.executable, self.JUDGE, brief, "--sample", "1"],
                             env=env, capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.runs = runs
        return json.load(open(os.path.join(runs, "verdict.json")))

    def test_a_baseline_offered_the_candidates_skill_invalidates_the_pair(self):
        v = self.judge_pair(offered=["dataviz", "demo-skill"])
        self.assertEqual(v["invalid_code"], "baseline_had_the_skill")
        self.assertEqual(v["winner_arm"], "invalid")

    def test_the_reason_names_the_skill_and_what_to_do_about_it(self):
        v = self.judge_pair(offered=["demo-skill"])
        self.assertIn("demo-skill", v["invalid_reason"])
        self.assertIn("Uninstall", v["invalid_reason"])

    def test_the_rest_of_the_fleet_is_not_a_leak(self):
        """The negative control, and the common case: 13 to 18 bundled skills are
        offered to both arms of every pair the loop has ever run."""
        v = self.judge_pair(offered=["dataviz", "code-review", "simplify"])
        self.assertFalse(v.get("invalid"), v.get("invalid_reason"))

    def test_a_rival_the_baseline_was_handed_is_not_a_leak(self):
        """--rival installs a skill in the baseline on purpose; it is supposed to
        reach it, and subtracting the without-arm's own installs is what allows it."""
        v = self.judge_pair(offered=["rival-skill"], without_skill="rival-skill",
                            without_loaded="rival-skill")
        self.assertFalse(v.get("invalid"), v.get("invalid_reason"))

    def test_a_baseline_handed_the_same_skill_is_a_populated_fleet_pair(self):
        """run_eval.sh's other supported shape: hand the baseline the skill already
        installed for this trigger, and the pair measures the skill against a fleet
        that has it rather than against an empty machine. Both arms advertise it
        because both were given it, and refusing that would delete the comparison an
        adoption into a populated fleet actually rests on."""
        v = self.judge_pair(offered=["demo-skill"], without_skill="demo-skill",
                            without_loaded="demo-skill")
        self.assertFalse(v.get("invalid"), v.get("invalid_reason"))

    def test_the_container_listing_shape_is_read_too(self):
        v = self.judge_pair(offered=["demo-skill"], shape="attachment")
        self.assertEqual(v["invalid_code"], "baseline_had_the_skill")

    def test_a_plugin_prefixed_name_is_the_same_skill(self):
        v = self.judge_pair(offered=["somebundle:demo-skill"])
        self.assertEqual(v["invalid_code"], "baseline_had_the_skill")

    def test_a_runner_that_lists_nothing_is_not_cleared(self):
        """Codex writes no listing at all. Recording that as an empty inventory would
        file every Codex baseline as checked when none of them were."""
        v = self.judge_pair(offered=None)
        self.assertIsNone(v["skills_advertised"]["without"])
        self.assertFalse(v.get("invalid"), v.get("invalid_reason"))

    def test_it_outranks_the_never_loaded_check(self):
        """Same pair, read from the other end: the with-arm looks silent, but the
        reason it had nothing to add is that the baseline had the skill as well."""
        v = self.judge_pair(offered=["demo-skill"], with_loaded=None)
        self.assertEqual(v["invalid_code"], "baseline_had_the_skill")

    def test_the_inventory_is_in_the_record(self):
        v = self.judge_pair(offered=["demo-skill", "dataviz"])
        self.assertEqual(v["skills_advertised"]["without"], ["dataviz", "demo-skill"])

    def test_no_blind_mapping_is_written(self):
        """Refused before the slots are drawn, so the rerun after the uninstall gets a
        fresh coin flip instead of inheriting this pair's."""
        self.judge_pair(offered=["demo-skill"])
        self.assertFalse(os.path.exists(os.path.join(self.runs, "mapping.private.json")))


class CutOffArm(unittest.TestCase):
    """An arm the clock killed is not an arm that failed the brief.

    edge-launch-intro-scene-ax41 is the pair that showed it. Sample 1: both arms exit
    0, both fail verify - a gate nobody passes. Sample 2: the without-arm finishes in
    1130s, the with-arm is killed at the 1200s cap mid-sentence on "Now rendering...".
    Both came back both_arms_failed_verify, whose reason reads "fix the brief, not the
    loop", and together they tripped the two-in-a-row rule and stopped the brief. Only
    one of the two was a measurement, and no rewrite of the brief can buy time.
    """

    JUDGE = os.path.join(SCRIPTS, "judge.py")

    def judge_pair(self, with_run=None, without_run=None, verify="false", finals=None):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        bin_, self.marker = stub_claude(tmp)
        brief = os.path.join(tmp, "brief.json")
        json.dump({"id": "b1", "prompt": "p", "verify": verify}, open(brief, "w"))
        self.runs = os.path.join(tmp, "runs", "b1", "s1")
        for arm, run in (("with", with_run), ("without", without_run)):
            work = os.path.join(self.runs, arm)
            meta = work + ".meta"
            os.makedirs(work)
            os.makedirs(meta)
            open(os.path.join(meta, "final.txt"), "w").write(
                (finals or {}).get(arm, "Here is the scene you asked for."))
            with open(os.path.join(meta, "transcript.jsonl"), "w") as fh:
                fh.write(json.dumps({"message": {"role": "assistant", "content": [
                    {"type": "text", "text": "Now rendering..."}]}}) + "\n")
            json.dump(run or {"agent": "claude", "exit": 0},
                      open(os.path.join(meta, "run.json"), "w"))
        env = dict(os.environ, FORGE_ROOT=tmp, FORGE_ENGINE="claude",
                   PATH=bin_ + os.pathsep + os.environ["PATH"], PYTHONDONTWRITEBYTECODE="1")
        out = subprocess.run([sys.executable, self.JUDGE, brief, "--sample", "1"],
                             env=env, capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        return json.load(open(os.path.join(self.runs, "verdict.json")))

    def judged(self):
        return os.path.exists(self.marker)

    def late(self, code=124, cap=1200):
        return {"agent": "claude", "exit": code, "seconds": cap + 1, "timeout_s": cap,
                "error": "timeout"}

    def test_an_arm_killed_at_the_cap_does_not_make_it_a_broken_brief(self):
        v = self.judge_pair(with_run=self.late())
        self.assertEqual(v["invalid_code"], "arm_timed_out")
        self.assertEqual(v["winner_arm"], "invalid")
        self.assertNotIn("fix the brief", v["invalid_reason"])

    def test_the_reason_names_the_arm_the_cap_and_the_fix(self):
        v = self.judge_pair(with_run=self.late())
        self.assertIn("the with-arm", v["invalid_reason"])
        self.assertIn("1200s", v["invalid_reason"])
        self.assertIn("FORGE_TIMEOUT", v["invalid_reason"])

    def test_both_arms_out_of_time_names_both(self):
        v = self.judge_pair(with_run=self.late(), without_run=self.late())
        self.assertEqual(v["invalid_code"], "arm_timed_out")
        self.assertIn("with-arm and without-arm", v["invalid_reason"])

    def test_a_cut_off_arm_that_still_passed_the_gate_is_a_real_comparison(self):
        """The brief's own verify is the only definition of done it offers. An agent
        killed at the cap whose work passes it is done, and throwing the pair away
        would discard a real verdict over the runner's bookkeeping."""
        v = self.judge_pair(with_run=self.late(), verify="true")
        self.assertNotEqual(v.get("invalid_code"), "arm_timed_out")
        self.assertTrue(self.judged())

    def test_the_perl_fallback_signal_is_the_same_event(self):
        """No `timeout` and no `gtimeout` leaves perl's alarm, which kills by SIGALRM
        and reports 128+14. Same cap, same cut-off, different number."""
        v = self.judge_pair(with_run=self.late(code=142))
        self.assertEqual(v["invalid_code"], "arm_timed_out")

    def test_an_ordinary_failure_is_still_a_failed_gate(self):
        """Only the cap's own exit codes count. A crash that fails verify is exactly
        what both_arms_failed_verify is for, and swallowing it here would hide briefs
        that genuinely cannot be passed."""
        run = {"agent": "claude", "exit": 1, "seconds": 30, "error": "boom"}
        v = self.judge_pair(with_run=run, without_run=run,
                            finals={"with": "tried", "without": "tried"})
        self.assertEqual(v.get("invalid_code"), "both_arms_failed_verify")

    def test_a_run_row_without_a_cap_still_refuses(self):
        """run.json rows written before the cap was recorded have no timeout_s. The
        refusal does not depend on it - only the seconds drop out of the sentence."""
        v = self.judge_pair(with_run={"agent": "claude", "exit": 124, "error": "timeout"})
        self.assertEqual(v["invalid_code"], "arm_timed_out")
        self.assertIn("ran into the cap", v["invalid_reason"])

    def test_two_different_caps_are_not_reported_as_one(self):
        v = self.judge_pair(with_run=self.late(cap=1200), without_run=self.late(cap=600))
        self.assertEqual(v["invalid_code"], "arm_timed_out")
        self.assertNotIn("1200s", v["invalid_reason"])
        self.assertNotIn("600s", v["invalid_reason"])

    def test_an_arm_that_never_started_outranks_it(self):
        """A container that timed out before launching anything is a runner fault, and
        its reason tells the operator to fix the runner rather than buy it more time."""
        v = self.judge_pair(with_run={"agent": "claude", "exit": 124, "timeout_s": 1200,
                                      "error": "timeout"},
                            finals={"with": "timeout"})
        self.assertEqual(v["invalid_code"], "arm_never_ran")

    def test_no_model_call_and_no_blind_mapping(self):
        """Refused before the slots are drawn and before the judge is paid, so the
        rerun under a bigger cap gets a fresh coin flip."""
        self.judge_pair(with_run=self.late())
        self.assertFalse(self.judged(), "a model call was spent on an arm that ran out of time")
        self.assertFalse(os.path.exists(os.path.join(self.runs, "mapping.private.json")))

    def test_the_run_row_is_in_the_record(self):
        v = self.judge_pair(with_run=self.late())
        self.assertEqual(v["run"]["with"]["timeout_s"], 1200)


if __name__ == "__main__":
    unittest.main(verbosity=2)
