# Mail backends

Load this only when wiring a real mailbox. The `fixture` backend needs none of it.

## gmail-api

Gmail REST v1 as the signed-in user. The script sends
`Authorization: Bearer $GMAIL_ACCESS_TOKEN` and nothing else.

| call | endpoint |
| --- | --- |
| search | `GET /gmail/v1/users/me/messages?q=<query>&maxResults=<n>` |
| headers | `GET /gmail/v1/users/me/messages/<id>?format=metadata&metadataHeaders=From&metadataHeaders=Subject&metadataHeaders=Date` |
| send | `POST /gmail/v1/users/me/messages/send` with `{"raw": <base64url RFC 2822>}` |

Scopes: `https://www.googleapis.com/auth/gmail.readonly` is enough for the brief.
Add `https://www.googleapis.com/auth/gmail.send` only if the user wants `--send`.
Do not request `gmail.modify` or full `https://mail.google.com/` — this skill
never needs write access to the mailbox.

`format=metadata` is deliberate: it returns headers and the snippet, not message
bodies. Full bodies are more data than the ranking needs.

Access tokens are short-lived (about an hour). The script does not refresh them;
whatever issues the token is responsible for that. A `401` surfaces as
`mail backend failed: HTTP 401 ...` and exit code `1`.

## composio

For a Composio-managed Gmail connection, where the OAuth refresh lives on
Composio's side.

```
POST https://backend.composio.dev/api/v3/tools/execute/GMAIL_FETCH_EMAILS
POST https://backend.composio.dev/api/v3/tools/execute/GMAIL_SEND_EMAIL
x-api-key: $COMPOSIO_API_KEY
{"connected_account_id": "<--connection-id>", "arguments": {...}}
```

`GMAIL_FETCH_EMAILS` takes `query`, `max_results` and `include_attachments`. The
response envelope has changed shape across Composio versions, so the backend
looks for a message list under `messages`, `data`, `response_data`, `result` or
`emails` and recurses once. If a future shape breaks that, the run reports zero
candidates rather than raising — check the raw response before concluding the
inbox is clear.

A response with `successful: false` is raised as a backend failure, not swallowed.

The connected-account id identifies which mailbox to use. It is not a credential
and is safe as an argument; `COMPOSIO_API_KEY` is a credential and is only ever
read from the environment.

## fixture

```json
{"in:inbox newer_than:10d from:me": [...], "in:inbox newer_than:10d -from:me": [...]}
```

Keys are the exact query strings the script issues, so a change to `--days`
changes the keys. Messages use the Gmail metadata shape
(`payload.headers[]` with `From`, `Subject`, `Date`, plus `snippet` and
`threadId`). `parse_message` also accepts the flatter `sender` / `subject` /
`messageText` / `thread_id` shape that Composio returns.

To capture your own mailbox into a fixture, run the `gmail-api` backend once and
save the raw responses. Scrub addresses before committing the file anywhere.

## Queries

```
in:inbox newer_than:{days}d from:me     threads you already answered
in:inbox newer_than:{days}d -from:me    candidate debt
```

`newer_than` counts in whole days only. `in:inbox` means archived mail is out of
scope by design: filing something is a decision that it is handled.
