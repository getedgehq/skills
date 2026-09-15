---
name: web-hero-video
description: >-
  Plan and generate a short background video for a website hero, sized for
  scroll scrubbing: the shot, the camera move, where the text will sit, the
  prompt for a video model (Seedance, Veo, Kling, Runway, Sora), and a
  still-to-motion fallback with ffmpeg when no video model is available. Use
  when the user asks for a "hero video", "background video for my site",
  "cinematic loop", "video for a landing page", or has a hero image they want
  to bring to life.
---

# Web hero video

A background video for a website is not a short film. It has no sound, nobody
watches it from the start, it will be scrubbed backward and forward, and text
has to sit on top of it. Most generated clips fail one of those, not on beauty
but on fit. This Skill plans the clip for the page first, then writes the
prompt.

Inspired by the workflow Viktor Oddy (motionsites.ai) demonstrates publicly:
start from a reference image, remove its text, animate it into a 16:9 clip of
about 7 seconds with no sound. The planning rules and script here are written
from scratch.

## 1. Write the shot plan before the prompt

Answer these in the conversation, in one short block, before generating
anything:

- **Subject:** one thing. A shoe, a valley, a cave, the night sky. Not a scene
  with five elements.
- **Text zone:** where the headline will sit (for example top-left third).
  That area must stay calm for the whole clip: sky, water, wall, shadow, soft
  focus. Nothing moves through it.
- **Camera move:** exactly one continuous move for the whole clip. Push in,
  pull out, slow pan, rise, orbit. Scrolling maps to that move, so the page
  feels like travel in one direction.
- **Start and end frame:** describe both. The first frame is the poster and
  the first impression. The last frame is what sits behind the footer.
- **Duration:** 6 to 8 seconds. A page four to six screens tall does not need
  more, and every extra second costs megabytes once the clip is re-encoded for
  scrubbing.
- **Light and palette:** name them, and check they match the brand colors the
  site will use.

## 2. Rules for a scrubbable clip

1. **No cuts.** A cut becomes a flash every time someone scrolls past it, in
   both directions. One shot.
2. **No fast motion.** Scrubbing speeds footage up. A move that looks calm at
   1x looks frantic when a visitor flicks the trackpad. Ask for slow, steady
   motion.
3. **No text, logos, watermarks or UI in the frame.** They fight the site's own
   type and they are often the model's hallucinated gibberish.
4. **No people's faces as the subject** unless the brand needs them and you
   have the rights. Faces warp under generation and draw the eye away from the
   headline.
5. **Background elements may move; the text zone may not.** Drifting clouds
   outside the text zone are fine. Flickering leaves behind the headline are
   not.
6. **16:9 at 1080p or better, no audio.** The page crops to portrait on phones
   with `object-fit: cover`, so keep the subject near the center column.

## 3. The prompt

Most video models respond best to a plain, ordered description. Use this
order, one sentence each:

```
[Shot type and lens]. [Subject and setting]. [Camera move, speed, direction].
[Light, time of day, palette]. [What stays still, where the empty space is].
[Constraints: single continuous shot, no cuts, no text, no people, no sound].
```

Example:

```
Wide shot on a 35mm lens. A stone hotel on a snowy ridge above a valley of
clouds. The camera pushes in slowly and steadily toward the hotel over the
whole clip. Blue hour, cold blues with warm window light. The upper left third
is open sky and stays empty. Single continuous shot, no cuts, no text, no
people, no sound.
```

If the user has a reference image, use image-to-video with that image as the
first frame, after removing any text from it. The prompt then only needs the
camera move, what moves, what stays still and the constraints.

Generate two or three variants and pick with the checks below, not by taste
alone.

## 4. Check the clip

With the `scroll-video-site` Skill available, run its scripts on the result:

- `text-safe-zones.py clip.mp4`: the planned text zone must come back calm. If
  it does not, regenerate; do not solve it with an overlay.
- `encode-scrub.sh clip.mp4 out/`: must pass both size budgets. If it does not,
  shorten the clip.

Then scrub it by hand: open it in any player and drag the playhead fast in both
directions. Look for flashes, morphing objects and a jump at either end.

## 5. No video model available: still-to-motion

`scripts/still-to-motion.sh hero.png out.mp4 --move push --seconds 8` turns
one still into a slow, eased camera move (`push`, `pan-left`, `pan-right`,
`rise`; `--amount 0.12` is the zoom or travel). It upscales before cropping so
the move does not step pixel by pixel. It is less alive than a generated clip
and more reliable. Use it when a generation route is blocked or the brand needs
an exact image, then run `encode-scrub.sh` on the result as usual.

## Rights

- Only use a reference image, footage or likeness the user owns or has a
  license for. A Pinterest save is not a license.
- Stock footage with a license (for example Creative Commons with attribution)
  is a valid source; record the author and license in the project, and credit
  it where the license requires.
- Do not generate recognizable real people, trademarked characters or other
  brands' products.
