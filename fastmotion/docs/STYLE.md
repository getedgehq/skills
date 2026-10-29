# Style guide: motion, pacing, styling

These rules were measured from a 105 s, 33-beat launch film built with this engine and are
encoded in `template/src/engine`. Use the engine helpers and they come for free; this page explains
the numbers so you can deviate on purpose.

## Pacing

| Rule | Value | Where |
|---|---|---|
| Beat length | median **2.7 s**, mean 3.2 s (33 beats / 105 s) | `timeline.ts` |
| Transit beats (track, whip, flag) | **0.8–1.5 s**, between every "act" | a whip or a short full-frame motif |
| Longest beats | 5–7 s, only for chat / story beats that need reading time | chat beats |
| Beat overlap | **0.3 s**, so exits and entrances crossfade | `OVERLAP` in `engine/timeline.tsx` |
| Things on screen at once | one idea per beat: title + 1 visual, or a chat thread | — |
| Reading time | a line must be fully typed ≥ 0.6 s before the beat leaves | — |

Structure that works: **hook (live-action) → product promise → what it learns → what it does
(chat + artefacts) → results → loop back to the hook.** Insert a ~1 s transit beat between acts.

## Motion

| Primitive | Setting | Use for |
|---|---|---|
| `pop()` spring | damping 16, stiffness 140, mass 0.9 (slight overshoot) | every element appearing: cards, pills, bubbles |
| `glide()` | bezier(0.16, 1, 0.3, 1), ~0.9 s | settles, layout moves, fades in |
| `Camera` ease | bezier(0.65, 0, 0.35, 1) | push-ins, pull-backs, pans between keyframes |
| Motion blur | automatic from camera speed (≈ 180° shutter), max 40 px | whips, push-ins, carousels |
| Whip transition | 0.3 s, ease-in cubic, 60 px directional blur | cuts between acts |
| Stagger | 0.08–0.15 s between siblings | card rows, stat bars, fans |
| Typing | **34 cps** default, 60–66 cps for long one-liners | `Bubble`, `typed()` |
| Depth of field | blur = distance × 9 px | background cards behind a hero card |
| Idle life | something always moves: slow camera drift, dust, counters | — |

Camera language: push in while text types, pull back when a reply arrives, tilt slightly
(rotateY 6–10°) so flat UI reads as 3D. Never hold a perfectly static frame more than ~1 s.

## Styling

| Token | Value |
|---|---|
| Background | warm grey `#ECEBE8` → `#F3F2EF` radial, plus 7 % film grain |
| Glow | soft radial orange `rgba(255,128,48,0.42)` behind the subject, optional blue at left |
| Accent | orange `#FF6A1A` (key words in copy: `**word**`), green `#1AA56B` for positive deltas |
| Ink | `#1C1B1A`, secondary `#4A4845`, muted `#9A9792` |
| Type | Inter; titles 44–70 px semibold, tracking −0.025em; chat 30–54 px medium |
| Cards | radius 18–26, fill `rgba(250,249,247,0.92)`, long soft warm shadow (`shadow`, `shadowLg`) |
| Bubbles | glassy white gradient, inset highlight, open at final width; user replies are solid orange pills |
| Media | 9:16 tiles, radius 18–22, photographic; placeholders keep the same tonal weight |

Change tokens in `src/engine/theme.ts` of your project to re-skin everything at once.

## Checklist for a new beat

1. Does it say one thing? Can it be read in its duration?
2. Does the camera move (push, drift or tilt)?
3. Do elements enter with `pop` / stagger rather than appear?
4. Is the key word orange?
5. Does it hand off with a transition or a shared element into the next beat?
