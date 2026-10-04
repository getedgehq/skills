# Delivery and QA

## Output contract

- 15 to 30 second MP4, 1920×1080, 30 fps, H.264, yuv420p, AAC audio, fast-start metadata.
- Editable HTML/JS timeline and source demo; JSON brief, asset inventory and source ledger.
- Contact sheet and representative first/payoff/end frames.
- The brand kit you used (logo SVGs and token files) kept with the project.
- No font files, third-party paid music, credentials, source video without clearance or fabricated run receipts.

## Tests

1. `python scripts/preflight.py PROJECT --mode preview`: required files, durations, sources, placeholder status, prohibited bundles.
2. `python scripts/preflight.py PROJECT --mode final`: same checks plus final-claim evidence and rights gates.
3. ffprobe: exact dimensions/fps/duration, picture and audio streams, nonzero file.
4. Decode full film with ffmpeg `-v error -f null -`; no decode errors.
5. Inspect each shot and boundary at full-size and 480-pixel-wide scale. Text must stay within the safe area and labels must remain legible.
6. Confirm no missing image, browser error, failed font, frozen scene, blank flash, uncontrolled shimmer or crop.
7. Check audio loudness/true peak, transitions, final decay, and sound-off comprehension.
8. Verify all supplied archive paths and ensure no font binary extension slipped into nested content. Do not package existing archives blindly.

## Installation

This is an Agent Skills directory, not a hosted MCP service. It has a root SKILL.md, references, assets, scripts and templates. Place it in the skill directory supported by your agent, or attach the ZIP and ask the agent to read SKILL.md before working. Exact discovery paths and installation UI vary by host; verify current official documentation before giving host-specific instructions.

Packaging does not install or publish the skill. Do not describe it as installed until that action has been requested and actually completed.

Format reference verified for this package:
https://agentskills.io/specification
