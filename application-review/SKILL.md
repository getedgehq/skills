---
name: application-review
description: >-
  Review a YC or a16z Speedrun application before the founder submits it. Use
  when a founder asks to review, score, cut or rewrite their accelerator
  application answers, asks "what would a YC partner think", or wants friends,
  mentors or alumni to review the draft. Scores every answer against public
  advice from YC and Speedrun partners, names the top issue, writes a rewrite,
  and drafts short review asks. Optionally creates one private link per
  reviewer that collects notes per question.
---

# Review your application

You review a founder's YC or a16z Speedrun answers the way a partner reads them: fast, in plain English, looking for what is built, who uses it and why this team. Then you help the founder get notes from people they trust. No account or server is needed. The private review links in step 5 are optional.

The rubric is in `references/rubric.md`. Every rule there cites its public source (Garry Tan, Dalton Caldwell, Michael Seibel, Kevin Hale, a16z Speedrun partners, Troy Kirwin's bad-vs-great Speedrun teardown). Read it before step 2.

## 1. Get the answers

Ask for the application text: a pasted draft, a doc or the portal export. Note the program (YC or Speedrun). Keep the questions exactly as the portal asks them and the answers verbatim. Do not invent answers. List empty questions back to the founder.

Ask for any facts you would need to check claims: what is live, real user counts with how they are measured, revenue. Never fill gaps with guesses.

## 2. Score every answer

For each answer, in the program's order:

1. **Score 0-10** against the rubric. The weakest critical rule caps the score (honesty B6, clarity A1-A3, the 20-second rule E1). It is not an average.
2. **Top issue:** one line, quoting the exact words that cost points, with the rule id (for example `A1: "AI-powered platform"`).
3. **Rewrite:** uses only facts from the founder's text or answers to your questions. Keeps their voice. Leads with the strongest fact. About 20 seconds to read (60-80 words) unless the question needs less. Things not built yet are in future tense.
4. **Word count** of the rewrite (character count for the 50-character YC description).

Checks to run on every answer:
- What it is, in the first sentence. No problem setup before the "what".
- Plain English, no jargon or "platform". Would they say it to a friend?
- Active metrics (DAU, WAU, retention, revenue) lead; cumulative totals only as support; each metric defined.
- Nothing reads as live that is not live. Every number defensible in the interview.
- No volunteered weakness the question did not ask for.
- The YC "describe in 50 characters" line: name what it does, concrete nouns, count the characters.

Output a table, one row per question:

| # | Question | Score | Top issue | Rewrite | Words |
|---|---|---|---|---|---|

Then three lines for the whole application: the strongest answer, the weakest answer, and whether the numbers agree across answers.

Show the rewrites as suggestions. The founder decides. Never claim the application will be accepted.

## 3. Whole-application pass

- The first answer gets the most attention. If it is weak, fix it first.
- Facts that are strong in one answer and missing in another (a defined user metric, a named customer, a first-hand founder insight): port them.
- Same number everywhere. A metric that changes between answers is a red flag.
- For Speedrun, also run the D levers (one-liner, specific traction, founder-market fit, play to win).

## 4. Draft review asks for friends

Founders get the best notes from people who know them: alumni of the program, founders one stage ahead, someone who knows the market, one blunt friend. Three to five people.

Draft one short message per reviewer for the founder to send from their own account. You never send it. Rules:

- Two to four lines, plain, in the founder's voice and the language they use with that person.
- Say what it is, the deadline, and the one thing you want ("tell me which answer you would cut", "would you submit this as is?").
- No pitch, no stats they did not ask for. Do not use the word "AI" and do not say an agent drafted it.

By default the founder attaches a shared doc or pastes the answers. Offer to produce a clean copy: questions in bold, answers below, one question per block, ready to paste into a doc or a message.

Example:

> Hey Jordan, I'm submitting to YC on Monday. Could you skim my answers and tell me where it reads weak? Takes about 5 minutes. Doc: <link>

## 5. Optional: one private review link per reviewer

Offer it once, in one line, after the asks are drafted:

> Want a private link per reviewer instead of a doc? Each person gets their own page, leaves notes on any answer, and I pull the notes back here. You see who opened it and how long they spent on each answer.

If they say no, stop here and keep working from the notes they paste back. If yes, use the hosted review service:

Base URL: `BASE=${EDGE_REVIEW_URL:-https://appreview-preview.91.99.110.206.nip.io}` (preview).

### 5a. Create the application

The first call creates a founder key. Store it in `~/.config/edge-app-review/key` with mode 600, and read it from there for every later call. Never print it in chat, commit it or paste it into a message. The founder can open the dashboard with it.

```bash
mkdir -p ~/.config/edge-app-review && umask 077
curl -s -X POST "$BASE/api/founders" -H 'Content-Type: application/json' -d '{}' \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["key"])' > ~/.config/edge-app-review/key
KEY=$(cat ~/.config/edge-app-review/key)
```

If the founder is signed in to Edge and you have their Edge access token, you can send that as the Bearer token instead of a key.

Use the answers the founder approved in step 2 as `a`. For long answers, a one-line `tl` (shown before the full text) must stay true to `a`.

Write the application JSON to a file, then post it:

```bash
# app.json: {"program":"yc" | "speedrun", "company":"Acme", "founder_name":"Maya Chen", "items":[{"sec":"FOUNDERS","q":"...","a":"...","tl":"..."}]}
curl -s -X POST "$BASE/api/apps" -H "Authorization: Bearer $KEY" -H 'Content-Type: application/json' --data @app.json
```

Keep the returned `id` (`app_...`). Limits: 80 questions, 12,000 characters per answer.

### 5b. Mint one link per reviewer

```bash
curl -s -X POST "$BASE/api/apps/$APP/links" -H "Authorization: Bearer $KEY" -H 'Content-Type: application/json' -d '{"name":"Jordan Park"}'
# -> {"token":"...","url":"$BASE/r/<token>"}
```

### 5c. Put the links in the asks

Use the asks from step 4 with each person's own link in place of the doc. One link per person, so the founder knows who said what. Never reuse a link for two people.

### 5d. Watch and pull the notes

```bash
curl -s "$BASE/api/apps/$APP" -H "Authorization: Bearer $KEY"        # dashboard data: links, opens, seconds per answer, versions seen
curl -s "$BASE/api/apps/$APP/notes" -H "Authorization: Bearer $KEY"  # notes grouped per question of the latest version
```

Tell the founder in a few lines: who opened it, who did not, which answers people stopped on longest, and how many notes came in. The founder's dashboard is `$BASE/dash` (they paste the key once).

### 5e. Rewrite from the notes

For each question with notes:

1. Quote the notes, with who wrote them and on which version (`on_version`; `answer_then` holds the answer they actually read when it differs).
2. Say what the notes have in common. Two reviewers stumbling on the same line matters more than one strong opinion.
3. Propose a rewrite with the step 2 rules that keeps the founder's facts and voice. Never invent numbers, users, revenue or names. If a note asks for a fact you do not have, ask the founder.
4. Shorter usually wins. Portal answers are read fast.

Get the founder's OK per answer, then post the whole set as a new version with a one-line change note:

```bash
# v2.json: {"change_note":"Shorter traction answer, clearer what we make","items":[...all questions, rewritten where agreed...]}
curl -s -X POST "$BASE/api/apps/$APP/versions" -H "Authorization: Bearer $KEY" -H 'Content-Type: application/json' --data @v2.json
```

Reviewers keep the same link. They see the new version with "Updated since you last looked" and a link to the previous version they saw. Their old notes stay attached to the version they wrote them on. Keep each question's `q` text identical across versions, so notes stay matched to it.

### 5f. Before they submit

Run one last pass with the founder: every note answered or consciously skipped, no answer over the portal limit, numbers consistent across answers. Revoke links when the review is over:

```bash
curl -s -X DELETE "$BASE/api/apps/$APP/links/$TOKEN" -H "Authorization: Bearer $KEY"
```

### Hosted API reference

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
