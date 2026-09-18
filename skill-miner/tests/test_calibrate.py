#!/usr/bin/env python3
"""Tests for the scoring feedback loop: priors in, predictions out.

The loop spent three weeks scoring candidates with a prompt nothing ever checked.
Two things close that: calibrate.py states the base rates the evals actually
produced, and score.py writes down what it predicted so the two can be joined.

Both have the same failure mode, which is why these tests exist: reporting a
number from too little evidence. A bucket of one, a prediction log with no
matching decision, or a scoring pass whose model call failed all have to come
out as "cannot say", not as a rate.

Run: python3 tests/test_calibrate.py   (stdlib only, no network, no model calls)
"""
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, "..", "scripts")
sys.path.insert(0, SCRIPTS)
import calibrate  # noqa: E402
import score  # noqa: E402


def row(skill, decision, kind="correction", src="/home/u/skill-forge/drafts/" , **kw):
    r = {"skill": skill, "decision": decision, "skill_src": src + skill,
         "failure": {"kind": kind, "signature": f"{skill} went wrong"}}
    r.update(kw)
    return r


class Provenance(unittest.TestCase):
    """The ledger stores a path; the scorer needs a class it can generalize over."""

    def test_classes(self):
        cases = {
            "/home/u/skill-forge/drafts/li-post-fede": "drafted by the loop",
            "/root/.agents/skills/fede-voice": "already installed locally",
            "/home/u/.claude/skills/x": "already installed locally",
            "getedgehq/skills@skill-miner": "found in a registry",
            "https://example.com/s": "found in a registry",
            None: "unknown",
            "": "unknown",
        }
        for src, want in cases.items():
            self.assertEqual(calibrate.provenance(src), want, src)

    def test_drafts_do_not_split_into_one_bucket_each(self):
        rows = [row(f"s{i}", "adopt") for i in range(5)]
        srcs = [k for k in calibrate.buckets(rows) if k[0] == "skill source"]
        self.assertEqual(srcs, [("skill source", "drafted by the loop")],
                         "one bucket per draft path can never reach min-n")


class Priors(unittest.TestCase):
    def test_states_a_rate_only_above_min_n(self):
        rows = [row(f"a{i}", "adopt") for i in range(3)] + [row(f"r{i}", "reject") for i in range(3)]
        rows += [row("lonely", "adopt", kind="tool_error")]
        text = calibrate.priors_text(rows, min_n=4)
        self.assertIn("failure kind = correction: 3 of 6 passed the gate (50%)", text)
        self.assertIn("failure kind = tool_error: 1/1", text)
        self.assertIn("Too few decided evals to call", text)
        self.assertNotIn("tool_error: 1 of 1 passed", text)

    def test_only_eval_outcomes_count(self):
        rows = [row("a", "adopt"), {"skill": "h", "decision": "infra-fix"},
                {"skill": "k", "decision": "revoked"}, row("bad", "reject", invalid=True)]
        self.assertEqual([r["skill"] for r in calibrate.decided(rows)], ["a"])

    def test_score_states_no_priors_on_a_thin_ledger(self):
        text = score.priors_block([row("a", "adopt"), row("b", "reject")])
        self.assertIn("too few to state a base rate", text)
        self.assertNotIn("passed the gate", text)

    def test_score_passes_measured_priors_through(self):
        rows = [row(f"a{i}", "adopt") for i in range(6)] + [row(f"r{i}", "reject") for i in range(4)]
        text = score.priors_block(rows)
        self.assertTrue(text.startswith("MEASURED PRIORS from"))
        self.assertIn("6 of 10 passed the gate (60%)", text)

    def test_priors_reach_the_prompt(self):
        prompt = score.SCORE_PROMPT.format(
            kind="correction", signature="s", count=1, session_count=1, evidence="-",
            note="",
            name="n", pool="p", installs=0, content="c", ledger="(none)",
            priors="MEASURED PRIORS from this user's own past evals:\n- x: 1 of 2")
        self.assertIn("MEASURED PRIORS", prompt)


