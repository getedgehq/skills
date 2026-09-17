# Session log: `top-down-comms.client-update-from-thread:loaded:s3`

| | |
| --- | --- |
| Task | `top-down-comms.client-update-from-thread` |
| Arm | **loaded** (SKILL.md loaded) |
| Sample | 3 of 3 |
| Agent model | `us.anthropic.claude-sonnet-4-5-20250929-v1:0` |
| Turns used | 5 (cap 40, plus up to 3 wrap-up turns) |
| Tool calls | 5 (0 returned an error) |
| Model cost | $0.0587 |
| Agent wall time | 73s (72s waiting on the model, 1s in tools) |
| Stop reason | `end_turn` |
| Hit a cap | no |
| Read SKILL.md | yes |
| Hard check | pass=True score=0.882 |

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

- primary doc: output/email_to_rosa.txt (480 words, 475 prose words, top window 130 words)
- PASS [gate] recommendation (Oct 5 go-live, 2019+ records) in the top section (oct5@36, 2019@151)
- PASS [gate] Fri Sep 18 decision deadline in the top section (first at word 9)
- PASS [gate] uses the full-run failure count (312,000 / 13%)
- PASS [gate] routes sign-off to Mira Castellanos and not to Tomasz
- PASS [gate] does not state 'the 25th' as the decision deadline
- PASS [gate] option A's EUR 18,400 is not the leading figure (18400@186, 6200@241)
- PASS [gate] first 70 words carry an ask, a date and an owner (ask=True, date=True, owner=True)
- PASS excludes the ops dashboard upsell
- PASS opening is not a blame or self-defence line
- PASS explains the timing mechanism (Stratacore / freeze window / 10 business days / peak)
- PASS both options are visible with their cost (18,400 and 6,200)
- PASS does not quote the superseded ~EUR 9k figure for option B
- PASS names the Nov 30 read-only archive date
- PASS says the old WMS / archive covers pre-2019 lookups in the meantime
- PASS says option A would land inside the peak-season freeze (Oct 19 / Oct 12)
- FAIL ends with a concrete, checkable next step (who does what, by when)
- FAIL phone-length (475 prose words <= 340)

## Files the agent left behind

- `output/email_to_rosa.txt`

## Turns

Every assistant turn, every tool call with its full arguments, and every tool result.
Tool output is recorded as the harness stored it, cut off at 6000 characters per call;
the agent itself saw the full text.

### Turn 1: assistant  (7.9s into the session)

I'll help you draft that update email. Let me first check what's in the folder to understand the context.

**calls `bash`**

```bash
find . -type f -name "*.txt" -o -name "*.md" -o -name "*.json" | head -20
```

**`bash` returned**

```
exit_code: 0
stdout:
./call_notes_halden_2026-09-10.md
./slack_export_halden-migration.txt


```

### Turn 2: assistant  (13.3s into the session)

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

### Turn 3: assistant  (19.4s into the session)

Now I'll draft a top-down update email for Rosa. Key points:
- Dry run 2 completed, found data quality issues in pre-2019 records (13% failure rate)
- Two options: delay go-live to Oct 19 (€18.4k) or go live Oct 5 with recent data, archive follows by Nov 30 (€6.2k)
- Decision needed by Friday Sep 18 to hold the Oct 5 cutover window
- This is about her Oct 1 board update and Oct 12 peak season constraint

Let me structure this top-down: governing thought first (decision required), action titles, clear complication, falsifiable next step.

**calls `bash`**

```bash
mkdir -p output
```

**`bash` returned**

```
exit_code: 0

```

### Turn 4: assistant  (63.0s into the session)

**calls `write_file`**

path: `output/email_to_rosa.txt`

