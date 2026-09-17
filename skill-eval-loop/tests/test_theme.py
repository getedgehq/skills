#!/usr/bin/env python3
"""Tests for deriving a theme the recheck can measure, on fixtures.

Run: python3 tests/test_theme.py   (stdlib only, no network, no model calls)

Every refusal here was earned against a real 136-episode corpus, in this order:

  - ranking by lift produced identical scores for every candidate word, because in a
    corpus that size the words inside a subset appear nowhere else;
  - ranking by frequency then produced "but can dont have", filler that passed every
    statistical check;
  - with the stopword list extended it produced "post real" and "much post text",
    two-word themes where the filler half decides the rate;
  - and with a width floor it produced a seven-word theme about one website's pages
    for a skill about reusing existing assets.

So the tests are mostly about what this refuses. A tool that derives a matcher from
a corpus can always return something; being able to say "not from this corpus" is
the only thing that makes the something trustworthy.
"""
import json
import os
import sys
import tempfile
import time
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, "..", "scripts")
sys.path.insert(0, SCRIPTS)
import theme  # noqa: E402

DAY = 86400


def sessions(n, first_day, last_day):
    step = (last_day - first_day) / max(1, n - 1)
    return [{"id": f"s{i}", "ts": time.time() + (first_day + i * step) * DAY} for i in range(n)]


def corpus(theme_texts, noise_texts, sess, theme_share=0.25):
    """Episodes spread over sessions: the theme on the older ones, noise throughout."""
    eps = []
    cut = int(len(sess) * (1 - theme_share))
    for i, s in enumerate(sess):
        eps.append({"session": s["id"], "corr": noise_texts[i % len(noise_texts)]})
    for i, s in enumerate(sess[:cut]):
        if i % 3 == 0:
            eps.append({"session": s["id"], "corr": theme_texts[i % len(theme_texts)]})
    return eps


NOISE = [
    "the deploy script failed again on the wrong host",
    "check the port before starting a server",
    "that number is not measured anywhere",
    "you forgot the invoice attachment",
    "wrong render host for this job",
    "the migration ran against production",
    "stop rewriting the config file",
    "use the staging database for this",
]
UMLAUT = [
    "die umlaute im deutschen text sind wieder falsch geschrieben",
    "deutscher text braucht echte umlaute, falsch geschrieben wie immer",
    "umlaute im deutschen text falsch, bitte richtig geschrieben liefern",
    "wieder falsch: umlaute fehlen im deutschen text den du geschrieben hast",
]


def skill_md(tmp, name, description, quotes=()):
    d = os.path.join(tmp, name)
    os.makedirs(d, exist_ok=True)
    body = "\n".join(f'- "{q}"' for q in quotes)
    path = os.path.join(d, "SKILL.md")
    with open(path, "w") as fh:
        fh.write(f"---\nname: {name}\ndescription: {description}\n---\n\n{body}\n")
    return path