class Check(unittest.TestCase):
    """--check joins predictions to outcomes, or says why it cannot."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.preds = os.path.join(self.tmp, "predictions.jsonl")

    def write(self, preds):
        with open(self.preds, "w") as fh:
            for p in preds:
                fh.write(json.dumps(p) + "\n")

    def run_check(self, rows):
        buf = io.StringIO()
        with redirect_stdout(buf):
            calibrate.check(calibrate.decided(rows), self.preds)
        return buf.getvalue()

    def test_no_prediction_log_is_not_a_verdict(self):
        out = self.run_check([row("a", "adopt")])
        self.assertIn("no predictions recorded yet", out)

    def test_predictions_about_other_skills_do_not_pair(self):
        self.write([{"skill": "somethingelse", "potential": 0.9}])
        out = self.run_check([row("a", "adopt")])
        self.assertIn("nothing to calibrate yet", out)

    def test_separating_scores_report_signal(self):
        self.write([{"skill": "winner", "potential": 0.8, "ts": "2026-09-01T00:00:00Z"},
                    {"skill": "loser", "potential": 0.3, "ts": "2026-09-01T00:00:00Z"}])
        out = self.run_check([row("winner", "adopt"), row("loser", "reject")])
        self.assertIn("scores carry signal", out)

    def test_scores_that_do_not_separate_say_so(self):
        self.write([{"skill": "winner", "potential": 0.5, "ts": "2026-09-01T00:00:00Z"},
                    {"skill": "loser", "potential": 0.7, "ts": "2026-09-01T00:00:00Z"}])
        out = self.run_check([row("winner", "adopt"), row("loser", "reject")])
        self.assertIn("no usable signal", out)

    def test_the_latest_prediction_for_a_skill_wins(self):
        self.write([{"skill": "winner", "potential": 0.1, "ts": "2026-08-01T00:00:00Z"},
                    {"skill": "winner", "potential": 0.9, "ts": "2026-09-01T00:00:00Z"},
                    {"skill": "loser", "potential": 0.2, "ts": "2026-09-01T00:00:00Z"}])
        out = self.run_check([row("winner", "adopt"), row("loser", "reject")])
        self.assertIn("mean predicted potential, passed the gate: 0.90", out)


class FirstObject(unittest.TestCase):
    """Reading the model's verdict out of whatever it actually replied with."""

    def test_a_plain_object(self):
        self.assertEqual(score.first_object('{"potential": 0.7}')["potential"], 0.7)

    def test_a_fenced_object_with_prose_around_it(self):
        text = 'Here is my assessment:\n```json\n{"potential": 0.4, "reason": "thin"}\n```\nDone.'
        self.assertEqual(score.first_object(text)["reason"], "thin")

    def test_a_second_object_after_the_verdict(self):
        # The real failure. Slicing from the first "{" to the last "}" spans both, which
        # is valid JSON followed by more, and json.loads rejects all of it with "Extra
        # data" - so the candidate scored 0.00 for a reason the model never gave.
        text = '{"potential": 0.6, "reason": "plausible"}\n\n{"note": "also worth a look"}'
        self.assertEqual(score.first_object(text)["potential"], 0.6)

    def test_a_brace_in_the_prose_before_the_verdict(self):
        text = 'The signature contains {<x>} placeholders.\n{"potential": 0.2}'
        self.assertEqual(score.first_object(text)["potential"], 0.2)

    def test_a_reply_with_no_object_is_an_error_not_a_zero(self):
        with self.assertRaises(ValueError):
            score.first_object("I cannot score this candidate.")

    def test_a_missing_comma_between_members(self):
        # The observed failure, from the queue on 18 Sep: "Expecting ',' delimiter:
        # line 3 column 1". The model wrote every value asked for and left out one
        # separator, and the whole score was discarded over it.
        text = '{"potential": 0.6,\n"reason": "%s"\n"risk": "the sample is small"}' % ("x" * 480)
        got = score.first_object(text)
        self.assertEqual(got["potential"], 0.6)
        self.assertEqual(got["risk"], "the sample is small")

    def test_a_literal_newline_inside_a_string(self):
        # A different malformation with a different message ("Invalid control
        # character"), tolerated by the same second pass.
        self.assertEqual(score.first_object('{"potential": 0.3, "reason": "a\nb"}')["reason"],
                         "a\nb")

    def test_an_unescaped_quote_is_still_a_failure(self):
        # Same "Expecting ',' delimiter" message as the missing comma above, and the
        # repair has no way to tell the two apart. It does not need one: a comma put
        # into the middle of a string leaves something no decoder accepts, so this
        # reply fails anyway rather than parsing into members nobody wrote.
        with self.assertRaises(ValueError):
            score.first_object('{"potential": 0.6, "reason": "he said "no" to it"}')

    def test_only_a_member_opening_with_a_quote_is_repaired(self):
        # The guard that keeps the repair on the observed shape. A separator missing
        # inside a list raises the same message and is deliberately left to fail:
        # every shape the repair learns to rewrite is one it can get wrong quietly.
        with self.assertRaises(ValueError):
            score.first_object('{"potential": 0.6, "tags": [1 2]}')

    def test_a_valid_reply_is_read_exactly_as_written(self):
        text = '{"potential": 0.5, "reason": "line one\\nline two", "risk": "none"}'
        self.assertEqual(score.first_object(text)["reason"], "line one\nline two")


