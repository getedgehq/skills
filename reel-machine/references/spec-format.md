# Reel spec format

One JSON file per reel. `mkreel.py SPEC.json` turns it into a bundle.

| key | required | meaning |
|---|---|---|
| `name` | yes | bundle and output name: `$REEL_WORK/bundles/<name>/`, `reel_<name>.mp4` |
| `clip` | yes | path to the source clip, or its stem in `$REEL_WORK/clips/` |
| `transcript` | no | Scribe JSON; default `$REEL_WORK/transcripts/<clip stem>.json` |
| `segments` | yes | kept parts in source seconds, in play order: `[start, end]`, or `[start, end, "other"]` for a part of another clip named in `clips` |
| `clips` | no | `{"other": "path or stem"}` extra sources for multi-clip reels (normalised to 1080x1920) |
| `hook` | yes | 2 lines split by `\n`, sentence case |
| `inline` | no | `{"Word": "icon.png"}`: icon drawn right after that word in the hook (logo or flag) |
| `strip` | no | a logo strip image under the hook |
| `cards` | no | list of `{"image", "at": [start, end], "w": 600, "y": 360, "pos": "top", "bare": true}`; `at` in source seconds of the main clip, inside a kept segment |
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
frame 0 for previews), `CAP_BOTTOM` (caption baseline from the bottom, 330 px),
`VIDEO_INSERTS` (full-frame b-roll cutaways), `CORNER_LOGO` (small persistent logo).
