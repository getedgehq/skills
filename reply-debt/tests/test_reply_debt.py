"""Tests for reply_debt. No network: every test uses a fixture or a stub backend."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import reply_debt as rd  # noqa: E402

NOW = datetime(2026, 9, 16, 12, 0, tzinfo=timezone.utc)
FIXTURE = ROOT / "tests" / "fixtures" / "inbox.json"


def msg(thread, sender, subject, date, snippet=""):
    return {"threadId": thread, "snippet": snippet,
            "payload": {"headers": [{"name": "From", "value": sender},
                                    {"name": "Subject", "value": subject},
                                    {"name": "Date", "value": date}]}}


class StubBackend(rd.Backend):
    can_send = True

    def __init__(self, sent=(), inbound=(), fail=False):
        self._sent, self._inbound, self._fail = list(sent), list(inbound), fail
        self.outbox = []

    def search(self, query, limit):
        if self._fail:
            raise rd.BackendError("HTTP 401 from gmail")
        return (self._sent if "-from:me" not in query else self._inbound)[:limit]

    def send(self, to, subject, body):
        self.outbox.append((to, subject, body))


def go(backend, tmp_path, rules=None, **kw):
    return rd.run(backend, rules or rd.load_rules(None), tmp_path / "brief.md",
                  now=NOW, **kw)


# --------------------------------------------------------------------------- #
# filtering
# --------------------------------------------------------------------------- #
def test_a_thread_you_already_replied_to_is_not_debt(tmp_path):
    backend = StubBackend(
        sent=[msg("t1", "You <you@example.com>", "Re: x", "Mon, 14 Sep 2026 09:00:00 +0000")],
        inbound=[msg("t1", "A <a@example.com>", "Re: x",
                     "Sun, 13 Sep 2026 09:00:00 +0000", "can you confirm?")])
    result = go(backend, tmp_path)
    assert result["awaiting"] == 0
    assert result["dropped"]["already_replied"] == 1


def test_a_noreply_sender_is_dropped(tmp_path):
    backend = StubBackend(inbound=[
        msg("t1", "no-reply@example.com", "Action required",
            "Sun, 13 Sep 2026 09:00:00 +0000", "please confirm your account?")])
    assert go(backend, tmp_path)["dropped"]["sender_rule"] == 1


def test_a_promotional_subject_is_dropped(tmp_path):
    backend = StubBackend(inbound=[
        msg("t1", "Anya <anya@example.com>", "Our webinar is starting",
            "Sun, 13 Sep 2026 09:00:00 +0000", "can you join?")])
    assert go(backend, tmp_path)["dropped"]["subject_rule"] == 1


def test_mail_that_asks_nothing_is_dropped(tmp_path):
    backend = StubBackend(inbound=[
        msg("t1", "Lena <lena@example.com>", "FYI office move",
            "Sun, 13 Sep 2026 09:00:00 +0000", "Sharing for visibility.")])
    result = go(backend, tmp_path)
    assert result["awaiting"] == 0 and result["dropped"]["no_ask"] == 1


def test_a_question_mark_alone_qualifies(tmp_path):
    backend = StubBackend(inbound=[
        msg("t1", "Lena <lena@example.com>", "thursday?",
            "Sun, 13 Sep 2026 09:00:00 +0000", "")])
    assert go(backend, tmp_path)["awaiting"] == 1


def test_a_removable_rule_can_be_removed(tmp_path):
    """support@ is a default skip, but at a small company a person writes from it."""
    inbound = [msg("t1", "Nia <support@example.com>", "about your question",
                   "Sun, 13 Sep 2026 09:00:00 +0000", "could you clarify?")]
    assert go(StubBackend(inbound=inbound), tmp_path)["awaiting"] == 0
    rules = dict(rd.DEFAULT_RULES)
    rules["skip_sender"] = [r for r in rules["skip_sender"] if r != "support@"]
    assert go(StubBackend(inbound=inbound), tmp_path, rules)["awaiting"] == 1


def test_one_row_per_thread(tmp_path):
    backend = StubBackend(inbound=[
        msg("t1", "A <a@example.com>", "budget?", "Sat, 12 Sep 2026 09:00:00 +0000"),
        msg("t1", "A <a@example.com>", "budget?", "Sun, 13 Sep 2026 09:00:00 +0000")])
    assert go(backend, tmp_path)["awaiting"] == 1


def test_a_message_with_an_unparseable_date_still_surfaces(tmp_path):
    backend = StubBackend(inbound=[
        msg("t1", "A <a@example.com>", "can you review?", "not a date")])
    result = go(backend, tmp_path)
    assert result["awaiting"] == 1 and "recent" in result["brief"]


# --------------------------------------------------------------------------- #
# ranking
# --------------------------------------------------------------------------- #
def test_longer_wait_outranks_shorter_wait(tmp_path):
    backend = StubBackend(inbound=[
        msg("new", "New <n@example.com>", "can you confirm?",
            "Tue, 15 Sep 2026 09:00:00 +0000"),
        msg("old", "Old <o@example.com>", "can you confirm?",
            "Thu, 10 Sep 2026 09:00:00 +0000")])
    assert [i["thread"] for i in go(backend, tmp_path)["ranked"]] == ["old", "new"]


def test_an_importance_hint_outranks_a_few_days_of_waiting(tmp_path):
    backend = StubBackend(inbound=[
        msg("plain", "A <a@example.com>", "can you confirm?",
            "Sat, 12 Sep 2026 09:00:00 +0000"),
        msg("legal", "B <b@example.com>", "contract: can you confirm?",
            "Mon, 14 Sep 2026 09:00:00 +0000")])
    assert go(backend, tmp_path)["ranked"][0]["thread"] == "legal"


def test_importance_hints_never_filter(tmp_path):
    """A hint list that matches nothing must change order only, never membership."""
    inbound = [msg("t1", "A <a@example.com>", "can you confirm?",
                   "Sat, 12 Sep 2026 09:00:00 +0000")]
    rules = dict(rd.DEFAULT_RULES, important_hints=["nothing-matches-this"])
    assert go(StubBackend(inbound=inbound), tmp_path, rules)["awaiting"] == 1


def test_wait_points_are_capped(tmp_path):
    rules = dict(rd.DEFAULT_RULES, wait_days_cap=2, wait_points_per_day=1)
    backend = StubBackend(inbound=[
        msg("t1", "A <a@example.com>", "can you confirm?",
            "Wed, 02 Sep 2026 09:00:00 +0000")])
    assert go(backend, tmp_path, rules)["ranked"][0]["score"] == 2


def test_top_limits_the_brief_but_not_the_count(tmp_path):
    inbound = [msg(f"t{i}", f"P{i} <p{i}@example.com>", f"can you confirm {i}?",
                   "Sat, 12 Sep 2026 09:00:00 +0000") for i in range(5)]
    rules = dict(rd.DEFAULT_RULES, top=2)
    result = go(StubBackend(inbound=inbound), tmp_path, rules)
    assert result["awaiting"] == 5
    assert result["brief"].count("- waiting ") == 2


# --------------------------------------------------------------------------- #
# sending: never a default recipient, never on by default
# --------------------------------------------------------------------------- #
def test_nothing_is_sent_without_the_send_flag(tmp_path):
    backend = StubBackend(inbound=[
        msg("t1", "A <a@example.com>", "can you confirm?",
            "Sat, 12 Sep 2026 09:00:00 +0000")])
    result = go(backend, tmp_path, notify_email="ops@example.com")
    assert backend.outbox == [] and "not sent" in result["delivery"]


def test_send_goes_only_to_the_address_you_passed(tmp_path):
    backend = StubBackend(inbound=[
        msg("t1", "A <a@example.com>", "can you confirm?",
            "Sat, 12 Sep 2026 09:00:00 +0000")])
    go(backend, tmp_path, notify_email="ops@example.com", send=True)
    assert [to for to, _, _ in backend.outbox] == ["ops@example.com"]


def test_without_a_recipient_send_refuses_rather_than_guessing(tmp_path):
    backend = StubBackend(inbound=[
        msg("t1", "A <a@example.com>", "can you confirm?",
            "Sat, 12 Sep 2026 09:00:00 +0000")])
    result = go(backend, tmp_path, send=True)
    assert backend.outbox == [] and "no recipient" in result["delivery"]


def test_the_fallback_recipient_comes_from_your_own_sent_mail(tmp_path):
    backend = StubBackend(
        sent=[msg("t0", "You <you@example.com>", "Re: x",
                  "Mon, 14 Sep 2026 09:00:00 +0000")],
        inbound=[msg("t1", "A <a@example.com>", "can you confirm?",
                     "Sat, 12 Sep 2026 09:00:00 +0000")])
    go(backend, tmp_path, send=True)
    assert [to for to, _, _ in backend.outbox] == ["you@example.com"]


def test_an_empty_list_sends_nothing(tmp_path):
    result = go(StubBackend(), tmp_path, notify_email="ops@example.com", send=True)
    assert "nothing is waiting" in result["delivery"]


def test_the_brief_is_written_even_when_empty(tmp_path):
    result = go(StubBackend(), tmp_path)
    assert "Nothing is waiting on you." in Path(result["brief_path"]).read_text()


# --------------------------------------------------------------------------- #
# failures are never an empty inbox
# --------------------------------------------------------------------------- #
def test_a_backend_failure_raises_instead_of_reporting_zero(tmp_path):
    with pytest.raises(rd.BackendError):
        go(StubBackend(fail=True), tmp_path)


def test_cli_exits_1_on_a_backend_failure(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(rd, "build_backend", lambda *a, **k: StubBackend(fail=True))
    assert rd.main(["--out", str(tmp_path / "b.md")]) == 1
    assert "mail backend failed" in capsys.readouterr().err


# --------------------------------------------------------------------------- #
# config and backends
# --------------------------------------------------------------------------- #
def test_an_unknown_config_key_is_refused(tmp_path):
    path = tmp_path / "c.json"
    path.write_text(json.dumps({"skip_senders": ["typo"]}))
    with pytest.raises(rd.ConfigError, match="unknown config keys: skip_senders"):
        rd.load_rules(path)


def test_a_config_replaces_a_list_wholesale(tmp_path):
    path = tmp_path / "c.json"
    path.write_text(json.dumps({"expects_reply": ["?"], "_comment": "ok"}))
    assert rd.load_rules(path)["expects_reply"] == ["?"]


def test_the_gmail_backend_refuses_without_a_token(monkeypatch):
    monkeypatch.delenv("GMAIL_ACCESS_TOKEN", raising=False)
    with pytest.raises(rd.ConfigError, match="GMAIL_ACCESS_TOKEN is not set"):
        rd.build_backend("gmail-api", None, None)


def test_the_composio_backend_refuses_without_a_connection(monkeypatch):
    monkeypatch.setenv("COMPOSIO_API_KEY", "not-a-real-key")
    with pytest.raises(rd.ConfigError, match="--connection-id is required"):
        rd.build_backend("composio", None, None)


def test_composio_finds_messages_in_a_nested_envelope():
    payload = {"data": {"response_data": {"messages": [{"threadId": "t1"}]}}}
    assert rd.ComposioBackend._messages(payload) == [{"threadId": "t1"}]


def test_the_composio_message_shape_parses():
    item = rd.parse_message({"thread_id": "t9", "sender": "A <a@example.com>",
                             "subject": "hi", "messageText": "can you confirm?"})
    assert item["thread"] == "t9" and item["snippet"] == "can you confirm?"


def test_fixture_backend_end_to_end(tmp_path):
    backend = rd.build_backend("fixture", FIXTURE, None)
    result = go(backend, tmp_path)
    subjects = [i["subject"] for i in result["ranked"]]
    assert "contract review" in " ".join(subjects).lower()
    # The bundled fixture drops one of each kind, which is the point of it.
    assert result["dropped"]["already_replied"] >= 1
    assert result["dropped"]["sender_rule"] >= 1
    assert result["dropped"]["no_ask"] >= 1


def test_cli_runs_the_fixture_and_prints_a_brief(tmp_path, capsys):
    code = rd.main(["--backend", "fixture", "--fixture", str(FIXTURE),
                    "--out", str(tmp_path / "b.md")])
    assert code == 0
    assert "You owe a reply" in capsys.readouterr().out


def test_cli_exits_2_on_a_missing_fixture(tmp_path, capsys):
    assert rd.main(["--backend", "fixture", "--fixture", str(tmp_path / "nope.json")]) == 2
    assert "fixture not found" in capsys.readouterr().err
