# Session log: `top-down-comms.client-update-from-thread:loaded:s1`

| | |
| --- | --- |
| Task | `top-down-comms.client-update-from-thread` |
| Arm | **loaded** (SKILL.md loaded) |
| Sample | 1 of 3 |
| Agent model | `us.anthropic.claude-sonnet-4-5-20250929-v1:0` |
| Turns used | 5 (cap 40, plus up to 3 wrap-up turns) |
| Tool calls | 5 (0 returned an error) |
| Model cost | $0.0541 |
| Agent wall time | 78s (77s waiting on the model, 1s in tools) |
| Stop reason | `end_turn` |
| Hit a cap | no |
| Read SKILL.md | yes |
| Hard check | pass=True score=0.941 |

## The request the agent was given

```
hey, can you draft the update email to Rosa at Halden about the migration dry run? slack export from our internal channel is in the folder plus last week's call notes. she reads these on her phone. put the draft in output/ (subject line + body), I'll send it myself
```

## System prompt

Identical in both arms except for the `<available_skills>` block, which is present only in the `skill` arm.

````
You are an AI assistant with access to a Linux computer through tools. The user's files are in /home/user/work, which is your current working directory.

Complete the user's request end to end: do the actual work with the tools, save deliverables as files when a file is the natural output, and finish with a reply to the user in chat. The user is not available for follow-up questions during the task; if something is ambiguous or missing, make a sensible call and say so, or explain clearly what blocks you.

Environment: Debian Linux, Python 3.11, Node 20, git, jq, curl, ImageMagick. Internet access is available (pip/npm/apt installs work). Today's date is 2026-09-17.

The user has enabled the skill below for this conversation. Its instructions are loaded here; follow them. Bundled files (scripts, references) are in /home/user/.skills/top-down-comms/.

<skill name="top-down-comms">
---
name: top-down-comms
description: >-
  Structure any client-facing artifact the way MBB consultants do: governing
  thought first, action titles that carry the argument, scope exclusions as
  metadata rather than the opening move. Load this BEFORE writing a client
  proposal, one-pager, share page, update email, deck, or memo. This is about
  ARGUMENT STRUCTURE, not tone. Triggers: "proposal", "one-pager", "client update", "make this clean for them", "top-down",
  "McKinsey/BCG style", "restructure this", "fix the storyline".
---

# Top-down client communication

Tone skills tell you how it sounds. This one tells you what goes first, and why.
A perfectly-voiced document with an inverted argument still fails.

## The failure this exists to stop

A reviewer, on a proposal page that had already passed three visual rounds:
*"This is better now, but fix the storyline. Why should we start with this?
Think about this from the perspective of a McKinsey consultant, a BCG
consultant, and top-down communication."*

The page opened with **"No automated analysis of the source imagery"** — a scope
exclusion. It was there for a good reason: the recipient's own experts had
beaten a machine benchmark, and liability was their live objection. But a
reader's first impression was a disclaimer about something the document was
not, and they had to reach section three before learning what was actually
being proposed.

**Defensive openings feel responsible and read as weak.** The instinct to
front-load the caveat is exactly the instinct to override.

## Rule 1: the governing thought goes first

Minto's pyramid. The first substantive sentence is **the answer**, not the
background, not the topic, not the caveat. Everything below supports it.

| Opening | Verdict |
|---|---|
| "No automated analysis of the source imagery." | Exclusion. What it is not. |
| "Ranking incoming orders by contribution margin" | Topic label. Names a subject, asserts nothing. |
| "At full capacity the question is not how many orders you accept but which ones. The proposal: score every incoming request automatically by expected contribution margin." | The answer. Recommendation + reason, first thing on the page. |

Test: if the reader stops after sentence one, do they know what you want them to
do? If not, rewrite sentence one.

## Rule 2: action titles, not topic labels

Every section heading states its **conclusion**. A reader who reads only the
headings must get the whole argument. This is the single highest-leverage move
and the one most often skipped.

| Topic label (weak) | Action title (right) |
|---|---|
| Background | The bottleneck is capacity, not demand |
| Scoring logic | Five criteria decide what an order is actually worth |
| Example | Two requests the same morning, same effort, different margin |
| The test | Checkable in an hour, before anything is built |
| Effort | A few days to running |

**The headline-only test.** Strip the body. Read the titles in sequence. If they
do not form a coherent argument, the structure is wrong and no amount of body
copy will save it.

## Rule 3: SCR, and the complication is the whole job

