---
name: application-review
description: >-
  Get a YC or a16z Speedrun application reviewed by people the founder trusts.
  Use when a founder wants feedback on their accelerator application answers,
  asks to send their YC or Speedrun draft to friends, mentors or alumni, wants
  to know who read it, or wants to rewrite answers from reviewer notes. Turns
  the answers into one private tracked link per reviewer, drafts the ask, pulls
  the notes back per question and proposes rewrites as a new version.
---

# Get your application reviewed

You help a founder get honest notes on their YC or a16z Speedrun answers before they submit. Every reviewer gets their own private link. The page greets them by first name, shows each answer cut to one line with the full text one click away, and lets them leave a note on any answer or a general note. The founder sees who opened it, how long they spent on each answer and every note. You pull the notes back and rewrite.

Base URL: `BASE=${EDGE_REVIEW_URL:-https://appreview-preview.91.99.110.206.nip.io}` (preview).

Work in this order.

## 1. Get the answers

Ask the founder for their application text: a pasted draft, a file, or the portal export. Do not invent answers. If a question has no answer yet, leave `a` as an empty string and tell the founder which ones are empty.

Build `items` in the program's order. One item per question:

- `q`: the question exactly as the portal asks it.
- `a`: the founder's answer, verbatim. Keep their line breaks; lines starting with `- ` render as a list.
- `sec` (optional): the portal section, for example `FOUNDERS`, `PROGRESS`, `IDEA`. It becomes the side navigation.
- `tl` (optional): a one-line summary shown before the full answer, for answers longer than about two lines. It must stay true to `a`. Never add a claim that is not in the answer.

Show the founder the list of questions and the one-liners before you post. Fix anything they object to.

## 2. Create the application

The first call creates a founder key. Store it in `~/.config/edge-app-review/key` with mode 600, and read it from there for every later call. Never print it in chat, commit it or paste it into a message. The founder can open the dashboard with it.

```bash
mkdir -p ~/.config/edge-app-review && umask 077
curl -s -X POST "$BASE/api/founders" -H 'Content-Type: application/json' -d '{}' \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["key"])' > ~/.config/edge-app-review/key
KEY=$(cat ~/.config/edge-app-review/key)
```

If the founder is signed in to Edge and you have their Edge access token, you can send that as the Bearer token instead of a key.

Write the application JSON to a file, then post it:

```bash
# app.json: {"program":"yc" | "speedrun", "company":"Acme", "founder_name":"Maya Chen", "items":[{"sec":"FOUNDERS","q":"...","a":"...","tl":"..."}]}
curl -s -X POST "$BASE/api/apps" -H "Authorization: Bearer $KEY" -H 'Content-Type: application/json' --data @app.json
```

Keep the returned `id` (`app_...`). Limits: 80 questions, 12,000 characters per answer.

## 3. Mint one link per reviewer

Ask who should review it. Good reviewers: alumni of the program, founders one stage ahead, someone who knows the market, one blunt friend. Three to five is enough. One link per person, so the founder knows who said what. Never reuse a link for two people.

```bash
curl -s -X POST "$BASE/api/apps/$APP/links" -H "Authorization: Bearer $KEY" -H 'Content-Type: application/json' -d '{"name":"Jordan Park"}'
# -> {"token":"...","url":"$BASE/r/<token>"}
```

## 4. Draft the ask

Draft one short message per reviewer for the founder to send from their own account. You never send it yourself. Rules:

- Two to four lines, plain, in the founder's voice and the language they use with that person.
- Say what it is, the deadline, and the one thing you want from them ("tell me which answer you'd cut", "would you submit this as is?").
- Their link only. No pitch, no stats they didn't ask for.
- Do not use the word "AI" and do not mention that an agent drafted it.

Example:

> Hey Jordan, I'm submitting to YC on Monday. Would you skim my answers and leave a note wherever something reads weak? Takes about 5 minutes: <link>

Show every draft to the founder and let them edit before they send.

## 5. Watch and pull the notes

```bash
curl -s "$BASE/api/apps/$APP" -H "Authorization: Bearer $KEY"        # dashboard data: links, opens, seconds per answer, versions seen
curl -s "$BASE/api/apps/$APP/notes" -H "Authorization: Bearer $KEY"  # notes grouped per question of the latest version
```

Tell the founder in a few lines: who opened it, who did not, which answers people stopped on longest, and how many notes came in. The founder's dashboard is `$BASE/dash` (they paste the key once).

## 6. Propose rewrites

For each question with notes:

1. Quote the notes, with who wrote them and on which version (`on_version`; `answer_then` holds the answer they actually read when it differs).
2. Say what the notes have in common. Two reviewers stumbling on the same line matters more than one strong opinion.
3. Propose a rewrite that keeps the founder's facts and voice. Never invent numbers, users, revenue or names. If a note asks for a fact you do not have, ask the founder.
4. Shorter usually wins. Portal answers are read fast.

Get the founder's OK per answer, then post the whole set as a new version with a one-line change note:

```bash
# v2.json: {"change_note":"Shorter traction answer, clearer what we make","items":[...all questions, rewritten where agreed...]}
curl -s -X POST "$BASE/api/apps/$APP/versions" -H "Authorization: Bearer $KEY" -H 'Content-Type: application/json' --data @v2.json
```

Reviewers keep the same link. They see the new version with "Updated since you last looked" and a link to the previous version they saw. Their old notes stay attached to the version they wrote them on. Keep each question's `q` text identical across versions, so notes stay matched to it.

## 7. Before they submit

Run one last pass with the founder: every note answered or consciously skipped, no answer over the portal limit, numbers consistent across answers. Revoke links when the review is over:

```bash
curl -s -X DELETE "$BASE/api/apps/$APP/links/$TOKEN" -H "Authorization: Bearer $KEY"
```

## API reference

| Call | Body | Returns |
|---|---|---|
| `POST /api/founders` | `{}` | `{key}` (shown once) |
| `POST /api/apps` | `{program, company?, founder_name?, items}` | `{id, latest_version, dashboard}` |
| `GET /api/apps` | | your applications |
| `GET /api/apps/<id>` | | versions, links with opens/seconds/versions seen, all notes |
| `GET /api/apps/<id>/notes` | | notes per question of the latest version, general notes |
| `POST /api/apps/<id>/versions` | `{items, change_note?}` | `{version}` |
| `POST /api/apps/<id>/links` | `{name}` | `{token, url}` |
| `DELETE /api/apps/<id>/links/<token>` | | revokes the link |

All founder calls need `Authorization: Bearer <key>`. Reviewer pages only ever see their own link's notes.