class KeepReply(unittest.TestCase):
    """A reply that could not be parsed is kept, or the next fix is another guess."""

    def test_the_reply_is_written_where_the_reason_says_it_is(self):
        tmp = tempfile.mkdtemp()
        path = score.keep_reply(tmp, "brand-visual-check", "{not json")
        self.assertTrue(path and os.path.exists(path))
        self.assertEqual(open(path).read(), "{not json")

    def test_a_name_with_a_slash_in_it_stays_inside_the_directory(self):
        tmp = tempfile.mkdtemp()
        path = score.keep_reply(tmp, "owner/repo@skill", "x")
        self.assertEqual(os.path.dirname(path), os.path.join(tmp, "mined", "score-failures"))

    def test_an_unwritable_root_does_not_raise(self):
        # Scoring already failed; a second failure on the way out would replace the
        # decoder's message with an OSError about a directory nobody asked about.
        self.assertEqual(score.keep_reply("/proc/nonexistent", "a", "x"), "")


class Record(unittest.TestCase):
    def test_creates_the_log_and_appends(self):
        tmp = tempfile.mkdtemp()
        path = os.path.join(tmp, "nested", "predictions.jsonl")
        score.record(path, [{"skill": "a", "potential": 0.5}])
        score.record(path, [{"skill": "b", "potential": 0.6}])
        with open(path) as fh:
            rows = [json.loads(l) for l in fh]
        self.assertEqual([r["skill"] for r in rows], ["a", "b"])

    def test_an_unwritable_log_does_not_stop_a_scoring_pass(self):
        tmp = tempfile.mkdtemp()
        blocker = os.path.join(tmp, "blocked")
        with open(blocker, "w") as fh:
            fh.write("not a directory")
        score.record(os.path.join(blocker, "predictions.jsonl"), [{"skill": "a"}])