Situation (what both sides agree is true) → Complication (why it cannot stay
that way) → Resolution (your recommendation). Most weak documents have a
situation and a resolution and no complication, so the recommendation arrives
unmotivated.

The complication should be arithmetic where possible: *"If you work orders in
arrival order rather than by margin, every thin-margin order you accept costs
you a fat-margin one."* That is a mechanism the reader can check, not an
assertion they must accept.

## Rule 4: exclusions and caveats are metadata

They belong in a scan strip near the top or a numbered section at the end. Never
in the opening position, never as a heading before the recommendation.

The **"at a glance" strip** solves this: a four-cell row directly under the
governing thought.

```
IN SCOPE            NOT IN SCOPE           DATA SOURCE            NEXT STEP
The order in        Automated analysis     Accounting exports,    20 to 30 invoices,
which requests      of the source          not project folders    about 1 hour
are worked          imagery
```

The exclusion is visible in the first screen, so nobody can claim it was buried,
but it is framed as scope rather than apology. Give it a full section at the end
if the objection is serious enough to deserve one.

## Rule 5: number the sections

01, 02, 03. Consultants do it because it makes a document referenceable in a
meeting ("go back to 02"). It also forces you to notice when you have eleven
sections, which means you have no argument, only a list.

## Rule 6: one falsifiable next step

End on something specific, small, and capable of failing. Not "let's discuss".
The strongest closer names the kill condition:

> If the ranking is wrong, the logic is wrong, and the idea is dead.

An offer that can fail is more credible than an offer that cannot, especially to
a room that has already been sold to.

## Rule 7: MECE, and cut to the load-bearing sections

Sections must not overlap and must not leave a hole in the argument. If two
sections make the same point, merge them. If a section supports nothing above
it, delete it.

Applied test from the same document: an unrelated reference case sat in the
middle of a proposal about order prioritisation. The reviewer's note: *"the text
is random ... either it goes in the email, or if it goes here, there has to be
clear context."* It supported a different governing thought, so it belonged in a
different artifact. It moved to the covering email and the page got shorter and
stronger.

## Checklist before shipping

1. First substantive sentence is the recommendation, not background or a caveat.
2. Headings read alone as a complete argument.
3. There is a stated complication, ideally arithmetic.
4. Exclusions live in a scan strip or a closing section, never the opening.
5. Sections are numbered and MECE.
6. The close is one specific, falsifiable next step.
7. Nothing on the page supports a different governing thought.

## Not covered here

Tone and register: this skill is about argument order, not voice. Length caps
for short client messages, and the build and publish mechanics of a share page,
are separate concerns.

</skill>
````

## Hard check detail

- primary doc: output/email_to_rosa.txt (345 words, 345 prose words, top window 120 words)
- PASS [gate] recommendation (Oct 5 go-live, 2019+ records) in the top section (oct5@34, 2019@81)
- PASS [gate] Fri Sep 18 decision deadline in the top section (first at word 11)
- PASS [gate] uses the full-run failure count (312,000 / 13%)
- PASS [gate] routes sign-off to Mira Castellanos and not to Tomasz
- PASS [gate] does not state 'the 25th' as the decision deadline
- PASS [gate] option A's EUR 18,400 is not the leading figure (18400@117, 6200@179)
- PASS [gate] first 70 words carry an ask, a date and an owner (ask=True, date=True, owner=True)
- PASS excludes the ops dashboard upsell
- PASS opening is not a blame or self-defence line
- PASS explains the timing mechanism (Stratacore / freeze window / 10 business days / peak)
- PASS both options are visible with their cost (18,400 and 6,200)
- PASS does not quote the superseded ~EUR 9k figure for option B
- PASS names the Nov 30 read-only archive date
- PASS says the old WMS / archive covers pre-2019 lookups in the meantime
- PASS says option A would land inside the peak-season freeze (Oct 19 / Oct 12)
- PASS ends with a concrete, checkable next step (who does what, by when)
- FAIL phone-length (345 prose words <= 340)

## Files the agent left behind

- `output/email_to_rosa.txt`

## Turns

Every assistant turn, every tool call with its full arguments, and every tool result.
Tool output is recorded as the harness stored it, cut off at 6000 characters per call;
the agent itself saw the full text.

### Turn 1: assistant  (9.7s into the session)

I'll draft that update email for Rosa. Let me first check what files are in the folder to find the Slack export and call notes.

**calls `bash`**

```bash
ls -la
```

**`bash` returned**

