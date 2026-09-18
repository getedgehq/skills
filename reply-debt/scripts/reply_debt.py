#!/usr/bin/env python3
"""Rank the mail still waiting on your reply. Deterministic, no model.

The pipeline:
  1. Fetch the threads you replied to recently   (in:inbox newer_than:Nd from:me)
  2. Fetch recent inbound mail                   (in:inbox newer_than:Nd -from:me)
  3. Drop threads from (1), drop bots and newsletters, keep mail that plausibly
     asks something of you
  4. Rank by how long the person has waited, plus a light importance signal
  5. Write a brief, and send it to one address only if you pass --send

No language model reads your mail. Every decision is a substring rule you can
read in the config and change.

Backends
--------
  gmail-api  Gmail REST v1 with an OAuth access token in GMAIL_ACCESS_TOKEN.
  composio   Composio-managed Gmail connection: COMPOSIO_API_KEY plus
             --connection-id (an account identifier, not a secret).
  fixture    A local JSON file of messages. No credential, no network. Use it to
             tune the filters before connecting a mailbox at all.

Usage
-----
  python scripts/reply_debt.py --backend fixture --fixture tests/fixtures/inbox.json
  python scripts/reply_debt.py --backend gmail-api --notify-email you@yours --send

Exit codes: 0 success, 1 the mail backend failed, 2 bad config or arguments.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

GMAIL_API_ROOT = "https://gmail.googleapis.com/gmail/v1/users/me"
COMPOSIO_EXECUTE = "https://backend.composio.dev/api/v3/tools/execute/{slug}"
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")

# Defaults are rules about mail in general, never about a particular person or
# mailbox. Every list is replaceable through --config.
DEFAULT_RULES: dict[str, Any] = {
    "days": 10,
    "max_fetch": 60,
    "top": 10,
    # Senders that are never a person waiting on your reply.
    "skip_sender": [
        "no-reply", "noreply", "no_reply", "donotreply", "do-not-reply", "[bot]",
        "notifications@", "newsletter", "mailer", "automated", "notify@", "updates@",
        "support@", "billing@", "receipts@", "team@", "hello@", "info@", "alerts@",
        "marketing@", "news@", "offers@", "promo", "calendar-", "registration",
        "tickets@", "events@", "comms@",
    ],
    # Subjects that are promotions, confirmations or invitations, never a debt.
    "skip_subject": [
        "invited you", "you are invited", "registration approved", "registration pending",
        "confirmation", "your flight", "boarding", "itinerary", "newsletter", "% off",
        "sale", "webinar", "livestream", "is starting", "reminder:", "receipt",
        "invoice paid", "new messages from", "new message in",
    ],
    # Phrasing that plausibly asks something of you.
    "expects_reply": [
        "?", "let me know", "lmk", "thoughts", "could you", "can you", "would you",
        "are you", "what do you think", "your thoughts", "please", "when can",
        "available", "free to", "intro", "introduce", "follow up", "following up",
        "circling back", "any update", "proposal", "review", "feedback", "confirm",
        "sign", "deadline", "waiting",
    ],
    # Ranking nudge only. Never filters anything in or out.
    "important_hints": [
        "investor", "vc", "capital", "legal", "lawyer", "contract", "client",
        "partner", "founder", "ceo", "intro", "term sheet", "deal",
    ],
    "wait_points_per_day": 2,
    "wait_days_cap": 14,
    "important_points": 6,
}


class ConfigError(ValueError):
    """Bad arguments or config."""


class BackendError(RuntimeError):
    """The mail backend failed. Never reported as an empty inbox."""


# --------------------------------------------------------------------------- #
# rules
# --------------------------------------------------------------------------- #
def load_rules(path: Path | None) -> dict[str, Any]:
    rules = dict(DEFAULT_RULES)
    if path is None:
        return rules
    try:
        override = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ConfigError(f"config file not found: {path}") from None
    except json.JSONDecodeError as exc:
        raise ConfigError(f"config file is not valid JSON: {exc}") from None
    if not isinstance(override, dict):
        raise ConfigError("config file must contain a JSON object")
    unknown = sorted(set(override) - set(DEFAULT_RULES) - {"_comment"})
    if unknown:
        raise ConfigError(f"unknown config keys: {', '.join(unknown)}")
    rules.update({k: v for k, v in override.items() if k != "_comment"})
    return rules


# --------------------------------------------------------------------------- #
# backends
# --------------------------------------------------------------------------- #
class Backend:
    """A mail source. search() returns raw message dicts; send() may be absent."""

    can_send = False

    def search(self, query: str, limit: int) -> list[dict[str, Any]]:
        raise NotImplementedError

    def send(self, to: str, subject: str, body: str) -> None:
        raise NotImplementedError


def _request(url: str, headers: dict[str, str], data: bytes | None = None,
             method: str = "GET", timeout: int = 60) -> Any:
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = ""
        try:
            detail = exc.read().decode("utf-8", "ignore")[:300]
        except Exception:
            pass
        # The token itself is never in the URL or the message.
        raise BackendError(f"HTTP {exc.code} from {urllib.parse.urlsplit(url).netloc}"
                           f"{urllib.parse.urlsplit(url).path}: {detail}") from None
    except Exception as exc:  # noqa: BLE001
        raise BackendError(f"{type(exc).__name__}: {exc}") from None
    return json.loads(raw) if raw else {}


class GmailApiBackend(Backend):
    """Gmail REST v1 with a user OAuth access token.

    The token is read from the environment here and goes out in an Authorization
    header. It is never an argument, never printed and never written to a file.
    Scopes: gmail.readonly to build the brief, gmail.send only if you use --send.
    """

    can_send = True

    def __init__(self) -> None:
        token = (os.environ.get("GMAIL_ACCESS_TOKEN") or "").strip()
        if not token:
            raise ConfigError(
                "GMAIL_ACCESS_TOKEN is not set. Export a Gmail OAuth access token "
                "with the gmail.readonly scope (and gmail.send if you use --send), "
                "or use --backend fixture to try the filters offline.")
        self._headers = {"Authorization": f"Bearer {token}",
                         "Content-Type": "application/json"}

    def search(self, query: str, limit: int) -> list[dict[str, Any]]:
        listing = _request(
            f"{GMAIL_API_ROOT}/messages?" + urllib.parse.urlencode(
                {"q": query, "maxResults": max(1, min(int(limit), 500))}),
            self._headers)
        out = []
        for stub in listing.get("messages", []) or []:
            params = urllib.parse.urlencode(
                [("format", "metadata"), ("metadataHeaders", "From"),
                 ("metadataHeaders", "Subject"), ("metadataHeaders", "Date")])
            out.append(_request(f"{GMAIL_API_ROOT}/messages/{stub['id']}?{params}",
                                self._headers))
        return out

    def send(self, to: str, subject: str, body: str) -> None:
        raw = (f"To: {to}\r\nSubject: {subject}\r\n"
               f"Content-Type: text/plain; charset=utf-8\r\n\r\n{body}")
        payload = json.dumps(
            {"raw": base64.urlsafe_b64encode(raw.encode("utf-8")).decode()}).encode()
        _request(f"{GMAIL_API_ROOT}/messages/send", self._headers,
                 data=payload, method="POST")


class ComposioBackend(Backend):
    """Gmail through a Composio-managed connection.

    COMPOSIO_API_KEY comes from the environment. The connection id is an account
    identifier, not a secret, so it is a normal argument.
    """

    can_send = True

    def __init__(self, connection_id: str) -> None:
        key = (os.environ.get("COMPOSIO_API_KEY") or "").strip()
        if not key:
            raise ConfigError("COMPOSIO_API_KEY is not set")
        if not connection_id:
            raise ConfigError("--connection-id is required for the composio backend")
        self._headers = {"x-api-key": key, "Content-Type": "application/json"}
        self._connection_id = connection_id

    def _execute(self, slug: str, arguments: dict[str, Any]) -> dict[str, Any]:
        payload = json.dumps({"connected_account_id": self._connection_id,
                              "arguments": arguments}).encode()
        response = _request(COMPOSIO_EXECUTE.format(slug=slug), self._headers,
                            data=payload, method="POST", timeout=90)
        if isinstance(response, dict) and response.get("successful") is False:
            raise BackendError(f"{slug}: {response.get('error') or 'tool reported failure'}")
        return response if isinstance(response, dict) else {}

    @staticmethod
    def _messages(payload: Any) -> list[dict[str, Any]]:
        if isinstance(payload, list):
            return [m for m in payload if isinstance(m, dict)]
        if not isinstance(payload, dict):
            return []
        for key in ("messages", "data", "response_data", "result", "emails"):
            value = payload.get(key)
            if isinstance(value, list):
                return [m for m in value if isinstance(m, dict)]
            if isinstance(value, dict):
                found = ComposioBackend._messages(value)
                if found:
                    return found
        return []

    def search(self, query: str, limit: int) -> list[dict[str, Any]]:
        return self._messages(self._execute(
            "GMAIL_FETCH_EMAILS",
            {"query": query, "max_results": int(limit), "include_attachments": False}))

    def send(self, to: str, subject: str, body: str) -> None:
        self._execute("GMAIL_SEND_EMAIL", {"recipient_email": to, "subject": subject,
                                           "body": body, "is_html": False})


class FixtureBackend(Backend):
    """A local JSON file: {"<gmail query>": [message, ...]}. No network."""

    def __init__(self, path: Path) -> None:
        try:
            self._data = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            raise ConfigError(f"fixture not found: {path}") from None
        except json.JSONDecodeError as exc:
            raise ConfigError(f"fixture is not valid JSON: {exc}") from None
        if not isinstance(self._data, dict):
            raise ConfigError("fixture must be a JSON object keyed by Gmail query")

    def search(self, query: str, limit: int) -> list[dict[str, Any]]:
        return list(self._data.get(query, []))[:limit]


def build_backend(name: str, fixture: Path | None, connection_id: str | None) -> Backend:
    if name == "gmail-api":
        return GmailApiBackend()
    if name == "composio":
        return ComposioBackend(connection_id or "")
    if name == "fixture":
        if fixture is None:
            raise ConfigError("--fixture is required for the fixture backend")
        return FixtureBackend(fixture)
    raise ConfigError(f"unknown backend: {name}")


# --------------------------------------------------------------------------- #
# parsing
# --------------------------------------------------------------------------- #
def headers_of(message: dict[str, Any]) -> dict[str, str]:
    payload = message.get("payload") or {}
    return {str(h.get("name", "")).lower(): str(h.get("value", ""))
            for h in payload.get("headers", []) or []}


def parse_message(message: dict[str, Any]) -> dict[str, Any]:
    headers = headers_of(message)
    subject = message.get("subject") or headers.get("subject", "(no subject)")
    sender = headers.get("from", message.get("sender", ""))
    raw_date = headers.get("date", "")
    snippet = message.get("snippet") or message.get("messageText") or ""
    try:
        when = parsedate_to_datetime(raw_date) if raw_date else None
        if when is not None and when.tzinfo is None:
            when = when.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        when = None
    return {"thread": message.get("threadId") or message.get("thread_id") or "",
            "subject": str(subject).strip(), "sender": str(sender),
            "snippet": str(snippet).strip(), "when": when}


def display_name(sender: str) -> str:
    return sender.split("<")[0].strip().strip('"') or sender


# --------------------------------------------------------------------------- #
# pipeline
# --------------------------------------------------------------------------- #
def collect(backend: Backend, rules: dict[str, Any]) -> dict[str, Any]:
    days = int(rules["days"])
    limit = int(rules["max_fetch"])

    replied: set[str] = set()
    own_address = ""
    for message in backend.search(f"in:inbox newer_than:{days}d from:me", limit):
        thread = message.get("threadId") or message.get("thread_id")
        if thread:
            replied.add(thread)
        if not own_address:
            match = EMAIL_RE.search(headers_of(message).get("from", "")
                                    or str(message.get("sender", "")))
            if match:
                own_address = match.group(0)

    skip_sender = [s.lower() for s in rules["skip_sender"]]
    skip_subject = [s.lower() for s in rules["skip_subject"]]
    expects = [s.lower() for s in rules["expects_reply"]]

    seen: set[str] = set()
    candidates: list[dict[str, Any]] = []
    dropped = {"already_replied": 0, "sender_rule": 0, "subject_rule": 0, "no_ask": 0}

    for message in backend.search(f"in:inbox newer_than:{days}d -from:me", limit):
        item = parse_message(message)
        key = item["thread"] or item["subject"]
        if not key or key in seen:
            continue
        seen.add(key)
        if item["thread"] and item["thread"] in replied:
            dropped["already_replied"] += 1
            continue
        if any(rule in item["sender"].lower() for rule in skip_sender):
            dropped["sender_rule"] += 1
            continue
        if any(rule in item["subject"].lower() for rule in skip_subject):
            dropped["subject_rule"] += 1
            continue
        haystack = f"{item['subject']} {item['snippet']}".lower()
        if not any(rule in haystack for rule in expects):
            dropped["no_ask"] += 1
            continue
        candidates.append(item)

    return {"candidates": candidates, "replied_threads": len(replied),
            "own_address": own_address, "dropped": dropped}


def rank(candidates: list[dict[str, Any]], rules: dict[str, Any],
         now: datetime) -> list[dict[str, Any]]:
    hints = [h.lower() for h in rules["important_hints"]]
    per_day = int(rules["wait_points_per_day"])
    cap = int(rules["wait_days_cap"])
    bonus = int(rules["important_points"])

    def score(item: dict[str, Any]) -> float:
        points = 0.0
        if item["when"]:
            points += min((now - item["when"]).days, cap) * per_day
        haystack = f"{item['subject']} {item['snippet']}".lower()
        points += sum(bonus for hint in hints if hint in haystack)
        return points

    scored = [{**item, "score": score(item)} for item in candidates]
    # Stable, explainable order: score, then oldest first, then subject.
    scored.sort(key=lambda i: (-i["score"],
                               i["when"].timestamp() if i["when"] else 0.0,
                               i["subject"]))
    return scored


def render_brief(ranked: list[dict[str, Any]], total: int, now: datetime,
                 top: int) -> str:
    lines = [f"## You owe a reply - {now.strftime('%A, %B %d, %Y')}", ""]
    if not ranked:
        lines.append("Nothing is waiting on you.")
    for index, item in enumerate(ranked[:top], start=1):
        if item["when"]:
            days = (now - item["when"]).days
            waited = "today" if days == 0 else f"{days} day{'s' if days != 1 else ''}"
        else:
            waited = "recent"
        lines.append(f"{index}. {display_name(item['sender'])} - {item['subject']} "
                     f"- waiting {waited}")
    lines += ["", f"Reviewed inbound mail; {total} thread(s) need a reply."]
    return "\n".join(lines) + "\n"


def run(backend: Backend, rules: dict[str, Any], out_path: Path,
        notify_email: str = "", send: bool = False,
        now: datetime | None = None) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    collected = collect(backend, rules)
    ranked = rank(collected["candidates"], rules, now)
    brief = render_brief(ranked, len(ranked), now, int(rules["top"]))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(brief, encoding="utf-8")

    recipient = notify_email or collected["own_address"]
    subject = f"Reply debt - {now.strftime('%b %d')}: {len(ranked)} threads awaiting you"
    delivery = "not sent (--send was not passed)"
    if send:
        if not recipient:
            delivery = ("not sent: no recipient. Pass --notify-email; the address "
                        "could not be read from your own sent mail either")
        elif not backend.can_send:
            delivery = f"not sent: the {type(backend).__name__} backend cannot send"
        elif not ranked:
            delivery = "not sent: nothing is waiting on you"
        else:
            backend.send(recipient, subject, brief)
            delivery = f"sent to {recipient}"

    return {"awaiting": len(ranked), "replied_threads": collected["replied_threads"],
            "dropped": collected["dropped"], "brief_path": str(out_path),
            "subject": subject, "delivery": delivery, "brief": brief,
            "ranked": ranked}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--backend", choices=("gmail-api", "composio", "fixture"),
                        default="gmail-api")
    parser.add_argument("--fixture", type=Path, default=None,
                        help="message fixture for --backend fixture")
    parser.add_argument("--connection-id", default=None,
                        help="Composio connected-account id (an identifier, not a secret)")
    parser.add_argument("--config", type=Path, default=None,
                        help="JSON overriding any of the filter and ranking rules")
    parser.add_argument("--out", type=Path, default=Path("out/brief.md"))
    parser.add_argument("--notify-email", default=None,
                        help="where to send the brief. No default: without it the "
                             "script falls back to the address on your own sent mail, "
                             "and refuses to send if it cannot find one.")
    parser.add_argument("--send", action="store_true",
                        help="actually send. Off by default; the brief is always written.")
    parser.add_argument("--days", type=int, default=None, help="lookback window")
    parser.add_argument("--top", type=int, default=None, help="rows in the brief")
    parser.add_argument("--json", action="store_true", help="print the summary as JSON")
    args = parser.parse_args(argv)

    try:
        rules = load_rules(args.config)
        if args.days is not None:
            rules["days"] = args.days
        if args.top is not None:
            rules["top"] = args.top
        backend = build_backend(args.backend, args.fixture, args.connection_id)
    except ConfigError as exc:
        print(f"config error: {exc}", file=sys.stderr)
        return 2

    try:
        result = run(backend, rules, args.out,
                     notify_email=(args.notify_email or ""), send=args.send)
    except BackendError as exc:
        # Never let a backend failure look like an empty inbox.
        print(f"mail backend failed: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps({k: v for k, v in result.items()
                          if k not in ("brief", "ranked")}, sort_keys=True, indent=2))
    else:
        print(result["brief"])
        print(f"[delivery] {result['delivery']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
