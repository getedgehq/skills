# Alternative: Next.js on Vercel + Supabase (Falco Schneider's original architecture)

Falco Schneider first built this system as part of a Next.js site (Pages Router) on Vercel. Supabase
held the database and a private storage bucket, and ntfy sent the push notifications. The Node + SQLite
version in this skill is a port of that design. Use this path only if the user already runs Vercel and
Supabase and does not want a server of their own. Otherwise use the default.

This folder does **not** bundle the Next.js source. Read this file as a blueprint. An agent can build
the routes from it, with `app/server.mjs` in this skill as the working reference for every rule
(states, active time, per-slide counting, devices, owner exclusion).

## Same model, different parts

| Concern | Node + SQLite (this skill) | Vercel + Supabase |
|---|---|---|
| Shell page with no content | `GET /d/<token>` in `server.mjs` | `pages/d/[slug].tsx`, server-rendered shell |
| Count the open, issue the deck URL | `POST /api/open`, HMAC-signed URL, 6 h | `pages/api/d/open.ts`, Supabase Storage signed URL, 6 h |
| Deck file | `$DECKLINKS_HOME/decks/<deck>/<version>/` | private bucket `docs` |
| Heartbeats | `POST /api/beat` | `pages/api/d/beat.ts` |
| "Visit ended" summary push | in-process timer, every 30 s | `pages/api/d/sweep.ts`, Vercel Cron every minute, protected by `CRON_SECRET` |
| Dashboard + API | `/admin`, `/api/admin` | `pages/d/admin.tsx`, `pages/api/d/admin.ts` |
| Database access | `node:sqlite` | PostgREST over HTTP with the service-role key, no SDK |
| Push | ntfy | ntfy |

## Setup steps for that stack

1. **Database.** Run `references/supabase-schema.sql` in the Supabase SQL editor. It creates three
   tables: links, views and owner devices. Row-level security is on, so only the service role can read
   or write.
2. **Bucket.** Create a **private** storage bucket called `docs` and upload the deck HTML there.
   Self-hosted Supabase serves HTML as `text/plain` by default. To render it in the frame, put a proxy
   rule in front of `/storage/v1/object/sign/docs/*.html` that sets `Content-Type: text/html` and a
   CSP `sandbox allow-scripts` with `frame-ancestors <your site>`. Supabase Cloud needs the same
   content-type override through a proxy or edge function. Raise the upload limit
   (`FILE_SIZE_LIMIT`) for decks over 50 MB.
3. **Environment variables** go in the Vercel project settings. Never put them in the repo, and the
   user enters the secret values:
   - `SUPABASE_URL`: the public URL of the Supabase project
   - `SUPABASE_SERVICE_ROLE_KEY`: server-side only, it bypasses row-level security
   - `DOC_ADMIN_PASSWORD`: the dashboard password
   - `CRON_SECRET`: Vercel sends it as a Bearer token to the sweep route
   - `NTFY_TOPIC`, and optionally `NTFY_SERVER`
4. **vercel.json.** Add the minute cron `{"path": "/api/d/sweep", "schedule": "* * * * *"}`. Set the
   function region close to the database.
5. **Register documents.** Each link points at a document id. Keep a small registry that maps each id
   to its storage object path, and use the document name as a readable link prefix, for example
   `/d/pitch-h5b5fze`.
6. **Publish.** Upload the HTML to the bucket, download it again and compare checksums. Falco's
   publisher also refuses to upload a file saved in the last 90 seconds, so that a half-edited file
   never goes live.

## Differences to know

- The original measures **scroll depth** for long documents, not per-slide time. If the user wants
  slide-level numbers on this stack, port the per-slide logic from `app/track.js` and the
  `slide_stats` table from `app/server.mjs`.
- The original records an approximate place (city and country) from Vercel's IP headers. It is
  approximate: VPNs and iCloud Private Relay move it.
- The original lets the owner mark a device as theirs in the dashboard ("that was me"). This skill only
  uses the unlocked-dashboard flag.
- The same wording rules apply on both stacks: preview is not an open, and you say "opened on a second
  device", never "forwarded".
