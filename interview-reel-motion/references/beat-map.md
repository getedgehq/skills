# Beat map and reel data

A reel is three JSON files. `template/build.py --data <folder>` reads them and writes the HyperFrames page
(`template/runtime/engine.js` assembles the scene from them). The optional Compound engine reads the same files
(`template-compound/index.tsx`).
All times are **output seconds** on the scene clock (30 fps), snapped to frames (`n / 30`).

## beats.json: time and phrase to component and props

One entry per graphic beat, in stacking order (later entries draw on top).

| Field | Type | Meaning |
|---|---|---|
| `id` | string | unique, used as the node id prefix |
| `t0`, `t1` | seconds | on and off. The engine eases every beat out over its last `exit` frames |
| `component` | string | a name from the registry (see components.md) |
| `layer` | `"overlay"` (default) or `"panel"` | `panel` beats draw on the scene ground **under** the footage (pair them with a card framing key, `m = 1`, so the face sits in a card over the panel) |
| `phrase` | string | the spoken words the beat answers (for review and the audit) |
| `meaning` | string | the one sentence a first-time viewer should get. A beat whose meaning you cannot write is cut |
| `props` | object | the component's props. Times inside props (`inAt`, item `t0`) are absolute scene seconds |
| `exit` | frames | eased exit length for engine-wrapped components, 6 to 8 (default 7) |
| `fadeIn` | frames | optional eased fade-in for engine-wrapped components (plates, the takeover) |
| `echo` | bool | the beat repeats the caption's key word (a sticker on "mom?"), so it may share the screen with that caption |

Example:

```json
[
 { "id": "cover", "t0": 0, "t1": 1.8, "component": "Cover", "phrase": "We crossed ten thousand teams",
   "meaning": "The company passed 10,000 teams against a 6,000 goal.",
   "props": { "chip": { "logo": "brand/logo.png", "label": "Demo Day" }, "lines": ["10,000 teams.", "Goal was 6,000."] } },
 { "id": "counter", "t0": 1.8, "t1": 4.6, "component": "CounterBar", "meaning": "10,000 teams, past the 6,000 goal.",
   "props": { "value": "10,000", "unit": "teams", "progress": 0.92, "goal": 0.552, "goalLabel": "GOAL 6,000", "x": 60, "y": 262, "width": 830, "k": 0.78 } },
 { "id": "word", "t0": 9.0, "t1": 10.4, "component": "Sticker", "echo": true, "meaning": "Keep it simple.",
   "props": { "text": "SIMPLE.", "x": 110, "y": 420, "width": 420, "rot": -6, "size": 76 } }
]
```

The same map as a review table (write this first, then the JSON):

| Time | Line | Component | Meaning |
|---|---|---|---|
| 0 to 1.8 | "We crossed ten thousand teams" | Cover | passed 10,000 against a 6,000 goal |
| 1.8 to 4.6 | "our goal was six thousand" | Plate + CounterBar | 10,000, past the goal |
| 9.0 to 10.4 | "it has to be simple" | Sticker SIMPLE. | keep it simple |

## captions.json: phrase captions

```json
[{ "t0": 4.6, "t1": 5.9, "text": "and we kept going", "y": 1400, "speaker": "guest" }]
```

- 2 to 5 words, one speaker, never split inside an idiom or a title ("over the moon", "co-founder").
- Up from the phrase's first word until the phrase ends plus 0.2 s where room allows, and at least max(0.7 s, 0.25 s per word).
- `y` is the line centre. Place it below the faces (centre at most 1455) or above them (centre at least 265),
  using the per-frame face boxes from `scripts/facezone.py` (`facezone.json`). Never in the face zone.
- Drop the caption when a graphic on screen already carries the same words.

## reel.json: cut list, framing, audio

| Field | Meaning |
|---|---|
| `scene` | `{ id, width: 1080, height: 1920, fill, duration }`. `duration` is the last frame of the end hold |
| `footage` | default source for clips and voice (path under `assets/`) |
| `clips` | the cut list: `{ start, end, sin, rate, src? }`. `sin` is the source second at `start`; `rate` the playback rate (1.2 for a tightened interview; 0.01 for a held frame: the cover and the end hold); `src` overrides the footage (a pre-rendered speed ramp) |
| `framePhase` | optional, HyperFrames only: added to the source frame position before flooring (default 0.001, the exact frame at that time). 0.25 matched a Compound render best in the port test: its browser video seek lands one source frame later on some frames of rate 1.2 clips, and not consistently |
| `splits` | extra cut times inside clips. Each footage piece carries at most 5 framing keys (the WGSL uniform limit), so split long clips where the framing changes |
| `blank` | `[t0, t1]` spans with no picture (a full-frame takeover) |
| `framings` | named boxes `[x, y, w, h]`: where the whole source frame sits in the 1080x1920 frame (a 1440x1920 source fills the height at `[-180, 0, 1440, 1920]`) |
| `keys` | `[t, framing, cardAmount, ease?]`. Between keys the box and the face card mask ease together (`io` inOut, `eo` expoOut, `lin`, `sin`). Two equal keys hold still. `cardAmount` 1 = the face card over a panel |
| `card` | the face card rect and corner radius |
| `audio.voice` | `{ start, sin, sout, rate, gain: [[sourceSecond, dB]] }`; split the voice where a ramp inserts a pause |
| `audio.music` | `{ src, rate, volume, keys: [[sourceSecond, dB]], fadeOut }` |
| `audio.sfx` | `[t, src, sourceIn, sourceOut, dB]`, on graphic pops only, never on caption words |
| `end.fadeFrames` | 10 to 15; the black fade over the held last frame |
| `captionStyle` | caption font size, weight, colour, tracking, width and shadow |

Cover and end: the first clip is the cover frame (`rate 0.01`, the guest's best expression, framed so the hook
sits above the head), and the last clip holds a natural frame after the final line while a key eases a slow push
(`[duration, "ZEND", 0, "sin"]`).