```
exit_code: 0
stdout:
total 12
drwxr-xr-x 2 user user  128 Sep 17 02:14 .
drwx------ 4 user user  128 Sep 17 02:14 ..
-rw-r--r-- 1 user user 1424 Sep 17 02:14 call_notes_halden_2026-09-10.md
-rw-r--r-- 1 user user 7151 Sep 17 02:14 slack_export_halden-migration.txt


```

### Turn 2: assistant  (13.7s into the session)

**calls `read_file`**

path: `call_notes_halden_2026-09-10.md`

**calls `read_file`**

path: `slack_export_halden-migration.txt`

**`read_file` returned**

```
# Halden Logistics weekly call, Thu 10 Sep 2026

Attendees: Rosa Lindqvist (VP Operations, Halden, exec sponsor), Mira Castellanos (IT Director, Halden), Aylin Demir (Northpine, engagement lead), Jonas Weber (Northpine, data engineer)
Apologies: Tomasz Novak (Halden, on leave)

Notes (Jonas, rough, not circulated)

- Rosa opened by reminding everyone the board gets a WMS update on Oct 1. She
  wants "no surprises", and a short written update whenever something moves,
  not a slide deck. She reads these on her phone between site visits.
- Rosa: peak season starts Oct 12. Hard no on anything touching the warehouse
  floor systems from Oct 12 to Dec 20 unless it is a fix to something broken.
  She was very clear about this, twice.
- Mira: Stratacore is hosting the new platform. Freeze windows and cutover slots
  get booked through Stratacore, not through Halden internally. Mira's team does
  not control that calendar.
- Mira asked who signs off changes now that Tomasz is out. Aylin said we would
  confirm against the SOW.
- Dry run 1 issues (carrier codes) closed and signed off.
- Dry run 2 scheduled for the weekend of Sep 12/13.
- Training for shift leads done at 2 of 3 sites. Third site (Rotterdam) Sep 29.
- Old WMS stays up read-only until Dec 31 per the SOW, so historical lookups
  have somewhere to go during and after cutover.
- Next call Thu 17 Sep. Rosa may miss it, she is at the Gothenburg site.

```

**`read_file` returned**

````
#halden-migration (internal, Northpine Data)
Export: Mon 14 Sep 2026 09:00 to Wed 16 Sep 2026 10:30
Members: Aylin Demir (engagement lead), Jonas Weber (data engineer), Priya Raman (delivery), Sam Okafor (QA), Nadia Frost (account)

[Mon 09:04] Sam Okafor: morning. standup in 10, I'm on the call from the car
[Mon 09:05] Priya Raman: no standup today, Aylin's in the Fernvale kickoff until 11
[Mon 09:12] Jonas Weber: dry run #2 finished overnight. not great. first sample check says roughly 40k shipment records failing validation, mostly the old date fields
[Mon 09:15] Priya Raman: 40k out of how many?
[Mon 09:16] Jonas Weber: 2.4M total historical shipment records in the legacy WMS
[Mon 09:17] Priya Raman: ok so like 2%. annoying but not a fire
[Mon 09:31] Sam Okafor: is it only dates? or also the carrier codes thing from dry run 1
[Mon 09:33] Jonas Weber: carrier codes are fixed and signed off. this is dates. legacy stored dd/mm and mm/dd mixed until they standardised in Jan 2019
[Mon 09:40] Sam Okafor: classic. anything from 2019 onward is clean?
[Mon 09:41] Jonas Weber: looks clean so far, I'm running the full validation now, it takes about 4 hours
[Mon 09:55] Nadia Frost: unrelated, does anyone have the signed SOW for Fernvale? the shared drive has two versions
[Mon 09:56] Priya Raman: v3 is the signed one, I'll dm you
[Mon 10:02] Aylin Demir: back. catching up. ok, we need to tell Rosa this week either way. go-live is Mon Oct 5 and their peak season starts Oct 12, so any slip lands right in peak
[Mon 10:05] Jonas Weber: can we open the email by saying the data quality problem comes from their legacy system and isn't on us? i don't want this turning into a "northpine broke our data" thing. we inherited 15 years of mixed date formats
[Mon 10:06] Sam Okafor: honestly yeah, we should protect ourselves here
[Mon 10:31] Nadia Frost: wrong channel sorry, ignore
[Mon 11:40] Priya Raman: side thought, this is a good moment to pitch the ops dashboard redesign (the 35k one). they're going to be staring at data quality anyway, it's a natural segue
[Mon 11:44] Nadia Frost: love that, Rosa asked about reporting in July
[Mon 12:05] Sam Okafor: lunch. somebody put the Rotterdam training date in the calendar, it's Sep 29 and half the team doesn't have it
[Mon 12:40] Jonas Weber: full validation still running, 70%
[Mon 14:02] Jonas Weber: done. dropping the tail of validation_full.log here
[Mon 14:02] Jonas Weber: ```
records_scanned=2,400,118
records_failed=312,004
fail_pct=13.0
failed_by_bucket: pre_2019=311,806  post_2019=198
worst_field: ship_date (mixed dd/mm and mm/dd)
```
[Mon 14:03] Jonas Weber: so it's basically all pre-2019. the sample this morning was skewed toward recent data
[Mon 14:06] Priya Raman: ok. that's a different conversation than the one we were having at 9
[Mon 14:11] Aylin Demir: right. so the options are:
[Mon 14:13] Aylin Demir: A) cleanse ALL history before cutover. Jonas estimates 9 more working days. go-live moves to Mon Oct 19. ch