class PredictWhatIsEvaluated(unittest.TestCase):
    """Whatever reaches the gate has to be what got a prediction.

    The scorer only ever saw candidates match.py had found, and a matched
    candidate is used only if it scores at least 0.5, so the skill that reached
    the gate was nearly always a draft that had never been scored. That is how
    the log ended up with 8 predictions, the ledger with 21 decisions, and
    --check with nothing to pair: not a wiring bug, a design that could not close
    however long it ran.
    """

    def args(self, **kw):
        base = {"candidates": None, "source": None, "index": 0, "top": 5,
                "out": None, "skill_dir": None, "pool": "drafted"}
        base.update(kw)
        return type("A", (), base)

    def test_a_skill_dir_is_named_the_way_the_ledger_names_it(self):
        # calibrate.py --check joins on the skill name, and the gate writes the
        # directory's basename. Any other name records a prediction that cannot
        # pair with its own outcome, which is the bug this fixes, restated.
        got = score.candidates_from(self.args(skill_dir="/home/u/skill-forge/drafts/tldr-replies/"))
        self.assertEqual(got[0]["name"], "tldr-replies")
        self.assertEqual(calibrate.norm(got[0]["name"]), calibrate.norm("tldr-replies"))

    def test_the_prediction_pairs_with_the_decision_that_follows_it(self):
        tmp = tempfile.mkdtemp()
        preds = os.path.join(tmp, "predictions.jsonl")
        cand = score.candidates_from(self.args(skill_dir=os.path.join(tmp, "drafts", "brand-visual-check")))
        score.record(preds, [{"skill": cand[0]["name"], "potential": 0.7}])
        ledger = [row("brand-visual-check", "adopt")]
        buf = io.StringIO()
        with redirect_stdout(buf):
            calibrate.check(ledger, preds)
        self.assertIn("paired 1 prediction", buf.getvalue())

    def test_the_provenance_recorded_is_the_one_the_priors_bucket_by(self):
        got = score.candidates_from(self.args(skill_dir="/x/find-existing-assets-first"))
        self.assertEqual(got[0]["pool"], "drafted")

    def test_a_brief_carries_the_cluster_so_the_caller_need_not(self):
        # forge.sh --brief has no mined file and no index in hand; the brief it
        # was handed already holds the cluster it was built from.
        brief = {"id": "voltbike", "source_failure": {"kind": "correction",
                                                      "signature": "review artifacts are text-heavy"}}
        self.assertEqual(score.cluster_from(brief, 0)["signature"],
                         "review artifacts are text-heavy")

    def test_a_mined_file_still_resolves_by_index(self):
        mined = {"clusters": [{"signature": "first"}, {"signature": "second"}]}
        self.assertEqual(score.cluster_from(mined, 1)["signature"], "second")

    def test_a_bare_cluster_is_taken_as_itself(self):
        self.assertEqual(score.cluster_from({"signature": "lone"}, 0)["signature"], "lone")

    def test_a_hand_written_brief_still_yields_a_scorable_cluster(self):
        # 22 of 37 briefs here have no source_failure. The old fallback handed the
        # brief back as if it were a cluster and the caller raised KeyError on
        # "signature", which forge.sh swallowed as "evaluating anyway" - so the
        # majority of decisions never got the prediction PR #29 exists to record.
        brief = {"id": "li-post__li-post-fede-rival", "prompt": "Write the launch post.",
                 "rubric": "voice", "verify": "true"}
        got = score.cluster_from(brief, 0)
        self.assertEqual(got["signature"], "li-post__li-post-fede-rival")
        self.assertTrue(got["no_mined_cluster"])
        self.assertEqual(got["evidence"], ["Write the launch post."])

    def test_a_brief_with_no_id_falls_back_to_its_own_prompt(self):
        got = score.cluster_from({"prompt": "  Ship  the\n post.  ", "rubric": "x"}, 0)
        self.assertEqual(got["signature"], "Ship the post.")

    def test_a_null_source_failure_is_not_a_cluster(self):
        # draft.py writes the key; a brief edited by hand can carry it as null,
        # and "source_failure" in data was true for exactly that shape.
        got = score.cluster_from({"id": "b", "source_failure": None,
                                  "prompt": "p", "rubric": "r"}, 0)
        self.assertTrue(got["no_mined_cluster"])

    def test_the_prompt_says_the_missing_evidence_is_not_weak_evidence(self):
        # Rubric item 3 scores more sessions higher, so an empty cluster reads as a
        # bad bet unless the prompt says otherwise, and every hand-written brief
        # would score near 0 for having been written by hand.
        self.assertIn("{note}", score.SCORE_PROMPT)
        self.assertIn("not read the absent evidence as weak evidence",
                      score.NO_CLUSTER_NOTE)

    def test_a_skill_dir_pass_does_not_overwrite_the_matched_scores(self):
        # Both run in one forge pass. The matched file is the record of why this
        # skill was the one evaluated, so landing on it loses that.
        self.assertIn("scored-skill.json", open(os.path.join(SCRIPTS, "score.py")).read())

    def test_one_of_the_two_inputs_is_required(self):
        out = os.popen(f"python3 {os.path.join(SCRIPTS, 'score.py')} 2>&1").read()
        self.assertIn("error:", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
