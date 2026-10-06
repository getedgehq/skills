# QA gates

Engine-agnostic: Python 3 plus ffmpeg (set `IRM_FFMPEG` and `IRM_FFPROBE` to pick a binary). `facezone.py` needs
`mediapipe` and its `face_landmarker.task` model; `whisper_diff.py` needs `faster-whisper`. Run the heavy ones on a
build machine, detached, and poll; never block a session for minutes.

Three renders of the same reel feed the gates. Build each into its own folder and render it
(`python3 build.py --data <reel> --assets assets --qa <mode> --out build_<mode>`; with Compound, flip
`src/engine/qa.ts` instead):

| `--qa` | Render | Feeds |
|---|---|---|
| `foot` | picture only | face boxes (facezone, faceboxes, caption placement) |
| `gfx` | graphics and captions alone on magenta `#FF00FF` | facezone, safezones |
| (none) | the final | everything else |

| Gate | Script | Pass |
|---|---|---|
| Readability (before rendering) | `readability.py beats.json captions.json` | 0 failures: every text element complete for max(0.7 s, 0.25 s/word), captions 2 to 5 words, no caption under a non-echo text beat |
| Trim | `trim.py export.mp4 final.mp4 --duration D` | exactly round(D x 30) frames (HyperFrames renders the exact count; Compound exports carry an outro frame to cut) |
| Face zone | `facezone.py --foot foot.mp4 --gfx gfx.mp4 --model face_landmarker.task` | 0 px outside the declared full-frame spans (the takeover, the end fade) |
| Safe zones | `safezones.py --gfx gfx.mp4` | nothing in the top 220, bottom 420, right 150 px outside the same spans |
| Cover | `grid_preview.py final.mp4` | at 360 px wide the hook reads, the logo is inside the crop, one message |
| Flashes | `lumaspikes.py final.mp4 --cuts ...` | no non-cut event that is a flash, snap or pop |
| Captions vs speech | `whisper_diff.py final.mp4 captions.json` | every line heard while it is up (contractions like "gonna" excepted); speech in sync after any ramp |
| Reference | `refgrid.py ref.mp4 final.mp4 --times ...` | same-timestamp pairs look like the reference; PSNR and SSIM per pair; `--min-ssim 0.95` for an engine port or rebuild |
| Ending | `last2s.py final.mp4` | natural expression, slow eased push, 10 to 15 frame fade, no branding |

Report a gate only after running it, with its number. A skipped gate is reported as skipped.