[... 1151 chars truncated ...]

e who approves this? she's the exec sponsor
[Mon 15:44] Jonas Weber: send the CR to Tomasz for signoff like last time?
[Mon 16:50] Priya Raman: heads up, Tomasz is on parental leave until November. and per SOW section 7.2 change requests are signed by Halden's IT Director. that's Mira Castellanos now
[Mon 16:51] Nadia Frost: does Rosa know that? she signed the last one I thought
[Mon 16:53] Priya Raman: no, Rosa countersigned the SOW. CRs are IT Director
[Mon 17:20] Sam Okafor: laptop died at the client site, back online tomorrow
[Tue 08:45] Jonas Weber: when do they need to decide? I told Mira's team informally "by the 25th" on Friday
[Tue 08:58] Nadia Frost: the 25th sounds fine, that's still 10 days before go-live
[Tue 09:10] Aylin Demir: it isn't fine. Stratacore host the new platform and they need the cutover freeze window confirmed 10 business days before cutover. cutover is Mon Oct 5
[Tue 09:11] Aylin Demir: and we need a day on our side to actually file the booking with them, we can't file it the same morning
[Tue 09:12] Jonas Weber: so Friday the 18th, EOD. ok. I'll correct the 25th with Mira's team
[Tue 09:13] Aylin Demir: if we miss that we lose the Oct 5 window and we're in option A territory whether we like it or not, which is go-live inside peak
[Tue 09:20] Priya Raman: also fwiw the CR can be signed digitally, 5 min job
[Tue 09:34] Aylin Demir: I'll ask our PM to draft the note today
[Tue 10:02] Sam Okafor: back. did we land on A or B
[Tue 10:04] Priya Raman: not formally
[Tue 10:30] Nadia Frost: Fernvale want a proposal by Friday btw, who's writing it
[Tue 10:31] Priya Raman: me, it's drafted
[Tue 11:15] Jonas Weber: archive cleanse for the pre-2019 set: 9 working days of compute either way, it's the same work, the question is just whether it happens before or after cutover
[Tue 11:40] Sam Okafor: happy birthday Priya btw
[Tue 11:41] Priya Raman: that was last week but thank you
[Tue 13:05] Jonas Weber: Rotterdam training is still Sep 29, confirmed with their site manager
[Tue 14:50] Nadia Frost: Rosa's assistant asked whether the Oct 1 board update is still fine. I said yes, is that right?
[Tue 14:55] Aylin Demir: depends entirely on whether we have a signed decision by then, which is the whole point
[Tue 16:20] Jonas Weber: pre-2019 archive would be loaded read-only by Mon Nov 30 under B, that's a firm date, I've got the window booked with ops
[Wed 08:15] Sam Okafor: one more thought on A: it's cleaner to tell the board "everything migrated" than "most things migrated"
[Wed 08:40] Priya Raman: the board update is Oct 1, before either go-live, so it's the same story on Oct 1 either way
[Wed 09:05] Aylin Demir: PM: the note goes to Rosa, she reads on her phone between sites, and she asked for written updates not decks. don't make it long
[Wed 09:30] Jonas Weber: I'm out Thu and Fri, ping Priya for anything on the data side
[Wed 10:12] Nadia Frost: reminder the ops dashboard deck is in the drive if anyone wants to reuse the slides

````

### Turn 3: assistant  (23.9s into the session)

Now let me create the output directory and draft the email following top-down communication principles, optimized for mobile reading.

**calls `bash`**

```bash
mkdir -p output
```

**`bash` returned**

```
exit_code: 0

```

### Turn 4: assistant  (59.9s into the session)

**calls `write_file`**

path: `output/email_to_rosa.txt`

