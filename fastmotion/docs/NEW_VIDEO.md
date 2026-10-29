# Making a new video

## 1. Start from the demo

```bash
bash <skill>/bin/new-video.sh my-video && cd my-video
cp -r src/videos/demo src/videos/myvideo
```

Rename the component (`Demo` → `MyVideo`) and register it in `src/Root.tsx`:

```tsx
<Composition id="MyVideo" component={MyVideo} durationInFrames={Math.round(MY_SEC * FPS)} fps={FPS} width={1920} height={1080} />
```

## 2. Write beats

A video is a list of beats. Each beat has absolute timing, optional engine transitions and a scene:

```tsx
import {Beat, Timeline, totalSec, Stage, TitleBeat, ChatThread, Carousel3D, StatBars, CounterCard, CardFan} from '../../engine';

const beats: (Beat & {el: React.ReactNode})[] = [
  {id: 'Hook', from: 0, to: 3, exit: 'blur', el: <Stage><TitleBeat text="Meet **Pilot**" y={420} size={64} /></Stage>},
  {id: 'Chat', from: 3, to: 9, enter: 'whipL', el: (
    <ChatThread agentName="Pilot" messages={[
      {from: 'agent', text: 'Your ads are fading.', at: 0.4},
      {from: 'user', text: 'Fix it', at: 2.2},
    ]} camera={[{t: 0, z: 1.25}, {t: 4, z: 1}]} />
  )},
];
```

Times inside a scene (`at`, camera `t`) are scene-local seconds.

## 3. Blocks

| Block | Use for |
|---|---|
| `TitleBeat` | typed headline + subline |
| `ChatThread` | agent/user conversation, typing, optional camera + dust |
| `Carousel3D` | stepping through formats/variants with motion blur |
| `CardFan` | one hero spawning variants |
| `StatBars` | before/after metrics |
| `CounterCard` | a big counting number |

For anything bespoke, write a component using the
primitives: `Stage`, `Bubble`, `AgentRow`, `Media`, `Phone`, `Pill`, `Tag`, `Cursor`,
`Camera`, `MotionBlur`, `Depth`, `Dust`, and the timing helpers `pop`, `glide`, `range`,
`typed`, `countUp`.

## 4. Media

`<Media>` renders a photo-like placeholder until you pass `src="media/clip.mp4"`
(files live in `public/media/`). Placeholders keep layout and tonal weight honest
while assets don't exist yet.

## 5. Iterate against a reference you own (optional)

Extract a timestamped contact sheet of the reference and of your render, and compare beat by beat:

```bash
ffmpeg -i reference.mp4 -vf "fps=1,scale=480:-1,tile=6x5" ref-sheet.jpg
npx remotion render MyVideo out/my.mp4 && ffmpeg -i out/my.mp4 -vf "fps=1,scale=480:-1,tile=6x5" my-sheet.jpg
```

Trust stills over metrics, and only rebuild videos you have the rights to.
