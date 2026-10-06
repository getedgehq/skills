# HyperFrames engine (default)

HyperFrames (heygen-com/hyperframes, Apache-2.0) renders an HTML page whose look is a pure function of a seek
time. Nothing to install beyond Node 22+, Python 3 (numpy, pillow) and ffmpeg: `npx hyperframes` fetches the CLI,
`build.py` runs the pre-passes (`IRM_FFMPEG` / `IRM_FFPROBE` pick the ffmpeg binaries).

## Layout of `template/`

| Path | What it is |
|---|---|
| `build.py` | pre-passes + page writer: cut list to frame stacks, audio mix, `index.html` (`--qa gfx`/`foot` for the QA renders) |
| `runtime/clock.js` | easings (the kit's cubic beziers), Soften, seeded PRNG, keyed tracks |
| `runtime/rules.js` | the house rules as numbers (same values as the Compound `rules.ts`) |
| `runtime/nodes.js` | html / group / rect / img / text primitives with `update(t)` |
| `runtime/kit.js` | every 2D component (overlays, stickers, panels, counter, orbit cards, camera push) |
| `runtime/three-kit.js` | ParticleText and TypeRing (three.js 0.170 on a canvas, vendored in `vendor/`) |
| `runtime/engine.js` | pieces, framing keys, the Framer, the beat registry, captions, end fade, the clock |
| `fonts/InterVariable.woff2` | Inter 4 (wght + opsz, OFL), subset to Latin plus the symbols the kit sets |
| `tools/ramp.py` | speed ramp pre-render (interpolated frames) |

## The clock

`render(t)` sets every pixel from `t`. It is driven by:

- the `hf-seek` event the runtime dispatches on every seek (the handler calls `waitUntil` on the readiness promise
  until fonts, frame stacks and the three.js pieces are ready);
- a wrapper on `window.__player.renderSeek` (the capture path);
- `#t=<seconds>` in the URL for a plain headless still, and `window.seek(t)` for scripts.

The scene is assembled from data and re-assembled if the runtime re-mounts the composition root, so script-built
nodes cannot be lost between load and capture.

## Footage

Each output frame shows one source frame: `floor((sin + (t - start) * rate) * fps + framePhase)` (`framePhase` in
`reel.json`, default 0.001). `build.py` decodes the
source once and writes exactly those frames to `stacks/<key>/<n>.jpe` (JPEG; the `.jpe` extension keeps the
HyperFrames bundler from inlining a thousand files as data URLs). The engine creates one `<img>` per frame and
shows the current one. Lambda renders never wait on `<video>` seeks, so this is the only exact path there.

Framer: the frame image sits on its framing box with `translate() scale()`; the layer is cut with
`clip-path: inset(top right bottom left round r)`; box, card amount and radius ease together between keys
(`io` = cubic-bezier(0.7, 0, 0.3, 1), `eo` = expo out, `sin`, `lin`). Same maths as the WGSL shader of the
Compound engine.

## Audio

`build.py` mixes the voice cut list (each segment resampled by its rate, dB gain keys in source seconds), the
music bed (rate, dB keys in source seconds, linear fade over `fadeOut` s at the end) and the SFX (dB) into
`assets/mix.wav`, placed as one `<audio>` at the composition root. The page never touches media playback.

## Commands

```bash
python3 build.py --data examples/starter --assets assets --out build          # pre-passes + index.html
npx hyperframes lint build && npx hyperframes validate build                    # 0 errors
npx hyperframes snapshot build --at 0,3.5,9.2 --no-end                          # stills at chosen times
npx hyperframes render build --output final.mp4 --quality high                  # local render
npx hyperframes lambda render build --width 1080 --height 1920 --fps 30 --wait  # AWS Lambda render
python3 build.py ... --qa gfx --out build_gfx  &&  python3 build.py ... --qa foot --out build_foot
```

Local renders need a real ffmpeg on PATH. Long reels or many renders go to Lambda (`hyperframes lambda deploy`
once, then `lambda render` from the project folder; it reads `.hyperframes/lambda-stack-<name>.json`).

## Pitfalls found in the port

- Font names must resolve: the distributed compiler fails closed on any unknown family (`inherit`,
  `-apple-system`). Use `Inter, sans-serif` only.
- Keep the classic runtime inline (`build.py` does): in testing, one external classic script was not executed by
  the Lambda compiler while inline code ran everywhere.
- Do not put the stacks in markup that page scripts move around: build them in the engine.
- Inter 4 has the check mark the kit uses on labels; older Inter builds draw a no-glyph box. Check labels at full
  resolution.

## Port check (HyperFrames rebuild of a shipped Compound reel)

Rendered on AWS Lambda from the same three JSON files, 1265 frames, compared with `refgrid.py --min-ssim 0.95`
on 10 preset times: SSIM mean 0.951, 7 of 10 frames at 0.95 or more. The three below it are not layout
differences: one frame where the Compound render shows the next source frame (its `<video>` seek is not a pure
function of time; across the reel it picks the next frame on a varying share of frames, so no `framePhase`
reproduces it exactly), one dense brick wall where encoder noise dominates (PSNR 30.8 dB), and the particle
takeover, whose thin streaks rasterise slightly differently. Face zone (0 px) and safe zones (0 hits) passed;
flash events (33 against 32, lower peak) and caption sync were in line with the original render; the readability audit is a check on the data, so it
reports the same lines for both engines. Lambda's audio path lands about 0.9 dB below
`assets/mix.wav` (envelope correlation 0.999 with the mix); references/qa.md has the loudnorm fix.

## Matte check (occlusion)

A 6 s test over a face clip (OrbitCards then TypeRing, each as a `back` beat, a Matte beat and a `front` beat,
matte from `scripts/matte_rvm.py`, `noGo` rows from `scripts/faceboxes.py --nogo`) rendered on Lambda: the rear
cards and the ring's back arc pass behind the head for 61 and 85 consecutive frames, with at most 2 px of back
layer showing over the person; face zone 0 px; no halo at the hair edge at 2x. Two things this test fixed: each
Matte beat needs its own copy of the matte stack (one shared element was hidden by the later beat), and the
matte RGB must be the full-resolution frame (a 720 px copy upscaled read softer than the A-roll around it).
In the `--qa gfx` pass the matte is painted magenta, so it still hides the back layers but counts as background.

