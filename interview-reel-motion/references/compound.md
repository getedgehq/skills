# Compound engine

The same reel also renders in the Compound editor, from `template-compound/`. It reads the same `reel.json`,
`beats.json` and `captions.json`, applies the same rules (`src/engine/rules.ts`) and passes the same QA gates;
the HyperFrames template is the default because it needs no app. Use Compound when the editor is already in the
loop (scrubbing, capture, an export from the app).

When the Edge connector offers Edge Video (`find_tool` lists `video.*` tools, "Edge Video · Powered by Compound"),
Compound is the engine: the connector has found the app running on this Mac. Without it, HyperFrames stays the
default.

## Through Edge Video

The Edge connector wraps the app's MCP tools as Edge tools and keeps the session for you (initialise, session id,
reopening the project if the app restarts). Call them with `use_tool`:

| Edge tool | Compound tool | Use |
| --- | --- | --- |
| `video.open_project` | `open` | once per session, `{"dir": "<absolute project folder>"}`; later calls default to this project |
| `video.check` | `check` | after every edit, `{"id": "<scene id>"}` |
| `video.capture` | `capture` | frames at chosen times, `{"id": "<scene id>", "times": ["0", "1.5"]}` |
| `video.export` | `export` | detached: returns once started, `{"id": "<scene id>", "path": "<absolute .mp4>"}` |
| `video.export_status` | `export_jobs` | poll until the export is done, then move the file off a full disk |
| `video.projects` | `projects` | registered projects |

Runs in the user's own Compound app on the user's plan; Edge charges no credits for these calls.

Workflow: copy `template-compound/` into the workspace's `projects/<name>/`, run `npm i three@0.170.0 --omit=dev`
there, put the footage under `assets/`, point the three imports in `index.tsx` at the reel folder, register the
folder with the MCP `open` tool and run `check`. Flip `src/engine/qa.ts` to `"foot"`, `"gfx"` and `""` for the
three QA renders, export each, trim by frame count.

## Compound specifics

- **MCP.** The Compound app serves MCP over streamable HTTP at `http://127.0.0.1:3284/mcp`. Initialise a session
  (`initialize`, then `notifications/initialized`), keep the `mcp-session-id` header, then call tools.
- **Per-session registration.** Project tools need a project ID. Call `open` with the project folder's absolute
  path at the start of every MCP session (it registers or creates the project and returns the ID); IDs from an
  earlier session are not reused.
- **Projects** live under the workspace's `projects/` directory. A project is a folder with `package.json`
  (`"main": "index.tsx"`), `index.tsx`, `src/` and `assets/`. Media paths in components are relative to `assets/`.
  JSON files import directly (`import beats from "./examples/starter/beats.json"`).
- **Loop.** `check` (structure, no render) after every edit; `capture` at chosen times to look at frames; `export`
  to encode. Exports are long: run them detached and poll, and move each file off a full disk straight away.
- **WebGPU.** Framer and CameraPush are WGSL `<shaderPaint>` passes on `<video>`, because `<video>` has no 3D
  transform. A fragment stage takes at most 12 uniform buffers; Framer uses 11 (5 framing keys plus config), so a
  footage piece carries at most 5 keys. Add a split in `reel.json` instead of more keys. `globals.time` inside a
  shader on a video is the clip's **source** time, so scene time = start + (source t - sourceIn) / rate.
- **html layers.** `<html>` rasterises a DOM subtree. It does not render `<img>` or `<video>`: put logos and stills
  in a native `<image>` node layered over a sized spacer in the html. Avoid `scale()` on big wrappers (use CSS
  `zoom`), map spaces in split glyphs to no-break spaces, and never set a fractional ancestor `opacity` over children
  that carry their own opacity or filter (the subtree blanks): fade with a `<group>` opacity keyframe track instead.
- **Fades.** `<animation>` fade presets front-load on html groups. Ease exits with scene-clock opacity keyframes on
  a `<group start={0} end={...}>` (the engine's `Out` and the overlays' `Frame` do this).
- **The outro.** Exports can end with the editor's outro frame. Trim by frame count (`scripts/trim.py`) and check the
  last 2 s strip.
- **Fonts.** Inter is assumed (`fonts` lists what the machine has). three.js components wait for the font through
  `useTicker().hold`.