```
SUBJECT: Migration dry run 2 — decision required by Friday 18 Sep

Rosa,

Dry run 2 is complete. We need you to choose between two options by end of day Friday 18 Sep to hold the Oct 5 go-live window. If we miss that deadline, the Oct 5 cutover slot with Stratacore is lost and go-live moves into your peak season.

Recommendation: Option B. Go live Oct 5 as planned, archive follows after peak.


AT A GLANCE

Decision by:     Fri 18 Sep, EOD
Go-live (B):     Mon 5 Oct (1 week before peak)
Go-live (A):     Mon 19 Oct (inside peak season)
Signoff:         Mira Castellanos (IT Director, per SOW section 7.2)


01. THE PROBLEM: 13% OF HISTORICAL RECORDS FAIL VALIDATION

Dry run 2 processed 2.4 million shipment records from the legacy WMS. 312,000 records (13%) failed validation. The cause: Halden's legacy system stored ship dates in mixed dd/mm and mm/dd formats until Jan 2019. Everything from Jan 2019 onward is clean (2.09M records, 0.008% failure rate).

This is a data quality inheritance from the old system, not new damage.


02. OPTION A: CLEANSE EVERYTHING BEFORE CUTOVER — €18,400, GO-LIVE 19 OCT

Cleanse all 2.4M records before cutover. Adds 9 working days. Go-live moves from Mon 5 Oct to Mon 19 Oct, which is one week into peak season (your hard constraint from the 10 Sep call).

Change request: EUR 18,400.


03. OPTION B (RECOMMENDED): GO LIVE 5 OCT, ARCHIVE AFTER PEAK — €6,200

Go live Mon 5 Oct with records from Jan 2019 onward (2.09M records, all validated). Pre-2019 archive gets cleansed and loaded read-only by Mon 30 Nov, after peak.

Warehouse floor operations only touch the last 2–3 years day to day. Pre-2019 records are an audit shelf. During the gap (Oct 5 to Nov 30), audit lookups for pre-2019 shipments use the old WMS, which stays up read-only until Dec 31 per the SOW.

Change request: EUR 6,200.


04. WHY FRIDAY 18 SEP IS THE HARD STOP

Stratacore requires cutover freeze windows booked 10 business days before go-live. We need one day on our side to file the booking. That makes Fri 18 Sep EOD the latest we can decide and still hold the Oct 5 slot.

If we miss Friday, Oct 5 is gone and we are in Option A whether we choose it or not.


05. WHAT HAPPENS NEXT

Mira Castellanos signs the change request (digital signature, 5 minutes). We file the cutover booking with Stratacore on Mon 21 Sep. You have a clean story for the board on Oct 1: go-live confirmed for Oct 5, one week before peak starts.

If the validation on the archive pass fails in November, the delivery date slips or we re-scope, but it does not touch the warehouse floor or peak season.


Rotterdam training still on track for 29 Sep. Next call Thu 17 Sep unless you are at Gothenburg.

Aylin

```

**`write_file` returned**

```
wrote 2706 chars to /home/user/work/output/email_to_rosa.txt
```

### Turn 5: assistant  (73.3s into the session)

Done. I've drafted the update email and saved it to `output/email_to_rosa.txt`.

**What I structured:**

- **Governing thought first**: Decision required by Friday to hold the Oct 5 window
- **Clear recommendation upfront**: Option B 
- **At-a-glance strip**: Key dates and approver in scannable format (mobile-friendly)
- **Action titles**: Each section heading states its conclusion
- **Arithmetic complication**: 13% failure rate, all pre-2019, vs. 0.008% post-2019
- **Two options with costs and dates** clearly separated
- **Falsifiable next step**: If archive validation fails in Nov, it slips or gets re-scoped but doesn't touch peak

The email respects Rosa's constraints from the call notes (peak season Oct 12, no surprises, reads on phone) and gives her what she needs for the Oct 1 board update. It's structured for mobile reading with short sections and a scannable strip at the top.

_stop reason: `end_turn`_

## Final message to the user

```
Done. I've drafted the update email and saved it to `output/email_to_rosa.txt`.

**What I structured:**

- **Governing thought first**: Decision required by Friday to hold the Oct 5 window
- **Clear recommendation upfront**: Option B 
- **At-a-glance strip**: Key dates and approver in scannable format (mobile-friendly)
- **Action titles**: Each section heading states its conclusion
- **Arithmetic complication**: 13% failure rate, all pre-2019, vs. 0.008% post-2019
- **Two options with costs and dates** clearly separated
- **Falsifiable next step**: If archive validation fails in Nov, it slips or gets re-scoped but doesn't touch peak

The email respects Rosa's constraints from the call notes (peak season Oct 12, no surprises, reads on phone) and gives her what she needs for the Oct 1 board update. It's structured for mobile reading with short sections and a scannable strip at the top.
```
