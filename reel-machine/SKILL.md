---
name: reel-machine
description: "Turn raw phone clips into scheduled vertical reels with no editor in the loop: iCloud Photos clips, word-level transcription (ElevenLabs Scribe), segment picking, a drift-free precut, hook text with a logo or flag on frame 0, bare stat cards, captions and a handle closer, a lip-sync check, written sensitivity rules, a second-model caption review, then Instagram Reels, TikTok and YouTube Shorts through Buffer. Use when someone wants their selfie or talking clips turned into finished, posted shorts, or wants a daily reel cadence run by an agent."
---

# reel-machine

Raw clips in, scheduled reels out. You make the editorial calls (which moment, which words,
which hook); the scripts do the cutting, drawing, rendering, checking and scheduling. A reel
is one JSON spec, so every render is reproducible and a fix is a one-line change.

**Done means:** the render exists, `avsync.py` passed, the sensitivity pass and the second-model
caption review both cleared, the owner approved anything on the show-first list, and the three
posts exist in Buffer (drafts until the owner arms them).

## Setup (once per machine)

Needs `ffmpeg`, `ffprobe` and Python 3. Any machine with those renders; no GPU.

```bash
bash scripts/setup.sh        # Python deps, Funnel Display hook font (SIL OFL), work dirs, config file
```
Then edit `~/.config/reel-machine/config.env` (template: `config.example.env`): your handle,
language, Buffer channels, where rendered files get hosted. Secrets stay in the environment:
`ELEVENLABS_API_KEY` for transcription, `BUFFER_TOKEN` for scheduling. Inject them from your
secrets manager for the one command that needs them; never write them to the config file.

For iCloud Photos as the clip source, install the `icloud-photos-bridge` skill and run its
setup. `selfie-picker` and `broll-picker` find the moments worth cutting; this skill starts
once you have clip UUIDs.

## The pipeline

### 1. Get clips
```bash
$PY $B/catalog.py --out catalog.jsonl --since <date> --kind video   # icloud-photos-bridge
bash scripts/fetch_clips.sh <UUID> [<UUID> ...]                       # -> $REEL_WORK/clips/
```
Clips from anywhere else: drop the files in `$REEL_WORK/clips/`.

### 2. Transcribe
```bash
python3 scripts/transcribe.py $REEL_WORK/clips/<clip>.mov     # or --watch to follow the folder
python3 scripts/words.py <clip>                                # sentences with times
python3 scripts/words.py <clip> 12-30                          # every word with start-end
```

### 3. Pick the segment(s)
Read the whole transcript before choosing. Rules, in order:
- **Story gate:** would a stranger send this to a friend? Utility, surprise, identity,
  aspiration or a strong opinion. A diary line ("wrote some code today") fails.
- **Strongest line first.** The first spoken words are a claim, a number or a stakes question.
  No greeting, no "so today". Move the best line to the front if it stands alone.
- **Cut filler, false starts and repetitions** at word boundaries from `words.py`. Keep a pause
  only when it carries personality. Length follows the payoff (most land at 15 to 60 s).
- Then run step 6's text pre-screen on the kept words before you invest in a render.

### 4. Write the spec
One JSON per reel, format in `references/spec-format.md`:
```json
{"name": "second-opinion", "clip": "<clip stem>",
 "segments": [[0.26, 4.74], [5.16, 9.08], [10.28, 11.4]],
 "hook": "I made Claude ask ChatGPT\nfor a second opinion",
 "inline": {"Claude": "sig/claude.png", "ChatGPT": "sig/openai.png"},
 "cards": [{"image": "sig/card_5m.png", "at": [7.6, 8.62], "w": 520, "y": 380}],
 "cap_fix": {"like, ": ""}}
```
The look (hook, signal, cards, captions, closer) is in `references/look.md`. Build the pieces:
```bash
python3 scripts/logo_png.py claude "#D97757" sig/claude.png     # brand mark (Simple Icons)
python3 scripts/emoji_png.py 🇺🇸 sig/us.png                       # flag as the place signal
python3 scripts/statcard.py sig/card_5m.png '$5M' 'raised'       # bare stat card
```

