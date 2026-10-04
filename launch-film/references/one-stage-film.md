# The one-stage film (HyperFrames path)

This is the build behind the example films (see `examples/README.md`). Use it when the starter's canvas look is not what you need, or when the film is mostly product UI: a prompt, a document, an inbox, a result.

## The idea

Build the whole film as one live HTML stage driven by one GSAP timeline, rendered with HyperFrames (HTML to MP4). Do not cut between pre-rendered stills. Every beat change is a motion of something already on screen: the highlight behind the hook opens into the workspace, the draft shrinks into the prompt as its attachment, the prompt frame morphs into the result, the skill card docks as the result's tag. Hard swaps between unrelated layouts are what make a film "pop".

## Arc (about 17 seconds at 128 BPM, beat = 0.469 s)

| beat | time | job |
| --- | --- | --- |
| Hook | 0 to 2.8 s | The pain line is readable on frame 0. The second line rises in on beat 1. |
| Problem shown | 2.8 to 5.6 s | The bad draft, the 127-message inbox, the five failed attempts. One stamp lands on the hit. |
| Request + pick | 5.6 to 9.4 s | The real request is typed. On the bar downbeat the tool or skill that was picked appears on the prompt, and its card slides out from under it. No "click to add" button. |
| Result | 9.4 to 12.2 s | On send, the prompt frame becomes the result. Items write in on half beats. |
| Text beat | 12.2 to 15.0 s | One line that says why it matters. |
| End card | 15.0 to 16.9 s | Logo, one line, one destination URL. Locked to the last frame. |

Put every cut on the beat grid, a riser into each cut and an accent on it. Land the end card on a bar downbeat with the resolve chord. `scripts/synthesize_audio.py` holds the instruments (kick, clap, hats, bass, stabs, pad; no samples); write the score to the film's own length and master to about -16 LUFS with true peak under -1 dBTP. The bundled sound effects go on the pick, the card transfer and the result.

## Rules that kept the example films clean

- Text never moves while someone is reading it. Arrivals rise or slide for at most 0.42 s, then hold.
- Typed lines reserve their full layout up front (`visibility`, not `display`), so typing never reflows.
- Set every initial state explicitly at frame 0. `gsap.fromTo` renders its start state immediately, so a card meant to arrive later can sit visible over the hook.
- Hide containers with `autoAlpha`. A child with `visibility: visible` shows through a hidden parent.
- Morph frames with `clip-path` on border and fill layers, not with left/top/width/height, which snap to whole pixels.
- Never switch attempts with a same-time hide-all/show-one. Stack opaque frames and only switch the next one on, or you get a one-frame flash.
- Measure text with the real font loaded before you lay out, and keep long lines inside the title-safe area.
- Use fictional people and companies on screen unless you have permission. Standard sample names (Contoso, Fabrikam) work.

## Render traps

- Cloud render images may have no emoji font. Emoji and symbols such as ✕ render as empty boxes even though local Chrome showed them. Rasterise emoji to PNG and draw symbols as inline SVG, then check stills from the actual render, not from local Chrome.
- Run `npx hyperframes check` on the project and fix contrast and layout findings before rendering.
- Render at the exact size and rate: pass width, height and fps explicitly.

## QA before you call it done

ffprobe (size, rate, frame count, streams), a full decode with `ffmpeg -v error -f null -`, loudness and true peak, a contact sheet every 0.5 s, three full-size stills, a flash detector (frame A, X, B where X differs from both), no unplanned single-frame jumps, no hold over 1.5 s outside the end card, end card frame difference near zero, and a font check. Then look at the stills yourself. Most of the fixes in the example films came from looking, not from the metrics.
