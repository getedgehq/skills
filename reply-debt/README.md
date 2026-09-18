# reply-debt

Ranks the mail still waiting on your reply. Drops threads you already answered,
bots and newsletters, keeps mail that asks something, and orders it by how long
the person has waited. Deterministic: no model reads your mail.

```
npx skills add getedgehq/skills --skill reply-debt
```

## Prerequisites

**This one is not credential-free.** It needs a mailbox:

- **`--backend gmail-api`** — a Gmail OAuth access token in `GMAIL_ACCESS_TOKEN`,
  scope `gmail.readonly` (plus `gmail.send` only if you use `--send`).
- **`--backend composio`** — `COMPOSIO_API_KEY` in the environment and
  `--connection-id <connected account id>`.
- **`--backend fixture`** — a local JSON file. No credential, no network. Use it
  to tune the filters before connecting anything.

Also: Python 3.9 or later, standard library only. `pytest` only for the tests.

The token is read from the environment inside the backend. It is never an
argument, never logged, never written to the config.

## Quick start

```
# offline, with the bundled sample inbox
python scripts/reply_debt.py --backend fixture --fixture tests/fixtures/inbox.json

# against real mail, writing the brief but sending nothing
export GMAIL_ACCESS_TOKEN=...
python scripts/reply_debt.py --backend gmail-api --days 10 --out out/brief.md

# and mail it to yourself
python scripts/reply_debt.py --backend gmail-api --notify-email you@yourdomain --send
```

Exit codes: `0` success, `1` the mail backend failed, `2` bad config.

## Output

```
## You owe a reply - Tuesday, March 04, 2025

1. Dana Okonkwo - Re: contract review before Friday - waiting 6 days
2. Sam Ruiz - Can you intro me to your design lead? - waiting 4 days
3. Priya Raman - quick question about the API limits - waiting 2 days

Reviewed inbound mail; 3 thread(s) need a reply.
```

## Honest limits

- The filters are substring rules, not comprehension. A one-line "thanks, go
  ahead" contains no question and gets dropped. Tune `expects_reply` against a
  fixture of your own mail before you trust the list to be complete.
- It only sees the snippet Gmail returns, not the full body. A request buried in
  paragraph four of a long message can be missed.
- "Already replied" means you sent something in that thread inside the window. If
  you answered by phone, by Slack, or 12 days ago with a 10-day window, the thread
  still shows up.
- Gmail's `newer_than` granularity is days. There is no hour-level window.
- It never writes to your mailbox except the optional brief you send yourself.

## Tests

```
python -m pytest tests -q
```

No network: the tests use the fixture backend and stubs.

Apache-2.0. See `LICENSE` and `DERIVATION.json`.
