# Motion kit

`assets/motion/motion-kit.js` adds the moving layer to a one-stage film (see [the one-stage film](one-stage-film.md)): a depth field built from the user's own UI, a camera keyed to the story, rack focus, a flare and ring at each event point, an iris scene change from the click, kinetic type and odometers. It generalises the kits behind the Edge launch film v17 and the inbound-triage film v6 (numbers in [pace and digestibility](pace-and-digestibility.md) and `examples/README.md`): no brand, paths or copy inside. Brand colours come from the user's kit.

Use it after the story, copy and timing are approved and the flat film works. Motion is the last layer, not a fix for a weak story or for too many words.

## Wire it up

The kit is one script with no dependencies. It is a pure function of the master clock, so it works with a paused GSAP timeline, HyperFrames, or the bundled `renderAt(t)` renderer.

```html
<script src="motion-kit.js"></script>
<script>
  const tokens = /* the user's tokens.json */;
  const at = MotionKit.beat(128);              // beats to seconds on the film's grid
  const kit = MotionKit.create({
    stage: "#stage", accent: tokens.colors.blue, paper: tokens.colors.sky,
    images: { inbox: ["assets/ui-inbox.jpg", 688, 592], row: ["assets/ui-row.jpg", 860, 80] },
    fields: [{ kinds: ["inbox", "row"], n: 30, seed: 7, drift: 400, before: "#board", z: 1,
               window: [0, at(26)], veil: [[960, 540, 1050, 560, 0.85]],
               rush: [{ t: at(25), dur: 0.9, dist: 2400 }] }],
    camera: { targets: ["#board"], keys: [
      { t: 0, z: -500, ry: 8 }, { t: 0.6, e: "spring" }, { t: at(9.6) },
      { t: at(10.4), x: -60, z: 90, e: "expo", label: "push to the stamp" }, { t: at(12), x: -62, z: 94 } ] },
    rack: [{ t: at(17), sharp: "#chip", soft: ["#prompt"], blur: 5 }],
    flares: [{ t: at(10), at: "#badge" }, { t: at(19.5), at: "#send" }],
    irises: [{ t: at(26), dur: 0.4, from: "#send", incoming: ["#line"], outgoing: ["#board"] }],
    glyphs: [{ el: "#line .headline", t: at(26) + 0.05 }],
    odometers: [{ el: "#stat", text: "61%", t: at(28), dur: 0.9 }],
  });
  tl.eventCallback("onUpdate", () => kit.apply(tl.time()));
  kit.apply(0);
</script>
```

`kit.events()` returns every motion event as `{t, kind, label}` (fly-in, push, drift, dolly, rack, flare, iris, glyphs, odometer, odometer-land). Use it as the SFX table and as the event list of the beat plan, so sound, picture and the audit come from one cue table.

## The parts

**Depth field from the user's real UI.** Crop 4 to 10 pieces of the film's own screens (inbox rows, the result, the skill or product card) from a flat render of the film, and pass them as `images` with their pixel size. Cards sit in 3D around the frame centre, blur by distance from `focus`, haze with depth (`haze`), drift toward the lens (`drift`, larger is faster) and fade out before they reach the content plane, so no card crosses the text. Only crops of the user's own product: no stock, no other company's UI, no footage from a reference film. A `veil` (paper-coloured ellipses) keeps the text on calm ground. Show only what the story has already shown: a field behind the inbox holds inbox rows, not the result it has not reached yet.

**Camera keyed to story cues.** `camera.targets` is the content plane (one element, or the layers that morph into it). Each key is `{t, x, y, z, rx, ry, e}` in master seconds, and `e` is the ease into that key: `spring` for a fly-in from depth that settles, `expo` for a push that lands fast and rests, `smooth` for a glide. Put every key on a story cue (the stamp lands, the prompt arrives, the tool is picked, send, the result writes in). Each move lands in 0.65 s or less, then holds with at most a few px of drift. The field sees the same camera, which is where the parallax comes from.

**Rack focus.** `rack` keys move sharpness from one element to the next (the record that matters is sharp, its neighbours blur), on the cue that makes it matter. Use it for a comparison or a hand-off, not as decoration.

**Event-point flare and ring.** `flares` put a short glow and an expanding shock ring on the element that caused the event (a click, a stamp, a send, a flip). They track the element, so they follow the camera. The white core is capped so a flare never whites out the frame.

**Scene change from the click.** `irises` open the next scene as a disc from the event point with a lit leading edge in the accent colour; the outgoing scene blurs and scales out over the same 0.4 s. The cut is motivated by the action, not by a timer. Use one or two per film; between them, keep morphing one object as in the one-stage film.

**Kinetic type.** `glyphs` land a statement line glyph by glyph from depth with blur, then settle to plain text (transform `none`) before anyone reads it. Use it for one or two statement lines, not for typed UI text or body copy.

**Odometers, real values only.** `odometers` roll digit columns and land on the value. The kit refuses text that is not a number, percent, sign or currency. Only values the film can source (see [evidence](evidence.md)); never a random intermediate number held long enough to read.

**Per-event sound.** Give every event from `kit.events()` a short sound under the score: air on pushes and dollies, a tick on rows and odometer digits, a soft thump on settles, a riser into each iris, a hit on flares. Hits sit about 5 dB over the bed. Master the whole mix to about -16 LUFS, true peak under -1 dBTP, and check the cloud render keeps the level.

## Rules that held in every pass

1. **The camera rests while text is read.** Moves happen between reading moments; during a read only the field behind moves.
2. **Text never translates while it is read.** Glyphs and rows settle before the read starts; a push never carries a line someone is reading.
3. **0 flashes.** No same-frame swap between a light and a dark layer; dissolve a world over at least 6 frames before a bloom or iris peaks. Run the flash detector in `scripts/pace.py` on every render.
4. **Pilot one window first.** Render the busiest 6 to 8 seconds (hook exit, the first push, the first event) before the full film, measure pace and look at stills. One first pilot ran at twice the reference mean because the camera never rested; finding that on a window is cheap.
5. **Measure pace.** Run `python scripts/pace.py film.mp4` on the flat film and on every render, and compare with [pace and digestibility](pace-and-digestibility.md). A local seek estimate (screenshots at 30 fps) matched the cloud render within 0.01 on mean motion, so tune locally and render once.
6. **Every property, every frame.** The kit writes every property it touches on every call. If you add your own motion, do the same: cloud renderers seek out of order, and a value left from an earlier frame shows up as a glitch in one chunk.
7. **Keep it inside action-safe.** Deep pushes move text toward the frame edge. If the safe-area check fails, make the push shallower rather than cutting the move.
8. **Frame 0 still sells.** The hook is complete and readable on frame 0 with the field far back behind it.

## Traps

- Hide containers with `autoAlpha` / `visibility`, and set field visibility from the kit, not with `display`: a card measured while `display: none` has no size.
- The kit file is ASCII only. Some checkers inline scripts into the page, and a stray `</script>` or non-ASCII character in a comment breaks them.
- Media inside a scene must be ready before the renderer's ready flag, or a cloud chunk can start on a black frame.
- Busy edges: a fast, dense field keeps reading seconds moving but crowds the frame edges. Prefer a slower field plus a stronger veil behind text.
