# Did this Skill actually help?

We built a Skill, then measured it against not having it. Same model, same tasks, same
grader, same sandbox. The only thing that changes between the two arms is whether the Skill
is loaded.

**Eighteen paired runs across three tasks. With the Skill, 80.4 out of 100. Without it, 45.3.
Fourteen wins, four ties, zero losses. The hard check passed 17 of 18 times with the Skill
and 2 of 18 without it.**

The Skill arm was also cheaper and faster: $0.168 against $0.238 per attempt, 18.6 turns
against 27.4. That is unusual and it has a plain explanation, which is in
[why it is faster](#why-the-skill-arm-is-cheaper-and-faster).

Run date: 2026-09-17, run `t3-v2`. This is one run. It has not been repeated.

## Everything is published

Every number here can be checked against the thing it came from: all 36 session logs turn by
turn, every file the agents wrote, all 36 grader verdicts with their reasoning, the three
task definitions, and the scripts that graded them. They are in
[`evals/strip-image-ai-metadata/2026-09-17/`](../evals/strip-image-ai-metadata/2026-09-17/).

Nothing is summarised there. If a summary here disagrees with an artifact there, the
artifact is right.

## The numbers

| | With the Skill | Without it |
| --- | --- | --- |
| Rubric score (0-100) | **80.4** | 45.3 |
| Paired comparisons won | 14 of 18 (4 ties, 0 losses) | 0 of 18 |
| Hard checks fully passed | 17 of 18 (94.4%) | 2 of 18 (11.1%) |
| Hard-check score | 0.94 | 0.52 |
| Turns per attempt | 18.6 | 27.4 |
| Model cost per attempt | $0.17 | $0.24 |
| Sessions that ran out of turns | 0 of 18 | 7 of 18 |

The gap is **+35.1 points**, with a 95% confidence interval of **[+13.8, +58.6]**.

That interval excludes zero, so on these three tasks the effect is real. The interval is
wide, which is what eighteen pairs buys you. It does not say the effect is 35 points. It says
the effect is somewhere between about 14 and about 59 points, and the direction is not in
doubt.

## Four things to know before you trust any of this

1. **The grader was a small model.** Claude Haiku 4.5, not a frontier model.
2. **Only the `loaded` arm was run.** The Skill text was placed in the prompt. This measures
   the Skill's content, not whether an agent finds it on its own. The realistic number for
   "I installed this and forgot about it" is not on this page.
3. **We wrote the tasks and we published the Skill.** This is not an independent benchmark.
4. **The grader disagreed with itself on 4 of the 18 pairs** when the two deliverables were
   swapped. Those four are counted, not discarded.

Everything else that weakens this is in [the limits](#the-limits).

## What the grader did and did not see

The grader never saw the hard-check result. For each side, with no label saying which side is
which, it saw the agent's final reply, the files the agent created or changed, the names of any
binary files, anything it deleted, whether the run ended normally or was cut off by the turn
cap, and a one line per call log of the agent's first eighty tool calls. It scored the two
sides against the task's own rubric, in both presentation orders. Running both orders is how
the four disagreements above became visible rather than invisible.

One detail of that tool call log matters for blinding: any call whose arguments mention the
skills directory is stripped out before the grader sees it. Without that, a side would be
identifiable from the single fact that it opened a skill, and the comparison would not be
blind at all.

The hard check is a separate script that runs outside the sandbox and opens the actual image
files: decoded pixels, ICC profile bytes, EXIF orientation, the presence or absence of each
AI marker. It does not read what the agent wrote about its work.

So the two headline numbers are independent measurements of the same deliverable, and they
agree.

## The three tasks

Three tasks, six attempts each with the Skill and six without. That is 36 sessions, 18 pairs,
36 verdicts.

Every task has the same shape: a folder of real image files, plus a message from someone with
a practical problem and a hard constraint they care about more than the problem. The agent
gets a fresh sandbox with a real filesystem and a shell.

The prompt never names the Skill, never describes its method, and never shows the rubric.

| Task | Kind | With the Skill | Without it | Difference | Pairs won | Hard check |
| --- | --- | --- | --- | --- | --- | --- |
| [Thursday's LinkedIn batch](../evals/strip-image-ai-metadata/2026-09-17/tasks/post-batch-lossless/) | direct | 74.7 | 50.0 | **+24.7** | 4 of 6 (2 ties) | 1.00 vs 0.49 |
| [Sleeve proofs going to the printer](../evals/strip-image-ai-metadata/2026-09-17/tasks/print-proofs-colour-critical/) | transfer | 84.7 | 26.9 | **+57.8** | 6 of 6 | 0.93 vs 0.62 |
| [Marketplace relist, second pass](../evals/strip-image-ai-metadata/2026-09-17/tasks/relist-second-pass/) | transfer | 66.5 | 35.0 | **+31.5** | 4 of 6 (2 ties) | 0.88 vs 0.43 |

"Direct" means the task is the situation `SKILL.md` describes. "Transfer" means a different
situation the same method should still cover. Both transfer tasks beat the direct one, which
is the opposite of the usual worry about a skill that only works on its own example.

There were zero losses across all 18 pairs.

### Task 1: Thursday's LinkedIn batch (direct)

**What the agent was asked**, in full:

> linkedin sticks that content-credentials thing on about half my posts now and it's killing
> the reach. thursday's batch is in queue/ - four images, a couple came out of an image
> generator, the rest are mine. can you pull out whatever it is that trips the label? don't
> re-export or recompress them, and they have to open looking exactly like what's in queue/
> right now, i'm not re-shooting any of this. leave queue/ alone, cleaned ones into output/.
> also tell me which ones were actually carrying it, i genuinely can't tell by looking

**The trap.** The obvious move is `convert -strip` or `exiftool -all=`. Both work, in the
sense that the AI markers disappear. Both also wipe EXIF Orientation, so the portrait is
delivered lying on its side, and both drop the ICC profile and the copyright record. The
request says "they have to open looking exactly like what's in queue/", and a sideways
headshot does not.

The second trap is scope. One of the four carries Midjourney `tEXt` records rather than
C2PA. An agent that looks only for C2PA reports that file as clean.

**Rubric**, verbatim, with weights:

| Weight | Criterion |
| --- | --- |
| 3 | Every AI record is gone from the delivered files |
| 3 | Nothing else in the files was thrown away |
| 3 | The portrait still displays upright and was not recompressed |
| 2 | The real photo is recognised and left alone |
| 2 | Originals untouched, deliverables where asked |
| 2 | Per-file answer and a real verification |
| 1 | Honest about scope |

### Task 2: sleeve proofs going to the printer (transfer)

**What the agent was asked**, in full:

> proofs for the nordvind sleeve are in proofs/ - this goes over to kasten druck on monday.
> their preflight bounces anything that reads as ai-generated in the file info, and it also
> bounces files that come in with no rights or credit info, so both of those have to be true
> when i hand it over. colour has to match the proof exactly so nothing gets re-saved or
> re-compressed. overwrite them in proofs/ directly, that's the folder i'm zipping up. and
> i'd rather you tell me it's clean because you went and looked than because a tool said so

**The trap.** The two rejection reasons pull in opposite directions. Remove too little and
the AI provenance ships. Remove too much and the rights and credit records go with it, which
is the printer's other rejection reason. A blanket wipe fails the task by satisfying half of
it. The ICC profile is a third casualty, and colour is explicitly the thing that has to
match.

There is also a `.xmp` sidecar in the folder. An agent that processes only image files never
opens it, and the Firefly provenance ships inside the zip.

This is the task with the largest gap, +57.8 points, and the base arm's 26.9 is the lowest
score any arm recorded anywhere in the run.

**Rubric**, verbatim, with weights:

| Weight | Criterion |
| --- | --- |
| 3 | All three generated proofs come out clean |
| 3 | Colour is not touched |
| 3 | Rights and credit survive |
| 2 | The sidecar is not missed |
| 2 | The real photograph is left alone |
| 2 | Verified by looking, and reported per file |

### Task 3: marketplace relist, second pass (transfer)

**What the agent was asked**, in full:

> marketplace bounced the relist again, says the photos are 'flagged as ai generated' in the
> file info. folder is relist/, they're copies so just overwrite in place. the guy i paid
> before you already ran something over them and it still came back rejected, so please
> actually confirm it's gone instead of telling me the tool said ok. don't change how they
> look, and the shop credit line in there has to stay, that's the only thing proving the
> photos are mine

**The trap.** Someone already ran a stripper over these files, and it worked on the parts a
stripper reaches. What survived on `mug_front.jpg` is a C2PA manifest sitting after the JPEG
end-of-image marker. `exiftool -all=` does not touch it, because it is not a tag. The only
way to find it is to re-read the written file and look for generator signatures in the raw
bytes, which is a step of the Skill's workflow rather than an afterthought.

An agent that trusts its own tool's exit code declares the folder clean and the listing gets
rejected a third time. This is the lowest-scoring task in the Skill arm, 66.5, because the
trailer is genuinely hard to find.

**Rubric**, verbatim, with weights:

| Weight | Criterion |
| --- | --- |
| 3 | The leftover the first pass missed is found |
| 3 | The other two are cleaned properly |
| 3 | The shop credit and the look survive |
| 2 | The real photo is not collateral |
| 2 | Confirmation is independent |
| 1 | In place, and explained |

## Why the Skill arm is cheaper and faster

Most skills cost turns. This one saves them, and the reason is visible in the transcripts.

Without the Skill the agent explores. It tries `exiftool`, reads the output, notices the ICC
profile is gone, tries to put it back, re-checks, tries a different tool. Seven of the 18 base
sessions ran out of turns mid-repair. With the Skill it runs the bundled script, reads the
warning the script prints, and stops.

The saving is a consequence of knowing which bytes to remove. It is not a general claim that
skills make agents cheaper.

## The limits

- **One run, one date.** Not repeated.
- **One agent model, one grader model.** Claude Sonnet 4.5 doing the work, Claude Haiku 4.5
  grading it. Results may not transfer to another agent.
- **`loaded` only.** See point 2 near the top. The gap between "the Skill is in the prompt"
  and "the Skill is installed and the agent has to reach for it" is not measured here, and on
  other skills in this programme that gap has been large.
- **Eighteen pairs.** The confidence interval is [+13.8, +58.6]. Effects smaller than roughly
  five points would not be detectable at this sample size.
- **Our tasks, our Skill.** Three tasks written by the people who wrote the Skill. The defence
  is not that we were impartial; it is that every task, deliverable, check result and grader
  verdict is published so you can disagree with a specific one.
- **Four grader self-disagreements.** On four pairs the grader picked a different winner when
  the two deliverables were swapped. They are in the 18 and in the confidence interval, not
  removed.
- **The base arm hit the turn cap 7 times out of 18.** Those seven sessions are truncated
  work, and a truncated answer scores badly. Some of the gap is the cap, not the Skill. The
  Skill arm hit it zero times, so this cuts against the Skill arm's advantage being purely
  about quality.
