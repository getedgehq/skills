---
name: connect-inbox
description: Set up WhatsApp, LinkedIn, Instagram and email in Edge so the agent can read chats and send with the user's one-tap approval. Use when the user says "set up my inbox", "connect my WhatsApp/LinkedIn/Instagram/email", "set up Edge messaging", or asks to read or reply to messages and nothing is connected yet.
---

# Connect inbox

Goal: the user connects every network they want in a few minutes, with one link at a time and nothing to configure.

## Edge tools

These are Edge connector tools. Call each one through Edge's `use_tool` with its tool id, for example `use_tool {"tool":"whatsapp.status","input":{}}`. If your Edge connector does not list them, run `find_tool` with "connect my WhatsApp to Edge" first.

| Network | Connect | Status | Latest chats |
| --- | --- | --- | --- |
| WhatsApp | `whatsapp.connect` | `whatsapp.status` | `whatsapp.list_chats` |
| LinkedIn | `linkedin.connect` | `linkedin.status` | `linkedin.list_chats` |
| Instagram | `instagram.connect` | `instagram.status` | `instagram.list_chats` |
| Email | `email.connect` | `email.status` | `email.list` |

## Steps

1. Ask once: "Which ones should I connect: WhatsApp, LinkedIn, Instagram, email? Say 'all' for all four." Default to all.
2. For each chosen network, one at a time, in this order: WhatsApp, LinkedIn, Instagram, email.
   - Call that network's status tool first. If it already says connected, go to the next network.
   - Call that network's connect tool.
   - Give the user the link it returns with one line on what to do:
     - WhatsApp: "Open this, then scan the QR code with WhatsApp on your phone (Settings, Linked devices)."
     - LinkedIn, Instagram, email: "Open this and sign in. Edge never sees your password."
   - Wait until the user says done, then call the network's status tool to confirm. If it is not connected, call the connect tool again for a fresh link (each link works for 10 minutes) and give it once.
3. Show it works: call the latest-chats tool of each connected network with `{"limit": 3}` and list the 3 latest chats (names and times only).
4. Tell the user how to use it, in three lines:
   - "Ask me things like: what did Anna write me on WhatsApp?"
   - "To send, say: reply to Anna on WhatsApp: see you at 3. You get a link, tap Send there. Nothing goes out without your tap."
   - "Your LinkedIn drafts and scheduled posts: ask me 'show my LinkedIn drafts'."

   When the user asks for them, call `linkedin.post_drafts` and `linkedin.scheduled_posts`.

## Rules

- Never send, post, invite or delete during setup.
- If a connect tool says the account is not in the beta, tell the user: "This is invite-only right now."
- Never ask for a password or a code in chat. Sign-in happens only on the linked page.
- Keep every message to the user short: one link, one line.
