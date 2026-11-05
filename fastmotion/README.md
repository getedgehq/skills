# fastmotion

A Claude skill and a [Remotion](https://www.remotion.dev) engine for product-launch videos in code.
Motion, pacing and styling are reusable code: camera moves with velocity motion blur, spring
pop-ins, typing chat bubbles, 3D carousels, card fans, stat bars, whip transitions, and warm-grey
plus orange styling tokens.

## Install as a skill

```bash
npx skills add getedgehq/skills --skill fastmotion
```

Then ask Claude for a launch video, an animated explainer, or a rebuild of a video in code. It
reads `SKILL.md` and uses the engine. The skill also works without Claude: the template is a
plain Remotion project.

## Use directly

```bash
bin/new-video.sh ~/videos/my-launch            # engine + Demo video, runs npm install
cd ~/videos/my-launch && npm run dev           # Remotion Studio
npm run render:demo                            # → out/demo.mp4
```

## What's inside

```
SKILL.md            how Claude uses this (workflow, cheat sheet, rules, gotchas)
bin/new-video.sh    scaffold a project from template/
docs/STYLE.md       motion, pacing and styling rules with measured numbers
docs/NEW_VIDEO.md   step-by-step: beats, blocks, media, QA
template/           the Remotion project
  src/engine/         reusable engine (import from 'src/engine')
    constants, theme, anim, motion, transitions, ui, blocks, timeline
  src/videos/demo/    27 s video built only from blocks (fictional brand)
  public/media/       your footage and images (placeholders render until they exist)
```

Work on the engine itself inside `template/`: `cd template && npm install && npm run dev`.

## Requirements

Node 18+, ffmpeg.

## License

Apache-2.0 (see `LICENSE`), Copyright 2026 Floom. Remotion itself is under the Remotion License: free for individuals and companies of up to 3 people, larger companies need a Remotion company license (https://www.remotion.dev/license).
