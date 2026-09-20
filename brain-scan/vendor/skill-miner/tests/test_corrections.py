#!/usr/bin/env python3
"""Tests for reading skill loads out of session logs.

recheck.py refuses to confirm a skill that was never loaded while its correction rate
fell, so what counts as "loaded" decides verdicts. Every case here is a spelling seen in
a real session file, because the first version of this parser read only Claude Code's
and returned None for every OpenCode load - which downstream does not look like a parse
bug, it looks like a skill nobody used, and a skill nobody used never gets confirmed.

Run: python3 tests/test_corrections.py   (stdlib only, no network, no model calls)
"""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import corrections  # noqa: E402


def call(name, payload):
    return {"type": "tool_call", "name": name, "input": json.dumps(payload)}


class SkillLoaded(unittest.TestCase):
    def test_claude_code_names_the_skill_in_skill(self):
        self.assertEqual(corrections.skill_loaded(call("Skill", {"skill": "rocketlist"})),
                         "rocketlist")

    def test_opencode_names_it_in_name_and_lowercases_the_tool(self):
        # The bug this file exists for. Both halves differ from Claude Code's spelling.
        self.assertEqual(corrections.skill_loaded(call("skill", {"name": "client-comms"})),
                         "client-comms")

    def test_extra_arguments_do_not_hide_the_skill(self):
        got = call("Skill", {"skill": "opendraft", "args": "write something about libraries"})
        self.assertEqual(corrections.skill_loaded(got), "opendraft")

    def test_a_plugin_skill_counts_under_the_name_it_is_installed_as(self):
        # The ledger adopts, installs and revokes "dataviz"; the call says "viz:dataviz".
        self.assertEqual(corrections.skill_loaded(call("Skill", {"skill": "viz:dataviz"})),
                         "dataviz")

    def test_a_truncated_input_still_yields_a_name(self):
        # sources.MAX_INPUT cuts long inputs mid-JSON, so json.loads fails and the name
        # has to come out of the raw string instead.
        cut = '{"skill": "fede-voice", "args": "a very long brief that ran past the'
        self.assertEqual(corrections.skill_loaded(
            {"type": "tool_call", "name": "Skill", "input": cut}), "fede-voice")

    def test_another_tool_is_not_a_skill_load(self):
        self.assertIsNone(corrections.skill_loaded(call("Bash", {"command": "skill"})))

    def test_a_non_tool_event_is_not_a_skill_load(self):
        self.assertIsNone(corrections.skill_loaded({"type": "user_text", "text": "use the skill"}))

    def test_an_unreadable_input_is_no_load_rather_than_a_crash(self):
        self.assertIsNone(corrections.skill_loaded(
            {"type": "tool_call", "name": "Skill", "input": "not json at all"}))


if __name__ == "__main__":
    unittest.main(verbosity=2)
