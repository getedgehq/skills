---
name: fastmotion
description: Make polished product-launch / explainer videos in code (Remotion, React) with a ready motion engine — camera moves with motion blur, spring pop-ins, typing chat bubbles, 3D carousels, card fans, stat bars, whip transitions, warm-grey + orange styling. Use when the user wants a launch video, product demo video, animated explainer, ad-style motion piece, or to rebuild/replicate an existing video in code, or mentions fastmotion. Also use to iterate an existing fastmotion project toward a reference cut you own.
license: Apache-2.0
---

# fastmotion

A Remotion engine where motion, pacing and styling are code. You scaffold a project, write a
list of **beats** using **blocks** and engine primitives, render, then iterate against stills
(or a reference video). Everything renders with placeholders until real media exists.

Skill folder layout (paths below are relative to this SKILL.md):
- `template/`: the Remotion project (engine in `template/src/engine`, a 27 s demo video built only from blocks)
- `bin/new-video.sh`: scaffolds a new project from the template
- `docs/STYLE.md`: **read before designing beats**: pacing, motion and styling rules with numbers
- `docs/NEW_VIDEO.md`: step-by-step for a new video, with code

## Workflow

1. **Scaffold**: `bash <skill>/bin/new-video.sh <project-dir>` (engine + Demo, runs `npm install`;
   `--no-install` skips it).
2. **Script**: write the story as beats before coding. Use the structure and timings in
   `docs/STYLE.md` (hook → promise → what it learns → what it does → results → callback; median
   beat ≈ 2.7 s; ~1 s transit beats between acts). Put all copy in one place.
3. **Build**: copy `src/videos/demo` → `src/videos/<name>`, edit the `beats` array, register a
   `<Composition>` in `src/Root.tsx`. Prefer blocks; write a bespoke scene component only when no
   block fits. Import everything from `src/engine` (barrel `index.ts`).
4. **Check**: `npx tsc -p .`, then render stills at several timestamps per beat and **look at them**:
   `npx remotion still <Comp> out/s.jpeg --frame=<sec*60> --scale=0.5`. Fix layout/timing, repeat.
5. **Render**: `npx remotion render <Comp> out/<name>.mp4` (1080p60; ~6k frames ≈ 15–25 min on 4 cores).
   Deliver the mp4 plus the project.

When **matching a reference cut you own**: extract contact sheets with ffmpeg (1 fps, timestamped)
to storyboard every beat; measure cut times (`ffmpeg -vf "select='gt(scene,0.1)',showinfo"`) into
your beats; then iterate per beat with side-by-side stills. Parallelise by giving each sub-agent
one scene file. Only rebuild videos you have the rights to; never copy another brand's names,
logos or characters.

## Engine cheat sheet (`src/engine`)

| Need | Use |
|---|---|
| Timeline of beats with transitions | `Timeline` + `Beat {id, from, to, enter?, exit?, shift?}`; `totalSec(beats)` |
| Transitions | `enter`/`exit`: `whipL` `whipR` `whipU` `whipD` `blur` `zoom` `fade` |
| Background | `<Stage>` (warm grey, orange glow, grain): wrap every scene in it |
| Appear / settle | `pop(frame, delaySec)` spring, `glide(frame, delay, dur)`, `range(frame, a, b, from, to)` |
| Typing / counting | `typed(frame, text, startSec, cps)`, `countUp(frame, from, to, start, dur)`, `<Bubble text start cps size>` |
| Copy emphasis | `**word**` → orange in `Bubble`, `Rich`, `TitleBeat`, `ChatThread` |
| Camera | `<Camera keys={[{t, x, y, z, rx, ry, rz}]}>`: motion blur from velocity is automatic |
| Blur / depth / particles | `<MotionBlur bx by>`, `<Depth z focus>`, `<Dust swirl>` |
| Chat | `<ChatThread messages={[{from:'agent'|'user', text, at}]} agentName camera dust>`, or `AgentRow` + `Bubble` + `UserBubble` |
| Media | `<Media w h src? hue seed variant='person'|'scene'|'product' caption>`: photo-like placeholder until `src` |
| Other UI | `Pill`, `Tag`, `Title`, `Phone`, `Cursor`, `AgentAvatar` (agent orb with initial), `Card` |
| Blocks | `TitleBeat`, `ChatThread`, `Carousel3D`, `CardFan`, `StatBars`, `CounterCard` |
| Re-skin | tokens in `src/engine/theme.ts` (`C`, `font`, `shadow`, `shadowLg`) |

Scene components receive `{dur}` (their mounted length in sec); all times inside a scene are
scene-local seconds. `FPS` lives in `src/engine/constants.ts` (60).

## Rules that make it look right

- Every element **enters** (pop/stagger 0.08–0.15 s), nothing just appears; something always moves.
- Camera: push in while text types, pull back when a reply lands, slight 6–10° tilt for depth.
- One idea per beat; a line is fully typed ≥ 0.6 s before the beat ends.
- Key word per line in orange; titles 44–70 px semibold, chat 30–54 px.
- Use engine transitions **or** in-scene fades, not both (doubling causes ghosting).

## Gotchas

- **Fonts**: never load Google Fonts at render time (sandboxes block it and renders time out).
  Bundle woff2 in `public/fonts` (e.g. from `@fontsource/*` on npm) and load via `staticFile`.
  Inter is assumed installed; otherwise bundle it the same way.
- **`backdrop-filter`** in headless Chrome copies edge pixels (ghost duplicates); blur a masked copy instead.
- **Sandboxes/CI**: set `REMOTION_BROWSER=/path/to/chrome-headless-shell` if Remotion can't download Chrome.
- Shell cleanup: quote variables in `rm` (`"${DIR:?}"/*`).
- Keep all art original: no third-party logos or recognisable characters; use placeholders for people.
