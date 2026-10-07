# Tracked Deck Links

Original tracking system and design by Falco Schneider. Personal, tracked links to a pitch deck, on your own server. A self-hosted
replacement for the "who opened my deck, and what did they read" part of DocSend.

- **Link previews are not opens.** The link serves an empty shell. WhatsApp, Slack and iMessage
  unfurls, and mail scanners, get no deck content and are counted as previews.
- **Opened and read are told apart.** "Opened" means the deck loaded in a real browser. "Read" also
  needs real input and at least 10 active seconds.
- **Per-slide attention.** Active seconds and visits per slide, across all visits.
- **Devices.** A second device shows as "opened on a second device". It never says "forwarded".
- **Small to run.** One Node 22.13+ process with built-in SQLite. No dependencies, no accounts, no
  third-party analytics.

Agents start with `SKILL.md`. Humans can do the same: the commands there are all you need.

```
app/server.mjs          the tracker: shell page, signed deck serving, open/beat API, dashboard API, ntfy push
app/track.js            injected into the deck: active time, per-slide time, works with Reveal.js or plain HTML
app/admin.html          browser dashboard (password protected)
scripts/decklinks.mjs   CLI: doctor, init, publish (HTML, folder or PDF), mint, revoke, links, report
references/hosting.md   systemd unit, nginx and Caddy snippets
references/supabase-vercel.md + supabase-schema.sql   Falco's original Vercel + Supabase architecture
```

## Credits

Falco Schneider designed and built the original system: the shell-only page, the three states
(preview, opened, read), the active-time rule, the per-visit heartbeats, the summary push and the
password-protected dashboard. It was a Next.js + Supabase app with German documentation.

This package ports that design to a single Node + SQLite process. It adds per-slide timing, several
named decks, versioned publishing, PDF-to-HTML conversion, signed deck URLs with a scoped cookie, and a
plain-words report for agents.

## Licence

Apache-2.0, under the repository default licence. Licence and credit approved by Falco Schneider, confirmed by Federico on 2026-10-07.
