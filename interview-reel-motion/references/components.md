# Component reference

Every component is a pure function of the scene clock: scrubbing, capture and export land on the same pixels.
Type never moves: words resolve in place (Soften: blur and opacity to sharp, or a hard pop with the object they sit
on). Only objects travel: cards, pills, bars, ticks, particles, rings, the camera. No count-ups: figures land final.

Names in **bold** are beat components (`component` in beats.json). "own" components ease themselves out; the rest
are wrapped by the engine in an eased group (`exit`, `fadeIn` frames).

## Overlays (`src/kit/Overlays.tsx`, own exit)

| Component | Props | Use |
|---|---|---|
| **Cover** | `chip {logo, label}`, `lines [hook, second?]`, `x`, `y` (hook top, default 400), `size` 110, `size2` 88, `scrimTop`, `scrimHeight` | frame 0 thumbnail: soft scrim, brand chip, a 3 to 6 word hook from the guest's own words or stated figures; inside the 3:4 crop |
| **BrandChip** | `logo`, `label`, `x`, `y`, `variant` `"cover"` or `"card"` | any logo + label (event, company, programme). The logo is a native `<image>` over an html spacer |
| **LowerThird** | `name`, `role`, `x`, `y`, `chip {logo, label, x, y}` | who is speaking, once, after their first line |
| **Headline** | `lines[]`, `x`, `y`, `size` 128, `tracking`, `color` | one resolved statement (the one-sentence answer) |
| **CompareCards** | `title`, `sub`, `leftLabel`, `rightLabel`, `inAt`, `subAt`, `leftAt`, `rightAt`, `rightLabelAt` | "made for X, nothing for Y": a filled profile card vs an empty dashed twin |
| **BlockMeter** | `title`, `n` 7, `dark` 3, `leftLabel`, `rightLabel`, `gridAt`, `titleAt`, `darkAt`, `leftLabelAt`, `lightAt`, `rightLabelAt`, `sweep [t0, t1]` | bad days then good days, a marker sweeping through |
| **StickerStack** | `items [{t0, t1?, text or lines[], x, y, rot, size, center?}]`, `safeWidth` 930 | pop stickers that echo the key word of the line; `center` centres each in the safe width |
| **EndCard** | `title`, `x`, `y`, `size` 84 | the closing line in the top band |
| **Text** | `text`, `x`, `y`, `width`, `size` 44, `weight`, `color`, `tracking` | a native text line (attribution under the end card) |

## Kit (`src/kit/*`, engine-wrapped)

| Component | Key props | Use |
|---|---|---|
| **Sticker** (KineticWord.tsx) | `text`, `x`, `y`, `width`, `height`, `rot`, `size`, `fill`, `ink`, `shadow` | white pill pops with overshoot; the word Softens in per character (complete at `0.3 + 0.022 (n - 1)` s) |
| **KineticWord** | `words [{t0, t1, text}]`, `y`, `size`, `per`, `overFace` | one-word-at-a-time captions (prefer phrase captions) |
| **ChatPrompt** (BuildPanel.tsx) | `text`, `x`, `y`, `width`, `size`, `cps`, `placeholder` | a question typed into a prompt box; typing starts at +0.55 s |
| **BarChart**, **TileGrid** | see BuildPanel.tsx | bars build one by one; a grid fills in reading order; values land final |
| **CounterBar** | `value`, `unit`, `progress`, `goal`, `goalLabel`, `travel`, `x`, `y`, `width`, `k` (scale) | a stated figure; the bar crosses the goal tick, which flips grey to ink |
| **Plate** | `x`, `y`, `width`, `height`, `radius`, `fill` | dark plate behind a figure (use `fadeIn: 6`) |
| **Arrow** | `x`, `y`, `width` 170, `height` 90, `flip` | hand-drawn arrow at an object in frame (keep the tip outside the face box) |
| **Image** | `src`, `x`, `y`, `width`, `height`, `radius` | a logo or still |
| **Takeover** | `text`, `size`, `y`, `height`, `resolve`, `dissolve`, `ground` | the one full-frame moment per reel: ground + ParticleText. Put its span in `blank` and use `fadeIn: 6`, `exit: 6` |
| **ParticleText** | `text`, `y`, `height`, `size`, `form`, `resolve`, `dissolve`, `count` | points swarm onto the word's raster, then the word resolves (three.js) |
| **TypeRing** | `text`, `inner`, `y`, `tilt`, `roll`, `spin` | chrome type ring (three.js); only for a brand line that earns it |
| **OrbitCards** | `cards [{kind: video, phone, stat, image, ...}]`, `cx`, `cy`, `rx`, `rz`, `every` | proof cards orbiting above a head; only with real, stated proof |

## Footage

| Piece | Where | Use |
|---|---|---|
| Framer (`src/kit/Framer.tsx`) | generated from `reel.json` keys | every A-roll piece: eased pushes, full-frame to card morphs, card mask radius; at most 5 keys per piece |
| CameraPush (`src/kit/CameraPush.tsx`) | custom `index.tsx` | perspective push or tilt on a clip with a pinhole camera; up to 4 keys |
| `tools/ramp.py` | pre-render, then a clip with `src` | a speed ramp 1.0x to vmin to 1.0x made of interpolated frames |