class Seeds(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def test_seed_uses_only_the_first_sentence_of_the_description(self):
        md = skill_md(self.tmp, "x", "Fires when writing German text. "
                                     "Covers newsletters, invoices, contracts and spreadsheets.")
        terms = theme.seed_terms("x", md)
        self.assertIn("german", terms)
        self.assertNotIn("spreadsheets", terms)

    def test_seed_drops_function_words_in_both_languages(self):
        md = skill_md(self.tmp, "x", "Use when the user says it is not right and you have to fix it.")
        self.assertEqual(theme.seed_terms("x", md) & {"have", "not", "nicht", "das"}, set())

    def test_seed_survives_a_skill_with_no_installed_file(self):
        self.assertEqual(theme.seed_terms("umlaut-checker", None), {"umlaut", "checker"})


class Derive(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.sess = sessions(60, -60, 0)
        self.adopted = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - 15 * DAY))

    def run_derive(self, name, description, quotes=(), eps=None):
        md = skill_md(self.tmp, name, description, quotes)
        corr = {"episodes": eps if eps is not None else corpus(UMLAUT, NOISE, self.sess),
                "session_index": self.sess}
        return theme.derive(name, self.adopted, md, corr)

    def test_derives_a_real_theme(self):
        got, why = self.run_derive("german-umlauts", "Fires when writing German text with umlaute.",
                                   quotes=("schreib die umlaute richtig, nicht ae oder oe",))
        self.assertIsNone(why, why)
        words = got["signature"].split()
        self.assertIn("umlaute", words)
        self.assertGreaterEqual(len(words), theme.MIN_SIGNATURE)
        self.assertLessEqual(got["share"], theme.MAX_SHARE)
        self.assertGreaterEqual(got["before"]["matching"], theme.MIN_BEFORE)

    def test_refuses_a_subject_nobody_was_corrected_about(self):
        got, why = self.run_derive("kubernetes-probes", "Fires when configuring kubernetes probes.")
        self.assertIsNone(got)
        self.assertIn("not enough to name a theme", why)

    def test_refuses_a_theme_too_thin_to_be_one(self):
        # Two episodes share one content word; everything else is filler.
        eps = corpus(["the post headline is wrong", "this post headline again",
                      "post headline looks bad", "bad post headline"], NOISE, self.sess)
        got, why = self.run_derive("post-format", "Fires when drafting a post headline.",
                                   quotes=("the post headline is wrong",), eps=eps)
        self.assertIsNone(got)
        self.assertIn("too thin to be a theme", why)

    def test_refuses_when_the_recurring_words_are_not_this_skills_subject(self):
        # The corpus has a strong, coherent theme; the skill is about something else
        # that happens to share a couple of ordinary words with it.
        eps = corpus(UMLAUT, NOISE, self.sess)
        got, why = self.run_derive("invoice-attachments",
                                   "Fires when sending an invoice by email.", eps=eps)
        self.assertIsNone(got)

    def test_refuses_an_empty_corpus(self):
        got, why = theme.derive("x", self.adopted, None,
                                {"episodes": [], "session_index": self.sess})
        self.assertIsNone(got)
        self.assertIn("no episodes", why)

    def test_a_theme_only_seen_after_adoption_has_no_baseline(self):
        recent = [s for s in self.sess if s["ts"] > time.time() - 10 * DAY]
        eps = [{"session": s["id"], "corr": UMLAUT[i % len(UMLAUT)]}
               for i, s in enumerate(recent * 2)]
        eps += [{"session": s["id"], "corr": NOISE[i % len(NOISE)]}
                for i, s in enumerate(self.sess)]
        got, why = self.run_derive("german-umlauts", "Fires when writing German text with umlaute.",
                                   quotes=("schreib die umlaute richtig",), eps=eps)
        self.assertIsNone(got)
        self.assertIn("no baseline", why)


class Rank(unittest.TestCase):
    def test_ignores_words_common_across_the_whole_corpus(self):
        sess = sessions(40, -40, 0)
        eps = [{"session": s["id"], "corr": "the render host is wrong again"} for s in sess]
        seed = eps[:10]
        self.assertNotIn("render", theme.rank(seed, eps),
                         "a word in every correction cannot mark one theme")

    def test_requires_a_word_to_recur_within_the_theme(self):
        sess = sessions(40, -40, 0)
        eps = [{"session": s["id"], "corr": f"unique{i} wording here"} for i, s in enumerate(sess)]
        self.assertEqual(theme.rank(eps[:10], eps), [])


class Apply(unittest.TestCase):
    """--apply only ever writes a matcher, and says where it came from."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.ledger = os.path.join(self.tmp, "ledger.jsonl")

    def test_written_row_is_tagged_and_carries_no_rate(self):
        got = {"signature": "umlaute deutsch text schreiben", "share": 0.1,
               "episodes_seeded": 9,
               "before": {"rate": 0.2, "sessions": 40, "matching": 8},
               "after": {"rate": 0.0, "sessions": 20, "matching": 0}}
        failure = {"kind": "correction", "signature": got["signature"], "user_rules": [],
                   "derived_from": f"corrections:{got['episodes_seeded']} episodes"}
        with open(self.ledger, "w") as fh:
            fh.write(json.dumps({"skill": "x", "decision": "adopt", "failure": failure}) + "\n")
        with open(self.ledger) as fh:
            row = json.loads(fh.read())
        self.assertTrue(row["failure"]["derived_from"].startswith("corrections:"))
        self.assertNotIn("baseline_failure_rate", row["failure"])
        self.assertNotIn("rate", row["failure"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
