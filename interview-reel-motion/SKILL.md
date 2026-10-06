---
name: interview-reel-motion
description: "Layer motion graphics on an already-cut 9:16 interview or talking-head short in the Compound editor: a cover frame for the feed grid, phrase captions, stickers, lower thirds, stat counters, typed prompts, a one-off particle takeover, eased camera pushes, an interpolated speed ramp and a clean end hold, all driven by a beat map (beats.json), then gate the render with face-zone, safe-zone, readability, flash and caption checks. Use when the cut and the voice are locked and the job is the graphic layer in Compound. Not for cutting raw footage into a short (use vlog-edit), generating video from nothing, or standalone motion graphics without a speaker."
---

# interview-reel-motion

Make an interview short read clearly with one graphic message at a time, never over a face, and never in the
platform UI. You write a beat map; the template renders it; the QA scripts prove it.

The template is a Compound project (`template/`): `src/engine` turns three JSON files into the scene,
`src/kit` holds the components, `scripts/` holds the QA gates, `tools/ramp.py` builds speed ramps.

## When to use

- The short is already cut (clip in and out points, voice) and needs its graphic layer, cover and ending.
- The editor is Compound (MCP at `127.0.0.1:3284`). The QA scripts work on any MP4.

Not for: cutting phone footage into a short (vlog-edit does the cut and its own cards), narrated product films,
or a motion graphic with no speaker.

## Workflow

1. **Copy the template** into the workspace's `projects/<name>/`, then `npm i three@0.170.0 --omit=dev` there.
   Put the footage under `assets/`. Register the folder with the MCP `open` tool (once per MCP session) and run
   `check`.
2. **Write `reel.json`** from the locked cut (references/beat-map.md): clips with source in-points and rate, the
   cover clip (the guest's best expression, held) and the end hold clip (a natural frame after the last line),
   framings, framing keys, voice, music, SFX on graphic pops only.
3. **Transcribe** the cut (`media_transcribe`) and write `captions.json`: whole phrases of 2 to 5 words, one
   speaker each, never splitting an idiom or a title.
4. **Write the beat map** as a table first (time, line, component, the one sentence a first-time viewer should
   get), then `beats.json`. Cut every beat whose meaning you cannot write in one sentence. Drop the caption where a
   graphic carries the same words. Label every number.
5. **Audit before rendering:** `python3 scripts/readability.py beats.json captions.json` until 0 failures.
6. **Look:** `capture` at every beat's complete moment and at frame 0. Fix placement against the safe zones.
7. **Render three passes** (`src/engine/qa.ts`: `"foot"`, `"gfx"`, then `""`), trim by frame count, and run the
   gates in references/qa.md. Place captions with the face boxes from `facezone.py` (below faces, centre at most
   1455; else above, centre at least 265), re-render, re-run.
8. **Hand over** the final MP4 with `frame0.jpg`, `frame0_grid.jpg` and the last-2s strip, and the gate numbers.

## Hard rules (defaults in `src/engine/rules.ts`)

- Frame 0 is the cover: everything important inside the 3:4 grid crop (y 260 to 1660 of 1080x1920), the hook
  readable at about 340 px wide, the logo inside the crop, a soft scrim, one message.
- Playback safe zones: no graphic in the top 220, bottom 420 or right 150 px.
- Zero graphic pixels in the face zone (brow - 65 to chin + 65, sides 65 px) on every frame, except the one
  declared full-frame takeover and the final fade.
- One graphic message at a time; no graphic competes with a caption (a sticker echoing the caption's key word is
  the exception, marked `echo`).
- Captions: 2 to 5 word phrases, never across speakers or idioms, up until the phrase ends plus 0.2 s.
- Every text element is complete for at least max(0.7 s, 0.25 s per word), or it is dropped.
- Morphs and pushes wait until the text on screen is complete.
- Every exit is eased over 6 to 8 frames; nothing vanishes in one frame. No flashes. No snap and freeze.
- Speed ramps use interpolated frames (`tools/ramp.py`), one continuous sine-eased ramp; cover the voice pause
  with room tone or a whoosh and keep the speech in sync afterwards.
- Type never moves (it resolves in place); objects travel. No count-ups: figures land final. Never invent a
  number; use only stated figures.
- Monochrome #09090B, #FAFAFC, #A0A0A5 and white stickers; brand colour only inside an official logo asset.
  No em or en dashes on screen.
- The end: hold a natural frame with a slow eased push, then a 10 to 15 frame fade. Trim the editor's outro by
  frame count, then check the last 2 s.

## QA gates

| Gate | Script | Pass |
|---|---|---|
| Readability | `scripts/readability.py` | 0 failures |
| Face zone | `scripts/facezone.py` (foot + gfx renders) | 0 px outside declared spans |
| Safe zones | `scripts/safezones.py` (gfx render) | 0 hits outside declared spans |
| Cover | `scripts/grid_preview.py` | hook reads at 360 px, logo in crop |
| Flashes | `scripts/lumaspikes.py` | no non-cut flash, snap or pop |
| Captions | `scripts/whisper_diff.py` | every line heard while up |
| Reference | `scripts/refgrid.py` | same-timestamp pairs match intent (PSNR for rebuilds) |
| Ending | `scripts/trim.py`, `scripts/last2s.py` | exact frame count, clean held end, no outro |

Never report a gate you did not run.

## Compound specifics

MCP at `http://127.0.0.1:3284/mcp`; call `open` with the project folder every session; projects live under the
workspace `projects/` directory; footage pieces are WebGPU WGSL shader passes limited to 5 keys (11 of the 12
uniform buffers); `<html>` cannot hold `<img>`, so logos are native `<image>` nodes; trim the export's outro frame
by frame count. Details in references/compound.md.

## References

- references/beat-map.md: beats.json, captions.json and reel.json schemas with examples.
- references/components.md: every component and its props.
- references/qa.md: the three renders and each gate.
- references/compound.md: MCP, registration, WebGPU, html layers, fades, the outro.
- template/examples/starter: a complete small reel to copy.