```
SUBJECT: WMS migration — dry run 2 complete, decision needed by Fri 18 Sep

Rosa,

Dry run 2 is complete. We need a decision by end of day Friday 18 Sep to hold the Oct 5 go-live window — Stratacore requires cutover booking 10 business days ahead and we need a day to file it.

THE ISSUE
13% of historical shipment records (312k out of 2.4M) fail validation. The legacy system stored dates in mixed formats (dd/mm and mm/dd) until Jan 2019. Post-2019 records are clean (99.99% pass).

TWO OPTIONS

A) Cleanse all history before cutover
   • Go-live moves to Mon 19 Oct (inside peak season)
   • All 2.4M records available from day one
   • Cost: EUR 18,400
   • 9 working days of compute

B) Go live Oct 5 with clean records, archive follows (RECOMMENDED)
   • Go-live stays Mon 5 Oct (before peak)
   • 2.09M records live (Jan 2019 forward, covers day-to-day operations)
   • Pre-2019 lookups use old WMS (stays read-only until Dec 31 per SOW)
   • Pre-2019 archive cleansed and loaded by Mon 30 Nov
   • Cost: EUR 6,200
   • Same 9 days of compute, happens after cutover

WHY B
Warehouse floor only touches the last 2-3 years operationally. Pre-2019 is audit shelf material. Going live Oct 19 puts initial rollout inside peak (Oct 12 start), which creates floor risk. The old system stays available for lookups until year-end anyway.

THE FALSIFIABLE TEST
If your auditors or ops team need pre-2019 shipment data routinely before Nov 30, option B breaks. If they don't, it's the safer path through peak.

NEXT STEP
Mira signs the change request (per SOW section 7.2, can be done digitally in 5 minutes). We need it by EOD Fri 18 Sep or we lose the Oct 5 window.

OTHER NOTES
• Dry run 1 issues (carrier codes) closed and signed off
• Rotterdam training confirmed for Sep 29
• This is a data quality problem inherited from the legacy system, not introduced by migration

Let me know which option by Friday, or if you need anything clarified before then.

Aylin

```

**`write_file` returned**

```
wrote 1962 chars to /home/user/work/output/email_to_rosa.txt
```

### Turn 5: assistant  (77.8s into the session)

Done. I've drafted the update email and saved it to `output/email_to_rosa.txt`.

**Key choices I made:**

1. **Governing thought first**: The opening line states the critical deadline (Fri 18 Sep) immediately, not buried in paragraph 3.

2. **Mobile-optimized structure**: Short paragraphs, clear section breaks, scannable headings in caps. No tables or formatting that breaks on a phone screen.

3. **Recommendation explicit**: Option B is marked as recommended, with the arithmetic reasoning (Oct 19 lands *inside* peak vs Oct 5 before it).

4. **Falsifiable test**: "If your auditors need pre-2019 data routinely before Nov 30, option B breaks" — gives Rosa a clear way to validate the logic against her operational reality.

5. **Defensive point positioned correctly**: The note about inherited data quality is at the end as metadata, not the opening move (your team discussed this concern in Slack, but leading with "it's not our fault" would have weakened the update).

6. **Action clarity**: Mira signs, needs to happen by EOD Friday, can be done in 5 minutes digitally — removes all ambiguity about who does what by when.

The email assumes you're sending it as Aylin (the engagement lead mentioned throughout). If that's not right, just change the signature line before sending.

_stop reason: `end_turn`_

## Final message to the user

```
Done. I've drafted the update email and saved it to `output/email_to_rosa.txt`.

**Key choices I made:**

1. **Governing thought first**: The opening line states the critical deadline (Fri 18 Sep) immediately, not buried in paragraph 3.

2. **Mobile-optimized structure**: Short paragraphs, clear section breaks, scannable headings in caps. No tables or formatting that breaks on a phone screen.

3. **Recommendation explicit**: Option B is marked as recommended, with the arithmetic reasoning (Oct 19 lands *inside* peak vs Oct 5 before it).

4. **Falsifiable test**: "If your auditors need pre-2019 data routinely before Nov 30, option B breaks" — gives Rosa a clear way to validate the logic against her operational reality.

5. **Defensive point positioned correctly**: The note about inherited data quality is at the end as metadata, not the opening move (your team discussed this concern in Slack, but leading with "it's not our fault" would have weakened the update).

6. **Action clarity**: Mira signs, needs to happen by EOD Friday, can be done in 5 minutes digitally — removes all ambiguity about who does what by when.

The email assumes you're sending it as Aylin (the engagement lead mentioned throughout). If that's not right, just change the signature line before sending.
```
