---
name: composio-gmail-operations
description: Use Composio CLI to select the right Gmail connection, inspect threads, and verify draft, reply, and send outcomes.
---

# Composio Gmail operations

Use the Composio CLI for Gmail tasks when a connection already exists. Mailbox identity and message state are part of the result, not assumptions.

## Configuration

Choose the intended connected mailbox alias for each task. Keep authentication in Composio's connection store or a process scoped secret provider. Define any organization specific authorization policy separately; this skill never grants permission to send.

## Procedure

1. Run `composio connections list` and identify the requested mailbox. If several Gmail connections exist, pass `--account <alias>` to every execution. If the mailbox is unclear, resolve it before touching messages.
2. Find the operation with `composio search "<task>" --toolkits gmail`, then inspect its current input using `composio execute <GMAIL_TOOL> --get-schema`. Tool slugs and fields may change; use the returned schema.
3. Search or read the real message and thread. For a reply, take To, CC, sender, and thread ID from the message headers and task instructions. Do not infer recipients from display names or snippets.
4. Preview a mutation with `composio execute <GMAIL_TOOL> --account <alias> --dry-run -d '<JSON>'` where supported. Create a draft or send only when the user's request authorizes that action. Labels, archive state, and read state are mutations too.
5. Re-read the result. For sends and replies verify the `SENT` label, expected thread ID, sender, recipients, and body. A successful tool call alone is insufficient evidence. Report a mismatch as unresolved and do not send a duplicate blindly.

If a required Composio operation fails or is missing, record the failure before choosing another interface. Avoid putting credentials in prompts, files, CLI arguments, or logs.

## Example

An operator asks for a reply to a support thread from the team mailbox. List connections and select that mailbox alias, read the full thread and headers, draft the reply, check the recipient list and thread ID, send after the operator authorizes the exact reply, then re-read the sent message and confirm `SENT`, sender, recipients, body, and thread ID.
