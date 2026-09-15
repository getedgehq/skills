---
name: scroll-video-site
description: >-
  Build a website whose background is a full-bleed video that plays forward and
  backward as the visitor scrolls, then check and deploy it. Covers the parts
  that decide whether it feels expensive or broken: encoding the video so seeks
  are instant, smoothing the scrub, keeping text readable with no dark overlay,
  mobile and reduced-motion fallbacks, and a size budget. Use when the user asks
  for a "scroll video", "video tied to scroll", "scrub on scroll", "Apple-style
  scroll animation", "cinematic hero", or gives you an mp4 to put behind a site.
---

# Scroll video site

One prompt gets an agent to put a video behind a page and set `currentTime` on
scroll. That version stutters, jumps when you scroll back up, weighs 40 MB,
hides the footage under a 50% black overlay so the text is legible, and shows a
frozen first frame on iPhone. Every one of those is a decision, not a bug in
the model. This Skill makes the decisions.

Inspired by the workflow Viktor Oddy (motionsites.ai) demonstrates publicly:
reference first, generated hero video, video as the whole page's background,
no overlay, full opacity. The instructions and scripts here are written from
scratch for that technique.

## Before you write any code

1. **Run the video through `scripts/check-scrub.py <video>`.** It reports the
   keyframe interval, audio track, moov position, duration, resolution and size.
   A raw export from a video model almost always fails on keyframe interval.
2. **Encode with `scripts/encode-scrub.sh <video> <outdir>`.** It writes
   `hero-desktop.mp4`, `hero-mobile.mp4`, `poster.jpg` and `poster-mobile.jpg`,
   then re-runs the check on both outputs. Use these files, never the original.
3. **Run `scripts/text-safe-zones.py <outdir>/hero-desktop.mp4`.** It splits the
   frame into a 3x3 grid and reports, across the whole clip, how bright and how
   busy each cell is. Put the headline in the calmest cell and pick its color
   from the brightness. This is how you avoid the overlay.

The scripts need `ffmpeg`, `ffprobe` and Python 3. No Python packages.

## The rules

### 1. Seeks must hit a keyframe

Browsers can only show a frame by decoding forward from the previous keyframe.
Model exports use a keyframe every 2 to 10 seconds, so each scroll tick
decodes up to hundreds of frames, and scrolling backward is worse. The encoder
script sets a keyframe every frame on mobile and every 2 frames on desktop
(`-g`), which makes every seek near-instant. It costs file size, which the next
rule controls.

### 2. Budget: desktop 12 MB, mobile 5 MB

Hit the budget with frame rate and resolution before quality: 24 fps, 1920
wide desktop, 960 wide mobile, CRF 26 to 30. Strip audio (`-an`) and move the
moov atom to the front (`-movflags +faststart`) so playback can start before
the download ends. If a clip is still over budget, shorten it. Six to eight
seconds of footage is plenty for a page that is four to six screens tall.

### 3. Scrub in `requestAnimationFrame`, never in the scroll event

Use `templates/scroll-scrub.js`. It reads scroll progress, eases the video time
toward the target (`current += (target - current) * 0.12`), skips a frame while
`video.seeking` is true so seeks never queue up, and stops the loop when the
value has settled. Setting `currentTime` directly inside `scroll` handlers is
what makes the result feel jittery.

### 4. One fixed video layer for the whole page

The video sits in a `position: fixed` layer at `inset: 0` with
`object-fit: cover`, behind everything, and progress is mapped across the whole
document height. Sections then scroll over footage that keeps moving, which is
what makes hero-to-catalog-to-footer transitions feel continuous. Use `100svh`
for anything that must equal the screen height so mobile address bars do not
resize it mid-scroll.

### 5. No overlay. Legibility comes from composition

Keep the video at 100% opacity with no gradient or tint over it. Instead:

- Place text in the cells `text-safe-zones.py` marks as calm.
- Use its brightness verdict for text color. Mixed cells get a light text
  shadow (`0 1px 24px rgba(0,0,0,.35)`), never a box.
- Content that needs a background (product cards, forms, cart) gets a
  surface of its own: solid, or `backdrop-filter: blur(16px)` with a
  translucent fill. The panel is local; the footage around it stays untouched.
- If no cell is calm, the clip is wrong for a text page. Say so and ask for a
  calmer clip rather than adding an overlay.

### 6. Mobile and reduced motion

- Pick the source in JavaScript by viewport width (the template does this).
  `<source media>` is not reliable across browsers for video.
- Always set `muted playsinline preload="auto"` and a `poster`.
- iOS Safari may not paint a seek until the video has played once. The
  template calls `play()` then `pause()` on the first `touchstart` or
  `scroll`. Test on a real iPhone; if frames still do not paint, switch to the
  frame-sequence path below.
- Under `prefers-reduced-motion: reduce`, show the poster image and do not
  scrub.

### 7. Frame-sequence fallback

When the video path fails on a target device, or the brief needs perfectly
smooth slow scrubbing, export frames instead
(`ffmpeg -i hero-desktop.mp4 -vf fps=24,scale=1600:-1 -q:v 5 f_%04d.jpg`),
preload them, and draw the current frame to a `<canvas>`. Expect roughly 3 to 4
times the bytes of the video. Lazy-load frames beyond the first screen.

### 8. Loading

Show the poster instantly. Hide scroll-dependent UI until
`video.readyState >= 3` (`HAVE_FUTURE_DATA`), or at most 2.5 seconds, then
fade it in. A preloader that blocks the page for longer than that loses more
visitors than the video wins.

## Deploying and checking

Deploy anywhere that serves byte ranges; Vercel, Netlify and Cloudflare Pages
all do. After deploying, confirm range support, because seeking depends on it:

```bash
curl -sI -H "Range: bytes=0-1" https://<site>/hero-desktop.mp4 | head -1   # expect 206
```

Before handing over, check:

- [ ] `check-scrub.py` passes on both encoded files
- [ ] Scroll to the bottom and back to the top quickly: no freeze, no jump
- [ ] Headline readable in every scroll position without an overlay
- [ ] 390px wide viewport: no horizontal scroll, mobile source loaded
- [ ] Reduced motion shows the poster
- [ ] Range request returns 206 on the deployed URL

## What not to do

- Do not add a full-screen dark overlay or lower the video opacity.
- Do not autoplay-loop the video and call it scroll-driven.
- Do not ship the original export from the video model.
- Do not use a scroll library for this alone; the template is ~80 lines.
- Do not put footage of real people, logos or characters you do not have the
  rights to in a site you publish.