### 5. Bundle, curate captions, render
```bash
python3 scripts/mkreel.py spec.json              # bundle + drafted captions printed with times
# edit $REEL_WORK/bundles/<name>/caps.json if needed, then:
python3 scripts/make_caps.py check $REEL_WORK/bundles/<name>/caps.json
bash $REEL_WORK/bundles/<name>/job.sh            # render here, or:
bash scripts/remote_render.sh $REEL_WORK/bundles/<name>    # on REEL_REMOTE over ssh
```
`mkreel.py spec.json --render` does bundle + local render in one go. The precut seeks each
segment as its own input and concatenates audio and video together, so long multi-cut reels do
not drift. The render: optional grade, wind high-pass, -14 LUFS, 1.1x, hook for the first
seconds, cards at their spoken words, captions, closer on the last ~0.9 s plus a 0.6 s hold,
H.264 high profile, faststart.

### 6. Check before anyone sees it
1. **Lip sync:** `python3 scripts/avsync.py <source clip> <render>`. Only rows with frame
   similarity >= 0.85 count; PASS means the offset does not grow across the reel. A FAIL is
   a render bug: fix it, never ship it.
2. **Sensitivity:** `python3 scripts/sensitivity_scan.py <transcript> <caps.json> --text "<hook>" --text "<post caption>" --posted <date>`,
   then apply `references/sensitivity-rules.md` yourself, including the frame pass. Every
   flag gets a decision: cut, keep with a reason, or show the owner.
3. **Second-model caption review:** `python3 scripts/caption_review.py $REEL_WORK/bundles/<name> --hook "..." --post "..."`.
   With `REEL_REVIEW_CMD` set it asks another model (Codex, Claude, any CLI that reads stdin);
   apply its fixes, re-render if captions changed, and loop in the same session until it answers AGREED.
4. **Look at it:** one frame per second (`references/sensitivity-rules.md`, frame pass) plus
   the first frame, which is the thumbnail.

### 7. Schedule
```bash
python3 scripts/schedule_reel.py channels
python3 scripts/schedule_reel.py schedule --file renders/reel_<name>.mp4 \
    --at 2026-11-02T12:00:00-08:00 --caption "..." --title "YouTube title"          # drafts
# after the owner approves the exact file + caption: same command with --armed
python3 scripts/schedule_reel.py swap --caption-start "first words" --file renders/reel_<name>_v2.mp4 --title "..."
```
Buffer fetches media from a public https URL at publish time (no upload API), so the file must
stay hosted with byte-range support until the post fires. Instagram needs
`metadata.instagram = {type: "reel", shouldShareToFeed: true}`; YouTube needs a title and a
`categoryId`; the script sets both. Never two similar topics back to back; mix street, people,
work and product.

## Rules

- Drafts by default. Arm a post only after the owner approved that exact file and caption.
- Anyone clearly identifiable on camera needs consent. The owner's standing-consent list is the
  only exception.
- Never invent words in captions. The transcript is ground truth; fix only recognition errors.
- A failed check is a stop, not a note. Fix, re-render, re-check.
- Keep media private until it is scheduled: host renders at an unlisted URL.

## Files

- `scripts/`: `setup.sh`, `fetch_clips.sh`, `transcribe.py`, `words.py`, `mkreel.py`,
  `precut.py`, `build_reel.py`, `make_caps.py`, `fit_hook.py`, `hook_png.py`, `statcard.py`,
  `closer_png.py`, `logo_png.py`, `emoji_png.py`, `remote_render.sh`, `avsync.py`,
  `sensitivity_scan.py`, `caption_review.py`, `schedule_reel.py`, `rmconf.py` (config loader).
- `references/spec-format.md`, `references/look.md`, `references/sensitivity-rules.md`.
- `config.example.env`. No EVALS.md ships yet, so no measured benefit over an agent without
  the skill is claimed.
