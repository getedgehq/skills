# Reel spec format

One JSON file per reel. `mkreel.py SPEC.json` turns it into a bundle.

| key | required | meaning |
|---|---|---|
| `name` | yes | bundle and output name: `$REEL_WORK/bundles/<name>/`, `reel_<name>.mp4` |
| `clip` | single-clip form | path to the source clip, or its stem in `$REEL_WORK/clips/` |
| `clips` | multi-clip form | list of clips (paths or stems). Their transcripts are laid end to end; every time in the spec becomes `[clip_index, start, end]`. Mixed sources are normalised to 1080x1920. (Older form, still read: a `{"other": "path"}` map plus `[start, end, "other"]` segments, which get no drafted captions.) |
| `transcript` / `transcripts` | no | Scribe JSON (a list in the multi-clip form); default `$REEL_WORK/transcripts/<clip stem>.json` |
| `segments` | yes | kept parts in play order: `[start, end]` in source seconds, or `[clip_index, start, end]` with `clips` |
| `hook` | yes | 2 lines split by `\n`, sentence case |
| `inline` | no | `{"Word": "icon.png"}`: icon drawn right after that word in the hook (logo or flag) |
| `strip` | no | a logo strip image under the hook |
| `cards` | no | list of `{"image", "at": [start, end], "w": 600, "y": 360, "pos": "top", "bare": true}`; `at` inside a kept segment (`[clip_index, start, end]` with `clips`) |
| `cuts` | no | full-screen cutaways, hard cut in and out, captions drawn on top: `{"image", "at", "title", "subtitle", "credit"}`. With `title` the card is built from the photo by `cutaway.py`; without it `image` is used as a ready 1080x1920 card. `credit` lines go to `credits.txt` for the post caption |
| `ending` | no | default `true`: end on the last whole word, voice fades, footage runs on under the closer |
| `tail_max` | no | seconds of footage after the last word (default 1.15). Lower it when the face after the last word is awkward |
| `hook_dur` | no | edited seconds the hook stays (default: up to 10, before the closer) |
| `cta` | no | product reels: `{"text": "yourproduct.com", "logo": "path.png", "at_end": 1.5}` replaces the handle closer |
| `corner_logo` | no | small logo kept in the top corner for the whole reel |
| `cap_fix` | no | `{"find": "replace"}` applied to drafted captions (drop "like, ", fix a name) |
| `captions` | no | path to a curated caps.json; skips drafting |
| `closer` | no | default `true`: handle closer on the last ~0.9 s |

## caps.json

`[{"text": "I made Claude", "en": "", "start": 0.0, "end": 1.02}, ...]`, times on the cut
timeline (edited seconds, before speed-up). `en` is an optional smaller second-language line
under the caption. Validate with `make_caps.py check`.

## Bundle layout

```
bundles/<name>/
  job.sh            renders the bundle; runs anywhere with ffmpeg + python3 + Pillow
  main.mov          source (hard link when possible)   clips/   other sources
  transcript.json   segments.json   caps.json   inserts.json
  hook.png          closer.png      cards/       fonts/
  precut.py         build_reel.py
  out/reel_<name>.mp4   out/build.log
```

## Render knobs (environment of build_reel.py, set by job.sh)

`SPEED` (1.1), `GRADE` (ffmpeg filter, empty = ungraded), `HOOK_DUR` (edited seconds the hook
stays, capped so it clears the closer), `END_HOLD` (0.6 s freeze at the end), `CRF` (20),
`DEBREATH=1` (gate breaths + light denoise), `LEAD_FRAME=<s>` (use that composited frame as
frame 0 for previews), `CAP_BOTTOM` (caption block bottom, 495 px above the frame bottom = y~1425),
`VIDEO_INSERTS` (full-frame b-roll cutaways), `CORNER_LOGO` (small persistent logo),
`CAP_SIZE` (55 px), `AUD_END` + `AUD_FADE` (ending rule: voice fade after the last word).
Insert entries with `"hard": true` cut in and out with no fade (cutaways).

## After the render

`finish.sh <bundle>` runs `voiceclean.py`, `pcut.py`, `vadgaps.py` and `facecheck.py` and copies the
result to `$REEL_WORK/renders/reel_<name>.mp4`. Each tool also runs on its own.
