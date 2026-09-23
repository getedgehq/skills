# EDIT.json

One file per video. Paths are relative to the file. Word references are either an index into the
default (first) clip, `14`, or `"clip:14"`. Indices come from `vlog.py transcribe`.

```json
{
  "name": "street",
  "language": "en",
  "vocabulary": "Tenderloin, getedge.cc",
  "clips": {"a": "media/street.MOV", "b": "media/walk.MOV"},
  "crop": {"a": 0.5},
  "keep": [{"clip": "a", "from": 0, "to": 36}],
  "tighten": 0.35,
  "fix": {"a:5-7": "for AI.", "a:12": "privacy"},
  "hook": {"text": "I didn't film the people on this street",
           "kicker": "Tenderloin, San Francisco", "hold": 1.8},
  "captions": {"keys": ["privacy", "street", "respect", "question"]},
  "cards": [
    {"kind": "map", "at": 10, "until": 18, "title": "Tenderloin", "sub": "San Francisco",
     "geojson": "tenderloin.geojson", "attribution": "Map: OpenStreetMap · Boundary: DataSF"},
    {"kind": "stat", "at": 22, "until": 27, "title": "Counted homeless in San Francisco",
     "value": "7,973", "unit": "people in the 2026 count", "total": 7973, "part": 7973,
     "source": "San Francisco Point-in-Time Count 2026"}
  ],
  "broll": [{"clip": "b", "from_s": 39.0, "at": 19, "until": 21, "crop": 0.0}],
  "outro": {"text": "would you have filmed them?", "dur": 2.0},
  "music": {"path": "bed.mp3", "below_lu": 12},
  "loudness": -14
}
```

## Top level

| key | meaning |
|---|---|
| `name` | output file stem: `renders/<name>.mp4`, `.plan.json`, `.qa.json`, `.contact.jpg` |
| `clips` | id -> path. The first id is the default clip for bare word indices |
| `language`, `vocabulary` | passed to Whisper; vocabulary is a spelling hint for names |
| `crop` | per clip, horizontal framing 0..1 when the source is wider than 9:16 (0.5 = centre) |
| `keep` | ordered list of `{clip, from, to}` word ranges, inclusive. This IS the story |
| `tighten` | longest pause kept inside a range, seconds. Longer pauses are cut to this |
| `fix` | `"clip:i"` or `"clip:i-j"` -> the words actually said. Captions use these; ids stay stable |
| `hook` | opening line over the first `hold` s (+0.35 s fade). Captions start after it |
| `captions.keys` | words that get the accent box once spoken. Matched case-insensitively |
| `cards` | full-frame graphics, see below. They may not overlap each other |
| `broll` | cutaways: `clip`, `from_s` (seconds into that clip), `at`, `until`, `crop` |
| `outro` | the last frame held for `dur` s with a closing line pushed in; `{}` for none |
| `music` | optional bed, ducked under the voice, `below_lu` quieter |
| `loudness` | integrated target in LUFS, default -14 |

## Cards

Every card is full frame, lands on its title, builds through its beat and keeps pushing until the
cut. Leave the bottom band (below y 1520 of 1920) empty: captions live there.

`stat`: `title`, `value` (a string, shown exactly), `unit`, `source` (required), and optionally
`total` + `part` for a bar (part == total fills in ink; a smaller part grows in the accent inside a
pale full-length track), `accent: true` for the blue figure. Two consecutive stats read as one
graphic that updates, like 38% -> 98%.

`list`: `title`, `items` (up to 8), optional `pick` (index) and `pick_label`. Items arrive one by
one; the pick lands late and dims the rest. Use it for "which one", "out of thousands", rankings.

`prompt`: `app` (label on the composer), `text` (typed in), optional `title`. The send button
lights up at the end. Use it when the speaker describes asking an AI something.

`map`: `title`, `sub`, and either `geojson` (a Feature/Polygon/MultiPolygon: draws the real
boundary) or `lat` + `lon` (a pin). Optional `zoom_start`, `zoom_end`, `attribution`. Pushes from
city scale to the block grid. Tiles come from OpenStreetMap and are cached; attribute them. A
neighbourhood is a shape, not a pin: get the city's own boundary file when one exists (for San
Francisco, DataSF dataset `gfpk-269f`); Nominatim often has only a point.

## Timing

`at` / `until` resolve to the gap before word `at` and the gap after word `until`, on the final
timeline after tightening, then snap to a frame and to any join within four frames. A card that
would leave a shot under 0.45 s next to a join or another card is stretched over it. The resolved
times are written to `renders/<name>.plan.json`; read it when something lands wrong.
